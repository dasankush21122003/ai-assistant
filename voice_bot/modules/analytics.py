"""
Analytics module for tracking and analyzing bot performance metrics
Tracks queries, response times, errors, and generates insights
"""
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import json

try:
    from modules.database import Database
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


class AnalyticsTracker:
    """
    Tracks and analyzes voice bot performance metrics
    """

    def __init__(self, database: Optional['Database'] = None):
        """
        Initialize analytics tracker

        Args:
            database: Database instance for persistent storage
        """
        self.database = database
        self.in_memory_metrics = defaultdict(list)
        self.session_start = datetime.now()

    def track_query(self, user_query: str, intent: str, confidence: float,
                   response_time: float, success: bool = True,
                   error_message: Optional[str] = None):
        """
        Track a user query and its processing

        Args:
            user_query: User's input query
            intent: Detected intent
            confidence: Confidence score
            response_time: Time taken to generate response (seconds)
            success: Whether query was handled successfully
            error_message: Error message if query failed
        """
        # Log to database if available
        if self.database:
            try:
                self.database.log_metric('query_count', 1, {
                    'intent': intent,
                    'confidence': confidence,
                    'success': success
                })

                self.database.log_metric('response_time', response_time, {
                    'intent': intent
                })

                if not success and error_message:
                    self.database.log_error('query_processing', error_message, context={
                        'query': user_query,
                        'intent': intent
                    })
            except Exception as e:
                print(f"Failed to log metrics to database: {e}")

        # Store in memory for session statistics
        self.in_memory_metrics['queries'].append({
            'timestamp': datetime.now().isoformat(),
            'intent': intent,
            'confidence': confidence,
            'response_time': response_time,
            'success': success,
            'error_message': error_message
        })

    def track_intent(self, intent: str, confidence: float):
        """Track intent recognition"""
        self.in_memory_metrics['intents'].append({
            'intent': intent,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        })

    def track_error(self, error_type: str, error_message: str, context: Dict = None):
        """
        Track an error occurrence

        Args:
            error_type: Type of error
            error_message: Error message
            context: Additional context about the error
        """
        if self.database:
            try:
                self.database.log_error(error_type, error_message, context=context)
            except Exception as e:
                print(f"Failed to log error: {e}")

        self.in_memory_metrics['errors'].append({
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': error_message,
            'context': context
        })

    def get_session_statistics(self) -> Dict:
        """
        Get statistics for the current session

        Returns:
            Dict: Session statistics
        """
        queries = self.in_memory_metrics.get('queries', [])
        intents = self.in_memory_metrics.get('intents', [])
        errors = self.in_memory_metrics.get('errors', [])

        total_queries = len(queries)
        successful_queries = sum(1 for q in queries if q['success'])
        failed_queries = total_queries - successful_queries

        # Calculate average response time
        response_times = [q['response_time'] for q in queries if q['response_time']]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        # Intent distribution
        intent_counts = defaultdict(int)
        for item in intents:
            intent_counts[item['intent']] += 1

        # Average confidence by intent
        intent_confidences = defaultdict(list)
        for item in intents:
            intent_confidences[item['intent']].append(item['confidence'])

        avg_confidence_by_intent = {
            intent: sum(confidences) / len(confidences)
            for intent, confidences in intent_confidences.items()
        }

        # Error types
        error_counts = defaultdict(int)
        for error in errors:
            error_counts[error['type']] += 1

        session_duration = (datetime.now() - self.session_start).total_seconds()

        return {
            'session_start': self.session_start.isoformat(),
            'session_duration_seconds': session_duration,
            'total_queries': total_queries,
            'successful_queries': successful_queries,
            'failed_queries': failed_queries,
            'success_rate': (successful_queries / total_queries * 100) if total_queries > 0 else 0,
            'average_response_time': avg_response_time,
            'intent_distribution': dict(intent_counts),
            'average_confidence_by_intent': avg_confidence_by_intent,
            'total_errors': len(errors),
            'error_types': dict(error_counts),
            'queries_per_minute': (total_queries / (session_duration / 60)) if session_duration > 0 else 0
        }

    def get_database_statistics(self, days: int = 7) -> Dict:
        """
        Get statistics from database for the specified period

        Args:
            days: Number of days to look back

        Returns:
            Dict: Database statistics
        """
        if not self.database:
            return {'error': 'Database not available'}

        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

            # Get query metrics
            query_metrics = self.database.get_metrics_summary('query_count', start_date=start_date)
            response_time_metrics = self.database.get_metrics_summary('response_time', start_date=start_date)

            total_queries = len(query_metrics)
            successful_queries = sum(1 for m in query_metrics
                                   if m['metadata'] and m['metadata'].get('success'))

            # Calculate average response time
            avg_response_time = (sum(m['metric_value'] for m in response_time_metrics) /
                               len(response_time_metrics) if response_time_metrics else 0)

            # Intent distribution
            intent_counts = defaultdict(int)
            intent_confidences = defaultdict(list)

            for metric in query_metrics:
                if metric['metadata']:
                    intent = metric['metadata'].get('intent', 'unknown')
                    confidence = metric['metadata'].get('confidence', 0)
                    intent_counts[intent] += 1
                    intent_confidences[intent].append(confidence)

            avg_confidence_by_intent = {
                intent: sum(confidences) / len(confidences)
                for intent, confidences in intent_confidences.items()
            }

            # Get error logs
            error_logs = self.database.get_error_logs(limit=1000)
            recent_errors = [e for e in error_logs
                           if datetime.fromisoformat(e['timestamp']) >= datetime.fromisoformat(start_date)]

            error_counts = defaultdict(int)
            for error in recent_errors:
                error_counts[error['error_type']] += 1

            return {
                'period_days': days,
                'start_date': start_date,
                'total_queries': total_queries,
                'successful_queries': successful_queries,
                'failed_queries': total_queries - successful_queries,
                'success_rate': (successful_queries / total_queries * 100) if total_queries > 0 else 0,
                'average_response_time': avg_response_time,
                'intent_distribution': dict(intent_counts),
                'average_confidence_by_intent': avg_confidence_by_intent,
                'total_errors': len(recent_errors),
                'error_types': dict(error_counts),
                'queries_per_day': total_queries / days if days > 0 else 0
            }

        except Exception as e:
            return {'error': f'Failed to get database statistics: {str(e)}'}

    def get_intent_performance(self) -> Dict:
        """Get performance metrics by intent"""
        queries = self.in_memory_metrics.get('queries', [])

        intent_stats = defaultdict(lambda: {
            'count': 0,
            'total_response_time': 0,
            'total_confidence': 0,
            'successes': 0,
            'failures': 0
        })

        for query in queries:
            intent = query['intent']
            stats = intent_stats[intent]

            stats['count'] += 1
            stats['total_response_time'] += query['response_time']
            stats['total_confidence'] += query['confidence']

            if query['success']:
                stats['successes'] += 1
            else:
                stats['failures'] += 1

        # Calculate averages
        result = {}
        for intent, stats in intent_stats.items():
            count = stats['count']
            result[intent] = {
                'count': count,
                'avg_response_time': stats['total_response_time'] / count,
                'avg_confidence': stats['total_confidence'] / count,
                'success_rate': (stats['successes'] / count * 100) if count > 0 else 0
            }

        return result

    def get_error_summary(self) -> Dict:
        """Get summary of errors"""
        errors = self.in_memory_metrics.get('errors', [])

        error_summary = defaultdict(lambda: {
            'count': 0,
            'latest_occurrence': None,
            'sample_messages': []
        })

        for error in errors:
            error_type = error['type']
            summary = error_summary[error_type]

            summary['count'] += 1
            summary['latest_occurrence'] = error['timestamp']

            # Keep only last 3 sample messages
            if len(summary['sample_messages']) < 3:
                summary['sample_messages'].append(error['message'])

        return dict(error_summary)

    def get_dashboard_data(self) -> Dict:
        """
        Get comprehensive dashboard data

        Returns:
            Dict: All metrics for dashboard display
        """
        return {
            'session_stats': self.get_session_statistics(),
            'intent_performance': self.get_intent_performance(),
            'error_summary': self.get_error_summary(),
            'database_stats': self.get_database_statistics() if self.database else None
        }

    def export_metrics(self, filepath: str):
        """
        Export metrics to JSON file

        Args:
            filepath: Path to export file
        """
        data = self.get_dashboard_data()

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Metrics exported to {filepath}")

    def reset_session_metrics(self):
        """Reset session metrics"""
        self.in_memory_metrics = defaultdict(list)
        self.session_start = datetime.now()


class MetricsCollector:
    """
    Context manager for collecting metrics around operations
    """

    def __init__(self, tracker: AnalyticsTracker, operation_name: str):
        """
        Initialize metrics collector

        Args:
            tracker: AnalyticsTracker instance
            operation_name: Name of the operation being tracked
        """
        self.tracker = tracker
        self.operation_name = operation_name
        self.start_time = None
        self.success = True
        self.error_message = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed_time = time.time() - self.start_time

        if exc_type is not None:
            self.success = False
            self.error_message = str(exc_val)

        # Log based on operation type
        if self.tracker.database:
            self.tracker.database.log_metric(
                f'{self.operation_name}_time',
                elapsed_time,
                {'success': self.success}
            )

        return False  # Don't suppress exceptions


if __name__ == "__main__":
    # Test analytics
    from modules.database import Database

    db = Database()
    tracker = AnalyticsTracker(database=db)

    # Simulate some queries
    tracker.track_query("Hello", "greeting", 0.95, 0.5, True)
    tracker.track_query("Check my order", "order_status", 0.85, 0.8, True)
    tracker.track_query("Unknown query", "unknown", 0.3, 1.2, False, "Low confidence")

    # Get statistics
    stats = tracker.get_session_statistics()

    print("Session Statistics:")
    print(json.dumps(stats, indent=2))
