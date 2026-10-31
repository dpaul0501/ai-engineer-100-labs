"""Generate data/records.txt: synthetic support tickets as compact JSON, in English and Hindi.

Deterministic: python data/make_records.py  rebuilds the same file.
"""

import json
import random
from pathlib import Path

SEPARATOR = "<|endoftext|>"

TEXT = {
    "en": [
        "my refund has not arrived", "the app crashes when I open settings", "I was charged twice",
        "cannot log in after the update", "please cancel my order", "the delivery is late by three days",
        "how do I change my address", "the invoice shows the wrong amount", "my account is locked",
        "the payment page does not load",
    ],
    "hi": [
        "मेरा रिफंड अभी तक नहीं आया", "सेटिंग खोलते ही ऐप बंद हो जाता है", "मुझसे दो बार पैसे कटे",
        "अपडेट के बाद लॉगिन नहीं हो रहा", "कृपया मेरा ऑर्डर रद्द करें", "डिलीवरी तीन दिन देर से है",
        "मैं अपना पता कैसे बदलूँ", "बिल में गलत राशि दिख रही है", "मेरा खाता लॉक हो गया है",
        "भुगतान पेज नहीं खुल रहा",
    ],
}
TAGS = ["billing", "refund", "login", "delivery", "app", "account", "payment"]


def record(rng: random.Random, i: int) -> dict:
    lang = rng.choice(["en", "hi"])
    r = {
        "id": 1000 + i,
        "lang": lang,
        "priority": rng.choice(["low", "medium", "high"]),
        "tags": rng.sample(TAGS, rng.randint(1, 3)),
        "text": rng.choice(TEXT[lang]),
        "amount": rng.choice([None, round(rng.uniform(1, 500), 2), rng.randint(1, 999)]),
        "escalate": rng.random() < 0.2,
    }
    if rng.random() < 0.5:
        r["customer"] = {"tier": rng.choice(["free", "pro"]), "years": rng.randint(0, 9)}
    return r


def main() -> None:
    rng = random.Random(1)
    docs = [json.dumps(record(rng, i), ensure_ascii=False, separators=(",", ":")) for i in range(2000)]
    out = Path(__file__).with_name("records.txt")
    out.write_text(f"\n{SEPARATOR}\n".join(docs) + "\n", encoding="utf-8")
    print(f"wrote {len(docs)} records to {out}")


if __name__ == "__main__":
    main()
