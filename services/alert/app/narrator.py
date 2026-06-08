from groq import Groq

from .config import settings

groq_client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None

FEATURE_DESCRIPTIONS = {
    "amount_norm": "normalized transaction amount",
    "amount_log": "log-scaled transaction amount",
    "hour": "hour of day (0-23)",
    "product_cd": "product type (0=goods, 2=cash, 3=service)",
    "card_brand": "card network (0=Visa, 1=Mastercard, 2=Amex, 3=Discover)",
    "card_type": "card category (0=credit, 1=debit)",
    "p_email_bin": "purchaser email domain (0=Gmail, 3=anonymous/suspicious)",
    "m1": "name on card matches billing name (1=yes, 0=no, -1=unchecked)",
    "m2": "billing address matches card address (1=yes, 0=no, -1=unchecked)",
    "m3": "billing address verified (1=yes, 0=no, -1=unchecked)",
    "m4": "transaction device fingerprint match (1=yes, 0=no, -1=unchecked)",
    "m5": "shipping address matches billing address (1=yes, 0=no, -1=unchecked)",
    "m6": "billing address linked to known fraud (1=yes, 0=no, -1=unchecked)",
    "device_type": "device used (0=desktop, 1=mobile, -1=unknown)",
    "user_tx_count": "number of transactions seen from this card",
    "addr1": "billing zip/postal code (-1=unknown)",
    "dist1": "distance between billing and shipping address",
    "c1": "number of billing addresses linked to this card",
    "c2": "number of phone numbers linked to this card",
    "c6": "number of phone numbers on the billing address",
    "c13": "number of payment accounts sharing this email",
    "c14": "account transaction history depth",
    "d1": "days since previous transaction (-1=first transaction)",
    "d4": "days since previous transaction (alternate window)",
}


async def narrate(alert):
    if groq_client is None:
        return ""

    contributors = ", ".join(
        f"{FEATURE_DESCRIPTIONS.get(c.feature, c.feature)} "
        f"(raw={c.feature_value:.2f}, impact={c.attribution:+.2f})"
        for c in alert.top_contributors
    )
    prompt = (
        f"Transaction {alert.transaction_id} flagged with fraud probability "
        f"{alert.risk_score:.2f} (risk level: {alert.risk_band}). "
        f"Top risk drivers: {contributors}. "
        f"Write exactly 2 sentences for a bank fraud analyst. "
        f"Use plain English, name the specific risk signals, and state what action to consider."
    )

    resp = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.3,
    )
    return resp.choices[0].message.content
