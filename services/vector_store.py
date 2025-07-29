from pinecone import Pinecone
from openai import OpenAI
from langchain.vectorstores import Pinecone as LangchainPinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config.settings import settings

pc = Pinecone(
  api_key=settings.PINECONE_API_KEY
)
index = pc.Index(settings.PINECONE_INDEX_NAME)

openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
EMBED_MODEL = "text-embedding-3-small"

def split_text(text: str, chunk_size=500, chunk_overlap=100) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)
  
async def embed_and_upsert(chunks: list[str], namespace: str):
    print(f"Embedding and upserting {len(chunks)} chunks into namespace: {namespace}")
    try:
        vectors = []
        batch_size = 50
        total_batches = (len(chunks) + batch_size - 1) // batch_size
        print(f"🧮 Total batches to process: {total_batches} (batch size = {batch_size})")

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            current_batch_number = (i // batch_size) + 1
            print(f"📦 Processing batch {current_batch_number}/{total_batches}...")

            embeddings = openai_client.embeddings.create(
                input=batch,
                model=EMBED_MODEL
            )

            for j, embedding in enumerate(embeddings.data):
                text = batch[j]
                metadata = {
                    "text": text,
                    "section": "unknown",
                    "page": -1,
                    "source": "",
                    "type": "paragraph",
                }

                vectors.append({
                    "id": f"{namespace}_{i + j}",
                    "values": embedding.embedding,
                    "metadata": metadata
                })

        print(f"⬆️ Finished embedding. Now upserting {len(vectors)} vectors to Pinecone...")
        response = index.upsert(vectors=vectors, namespace=namespace)
        print(f"✅ Upsert completed. Pinecone response: {response}")

        return {"status": "success", "inserted": len(vectors)}

    except Exception as e:
        print(f"❌ Error in embed_and_upsert: {e}")
        return {"status": "error", "error": str(e)}

async def retrieve_from_kb(input_params):
    try:
        query = input_params.get("query", "")
        agent_id = input_params.get("agent_id", "")
        top_k = input_params.get("top_k", 5)

        if not query:
            return {"chunks": [], "status": "error", "message": "Query is required"}
        if not agent_id:
            return {"chunks": [], "status": "error", "message": "Agent ID is required"}

        # Get embedding for query
        query_embedding_response = openai_client.embeddings.create(
            input=[query],
            model=EMBED_MODEL
        )
        query_vector = query_embedding_response.data[0].embedding

        # Search in Pinecone using the vector
        results = index.query(
            vector=query_vector,
            namespace=agent_id,
            top_k=top_k,
            include_metadata=True
        )

        content_blocks = []
        for match in results.matches:
            score = match.score
            if score > 0.0:
                metadata = match.metadata or {}
                text = metadata.get("text", "")
                if text:
                    content_blocks.append(text)

        return {"chunks": content_blocks}

    except Exception as e:
        print(f"Error in retrieve_from_kb: {e}")
        return {"chunks": [], "status": "error", "error": str(e)}
  
  
FUNCTION_HANDLERS = {
    "retrieve_from_kb": retrieve_from_kb
}

FUNCTION_DEFINITIONS = [
    {
        "name": "retrieve_from_kb",
        "description": "Retrieves top-k chunks from the knowledge base using a query and agent_id (namespace).",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The user's search query."
                },
                "agent_id": {
                    "type": "string",
                    "description": "The namespace or agent ID to search in."
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of top results to return.",
                    "default": 3
                }
            },
            "required": ["query", "agent_id"]
        }
    }
]