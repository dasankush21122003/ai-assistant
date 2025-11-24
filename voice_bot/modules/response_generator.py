"""
Response Generation module for creating bot responses
Supports both template-based and AI-powered (OpenAI GPT) response generation
"""
import os
import random
from typing import Dict, List, Optional
from config.settings import Config

# Try to import OpenAI - it's optional
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Try to import database module
try:
    from modules.database import Database
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


class ResponseGenerator:
    def __init__(self):
        """Initialize the Response Generator with template-based responses"""
        self.response_templates = Config.RESPONSE_TEMPLATES
        self.conversation_history = []

    def generate_response(self, intent: str, entities: Dict = None, context: Dict = None) -> str:
        """
        Generate a response based on intent and entities

        Args:
            intent (str): Recognized intent
            entities (Dict, optional): Extracted entities
            context (Dict, optional): Conversation context

        Returns:
            str: Generated response
        """
        # Get response templates for the intent
        templates = self.response_templates.get(intent, self.response_templates['unknown'])

        # Select a random template to add variety
        base_response = random.choice(templates)

        # Enhance response with entity information if available
        if entities and intent in ['order_status', 'product_info']:
            base_response = self._enhance_with_entities(base_response, entities)

        # Add context-aware enhancements if needed
        if context:
            base_response = self._add_context_awareness(base_response, context)

        # Store in conversation history
        self.conversation_history.append({
            'intent': intent,
            'response': base_response
        })

        return base_response

    def _enhance_with_entities(self, response: str, entities: Dict) -> str:
        """
        Enhance response with entity information

        Args:
            response (str): Base response
            entities (Dict): Extracted entities

        Returns:
            str: Enhanced response
        """
        # Add order number if available
        if 'numbers' in entities and entities['numbers']:
            order_num = entities['numbers'][0]
            response += f" I see you mentioned order number {order_num}."

        # Add email if available
        if 'emails' in entities and entities['emails']:
            email = entities['emails'][0]
            response += f" I'll send updates to {email}."

        return response

    def _add_context_awareness(self, response: str, context: Dict) -> str:
        """
        Add context-aware enhancements to response

        Args:
            response (str): Base response
            context (Dict): Conversation context

        Returns:
            str: Context-enhanced response
        """
        # Check if this is a follow-up query
        if context.get('last_intent') and len(self.conversation_history) > 0:
            # Add continuity to conversation
            last_intent = context.get('last_intent')
            if last_intent == 'product_info':
                response += " Is there anything specific about the product you'd like to know?"

        return response

    def generate_clarification(self, missing_info: str) -> str:
        """
        Generate a clarification request

        Args:
            missing_info (str): Type of missing information

        Returns:
            str: Clarification request
        """
        clarifications = {
            'order_number': "Could you please provide your order number?",
            'product_name': "Which product are you asking about?",
            'email': "Could you provide your email address?",
            'phone': "What's your phone number?",
            'details': "Could you provide more details about your query?"
        }

        return clarifications.get(missing_info, "Could you provide more information?")

    def generate_error_response(self) -> str:
        """
        Generate a response for error scenarios

        Returns:
            str: Error response
        """
        error_responses = [
            "I'm sorry, I'm having trouble processing your request. Could you try again?",
            "Oops! Something went wrong. Please rephrase your question.",
            "I apologize, but I didn't catch that. Can you say it again?"
        ]

        return random.choice(error_responses)

    def get_conversation_history(self) -> List[Dict]:
        """
        Get conversation history

        Returns:
            List[Dict]: Conversation history
        """
        return self.conversation_history

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []


class AdvancedResponseGenerator(ResponseGenerator):
    """
    Advanced response generator with AI model integration
    Supports OpenAI GPT for dynamic, context-aware responses
    """

    def __init__(self, use_ai_model=False, api_key=None, database: Optional['Database'] = None):
        """
        Initialize advanced response generator

        Args:
            use_ai_model (bool): Whether to use AI models for response generation
            api_key (str): API key for OpenAI (can also be set via OPENAI_API_KEY env var)
            database (Database): Database instance for FAQ lookup
        """
        super().__init__()
        self.use_ai_model = use_ai_model and OPENAI_AVAILABLE
        self.database = database

        # Initialize OpenAI client if requested and available
        self.ai_client = None
        if self.use_ai_model:
            if not api_key:
                api_key = os.getenv('OPENAI_API_KEY')

            if api_key:
                try:
                    self.ai_client = OpenAI(api_key=api_key)
                    print("OpenAI client initialized successfully")
                except Exception as e:
                    print(f"Failed to initialize OpenAI client: {e}")
                    self.use_ai_model = False
            else:
                print("No OpenAI API key provided, falling back to template-based responses")
                self.use_ai_model = False

    def generate_response(self, intent: str, entities: Dict = None, context: Dict = None,
                         user_query: str = None) -> str:
        """
        Generate response using AI or templates based on configuration

        Args:
            intent (str): Recognized intent
            entities (Dict, optional): Extracted entities
            context (Dict, optional): Conversation context
            user_query (str, optional): Original user query for AI generation

        Returns:
            str: Generated response
        """
        # Try FAQ lookup first if database is available
        if self.database and user_query:
            faq_response = self._check_faq(user_query)
            if faq_response:
                return faq_response

        # Use AI if enabled and user query is available
        if self.use_ai_model and self.ai_client and user_query:
            try:
                return self.generate_response_ai(intent, user_query, entities, context)
            except Exception as e:
                print(f"AI generation failed: {e}, falling back to templates")

        # Fall back to template-based generation
        return super().generate_response(intent, entities, context)

    def _check_faq(self, user_query: str) -> Optional[str]:
        """
        Check if user query matches any FAQ

        Args:
            user_query (str): User's question

        Returns:
            str: FAQ answer if found, None otherwise
        """
        if not self.database:
            return None

        try:
            # Extract keywords from query
            keywords = user_query.lower().split()
            faq = self.database.get_faq_by_keywords(keywords)

            if faq:
                return faq['answer']
        except Exception as e:
            print(f"FAQ lookup failed: {e}")

        return None

    def generate_response_ai(self, intent: str, user_query: str,
                            entities: Dict = None, context: Dict = None) -> str:
        """
        Generate response using OpenAI GPT

        Args:
            intent (str): Recognized intent
            user_query (str): Original user query
            entities (Dict, optional): Extracted entities
            context (Dict, optional): Conversation context

        Returns:
            str: AI-generated response
        """
        if not self.ai_client:
            return self.generate_response(intent, entities, context)

        # Build context for AI
        system_prompt = """You are a helpful customer service assistant for a voice bot system.
Your responses should be:
- Concise and clear (2-3 sentences maximum)
- Friendly and professional
- Action-oriented when appropriate
- Natural for speech synthesis

Do not use special characters or formatting that would sound awkward when spoken."""

        # Build user prompt with context
        user_prompt = f"User query: {user_query}\n"
        user_prompt += f"Detected intent: {intent}\n"

        if entities:
            user_prompt += f"Extracted entities: {entities}\n"

        if context and context.get('last_intent'):
            user_prompt += f"Previous intent: {context.get('last_intent')}\n"

        user_prompt += "\nGenerate a helpful, natural-sounding response:"

        try:
            # Call OpenAI API
            response = self.ai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )

            ai_response = response.choices[0].message.content.strip()

            # Store in conversation history
            self.conversation_history.append({
                'intent': intent,
                'response': ai_response,
                'method': 'ai'
            })

            return ai_response

        except Exception as e:
            print(f"OpenAI API error: {e}")
            # Fall back to template-based response
            return super().generate_response(intent, entities, context)


if __name__ == "__main__":
    # Simple test
    generator = ResponseGenerator()

    print("Testing Response Generator:")
    print("-" * 50)

    # Test cases
    test_cases = [
        ('greeting', None, None),
        ('product_info', {'products': ['laptop']}, None),
        ('order_status', {'numbers': ['12345']}, None),
        ('farewell', None, None)
    ]

    for intent, entities, context in test_cases:
        response = generator.generate_response(intent, entities, context)
        print(f"\nIntent: {intent}")
        print(f"Response: {response}")
