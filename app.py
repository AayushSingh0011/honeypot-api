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

            "bank", "rbi", "income tax", "police", "customer care",



    # 🔐 Sensitive Info
    "otp", "one time password", "pin", "password", "cvv", "atm pin",
    "bank details", "account number", "ifsc", "card details",

    # 🏦 Banking / Threat
    "account blocked", "account suspended", "account frozen",
    "verify account", "update kyc", "kyc pending", "kyc expired",
    "unauthorized transaction", "suspicious activity",
    "reactivate account", "bank alert", "security alert",

    # 💰 Money / Rewards
    "win money", "winner", "lottery", "jackpot", "prize",
    "cashback", "reward", "bonus", "free money", "gift",
    "congratulations you won", "claim your prize",

    # 💳 Payments / UPI
    "upi", "request money", "send money", "receive money",
    "payment failed", "pending payment", "pay now",
    "collect request", "approve payment",

    # 🔗 Links / Phishing
    "click link", "open link", "verify link",
    "short link", "bit.ly", "tinyurl", "grabify",
    "http", "https", "login here",

    # ⏰ Urgency / Pressure
    "urgent", "immediately", "act now", "hurry",
    "limited time", "last chance", "expire today",
    "within 24 hours", "deadline",

    # 🧑‍💼 Authority / Impersonation
    "bank", "rbi", "income tax", "customs", "police",
    "government", "support team", "customer care",
    "official notice", "helpline",

    # 💼 Job Scams
    "work from home", "online job", "part time job",
    "no experience needed", "easy job", "earn money",
    "daily income", "weekly income",

    # 📦 Delivery / Courier Scams
    "parcel", "courier", "delivery failed",
    "shipment", "track package", "address issue",

    # 💸 Fees / Charges
    "registration fee", "joining fee", "processing fee",
    "service charge", "activation fee",

    # 📱 SIM / KYC Fraud
    "sim blocked", "sim verification", "mobile kyc",
    "number suspended",

    # 🎣 Generic Tricks
    "click here", "tap here", "login now",
    "confirm now", "verify now"

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
            # ✅ Better UPI detection
            "upi_ids": list(set(re.findall(r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}", text))),

            # ✅ Better link detection
            "links": list(set(re.findall(r"https?://[^\s]+", text)))
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
