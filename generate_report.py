"""Generate my project report for the citizen-services AI system."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).parent
OUTPUT = ROOT / "citizen_ai_demo_report.pdf"


def build_report(path):
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=26,
            leading=32,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#123B5D"),
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverSubtitle",
            parent=styles["Normal"],
            fontSize=13,
            leading=18,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#486581"),
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Section",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=17,
            leading=22,
            textColor=colors.HexColor("#123B5D"),
            spaceBefore=14,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Subsection",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1F5F78"),
            spaceBefore=8,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Small",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#52606D"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="Callout",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            leftIndent=10,
            rightIndent=10,
            borderColor=colors.HexColor("#9FB3C8"),
            borderWidth=0.7,
            borderPadding=8,
            backColor=colors.HexColor("#F0F4F8"),
            spaceBefore=8,
            spaceAfter=10,
        )
    )

    def p(text, style="BodyText"):
        return Paragraph(text, styles[style])

    def bullet(text):
        return Paragraph(f"&bull;&nbsp;&nbsp;{text}", styles["BodyText"])

    def table(data, widths):
        converted = []
        for row in data:
            converted.append(
                [
                    cell if isinstance(cell, Paragraph) else p(str(cell), "Small")
                    for cell in row
                ]
            )
        result = Table(converted, colWidths=widths, repeatRows=1, hAlign="LEFT")
        result.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#123B5D")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#BCCCDC")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
                ]
            )
        )
        return result

    story = [
        Spacer(1, 35 * mm),
        p("AI for Citizen Services<br/>and Document Processing", "CoverTitle"),
        p("My technical project report", "CoverSubtitle"),
        HRFlowable(width="55%", thickness=1.5, color=colors.HexColor("#2F80A8")),
        Spacer(1, 13 * mm),
        p(
            "<b>Scope:</b> Multilingual citizen-service intent detection and OCR-assisted "
            "document processing with human review safeguards.",
            "Callout",
        ),
    ]

    story += [
        p("1. Executive summary", "Section"),
        p(
            "In this project, I built a small, runnable model of an AI-enabled "
            "citizen-services workflow. It demonstrates two complementary lanes: a "
            "text assistant that recognizes common service requests, and a document "
            "reader that extracts fields from scanned forms. Both lanes expose "
            "confidence information and route low-confidence cases to a human officer."
        ),
        p(
            "I designed this as a demonstration and learning project using invented data, "
            "a small training set, local processing, and synthetic sample documents. It "
            "is not connected to official records and must not be used to make real "
            "administrative decisions."
        ),
        p("Key capabilities", "Subsection"),
        bullet("Intent classification for English, Hinglish, and Hindi text."),
        bullet("Service guidance with required documents and next steps."),
        bullet("OCR with per-word confidence estimates."),
        bullet("Field extraction and regular-expression format validation."),
        bullet("Automatic acceptance only when all required fields pass checks."),
        bullet("Human handoff for uncertain, invalid, or out-of-scope requests."),
        p("2. System overview", "Section"),
        table(
            [
                ["Component", "Implementation", "Purpose"],
                ["Citizen assistant", "TF-IDF character n-grams + logistic regression", "Classify requests and provide service guidance."],
                ["Service knowledge base", "Local Python dictionary", "Map recognized intents to documents, steps, and Hindi guidance."],
                ["Document reader", "Tesseract OCR + Pillow preprocessing", "Read text from scanned form images."],
                ["Field validation", "Regular expressions and threshold checks", "Detect malformed or low-confidence values."],
                ["Decision layer", "Human-review rule", "Auto-accept clear documents; escalate uncertain cases."],
            ],
            [34 * mm, 62 * mm, 75 * mm],
        ),
        Spacer(1, 5),
        p(
            "I kept the implementation transparent so that each stage can be run from "
            "the command line and inspected in the Python source files."
        ),
        p("3. Workflow design", "Section"),
        p("Citizen assistant workflow", "Subsection"),
        table(
            [
                ["Step", "Description"],
                ["1. Request", "A citizen enters a typed request in English, Hinglish, or Hindi."],
                ["2. Intent", "The classifier predicts one of the supported service categories or out-of-scope."],
                ["3. Confidence", "The prediction confidence is displayed to the operator or user."],
                ["4. Guidance", "The local knowledge base returns documents and process steps."],
                ["5. Handoff", "Low-confidence or unsupported requests are handed to an officer."],
            ],
            [31 * mm, 140 * mm],
        ),
        Spacer(1, 7),
        p("Document reader workflow", "Subsection"),
        table(
            [
                ["Step", "Description"],
                ["1. Scan", "A form image is supplied to the command-line demo."],
                ["2. OCR", "Tesseract identifies words and reports word-level confidence."],
                ["3. Extract", "Expected labels such as Name and Mobile are matched to values."],
                ["4. Validate", "Values are checked against expected formats."],
                ["5. Decide", "All clear fields are auto-accepted; any flagged field triggers review."],
            ],
            [31 * mm, 140 * mm],
        ),
        PageBreak(),
    ]

    story += [
        p("4. Technical implementation", "Section"),
        p("Citizen assistant", "Subsection"),
        p(
            "The assistant uses character-level TF-IDF features with logistic regression. "
            "Character n-grams help tolerate spelling variation and transliterated Hindi "
            "(Hinglish). The training examples cover services such as income certificates, "
            "birth certificates, ration cards, pensions, passports, driving licences, "
            "complaints, and bill or tax payments."
        ),
        p(
            "The classifier is deliberately small and local. The service response is not "
            "generated from an external model; it is selected from a fixed knowledge base. "
            "This makes the demo predictable and easy to audit, while also limiting its "
            "coverage."
        ),
        p("Document reader", "Subsection"),
        p(
            "The reader converts an image to grayscale, applies autocontrast and mild "
            "sharpening, and passes the result to Tesseract. OCR words are grouped into "
            "lines. Each expected field is extracted from a line in the form "
            "<font name='Courier'>Label: value</font>."
        ),
        p(
            "A field is accepted only when its value matches the configured format and its "
            "average OCR confidence is at least 85 percent. Missing fields, malformed "
            "values, and lower-confidence values are marked <b>needs review</b>."
        ),
        p("5. Demonstration and observations", "Section"),
        p("Installation and execution", "Subsection"),
        p(
            "My implementation uses the Python packages listed in <font name='Courier'>requirements.txt</font> "
            "and requires the system Tesseract executable."
        ),
        table(
            [
                ["Command", "Purpose"],
                ["python3 -m venv .venv", "Create an isolated Python environment."],
                [".venv/bin/python -m pip install -r requirements.txt", "Install Python dependencies."],
                [".venv/bin/python make_samples.py", "Generate clean and poor-quality sample forms."],
                [".venv/bin/python demo.py", "Run the scripted assistant and OCR demonstration."],
                [".venv/bin/python demo.py chat", "Interact with the citizen assistant."],
                [".venv/bin/python demo.py doc samples/sample_poor.png", "Process one document image."],
            ],
            [83 * mm, 88 * mm],
        ),
        p("Expected behavior", "Subsection"),
        bullet("Supported service requests return an intent, confidence score, and practical guidance."),
        bullet("An unrelated weather request is outside scope and is handed to an officer."),
        bullet("The clean synthetic form is intended to pass all field checks."),
        bullet("The poor-quality synthetic form is intended to produce review flags."),
        p(
            "Exact OCR confidence values can vary with the installed Tesseract version, "
            "fonts, image libraries, and operating system. The report therefore treats "
            "the results as qualitative demonstration behavior rather than fixed benchmark "
            "values."
        ),
        p("6. Limitations and responsible-use considerations", "Section"),
        bullet("The intent model is trained on roughly 90 short examples, so unusual wording may be misclassified."),
        bullet("Speech recognition and automatic translation are not implemented."),
        bullet("The document reader expects a simple label-and-value layout rather than complex real-world forms."),
        bullet("No verification against government records is implemented."),
        bullet("OCR confidence is an indicator of recognition quality, not proof of truth."),
        bullet("All sample data is fictional; no personal or official data should be added to this demo without appropriate controls."),
        p(
            "A production system would require privacy controls, secure integration with "
            "authorized records, audit logging, accessibility testing, multilingual "
            "evaluation, bias monitoring, operational monitoring, and clearly defined "
            "human accountability."
        ),
        PageBreak(),
    ]

    story += [
        p("7. Roadmap", "Section"),
        table(
            [
                ["Priority", "Extension", "Expected benefit"],
                ["High", "Expand and evaluate multilingual training data.", "Improve classification coverage and fairness."],
                ["High", "Add automated tests and reproducible evaluation metrics.", "Detect regressions and measure accuracy."],
                ["High", "Add secure audit logs and explicit review queues.", "Support accountability and operational oversight."],
                ["Medium", "Use layout-aware document models.", "Handle complex government forms."],
                ["Medium", "Add a Streamlit or Gradio interface.", "Make the prototype easier to demonstrate."],
                ["Medium", "Add speech input and translation.", "Improve accessibility for more citizens."],
                ["Future", "Integrate approved verification APIs.", "Reduce manual verification while preserving authorization controls."],
            ],
            [20 * mm, 78 * mm, 73 * mm],
        ),
        p("8. Conclusion", "Section"),
        p(
            "I used this project to show how a citizen-service assistant and an OCR "
            "document workflow can be combined with confidence thresholds and human "
            "oversight. Its strongest design feature is the explicit handoff rule that "
            "prevents uncertain predictions and document reads from being presented as "
            "reliable decisions."
        ),
        p(
            "If I developed this further, I would focus on disciplined evaluation and "
            "governance: larger representative datasets, secure data handling, "
            "measurable quality targets, and a review process that keeps human officers "
            "accountable for final outcomes."
        ),
        Spacer(1, 15),
        HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#BCCCDC")),
        Spacer(1, 7),
        p("Implementation: Python, scikit-learn, Tesseract OCR, and Pillow.", "Small"),
    ]

    def footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#D9E2EC"))
        canvas.line(18 * mm, 14 * mm, 192 * mm, 14 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#627D98"))
        canvas.drawString(18 * mm, 9 * mm, "AI for Citizen Services and Document Processing")
        canvas.drawRightString(192 * mm, 9 * mm, f"Page {document.page}")
        canvas.restoreState()

    document = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=20 * mm,
        title="AI for Citizen Services and Document Processing",
        author="Project author",
    )
    document.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    build_report(OUTPUT)
    print(f"Created {OUTPUT}")
