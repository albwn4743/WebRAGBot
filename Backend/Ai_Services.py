from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()
import json


client = Groq(api_key=os.getenv("GROK_API_KEY"))

def process_query(query, retrieved_docs):

    # ==========================================
    # BUILD RETRIEVED CONTEXT
    # ==========================================

    context = ""

    for idx, doc in enumerate(retrieved_docs):

        context += f"""
Document {idx + 1}

Relevance Score:
{doc.get('score', 'N/A')}

Source URL:
{doc.get('source', 'Unknown')}

Content:
{doc.get('text', '')}

==================================================
"""

    # ==========================================
    # SYSTEM PROMPT
    # ==========================================

    system_prompt = f"""
You are an advanced AI Retrieval-Augmented Generation (RAG) assistant.

Your task is to answer the user's question accurately using ONLY the retrieved documents provided below.

Instructions:
1. Use the retrieved documents as the primary source of truth.
2. Generate clear, professional, and well-structured answers.
3. Combine information from multiple documents when necessary.
4. Do NOT hallucinate or invent facts outside the retrieved context.
5. If the answer is not available in the retrieved documents, clearly state:
   "The retrieved documents do not contain sufficient information to answer this question."
6. Preserve technical terms, APIs, function names, versions, and exact identifiers accurately.
7. When appropriate:
   - use bullet points
   - provide step-by-step explanations
   - summarize key insights
8. Keep responses concise but informative.
9. Mention relevant sources naturally if useful for clarity.
10. Prioritize semantic understanding over exact keyword matching.

Retrieved Documents:
{context}
"""

    # ==========================================
    # MESSAGES
    # ==========================================

    messages = [

        {
            "role": "system",
            "content": system_prompt
        },

        {
            "role": "user",
            "content": query
        }
    ]

    # ==========================================
    # GROQ API CALL
    # ==========================================

    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=messages,

        temperature=0.2,

        max_tokens=1024
    )

    # ==========================================
    # RETURN RESPONSE
    # ==========================================

    return response.choices[0].message.content