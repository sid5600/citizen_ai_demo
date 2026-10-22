# AI for Citizen Services and Document Processing: working prototype

A small, runnable model of the system described in the presentation. It has two parts that match the two lanes on the workflow slide.

| Part | File | Technique |
|---|---|---|
| Citizen assistant | `assistant.py` | TF-IDF character n-grams + logistic regression intent classifier; answers from a small service knowledge base; hands low-confidence or out-of-scope requests to a human officer |
| Document reader | `document_reader.py` | Tesseract OCR with per-word confidence, regex field extraction, format validation, confidence threshold, human review flag |

All data is invented. Nothing here connects to a real government system.

## Setup

```
sudo apt install python3-venv tesseract-ocr
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python make_samples.py      # creates samples/sample_clear.png and samples/sample_poor.png
```

Ubuntu may report `externally-managed-environment` when `pip` is run outside a
virtual environment. The commands above install the Python packages locally in
`.venv` and avoid modifying the system Python installation. If you activate the
environment, the commands can be shortened:

```
source .venv/bin/activate
python -m pip install -r requirements.txt
python make_samples.py
```

## Run

```
.venv/bin/python demo.py                        # scripted demo of both parts
.venv/bin/python demo.py chat                   # type your own requests (English, Hinglish, Hindi)
.venv/bin/python demo.py doc samples/sample_poor.png   # read any scanned form image
```

## Expected demo output

- 5 service requests are recognised (income certificate, passport, birth certificate in Hindi, complaint, bill payment) with confidence scores and a reply that lists the documents needed.
- "what is the weather tomorrow" is out of scope, so it is handed to an officer.
- `sample_clear.png`: all 5 fields extracted at 89 to 96 percent confidence, so it is auto-accepted.
- `sample_poor.png`: a photocopy-style scan; the fields OCR cannot read confidently are flagged "needs review" and the application goes to an officer.

## How it maps to the slides

- Slide 3 (techniques): intent detection (NLP classifier), OCR, entity extraction, confidence scores.
- Slide 4 (workflow): request, intent, answer; scan, OCR, extract, check, approve or send to officer.
- Slide 6 (demo): same behaviours, now running on real code.
- Slide 7 (limitations): the human-handoff rule is the safeguard for accuracy and trust.

## Limits of this prototype

- The intent classifier is trained on about 90 short phrases, so unusual wording may be misread. A real system needs thousands of examples per language.
- Speech recognition and translation are not included; the assistant takes typed text.
- The reader expects a simple "Label: value" form layout. Real forms need layout-aware models.
- Verification "against records" is described on the slide but not implemented.

## Ideas to extend

- Add speech input (for example the open-source Whisper model) in front of the assistant.
- Add a Streamlit or Gradio web page for the demo.
- Add more intents, or retrain from a CSV file of real citizen queries.
