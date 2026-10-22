"""Run the full demo:  python demo.py            (scripted demo)
                      python demo.py chat       (type your own requests)
                      python demo.py doc FILE   (read your own scanned form image)
"""
import sys
from pathlib import Path

from assistant import CitizenAssistant
from document_reader import decide, read_document

HERE = Path(__file__).parent

SAMPLE_REQUESTS = [
    "Mujhe income certificate banwana hai",
    "how do I apply for a passport",
    "बच्चे का जन्म प्रमाण पत्र चाहिए",
    "street light not working in my area",
    "pani ka bill kaise bharein",
    "what is the weather tomorrow",  # outside scope: should go to a human
]


def show_request(assistant, request):
    r = assistant.ask(request)
    print(f'\nCitizen : {request}')
    print(f'Intent  : {r["intent"]}  (confidence {r["confidence"]:.2f})')
    if r["needs_human"]:
        print("Action  : HANDED TO OFFICER")
    print(f'Reply   : {r["reply"]}')


def show_document(path):
    print(f"\nDocument: {Path(path).name}")
    results = read_document(path)
    print(f'{"Field":<15}{"Extracted":<30}{"Conf.":>7}  Status')
    print("-" * 66)
    for r in results:
        print(f"{r.field:<15}{r.value:<30}{r.confidence:>6.1f}%  {r.status}")
    decision, _ = decide(results)
    print("Decision:", decision)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "demo"
    if mode == "doc":
        show_document(sys.argv[2])
        return
    assistant = CitizenAssistant()
    if mode == "chat":
        print("Citizen assistant. Type a request (English, Hinglish or Hindi). Empty line to quit.")
        while True:
            request = input("\n> ").strip()
            if not request:
                break
            show_request(assistant, request)
        return

    print("=" * 66)
    print("PART 1: CITIZEN ASSISTANT (intent detection)")
    print("=" * 66)
    for request in SAMPLE_REQUESTS:
        show_request(assistant, request)

    print("\n" + "=" * 66)
    print("PART 2: DOCUMENT READER (OCR + extraction + human review)")
    print("=" * 66)
    for name in ("sample_clear.png", "sample_poor.png"):
        show_document(HERE / "samples" / name)


if __name__ == "__main__":
    main()
