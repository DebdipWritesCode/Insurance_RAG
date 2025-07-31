from openai import AsyncOpenAI
from config.settings import settings

openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def ask_gpt(context: str, question: str) -> str:
    system_prompt = (
        "Answer using only the context. Be brief and factual. "
        "If the answer is not in context, use your general knowledge to answer the question assuming the question is from an Indian citizen. "
        "Avoid elaboration, opinions, and markdown. Use plain text. Keep answers as short as possible in not more than 75 words. Make it precise and to the point."
        "No using of newline characters, just single paragraph responses"
    )


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

    return response.choices[0].message.content.strip()
