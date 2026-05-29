from groq import Groq

from .config import settings

groq_client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None


async def narrate(alert):
    if groq_client is None:
        return ""

    contributors = ", ".join(
        f"{c.feature}={c.feature_value:.2f} (attribution {c.attribution:+.4f})"
        for c in alert.top_contributors
    )
    prompt = (
        f"Transaction flagged with fraud probability {alert.risk_score:.2f}. "
        f"Risk drivers: {contributors}. Write 2 sentences for a bank analyst. "
        f"Be specific about numbers."
    )

    resp = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=120,
        temperature=0.3,
    )
    return resp.choices[0].message.content
