"""
Test script to verify Voice Bot installation and configuration
"""
import sys
import os

def test_python_version():
    """Test Python version"""
    print("Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor} (Requires 3.8+)")
        return False


def test_imports():
    """Test if all required modules can be imported"""
    print("\nTesting module imports...")
    modules_to_test = [
        ('pyaudio', 'PyAudio'),
        ('google.cloud.speech', 'Google Cloud Speech'),
        ('google.cloud.texttospeech', 'Google Cloud TTS'),
        ('numpy', 'NumPy'),
        ('dotenv', 'python-dotenv'),
    ]

    all_passed = True
    for module_name, display_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"  ✓ {display_name}")
        except ImportError as e:
            print(f"  ✗ {display_name} - {str(e)}")
            all_passed = False

    return all_passed


def test_project_modules():
    """Test if project modules can be imported"""
    print("\nTesting project modules...")

    # Add parent directory to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    project_modules = [
        ('modules.intent_recognizer', 'IntentRecognizer'),
        ('modules.response_generator', 'ResponseGenerator'),
        ('modules.audio_recorder', 'AudioRecorder'),
    ]

    all_passed = True
    for module_name, display_name in project_modules:
        try:
            __import__(module_name)
            print(f"  ✓ {display_name}")
        except ImportError as e:
            print(f"  ✗ {display_name} - {str(e)}")
            all_passed = False

    return all_passed


def test_google_cloud_modules():
    """Test if Google Cloud modules can be imported (may fail without credentials)"""
    print("\nTesting Google Cloud modules...")

    # Add parent directory to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    all_passed = True

    # Test Speech-to-Text
    try:
        from modules.speech_to_text import SpeechToText
        print(f"  ✓ SpeechToText module")
    except Exception as e:
        print(f"  ⚠ SpeechToText module - {str(e)}")
        print(f"     (This may fail without Google Cloud credentials)")
        all_passed = False

    # Test Text-to-Speech
    try:
        from modules.text_to_speech import TextToSpeech
        print(f"  ✓ TextToSpeech module")
    except Exception as e:
        print(f"  ⚠ TextToSpeech module - {str(e)}")
        print(f"     (This may fail without Google Cloud credentials)")
        all_passed = False

    return all_passed


def test_config():
    """Test configuration"""
    print("\nTesting configuration...")

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    try:
        from config.settings import Config

        # Test basic config
        print(f"  ✓ Config loaded")
        print(f"    - Language: {Config.LANGUAGE_CODE}")
        print(f"    - Sample Rate: {Config.SAMPLE_RATE}")

        # Check if .env file exists
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        if os.path.exists(env_file):
            print(f"  ✓ .env file found")
        else:
            print(f"  ⚠ .env file not found (create from .env.example)")

        # Check credentials file
        if Config.GOOGLE_APPLICATION_CREDENTIALS:
            if os.path.exists(Config.GOOGLE_APPLICATION_CREDENTIALS):
                print(f"  ✓ Google Cloud credentials file found")
            else:
                print(f"  ⚠ Google Cloud credentials file not found at:")
                print(f"     {Config.GOOGLE_APPLICATION_CREDENTIALS}")
        else:
            print(f"  ⚠ GOOGLE_APPLICATION_CREDENTIALS not set in .env")

        return True

    except Exception as e:
        print(f"  ✗ Config error - {str(e)}")
        return False


def test_intent_recognition():
    """Test intent recognition functionality"""
    print("\nTesting intent recognition...")

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    try:
        from modules.intent_recognizer import IntentRecognizer

        recognizer = IntentRecognizer()
        intent, confidence = recognizer.recognize_intent("Hello, how are you?")

        if intent == 'greeting':
            print(f"  ✓ Intent recognition working")
            print(f"    - Intent: {intent}")
            print(f"    - Confidence: {confidence:.2f}")
            return True
        else:
            print(f"  ⚠ Unexpected intent: {intent}")
            return False

    except Exception as e:
        print(f"  ✗ Intent recognition test failed - {str(e)}")
        return False


def test_response_generation():
    """Test response generation functionality"""
    print("\nTesting response generation...")

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    try:
        from modules.response_generator import ResponseGenerator

        generator = ResponseGenerator()
        response = generator.generate_response('greeting')

        if response:
            print(f"  ✓ Response generation working")
            print(f"    - Sample response: {response}")
            return True
        else:
            print(f"  ✗ Empty response generated")
            return False

    except Exception as e:
        print(f"  ✗ Response generation test failed - {str(e)}")
        return False


def test_directories():
    """Test if required directories exist"""
    print("\nTesting directory structure...")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    required_dirs = [
        'config',
        'modules',
        'data',
        'data/audio'
    ]

    all_passed = True
    for dir_name in required_dirs:
        dir_path = os.path.join(base_dir, dir_name)
        if os.path.exists(dir_path):
            print(f"  ✓ {dir_name}/")
        else:
            print(f"  ✗ {dir_name}/ (missing)")
            all_passed = False

    return all_passed


def main():
    """Run all tests"""
    print("=" * 60)
    print("Voice Bot Installation Test")
    print("=" * 60)

    tests = [
        ("Python Version", test_python_version),
        ("Package Imports", test_imports),
        ("Project Modules", test_project_modules),
        ("Google Cloud Modules", test_google_cloud_modules),
        ("Configuration", test_config),
        ("Directory Structure", test_directories),
        ("Intent Recognition", test_intent_recognition),
        ("Response Generation", test_response_generation),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed! Voice Bot is ready to use.")
        print("\nNext steps:")
        print("  1. Run 'python demo.py' to see the bot in action (no API required)")
        print("  2. Set up Google Cloud credentials for full voice features")
        print("  3. Run 'python main.py' to start the voice bot")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")
        print("\nCommon fixes:")
        print("  - Install missing packages: pip install -r requirements.txt")
        print("  - Create .env file from .env.example")

    print("=" * 60)


if __name__ == "__main__":
    main()
