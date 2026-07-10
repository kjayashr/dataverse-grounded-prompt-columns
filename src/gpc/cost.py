"""Cost estimation (feature F5).

Copilot Credits bill on tokens. Retrieval (search) is effectively free next to a
generation, which is the whole reason incremental refresh is cheap: we run cheap
retrieval to detect change and only pay for generation where something moved.
"""
CREDIT_PER_1K_TOKENS = 0.12   # approx: ~0.5 credit at ~4200 tokens (1 credit = $0.01)


def tokens(text):
    return max(1, len(text) // 4)


def generation_credits(prompt, answer=""):
    return round((tokens(prompt) + tokens(answer)) / 1000 * CREDIT_PER_1K_TOKENS, 3)


def dollars(credits):
    return round(credits * 0.01, 4)
