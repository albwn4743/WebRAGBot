from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()
import json


client = Groq(api_key=os.getenv("GROK_API_KEY"))

def process_query(query,retrieved_docs):
    # Combine the query and retrieved documents into a single input for the model
    system_prompt = "You are an assistant that helps answer questions based on retrieved documents. Use the following retrieved documents to answer the query:\n\n"
    for idx, doc in enumerate(retrieved_docs):
        system_prompt += f"Document {idx+1} (Score: {doc['score']}):\n{doc['text']}\nSource: {doc['source']}\n\n"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]
    # Call the Groq API to process the input data
    response = client.chat.completions.create(
        model = 'llama-3.1-8b-instant',
        messages = messages
    )
    return response.choices[0].message.content