import logging
import streamlit as st

from mevy_bot.vector_store.vector_store import VectorStore
from mevy_bot.generator.openai_generator import OpenAIGenerator
from mevy_bot.vector_store.qdrant_collection import QdrantCollection
from mevy_bot.models.openai import OpenAIModelFactory
from mevy_bot.rewriter.openai_rewriter import OpenAIRewriter

# Set up logger (you could redirect to a log file if needed)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set Streamlit page config (optional)
st.set_page_config(page_title="Assistant virtuel Mevy", page_icon="💬")

st.title("💬 Assistant virtuel Mevy")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render the chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input box
user_query = st.chat_input("Comment puis-je vous aider ?")

if user_query:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    logger.info("Starting chat operation...")

    # Model and store setup
    embedding_model_info = OpenAIModelFactory.text_embedding_3_small()
    generator_model_info = OpenAIModelFactory.gpt4o_mini()

    store_client = QdrantCollection(embedding_model_info.vector_dimensions)
    vector_store = VectorStore(
        store_client,
        embedding_model_info,
        generator_model_info
    )
    collection_name = "full_knowledge_test_19022025"

    # Rewrite the query
    rewriter = OpenAIRewriter(generator_model_info.name)
    rewrited_user_query = rewriter.rewrite_user_query(user_query)

    logger.info("User query:\n%s\n\nRewrited query:\n%s",
                user_query, rewrited_user_query)

    # Search context in vector store
    context = vector_store.search_in_store(
        rewrited_user_query, collection_name)

    # Generate response
    generator = OpenAIGenerator(generator_model_info, vector_store)
    completion = generator.generate_response_with_context(
        rewrited_user_query, collection_name)

    # Build the AI response
    ai_response = f"**Assistant Mevy**\n\n{completion}"

    # Add AI message to history
    st.session_state.messages.append(
        {"role": "assistant", "content": ai_response}
    )
    with st.chat_message("assistant"):
        st.markdown(ai_response)
