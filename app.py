from flask import Flask, render_template, request
import re
import os

app = Flask(__name__)

# ---------------- Scam Detector ----------------
class ScamDetector:
    def __init__(self):
        self.keywords = [
            "otp", "upi", "verify", "kyc",
            "account blocked", "urgent", "click", "link",
            "winner", "lottery", "cashback",
            
"account blocked", "account suspended", "verify account",
"update kyc", "kyc pending", "bank alert",
"unauthorized transaction", "suspicious activity",
"account frozen", "reactivate account",
            
"win money", "winner", "lottery", "prize",
"cashback", "reward", "gift", "bonus",
"congratulations you won", "free money",
            "otp", "pin", "password", "cvv",
"share otp", "enter otp", "verify otp",
            "upi", "request money", "send money",
"payment failed", "urgent payment",
"pay now", "click to pay",
            "click link", "open link", "verify link",
"short link", "bit.ly", "tinyurl",
"http://", "https://"
            "urgent", "immediately", "act now",
"limited time", "last chance",
"expire today", "within 24 hours",
            "bank", "rbi", "income tax", "customs",
"police", "government", "support team",
"customer care", "official notice"
]


        ]

    def analyze(self, message):
        score = 0.0
        text = message.lower()

        for k in self.keywords:
            if k in text:
                score += 0.15

        is_scam = score >= 0.45

        # Scam level
        if score >= 0.75:
            level = "HIGH"
        elif score >= 0.45:
            level = "MEDIUM"
        else:
            level = "LOW"

        return {
            "is_scam": is_scam,
            "confidence": round(min(score, 1.0), 2),
            "level": level
        }


# ---------------- LLM Persona Agent ----------------
class LLMPersonaAgent:
    def generate_reply(self, message):
        msg = message.lower()

        if "upi" in msg:
            return "Sir, please confirm the UPI ID again."
        if "link" in msg:
            return "The link is not opening. Can you resend it?"
        if "account" in msg:
            return "Which bank is this related to?"
        return "I am not able to understand. Please explain again."


# ---------------- Extractor ----------------
class Extractor:
    def extract(self, text):
        return {
            "upi_ids": list(set(re.findall(r"\b\w+@\w+\b", text))),
            "links": list(set(re.findall(r"https?://\S+", text)))
        }


# ---------------- Guard ----------------
class Guard:
    def safe(self, reply):
        blocked = ["otp", "pin", "password", "cvv"]
        return not any(b in reply.lower() for b in blocked)


# ---------------- Initialize ----------------
detector = ScamDetector()
agent = LLMPersonaAgent()
extractor = Extractor()
guard = Guard()


# ---------------- Dashboard Route ----------------
@app.route("/", methods=["GET", "POST"])
def dashboard():
    result = None

   if request.method == "POST":
    message = request.form.get("message", "")
    text = message.lower()

    score = 0.0

    # simple scoring
    if "otp" in text or "upi" in text:
        score += 0.4
    if "account" in text or "blocked" in text:
        score += 0.3
    if "verify" in text:
        score += 0.2

    is_scam = score >= 0.5

    # level
    if score >= 0.7:
        level = "HIGH"
    elif score >= 0.4:
        level = "MEDIUM"
    else:
        level = "LOW"

    # reply
    if "account" in text:
        reply = "Why is my account being suspended?"
    elif "verify" in text:
        reply = "What details do you need for verification?"
    elif "otp" in text or "upi" in text:
        reply = "Why is this information required?"
    else:
        reply = "Can you explain this in more detail?"

    result = {
        "is_scam": is_scam,
        "confidence": round(score, 2),
        "level": level,
        "agent_reply": reply,
        "extracted_data": {
            "links": [],
            "upi_ids": []
        }
    }
    return render_template("dashboard.html", result=result or {})


# ---------------- Run ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
