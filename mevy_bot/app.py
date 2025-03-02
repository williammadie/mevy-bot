import logging

import streamlit as st

from mevy_bot.vector_store.vector_store import VectorStore
from mevy_bot.generator.openai_generator import OpenAIGenerator
from mevy_bot.vector_store.qdrant_collection import QdrantCollection
from mevy_bot.models.openai import OpenAIModelFactory
from mevy_bot.rewriter.openai_rewriter import OpenAIRewriter

logger = logging.getLogger(__name__)

# Streamlit App Layout
st.title("RAG Chat Interface")

user_query = st.text_input("Pose your question:")

# Button to trigger the process
if st.button("Ask"):
    if not user_query.strip():
        st.warning("Please enter a question.")
        st.stop()

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
    st.write("### Retrieved Context")
    st.write(context)

    # Generate response
    generator = OpenAIGenerator(generator_model_info, vector_store)
    completion = generator.generate_response_with_context(
        rewrited_user_query, collection_name)

    # Show final answer
    st.success("### Response")
    st.write(completion)
