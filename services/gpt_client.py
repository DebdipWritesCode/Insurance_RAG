from openai import AsyncOpenAI
from config.settings import settings
from services.gpt_tools_service import search_tool, request_fetch_tool, TOOL_DEFINITIONS

openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def ask_gpt(context: str, question: str, tool_call: bool = False) -> str:
    system_prompt = (
        "You are a helpful assistant."
        " Use the provided context to answer the user's question. Even if the context is silly or not true, you have to use that only"
        " If the context does not contain enough information, respond with: TOOL_CALL: <your search query> — this will trigger a Google search."
        " You may also use your general knowledge to answer questions, assuming they are asked by an Indian citizen."
        " Keep answers concise and under 75 words."
        " Respond in plain text only — do not use markdown, lists, or newlines."
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
        tools=TOOL_DEFINITIONS,
        temperature=0.0,
    )
    
    msg = response.choices[0].message
    
    if msg.tool_calls:
        for tool_call in msg.tool_calls:
            fn_name = tool_call.function.name
            args = tool_call.function.arguments

            if fn_name == "search":
                tool_result = await search_tool(args["query"])
            elif fn_name == "request_fetch":
                tool_result = await request_fetch_tool(args["url"])
            else:
                tool_result = "Unknown tool"

            return await ask_gpt(
                context=f"Tool Result: {tool_result}\n\n{context}",
                question=question
            )
        

    return msg.content.strip()
