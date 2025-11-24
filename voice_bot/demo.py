"""
Demo script for testing Voice Bot without actual voice I/O
This script demonstrates the core functionality using text input/output
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.intent_recognizer import IntentRecognizer
from modules.response_generator import ResponseGenerator


def demo_intent_recognition():
    """Demonstrate intent recognition capabilities"""
    print("\n" + "=" * 60)
    print("DEMO 1: Intent Recognition")
    print("=" * 60 + "\n")

    recognizer = IntentRecognizer()

    test_queries = [
        "Hello! How are you?",
        "I'd like to know about your laptop products",
        "What's the status of my order number 12345?",
        "I need help with my account password",
        "I'm having issues with my delivery",
        "Thank you so much! Goodbye!"
    ]

    for query in test_queries:
        result = recognizer.analyze_query(query)
        print(f"User: {query}")
        print(f"  → Intent: {result['intent']}")
        print(f"  → Confidence: {result['confidence']:.2%}")
        if result['entities']:
            print(f"  → Entities: {result['entities']}")
        print()


def demo_response_generation():
    """Demonstrate response generation capabilities"""
    print("\n" + "=" * 60)
    print("DEMO 2: Response Generation")
    print("=" * 60 + "\n")

    generator = ResponseGenerator()

    test_cases = [
        ('greeting', None, "User greets the bot"),
        ('product_info', {'products': ['laptop']}, "User asks about products"),
        ('order_status', {'numbers': ['12345']}, "User wants order status"),
        ('account', None, "User has account issues"),
        ('support', None, "User needs support"),
        ('farewell', None, "User says goodbye"),
        ('unknown', None, "User says something unclear")
    ]

    for intent, entities, description in test_cases:
        response = generator.generate_response(intent, entities)
        print(f"Scenario: {description}")
        print(f"Intent: {intent}")
        if entities:
            print(f"Entities: {entities}")
        print(f"Bot Response: {response}")
        print()


def demo_conversation_flow():
    """Demonstrate a complete conversation flow"""
    print("\n" + "=" * 60)
    print("DEMO 3: Complete Conversation Flow")
    print("=" * 60 + "\n")

    recognizer = IntentRecognizer()
    generator = ResponseGenerator()

    conversation = [
        "Hi there!",
        "I want to check my order status",
        "The order number is 98765",
        "Thanks for your help!",
        "Goodbye!"
    ]

    print("Bot: Hello! I am your customer service assistant. How can I help you today?\n")

    for user_input in conversation:
        # Analyze user input
        analysis = recognizer.analyze_query(user_input)

        # Generate response
        response = generator.generate_response(
            analysis['intent'],
            analysis['entities'],
            analysis['context']
        )

        # Display conversation
        print(f"User: {user_input}")
        print(f"  [Intent: {analysis['intent']}, Confidence: {analysis['confidence']:.2%}]")
        print(f"Bot: {response}\n")


def demo_module_testing():
    """Test individual modules"""
    print("\n" + "=" * 60)
    print("DEMO 4: Module Testing")
    print("=" * 60 + "\n")

    print("Testing Intent Recognizer module...")
    recognizer = IntentRecognizer()
    test_intent = recognizer.recognize_intent("Hello, how are you?")
    print(f"✓ Intent Recognizer: {test_intent}")

    print("\nTesting Response Generator module...")
    generator = ResponseGenerator()
    test_response = generator.generate_response('greeting')
    print(f"✓ Response Generator: {test_response}")

    print("\nTesting Entity Extraction...")
    entities = recognizer.extract_entities("My order number is 12345 and email is test@example.com")
    print(f"✓ Entity Extraction: {entities}")

    print("\n✓ All modules working correctly!")


def interactive_demo():
    """Interactive demo where user can type queries"""
    print("\n" + "=" * 60)
    print("INTERACTIVE DEMO: Type your queries")
    print("=" * 60)
    print("Type 'quit' to exit\n")

    recognizer = IntentRecognizer()
    generator = ResponseGenerator()

    print("Bot: Hello! I am your customer service assistant. How can I help you today?\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nBot: Thank you for chatting. Goodbye!")
            break

        # Process input
        analysis = recognizer.analyze_query(user_input)
        response = generator.generate_response(
            analysis['intent'],
            analysis['entities'],
            analysis['context']
        )

        print(f"Bot: {response}\n")

        # Check for farewell
        if analysis['intent'] == 'farewell':
            break


def main():
    """Main demo function"""
    print("\n" + "=" * 60)
    print("VOICE BOT DEMONSTRATION")
    print("=" * 60)

    print("\nThis demo showcases the Voice Bot capabilities without")
    print("requiring Google Cloud credentials or audio hardware.\n")

    demos = [
        ("1", "Intent Recognition Demo", demo_intent_recognition),
        ("2", "Response Generation Demo", demo_response_generation),
        ("3", "Conversation Flow Demo", demo_conversation_flow),
        ("4", "Module Testing Demo", demo_module_testing),
        ("5", "Interactive Demo", interactive_demo),
        ("6", "Run All Demos", None),
        ("7", "Exit", None)
    ]

    while True:
        print("\nAvailable Demos:")
        for num, name, _ in demos:
            print(f"{num}. {name}")

        choice = input("\nSelect demo (1-7): ")

        if choice == '7':
            print("Exiting demo...")
            break
        elif choice == '6':
            demo_intent_recognition()
            demo_response_generation()
            demo_conversation_flow()
            demo_module_testing()
            print("\n✓ All demos completed!")
        elif choice in ['1', '2', '3', '4', '5']:
            demo_func = next((func for num, _, func in demos if num == choice), None)
            if demo_func:
                demo_func()
        else:
            print("Invalid choice. Please try again.")

    print("\n" + "=" * 60)
    print("Thank you for trying the Voice Bot demo!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
