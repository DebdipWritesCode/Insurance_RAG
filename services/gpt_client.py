from openai import AsyncOpenAI
from config.settings import settings

openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def ask_gpt(context: str, question: str) -> str:
    system_prompt = (
        "Answer using the given context. Be brief and factual. "
        "If the answer is not found in the context, use your general knowledge to answer as if the question is from an Indian citizen. "
        "Do not mention that the answer is not in the context. "
        "Avoid elaboration, opinions, or markdown. Use plain text only. Keep responses concise, clear, and under 75 words. "
        "Do not use newline characters; respond in a single paragraph."
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
