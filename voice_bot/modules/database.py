"""
Database module for storing conversations, user data, and FAQs
Supports both SQLite (development) and PostgreSQL (production)
"""
import os
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager


class Database:
    """Database handler for voice bot data persistence"""

    def __init__(self, db_path: str = None, db_type: str = "sqlite"):
        """
        Initialize database connection

        Args:
            db_path: Path to database file (for SQLite) or connection string
            db_type: Type of database ('sqlite' or 'postgresql')
        """
        self.db_type = db_type

        if db_path is None:
            # Default to SQLite in data directory
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
            os.makedirs(data_dir, exist_ok=True)
            self.db_path = os.path.join(data_dir, 'voice_bot.db')
        else:
            self.db_path = db_path

        self._initialize_database()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        if self.db_type == "sqlite":
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
        else:
            raise NotImplementedError("PostgreSQL support not yet implemented")

    def _initialize_database(self):
        """Create database tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    intent TEXT,
                    confidence REAL,
                    entities TEXT,
                    response_time REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            """)

            # FAQs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS faqs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    category TEXT,
                    keywords TEXT,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # User profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    name TEXT,
                    email TEXT,
                    phone TEXT,
                    preferences TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Analytics/Metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metadata TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Error logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_type TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    stack_trace TEXT,
                    context TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Insert default FAQs if table is empty
            cursor.execute("SELECT COUNT(*) FROM faqs")
            if cursor.fetchone()[0] == 0:
                self._insert_default_faqs(cursor)

    def _insert_default_faqs(self, cursor):
        """Insert default FAQ entries"""
        default_faqs = [
            {
                'question': 'What are your business hours?',
                'answer': 'We are available 24/7 to assist you with your queries.',
                'category': 'general',
                'keywords': json.dumps(['hours', 'business', 'available', 'open'])
            },
            {
                'question': 'How can I track my order?',
                'answer': 'You can track your order by providing your order number. We will fetch the latest status for you.',
                'category': 'orders',
                'keywords': json.dumps(['track', 'order', 'status', 'shipping'])
            },
            {
                'question': 'What is your return policy?',
                'answer': 'We offer a 30-day return policy on most items. Please contact customer service with your order details.',
                'category': 'returns',
                'keywords': json.dumps(['return', 'refund', 'policy', 'exchange'])
            },
            {
                'question': 'How do I reset my password?',
                'answer': 'You can reset your password by clicking the "Forgot Password" link on the login page or contact support.',
                'category': 'account',
                'keywords': json.dumps(['password', 'reset', 'account', 'login'])
            },
            {
                'question': 'What payment methods do you accept?',
                'answer': 'We accept credit cards, debit cards, PayPal, and other digital payment methods.',
                'category': 'payment',
                'keywords': json.dumps(['payment', 'credit', 'card', 'paypal', 'pay'])
            }
        ]

        for faq in default_faqs:
            cursor.execute("""
                INSERT INTO faqs (question, answer, category, keywords)
                VALUES (?, ?, ?, ?)
            """, (faq['question'], faq['answer'], faq['category'], faq['keywords']))

    # Conversation Management
    def create_conversation(self, session_id: str, user_id: Optional[str] = None) -> int:
        """Create a new conversation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (session_id, user_id) VALUES (?, ?)",
                (session_id, user_id)
            )
            return cursor.lastrowid

    def add_message(self, conversation_id: int, role: str, content: str,
                   intent: Optional[str] = None, confidence: Optional[float] = None,
                   entities: Optional[Dict] = None, response_time: Optional[float] = None):
        """Add a message to a conversation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            entities_json = json.dumps(entities) if entities else None
            cursor.execute("""
                INSERT INTO messages (conversation_id, role, content, intent, confidence, entities, response_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (conversation_id, role, content, intent, confidence, entities_json, response_time))

    def get_conversation_history(self, conversation_id: int) -> List[Dict]:
        """Get all messages in a conversation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM messages
                WHERE conversation_id = ?
                ORDER BY timestamp ASC
            """, (conversation_id,))

            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'id': row['id'],
                    'role': row['role'],
                    'content': row['content'],
                    'intent': row['intent'],
                    'confidence': row['confidence'],
                    'entities': json.loads(row['entities']) if row['entities'] else None,
                    'response_time': row['response_time'],
                    'timestamp': row['timestamp']
                })
            return messages

    # FAQ Management
    def get_faq_by_keywords(self, keywords: List[str]) -> Optional[Dict]:
        """Find FAQ matching given keywords"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM faqs")

            best_match = None
            best_score = 0

            for row in cursor.fetchall():
                faq_keywords = json.loads(row['keywords'])
                score = sum(1 for kw in keywords if any(faq_kw in kw.lower() for faq_kw in faq_keywords))

                if score > best_score:
                    best_score = score
                    best_match = {
                        'id': row['id'],
                        'question': row['question'],
                        'answer': row['answer'],
                        'category': row['category'],
                        'usage_count': row['usage_count']
                    }

            if best_match:
                # Increment usage count
                cursor.execute(
                    "UPDATE faqs SET usage_count = usage_count + 1 WHERE id = ?",
                    (best_match['id'],)
                )
                conn.commit()

            return best_match

    def add_faq(self, question: str, answer: str, category: str, keywords: List[str]):
        """Add a new FAQ"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO faqs (question, answer, category, keywords)
                VALUES (?, ?, ?, ?)
            """, (question, answer, category, json.dumps(keywords)))

    def get_all_faqs(self) -> List[Dict]:
        """Get all FAQs"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM faqs ORDER BY usage_count DESC")

            faqs = []
            for row in cursor.fetchall():
                faqs.append({
                    'id': row['id'],
                    'question': row['question'],
                    'answer': row['answer'],
                    'category': row['category'],
                    'usage_count': row['usage_count']
                })
            return faqs

    # User Profile Management
    def create_or_update_user(self, user_id: str, name: Optional[str] = None,
                             email: Optional[str] = None, phone: Optional[str] = None,
                             preferences: Optional[Dict] = None):
        """Create or update user profile"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            preferences_json = json.dumps(preferences) if preferences else None

            cursor.execute("""
                INSERT INTO user_profiles (user_id, name, email, phone, preferences, last_interaction)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    name = COALESCE(?, name),
                    email = COALESCE(?, email),
                    phone = COALESCE(?, phone),
                    preferences = COALESCE(?, preferences),
                    last_interaction = CURRENT_TIMESTAMP
            """, (user_id, name, email, phone, preferences_json,
                  name, email, phone, preferences_json))

    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()

            if row:
                return {
                    'user_id': row['user_id'],
                    'name': row['name'],
                    'email': row['email'],
                    'phone': row['phone'],
                    'preferences': json.loads(row['preferences']) if row['preferences'] else None,
                    'created_at': row['created_at'],
                    'last_interaction': row['last_interaction']
                }
            return None

    # Analytics
    def log_metric(self, metric_name: str, metric_value: float, metadata: Optional[Dict] = None):
        """Log a metric for analytics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            metadata_json = json.dumps(metadata) if metadata else None
            cursor.execute("""
                INSERT INTO analytics (metric_name, metric_value, metadata)
                VALUES (?, ?, ?)
            """, (metric_name, metric_value, metadata_json))

    def get_metrics_summary(self, metric_name: Optional[str] = None,
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> List[Dict]:
        """Get metrics summary"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM analytics WHERE 1=1"
            params = []

            if metric_name:
                query += " AND metric_name = ?"
                params.append(metric_name)

            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)

            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)

            query += " ORDER BY timestamp DESC"
            cursor.execute(query, params)

            metrics = []
            for row in cursor.fetchall():
                metrics.append({
                    'metric_name': row['metric_name'],
                    'metric_value': row['metric_value'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else None,
                    'timestamp': row['timestamp']
                })
            return metrics

    # Error Logging
    def log_error(self, error_type: str, error_message: str,
                 stack_trace: Optional[str] = None, context: Optional[Dict] = None):
        """Log an error"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            context_json = json.dumps(context) if context else None
            cursor.execute("""
                INSERT INTO error_logs (error_type, error_message, stack_trace, context)
                VALUES (?, ?, ?, ?)
            """, (error_type, error_message, stack_trace, context_json))

    def get_error_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent error logs"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM error_logs
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))

            errors = []
            for row in cursor.fetchall():
                errors.append({
                    'error_type': row['error_type'],
                    'error_message': row['error_message'],
                    'stack_trace': row['stack_trace'],
                    'context': json.loads(row['context']) if row['context'] else None,
                    'timestamp': row['timestamp']
                })
            return errors


if __name__ == "__main__":
    # Test database operations
    db = Database()

    print("Database initialized successfully!")
    print("\nDefault FAQs:")
    faqs = db.get_all_faqs()
    for faq in faqs:
        print(f"- {faq['question']}")
