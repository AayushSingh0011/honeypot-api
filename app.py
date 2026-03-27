from flask import Flask, render_template, request
import re

app = Flask(__name__)

# ---------------- Scam Detector ----------------
class ScamDetector:
    def __init__(self):
        # ✅ KEYWORDS ONLY
        self.keywords = [
            "otp", "upi", "verify", "kyc",
            "account blocked", "account suspended",
            "update kyc", "bank alert",
            "unauthorized transaction",

            "win money", "winner", "lottery", "prize",
            "cashback", "reward", "bonus", "free money",

            "pin", "password", "cvv",

            "request money", "pay now",

            "click link", "bit.ly", "tinyurl", "http", "https",

            "urgent", "act now", "limited time",

            "bank", "rbi", "income tax", "police", "customer care"
        ]

        # ✅ REGEX PATTERNS (SEPARATE)
        self.patterns = {
            "high_income": r"(₹\s?\d{3,}/day|₹\s?\d{4,}/week|earn\s?\₹?\d+)",
            "no_experience": r"(no experience needed|no experience required)",
            "job_offer": r"(part[- ]?time job|work from home|online job)",
            "payment_request": r"(registration fee|joining fee|processing fee)",
            "urgency": r"(urgent|act now|limited time)",
            "sensitive_info": r"(otp|password|cvv|bank details)",
            "links": r"(http[s]?://|bit\.ly|tinyurl)"
        }

    def analyze(self, message):
        score = 0.0
        text = message.lower()

        # keyword scoring
        for k in self.keywords:
            if k in text:
                if k in ["otp", "pin", "password", "cvv"]:
                    score += 0.4
                elif k in ["upi", "bank", "account blocked"]:
                    score += 0.25
                else:
                    score += 0.15

        # regex scoring
        for pattern in self.patterns.values():
            if re.search(pattern, text):
                score += 0.3

        is_scam = score >= 0.5

        if score >= 0.7:
            level = "HIGH"
        elif score >= 0.4:
            level = "MEDIUM"
        else:
            level = "LOW"

        return {
            "is_scam": is_scam,
            "confidence": round(min(score, 1.0), 2),
            "level": level
        }


# ---------------- Agent ----------------
class LLMPersonaAgent:
    def generate_reply(self, message):
        msg = message.lower()

        if "upi" in msg:
            return "Sir, please confirm the UPI ID again."
        if "link" in msg:
            return "The link is not opening. Can you resend it?"
        if "account" in msg:
            return "Which bank is this related to?"
        return "Please explain your message again."


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


# ---------------- Route ----------------
@app.route("/", methods=["GET", "POST"])
def dashboard():
    result = None

    if request.method == "POST":
        message = request.form.get("message", "")

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

    return render_template("dashboard.html", result=result or {})


# ---------------- Run ----------------
if __name__ == "__main__":
    app.run(debug=True)
