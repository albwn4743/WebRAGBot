from Dataset import connect_weaviate, get_embeddings, search_query
import warnings

warnings.filterwarnings("ignore")

print("Initializing Retrieval System...")
client = connect_weaviate()
embeddings = get_embeddings()

print("Retrieval System Ready!\n")
print("Type 'quit' or 'exit' to stop.")

while True:
    query = input("\n👤 You: ")

    if query.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break

    if not query.strip():
        continue

    # Search in Weaviate
    results = search_query(query, client, embeddings)

    print("\n🔍 Retrieved Results:\n")

    if not results:
        print("No relevant documents found.")
    else:
        for i, result in enumerate(results, start=1):

            # Adjust these keys based on your returned data structure
            text = result.get("text", "No text found")
            source = result.get("source", "Unknown Source")
            score = result.get("score", "N/A")

            print(f"Result {i}")
            print(f"Source : {source}")
            print(f"Score  : {score}")
            print(f"Text   :\n{text}")
            print("-" * 60)

client.close()