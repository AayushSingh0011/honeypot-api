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
            "winner", "lottery", "cashback"
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

        if message:
            detection = detector.analyze(message)

            if detection["is_scam"]:
                reply = agent.generate_reply(message)

                if not guard.safe(reply):
                    reply = "Please clarify your request."

                extracted = extractor.extract(message)

                result = {
                    "is_scam": True,
                    "level": detection["level"],
                    "confidence": detection["confidence"],
                    "agent_reply": reply,
                    "extracted_data": extracted
                }
            else:
                result = {
                    "is_scam": False,
                    "level": detection["level"],
                    "confidence": detection["confidence"]
                }

    return render_template("dashboard.html", result=result)


# ---------------- Run ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
