"""Citizen assistant: understands a request (text) and answers with the service steps.

Technique: TF-IDF character n-grams + logistic regression intent classifier.
Character n-grams make it tolerant of spelling variation and Hindi written in
English letters (Hinglish), which is how many citizens actually type.
Low-confidence requests are handed to a human officer instead of guessed.
"""
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

# --- Training data: intent -> example requests (English, Hinglish, Hindi) -------------
TRAINING = {
    "income_certificate": [
        "I want an income certificate", "how to apply for income certificate",
        "need income proof certificate for scholarship", "mujhe income certificate banwana hai",
        "income certificate kaise banega", "aay praman patra chahiye",
        "आय प्रमाण पत्र बनवाना है", "apply income certificate online",
        "my annual income certificate is needed", "income certificate documents required",
    ],
    "birth_certificate": [
        "I need a birth certificate for my baby", "how to get birth certificate",
        "apply for birth certificate", "bachche ka janam praman patra chahiye",
        "birth certificate kaise banwaye", "janm pramaan patra banwana hai",
        "जन्म प्रमाण पत्र चाहिए", "register newborn birth",
        "lost birth certificate duplicate copy", "birth certificate documents required",
    ],
    "ration_card": [
        "apply for a new ration card", "I want to add a member to my ration card",
        "ration card kaise banwaye", "naya ration card banwana hai",
        "ration card status check", "ration card me naam jodna hai",
        "राशन कार्ड बनवाना है", "my ration card is lost",
        "food subsidy card application", "ration card documents required",
    ],
    "pension_status": [
        "check my old age pension status", "when will I get my pension",
        "pension payment not received", "mera pension kab aayega",
        "vridha pension status dekhna hai", "widow pension application",
        "पेंशन की स्थिति जाननी है", "apply for old age pension",
        "pension amount not credited", "senior citizen pension scheme",
    ],
    "passport_apply": [
        "how do I apply for a passport", "passport renewal process",
        "I want a new passport", "passport banwana hai",
        "passport kaise apply kare", "passport documents required",
        "पासपोर्ट बनवाना है", "passport appointment booking",
        "lost passport what to do", "passport verification status",
    ],
    "driving_licence": [
        "apply for driving licence", "how to get learner licence",
        "driving license renewal", "driving licence banwana hai",
        "licence kaise banega", "learner licence ka test kab hai",
        "ड्राइविंग लाइसेंस बनवाना है", "book driving test slot",
        "duplicate driving licence lost", "driving licence documents required",
    ],
    "file_complaint": [
        "I want to file a complaint", "register a grievance with the department",
        "street light not working complaint", "shikayat darj karni hai",
        "road me gadda hai complaint karna hai", "garbage not collected in my area",
        "शिकायत दर्ज करनी है", "water supply problem complaint",
        "report a problem to the municipal office", "track my complaint status",
    ],
    "pay_bill_tax": [
        "pay my property tax", "how to pay water bill online",
        "electricity bill payment", "property tax kaise bharein",
        "pani ka bill bharna hai", "bijli bill payment karna hai",
        "संपत्ति कर भरना है", "pay municipal tax online",
        "tax payment receipt download", "due date for house tax",
    ],
    # Requests the government service cannot handle: go to a human, never guess.
    "out_of_scope": [
        "what is the weather tomorrow", "tell me a joke", "who won the cricket match",
        "aaj mausam kaisa hai", "latest movie news", "how are you",
        "what is the time now", "best restaurant near me", "hello", "kya haal hai",
    ],
}

# --- Knowledge base: what the citizen needs to do for each service -------------------
SERVICES = {
    "income_certificate": {
        "title": "Income Certificate",
        "documents": ["Identity proof", "Address proof", "Salary slip or self-declaration of income", "Passport-size photo"],
        "steps": "Fill the online form, upload the documents, pay the fee, and track the application.",
        "hi": "आय प्रमाण पत्र के लिए पहचान पत्र, पता प्रमाण, आय की घोषणा और फोटो चाहिए। ऑनलाइन फॉर्म भरकर दस्तावेज़ अपलोड करें।",
    },
    "birth_certificate": {
        "title": "Birth Certificate",
        "documents": ["Hospital discharge or birth report", "Parents' identity proof", "Address proof"],
        "steps": "Register the birth with the local registrar within the legal time limit, then download the certificate.",
        "hi": "जन्म प्रमाण पत्र के लिए अस्पताल की रिपोर्ट, माता-पिता का पहचान पत्र और पता प्रमाण चाहिए।",
    },
    "ration_card": {
        "title": "Ration Card",
        "documents": ["Identity proof of all members", "Address proof", "Income declaration", "Family photo"],
        "steps": "Apply through the food and civil supplies portal or the nearest service centre.",
        "hi": "राशन कार्ड के लिए सभी सदस्यों का पहचान पत्र, पता प्रमाण और आय घोषणा चाहिए।",
    },
    "pension_status": {
        "title": "Pension Services",
        "documents": ["Pension application number or ID", "Bank account details"],
        "steps": "Enter your application number to see status, or apply if you have not yet applied.",
        "hi": "पेंशन की स्थिति देखने के लिए आवेदन संख्या और बैंक खाते की जानकारी डालें।",
    },
    "passport_apply": {
        "title": "Passport Application",
        "documents": ["Proof of date of birth", "Address proof", "Identity proof", "Old passport (for renewal)"],
        "steps": "Register on the passport portal, fill the form, pay the fee and book an appointment.",
        "hi": "पासपोर्ट के लिए जन्म तिथि प्रमाण, पता प्रमाण और पहचान पत्र चाहिए। पोर्टल पर पंजीकरण करके अपॉइंटमेंट बुक करें।",
    },
    "driving_licence": {
        "title": "Driving Licence",
        "documents": ["Age proof", "Address proof", "Medical certificate (if required)", "Passport-size photo"],
        "steps": "Apply for a learner licence, book a test slot, and apply for the permanent licence after the test.",
        "hi": "ड्राइविंग लाइसेंस के लिए आयु प्रमाण, पता प्रमाण और फोटो चाहिए। पहले लर्नर लाइसेंस के लिए आवेदन करें।",
    },
    "file_complaint": {
        "title": "Complaint / Grievance",
        "documents": ["Description of the problem", "Location", "Photo (optional)"],
        "steps": "Submit the complaint, note the reference number, and track its status online.",
        "hi": "शिकायत में समस्या का विवरण और स्थान लिखें। संदर्भ संख्या से स्थिति देखें।",
    },
    "pay_bill_tax": {
        "title": "Bill and Tax Payment",
        "documents": ["Consumer or property ID"],
        "steps": "Enter your consumer or property ID, check the amount due, pay online and download the receipt.",
        "hi": "बिल या कर भरने के लिए उपभोक्ता या संपत्ति आईडी डालें, राशि देखें और ऑनलाइन भुगतान करें।",
    },
}

# Below this confidence the assistant does not guess: it hands over to a human officer.
CONFIDENCE_THRESHOLD = 0.55


class CitizenAssistant:
    def __init__(self):
        texts, labels = [], []
        for intent, examples in TRAINING.items():
            for example in examples:
                texts.append(self._clean(example))
                labels.append(intent)
        self.model = make_pipeline(
            TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), sublinear_tf=True),
            LogisticRegression(max_iter=2000, C=20),
        )
        self.model.fit(texts, labels)

    @staticmethod
    def _clean(text):
        return re.sub(r"\s+", " ", text.lower()).strip()

    @staticmethod
    def _is_hindi(text):
        return bool(re.search(r"[ऀ-ॿ]", text))

    def ask(self, request):
        """Return the predicted service, confidence and the reply for a citizen request."""
        cleaned = self._clean(request)
        if not cleaned:
            return {"intent": None, "confidence": 0.0, "needs_human": True,
                    "reply": "Please type or say what you need."}

        probs = self.model.predict_proba([cleaned])[0]
        ranked = sorted(zip(self.model.classes_, probs), key=lambda p: -p[1])
        intent, confidence = ranked[0]
        runner_up = ranked[1]

        if intent == "out_of_scope" or confidence < CONFIDENCE_THRESHOLD:
            return {
                "intent": "out_of_scope" if intent == "out_of_scope" else "unclear",
                "confidence": float(confidence), "needs_human": True,
                "alternatives": [(i, float(p)) for i, p in ranked[:3]],
                "reply": "I am not sure I understood. I am connecting you to an officer who can help.",
            }

        service = SERVICES[intent]
        if self._is_hindi(request):
            reply = service["hi"]
        else:
            docs = "; ".join(service["documents"])
            reply = f"{service['title']}: documents needed: {docs}. {service['steps']}"
        return {
            "intent": intent, "confidence": float(confidence), "needs_human": False,
            "alternatives": [(runner_up[0], float(runner_up[1]))],
            "reply": reply,
        }
