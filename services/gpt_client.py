from openai import AsyncOpenAI
from config.settings import settings

openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def ask_gpt(context: str, question: str) -> str:
    system_prompt = (
    "Use only the context to answer. Be brief. If not found, say 'Not mentioned in the context.'"
)


    user_prompt = f"""
    Context:
    {context}

    Question: {question}
    """

    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
    )

    return response.choices[0].message.content.strip()
