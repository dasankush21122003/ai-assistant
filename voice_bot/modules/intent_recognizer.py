"""
Intent Recognition module for understanding user queries
"""
import re
from typing import Dict, List, Tuple
from config.settings import Config


class IntentRecognizer:
    def __init__(self):
        """Initialize the Intent Recognizer with keyword-based matching"""
        self.intent_keywords = Config.INTENT_KEYWORDS
        self.context = {}  # Store conversation context

    def recognize_intent(self, text: str) -> Tuple[str, float]:
        """
        Recognize intent from user input text using keyword matching

        Args:
            text (str): User input text

        Returns:
            Tuple[str, float]: (intent_name, confidence_score)
        """
        if not text:
            return 'unknown', 0.0

        # Normalize text
        text_lower = text.lower()

        # Score each intent based on keyword matches
        intent_scores = {}
        for intent, keywords in self.intent_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    # Increase score for exact phrase match
                    score += 1.0
                    # Bonus for word boundary match
                    if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                        score += 0.5

            if score > 0:
                intent_scores[intent] = score

        # Return intent with highest score
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            # Normalize confidence score
            confidence = min(best_intent[1] / 3.0, 1.0)
            return best_intent[0], confidence

        return 'unknown', 0.0

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities from text (basic implementation)

        Args:
            text (str): User input text

        Returns:
            Dict[str, List[str]]: Dictionary of entity types and their values
        """
        entities = {
            'numbers': [],
            'emails': [],
            'dates': [],
            'products': []
        }

        # Extract numbers (potential order IDs, phone numbers)
        numbers = re.findall(r'\b\d+\b', text)
        entities['numbers'] = numbers

        # Extract email addresses
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        entities['emails'] = emails

        # Extract dates (simple patterns)
        dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text)
        entities['dates'] = dates

        # Remove empty entity lists
        entities = {k: v for k, v in entities.items() if v}

        return entities

    def update_context(self, intent: str, entities: Dict[str, List[str]]):
        """
        Update conversation context

        Args:
            intent (str): Recognized intent
            entities (Dict): Extracted entities
        """
        self.context['last_intent'] = intent
        self.context['last_entities'] = entities

    def get_context(self) -> Dict:
        """
        Get current conversation context

        Returns:
            Dict: Current context
        """
        return self.context

    def clear_context(self):
        """Clear conversation context"""
        self.context = {}

    def analyze_query(self, text: str) -> Dict:
        """
        Complete analysis of user query

        Args:
            text (str): User input text

        Returns:
            Dict: Analysis results including intent, entities, and confidence
        """
        intent, confidence = self.recognize_intent(text)
        entities = self.extract_entities(text)
        self.update_context(intent, entities)

        return {
            'text': text,
            'intent': intent,
            'confidence': confidence,
            'entities': entities,
            'context': self.context
        }


class AdvancedIntentRecognizer(IntentRecognizer):
    """
    Advanced intent recognizer that can be extended with ML models
    (Placeholder for future enhancements with Transformers, spaCy, etc.)
    """

    def __init__(self, use_ml_model=False):
        """
        Initialize advanced intent recognizer

        Args:
            use_ml_model (bool): Whether to use ML-based models (future enhancement)
        """
        super().__init__()
        self.use_ml_model = use_ml_model

        # Placeholder for ML model initialization
        # if use_ml_model:
        #     from transformers import pipeline
        #     self.classifier = pipeline("text-classification", model="...")

    def recognize_intent_ml(self, text: str) -> Tuple[str, float]:
        """
        ML-based intent recognition (placeholder for future implementation)

        Args:
            text (str): User input text

        Returns:
            Tuple[str, float]: (intent_name, confidence_score)
        """
        # TODO: Implement ML-based intent recognition
        # Example using Transformers:
        # result = self.classifier(text)
        # return result[0]['label'], result[0]['score']

        # For now, fall back to keyword-based recognition
        return self.recognize_intent(text)


if __name__ == "__main__":
    # Simple test
    recognizer = IntentRecognizer()

    # Test cases
    test_queries = [
        "Hello, how are you?",
        "I want to know about your products",
        "What's the status of my order #12345?",
        "I need help with my account",
        "Thank you, goodbye!"
    ]

    print("Testing Intent Recognizer:")
    print("-" * 50)
    for query in test_queries:
        result = recognizer.analyze_query(query)
        print(f"\nQuery: {query}")
        print(f"Intent: {result['intent']} (Confidence: {result['confidence']:.2f})")
        print(f"Entities: {result['entities']}")
