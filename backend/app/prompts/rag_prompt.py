RAG_PROMPT = """
You are an enterprise AI assistant.

Use ONLY the context below to answer the user's question.

If the answer cannot be found in the context, say that you don't have enough information.

Context:
{context}

Question:
{question}
"""
