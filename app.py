from flask import Flask, render_template, request
import re

app = Flask(__name__)

# ---------------- Scam Detector ----------------
class ScamDetector:
    def __init__(self):
        self.keywords = [
            "otp", "upi", "verify", "kyc",
            "account blocked", "urgent", "click link"
        ]

    def analyze(self, message):
        score = 0
        for k in self.keywords:
            if k in message.lower():
                score += 0.15
        return {
            "is_scam": score >= 0.45,
            "confidence": round(min(score, 1.0), 2)
        }


# ---------------- LLM Persona Agent ----------------
class LLMPersonaAgent:
    """
    Simulated LLM agent (hackathon-safe).
    Can later be replaced with OpenAI / Gemini / etc.
    """
    def generate_reply(self, message):
        if "upi" in message.lower():
            return "Sir, can you please repeat the UPI ID? I want to confirm."
        if "link" in message.lower():
            return "The link is not opening, can you send it again?"
        return "I am confused, which bank is this regarding?"


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


# ---------------- Controller ----------------
detector = ScamDetector()
agent = LLMPersonaAgent()
extractor = Extractor()
guard = Guard()

@app.route("/", methods=["GET", "POST"])
def dashboard():
    result = None

    if request.method == "POST":
        message = request.form["message"]

        detection = detector.analyze(message)

        if detection["is_scam"]:
            reply = agent.generate_reply(message)
            if not guard.safe(reply):
                reply = "Please clarify your request."

            result = {
                "is_scam": True,
                "confidence": detection["confidence"],
                "agent_reply": reply,
                "extracted_data": extractor.extract(message)
            }
        else:
            result = {"is_scam": False}

    return render_template("dashboard.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
