from openai import AsyncOpenAI
from config.settings import settings
from services.search_api import serper_search

openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def ask_gpt(context: str, question: str, tool_call: bool = False) -> str:
    system_prompt = (
        "You are a helpful assistant."
        " Use the provided context to answer the user's question."
        " If the context does not contain enough information, respond with: TOOL_CALL: <your search query> — this will trigger a Google search."
        " You may also use your general knowledge to answer questions, assuming they are asked by an Indian citizen."
        " Keep answers concise and under 75 words."
        " Respond in plain text only — do not use markdown, lists, or newlines."
        " If the user asks for illegal actions, private data, internal systems, or anything unethical or prohibited, clearly state that you do not have access to that information and cannot assist with such requests."
    )
    
    if tool_call:
        print(f"User context: {context}")

    user_prompt = f"""
    Context:
    {context}

    Question: {question}
    """

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
    )
    
    answer = response.choices[0].message.content.strip()
    
    if answer.startswith("TOOL_CALL:"):
        query = answer.replace("TOOL_CALL:", "").strip()
        print(f"🔍 Calling external tool with query: {query}")
        tool_result = serper_search(query)
        
        print(f"🔍 Tool result: {tool_result}")
        
        updated_context = f"Additional Search Result: {tool_result}\n\n{context}"
        return await ask_gpt(updated_context, question, tool_call=True)

    return answer
