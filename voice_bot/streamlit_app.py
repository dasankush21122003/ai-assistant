"""
Streamlit Web Interface for Voice Bot with Analytics Dashboard
A modern, interactive web UI with database integration and performance monitoring
"""
import os
import sys
import base64
import tempfile
import time
from datetime import datetime
import streamlit as st
from audio_recorder_streamlit import audio_recorder

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.speech_to_text import SpeechToText
from modules.text_to_speech import TextToSpeech
from modules.intent_recognizer import IntentRecognizer
from modules.response_generator import AdvancedResponseGenerator
from modules.database import Database
from modules.analytics import AnalyticsTracker
from config.settings import Config


# Page configuration
st.set_page_config(
    page_title="AI Voice Assistant",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main { padding: 0rem 1rem; }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #667eea;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #5568d3;
        border-color: #5568d3;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #667eea;
        color: white;
        margin-left: 20%;
    }
    .bot-message {
        background-color: #f0f2f6;
        margin-right: 20%;
    }
    .message-header {
        font-weight: bold;
        margin-bottom: 0.5rem;
        font-size: 0.9em;
    }
    .message-content {
        font-size: 1em;
        line-height: 1.5;
    }
    .info-box {
        background-color: #e8eaf6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .intent-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        background-color: #667eea;
        color: white;
        font-size: 0.8em;
        margin-right: 0.5rem;
    }
    .confidence-bar {
        height: 8px;
        background-color: #e0e0e0;
        border-radius: 4px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    .confidence-fill {
        height: 100%;
        background-color: #667eea;
        transition: width 0.3s ease;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = None
if 'show_analysis' not in st.session_state:
    st.session_state.show_analysis = True
if 'use_ai_responses' not in st.session_state:
    st.session_state.use_ai_responses = False


@st.cache_resource
def initialize_bot():
    """Initialize the voice bot components"""
    try:
        Config.validate()

        # Initialize database
        db = Database()

        # Initialize analytics tracker
        analytics = AnalyticsTracker(database=db)

        # Check for OpenAI API key
        openai_key = os.getenv('OPENAI_API_KEY')
        use_ai = openai_key is not None

        # Initialize advanced response generator
        response_gen = AdvancedResponseGenerator(
            use_ai_model=use_ai,
            api_key=openai_key,
            database=db
        )

        return {
            'stt': SpeechToText(),
            'tts': TextToSpeech(),
            'intent_recognizer': IntentRecognizer(),
            'response_generator': response_gen,
            'database': db,
            'analytics': analytics,
            'initialized': True,
            'ai_available': use_ai
        }
    except Exception as e:
        st.error(f"Error initializing bot: {str(e)}")
        return {'initialized': False, 'error': str(e)}


def autoplay_audio(audio_bytes):
    """Autoplay audio in the browser"""
    audio_base64 = base64.b64encode(audio_bytes).decode()
    audio_html = f"""
    <audio autoplay>
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)


def process_message(user_input, bot_components, is_audio=False):
    """Process user input and generate response"""
    start_time = time.time()
    success = True
    error_msg = None

    try:
        with st.spinner('Processing your message...'):
            # If audio, transcribe first
            if is_audio:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                    tmp_file.write(user_input)
                    tmp_path = tmp_file.name

                user_text = bot_components['stt'].transcribe_audio_file(tmp_path)
                os.unlink(tmp_path)

                if not user_text:
                    st.error("Failed to transcribe audio")
                    return None
            else:
                user_text = user_input

            # Analyze intent
            analysis = bot_components['intent_recognizer'].analyze_query(user_text)

            # Generate response
            response_text = bot_components['response_generator'].generate_response(
                analysis['intent'],
                analysis['entities'],
                analysis['context'],
                user_query=user_text
            )

            # Generate audio response
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = os.path.join(os.path.dirname(__file__), 'data', 'audio')
            os.makedirs(output_dir, exist_ok=True)

            audio_file = os.path.join(output_dir, f'response_{timestamp}.mp3')
            bot_components['tts'].synthesize_speech(response_text, audio_file)

            with open(audio_file, 'rb') as f:
                audio_bytes = f.read()

            response_time = time.time() - start_time

            # Track analytics
            bot_components['analytics'].track_query(
                user_text,
                analysis['intent'],
                analysis['confidence'],
                response_time,
                success=True
            )

            # Save to database
            if st.session_state.conversation_id:
                bot_components['database'].add_message(
                    st.session_state.conversation_id,
                    'user',
                    user_text,
                    analysis['intent'],
                    analysis['confidence'],
                    analysis['entities']
                )

                bot_components['database'].add_message(
                    st.session_state.conversation_id,
                    'assistant',
                    response_text,
                    response_time=response_time
                )

            return {
                'user_text': user_text,
                'response_text': response_text,
                'intent': analysis['intent'],
                'confidence': analysis['confidence'],
                'entities': analysis['entities'],
                'audio_bytes': audio_bytes,
                'response_time': response_time
            }

    except Exception as e:
        success = False
        error_msg = str(e)
        response_time = time.time() - start_time

        # Track error
        bot_components['analytics'].track_error('processing_error', error_msg, {
            'user_input': user_input[:100] if not is_audio else 'audio'
        })

        st.error(f"Error processing message: {error_msg}")
        return None


def display_message(role, content, intent=None, confidence=None, response_time=None):
    """Display a chat message"""
    css_class = "user-message" if role == "user" else "bot-message"
    icon = "[User]" if role == "user" else "[Bot]"

    message_html = f"""
    <div class="chat-message {css_class}">
        <div class="message-header">{icon} {role.title()}</div>
        <div class="message-content">{content}</div>
    """

    if intent and confidence is not None:
        message_html += f"""
        <div style="margin-top: 0.8rem; font-size: 0.85em; opacity: 0.9;">
            <span class="intent-badge">{intent}</span>
            <span>Confidence: {confidence:.0%}</span>
        """
        if response_time:
            message_html += f" | Response time: {response_time:.2f}s"

        message_html += """
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: {:.0%};"></div>
            </div>
        </div>
        """.format(confidence)

    message_html += "</div>"
    st.markdown(message_html, unsafe_allow_html=True)


def show_analytics_dashboard(bot_components):
    """Show analytics dashboard"""
    st.header("Analytics Dashboard")

    analytics = bot_components['analytics']
    stats = analytics.get_session_statistics()

    # Session overview
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Queries", stats['total_queries'])

    with col2:
        st.metric("Success Rate", f"{stats['success_rate']:.1f}%")

    with col3:
        st.metric("Avg Response Time", f"{stats['average_response_time']:.2f}s")

    with col4:
        st.metric("Total Errors", stats['total_errors'])

    # Intent distribution
    if stats['intent_distribution']:
        st.subheader("Intent Distribution")
        st.bar_chart(stats['intent_distribution'])

    # Intent performance
    intent_perf = analytics.get_intent_performance()
    if intent_perf:
        st.subheader("Intent Performance")

        perf_data = []
        for intent, data in intent_perf.items():
            perf_data.append({
                'Intent': intent,
                'Count': data['count'],
                'Avg Response Time': f"{data['avg_response_time']:.2f}s",
                'Avg Confidence': f"{data['avg_confidence']:.0%}",
                'Success Rate': f"{data['success_rate']:.1f}%"
            })

        st.table(perf_data)

    # Error summary
    error_summary = analytics.get_error_summary()
    if error_summary:
        st.subheader("Error Summary")
        for error_type, data in error_summary.items():
            with st.expander(f"{error_type} ({data['count']} occurrences)"):
                st.write(f"Latest: {data['latest_occurrence']}")
                st.write("Sample messages:")
                for msg in data['sample_messages']:
                    st.text(f"- {msg}")

    # Database statistics (if available)
    if bot_components['database']:
        st.subheader("Historical Data (Last 7 Days)")
        db_stats = analytics.get_database_statistics(days=7)

        if 'error' not in db_stats:
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Queries (7d)", db_stats['total_queries'])

            with col2:
                st.metric("Queries/Day", f"{db_stats['queries_per_day']:.1f}")

            with col3:
                st.metric("Avg Response Time", f"{db_stats['average_response_time']:.2f}s")


def show_faq_manager(bot_components):
    """Show FAQ management interface"""
    st.header("FAQ Management")

    db = bot_components['database']

    # Display existing FAQs
    st.subheader("Current FAQs")
    faqs = db.get_all_faqs()

    for faq in faqs:
        with st.expander(f"{faq['question']} (used {faq['usage_count']} times)"):
            st.write(f"**Answer:** {faq['answer']}")
            st.write(f"**Category:** {faq['category']}")

    # Add new FAQ
    st.subheader("Add New FAQ")

    with st.form("add_faq"):
        question = st.text_input("Question")
        answer = st.text_area("Answer")
        category = st.selectbox("Category", ["general", "orders", "returns", "account", "payment", "other"])
        keywords = st.text_input("Keywords (comma-separated)")

        submitted = st.form_submit_button("Add FAQ")

        if submitted and question and answer:
            keyword_list = [k.strip() for k in keywords.split(",")]
            db.add_faq(question, answer, category, keyword_list)
            st.success("FAQ added successfully!")
            st.rerun()


def main():
    """Main application"""

    # Sidebar navigation
    with st.sidebar:
        page = st.radio("Navigation", ["Chat", "Analytics", "FAQ Manager", "Settings"])

    # Initialize bot
    bot_components = initialize_bot()

    if not bot_components.get('initialized'):
        st.error("Voice Bot not properly initialized. Please check your configuration.")
        with st.expander("Error Details"):
            st.code(bot_components.get('error', 'Unknown error'))
        return

    # Create conversation if not exists
    if st.session_state.conversation_id is None:
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        st.session_state.conversation_id = bot_components['database'].create_conversation(session_id)

    # Route to appropriate page
    if page == "Analytics":
        show_analytics_dashboard(bot_components)
        return
    elif page == "FAQ Manager":
        show_faq_manager(bot_components)
        return
    elif page == "Settings":
        st.header("Settings")

        st.subheader("AI Configuration")
        ai_available = bot_components.get('ai_available', False)

        if ai_available:
            st.success("OpenAI API is configured and available")
            st.info("AI-powered responses are automatically used when appropriate. The system will also check FAQs first before generating responses.")
        else:
            st.warning("OpenAI API key not configured")
            st.info("Add OPENAI_API_KEY to your .env file to enable AI-powered responses")

        st.subheader("Database")
        st.info(f"SQLite database initialized at: {bot_components['database'].db_path}")

        st.subheader("Session Information")
        st.write(f"Conversation ID: {st.session_state.conversation_id}")
        st.write(f"Total Messages: {len(st.session_state.messages)}")

        if st.button("Export Analytics"):
            filepath = os.path.join(os.path.dirname(__file__), 'data', 'analytics_export.json')
            bot_components['analytics'].export_metrics(filepath)
            st.success(f"Analytics exported to {filepath}")

        return

    # Chat page (default)
    st.title("AI Voice Assistant")
    st.caption("Powered by Google Cloud Speech & Language AI" +
              (" + OpenAI GPT" if bot_components.get('ai_available') else ""))

    # Sidebar info
    with st.sidebar:
        st.header("Controls")

        st.info(f"**Bot Name:** {Config.BOT_NAME}")

        st.markdown("---")

        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()

        st.markdown("---")

        st.header("About")
        st.markdown("""
        This AI Voice Assistant can:
        - Process voice input
        - Handle text messages
        - Understand your intent
        - Provide intelligent responses
        - Speak responses back to you
        - Learn from FAQs
        - Track performance metrics
        """)

        st.markdown("---")

        st.header("Statistics")
        stats = bot_components['analytics'].get_session_statistics()
        st.metric("Total Messages", len(st.session_state.messages))
        st.metric("Success Rate", f"{stats['success_rate']:.1f}%")

        if st.session_state.messages:
            last_msg = st.session_state.messages[-1]
            if 'intent' in last_msg:
                st.metric("Last Intent", last_msg['intent'])
                st.metric("Confidence", f"{last_msg.get('confidence', 0):.0%}")

    # Display greeting if first time
    if not st.session_state.messages:
        st.markdown(f"""
        <div class="info-box">
            <h3>{Config.GREETING_MESSAGE}</h3>
            <p>You can type a message below or use the voice recorder to speak with me.</p>
        </div>
        """, unsafe_allow_html=True)

    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            display_message(
                message['role'],
                message['content'],
                message.get('intent'),
                message.get('confidence'),
                message.get('response_time')
            )

    # Input area
    st.markdown("---")

    col1, col2 = st.columns([3, 1])

    with col1:
        user_input = st.text_input(
            "Type your message:",
            key="user_input",
            placeholder="Type something...",
            label_visibility="collapsed"
        )

    with col2:
        send_clicked = st.button("Send", use_container_width=True)

    # Voice recording
    st.markdown("##### Or use voice:")
    audio_bytes = audio_recorder(
        pause_threshold=2.0,
        sample_rate=16000,
        text="Click to record",
        recording_color="#667eea",
        neutral_color="#6b7280",
        icon_name="microphone",
        icon_size="2x"
    )

    # Process text input
    if send_clicked and user_input:
        st.session_state.messages.append({
            'role': 'user',
            'content': user_input
        })

        result = process_message(user_input, bot_components, is_audio=False)

        if result:
            st.session_state.messages.append({
                'role': 'assistant',
                'content': result['response_text'],
                'intent': result['intent'],
                'confidence': result['confidence'],
                'response_time': result['response_time']
            })

            autoplay_audio(result['audio_bytes'])
            st.rerun()

    # Process voice input
    if audio_bytes:
        result = process_message(audio_bytes, bot_components, is_audio=True)

        if result:
            st.session_state.messages.append({
                'role': 'user',
                'content': result['user_text']
            })

            st.session_state.messages.append({
                'role': 'assistant',
                'content': result['response_text'],
                'intent': result['intent'],
                'confidence': result['confidence'],
                'response_time': result['response_time']
            })

            autoplay_audio(result['audio_bytes'])
            st.rerun()


if __name__ == "__main__":
    main()
