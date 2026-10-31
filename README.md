# AI for Citizen Services and Document Processing

A small, runnable prototype demonstrating two AI-assisted government-service workflows:

1. A multilingual citizen assistant that identifies service requests and provides guidance.
2. An OCR-based document reader that extracts form fields and sends uncertain results for human review.

> **Important:** This is a demonstration prototype. It uses invented data and does not connect to any government system or official records.

## Features

### Citizen assistant

- Detects service-request intents using TF-IDF character n-grams and logistic regression
- Accepts English, Hinglish, and Hindi text
- Provides document requirements from a small local knowledge base
- Reports prediction confidence
- Hands off low-confidence or out-of-scope requests to a human officer

Implemented in [`assistant.py`](./assistant.py).

### Document reader

- Reads scanned form images with Tesseract OCR
- Calculates per-field OCR confidence
- Extracts values from `Label: value` form lines
- Validates field formats using regular expressions
- Marks uncertain or invalid fields for human review
- Produces an overall auto-accept or officer-review decision

Implemented in [`document_reader.py`](./document_reader.py).

## Project structure

```text
.
├── assistant.py          # Citizen-service intent classifier and responses
├── document_reader.py    # OCR, field extraction, validation, and review decisions
├── demo.py               # Command-line demo entry point
├── make_samples.py       # Generates synthetic sample documents
├── requirements.txt      # Python dependencies
└── samples/
    ├── sample_clear.png
    └── sample_poor.png
