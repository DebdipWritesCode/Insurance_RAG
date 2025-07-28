from services.vector_store import retrieve_from_kb
from services.gpt_client import ask_gpt

async def answer_query_with_rag(agent_id: str, query: str) -> dict:
    try:
        retrieval_result = await retrieve_from_kb({
            "query": query,
            "agent_id": agent_id,
            "top_k": 3
        })

        if "error" in retrieval_result:
            return {
                "answer": None,
                "chunks": [],
                "error": retrieval_result["error"]
            }

        chunks = retrieval_result["chunks"]

        if not chunks:
            return {
                "answer": "Sorry, I couldn't find any relevant information.",
                "chunks": [],
            }

        context = "\n\n".join(chunks)

        answer = ask_gpt(context=context, question=query)

        return {
            "answer": answer,
            "chunks": chunks
        }

    except Exception as e:
        return {
            "answer": None,
            "chunks": [],
            "error": str(e)
        }
