from openai import OpenAI
from config.settings import settings

openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

def ask_gpt(context: str, question: str) -> str:
    system_prompt = (
        "You are a concise and factual assistant. Answer only based on the provided context. "
        "Do not speculate, generalize, or include information not present in the context. "
        "Keep answers brief, accurate, and aligned exactly with the wording of the source. "
        "When the context does not contain an answer, clearly respond with 'Not mentioned in the context.'"
    )

    user_prompt = f"""
    Context:
    {context}

    Question: {question}
    """

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
    )

    return response.choices[0].message.content.strip()