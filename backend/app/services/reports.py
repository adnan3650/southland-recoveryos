from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate

from .rules import match_programs, readiness


class ReportService:
    @staticmethod
    def generate(case, resources):
        stream = BytesIO()
        doc = SimpleDocTemplate(
            stream,
            pagesize=letter,
            rightMargin=48,
            leftMargin=48,
            topMargin=50,
            bottomMargin=48,
            title="Southland RecoveryOS - Recovery packet",
            author="Southland RecoveryOS",
        )
        styles = getSampleStyleSheet()
        styles.add(
            ParagraphStyle(
                name="SmallSource",
                fontSize=8,
                leading=11,
                textColor=colors.HexColor("#586775"),
                spaceAfter=7,
                wordWrap="CJK",
            )
        )
        styles["Title"].textColor = colors.HexColor("#123f39")
        styles["Heading2"].textColor = colors.HexColor("#123f39")
        styles["BodyText"].spaceAfter = 7
        styles["BodyText"].leading = 14
        story = []

        def safe(value):
            # Standard font has limited Unicode. Normalize punctuation before escaping.
            text = (
                str(value).replace("\u2019", "'").replace("\u2014", "-").replace("\u2013", "-").replace("\u2022", "-")
            )
            return escape(text.encode("latin-1", errors="replace").decode("latin-1")).replace("\n", "<br/>")

        def para(text, style="BodyText"):
            story.append(Paragraph(safe(text), styles[style]))

        def heading(text):
            para(text, "Heading2")

        para("SOUTHLAND / RECOVERYOS", "Title")
        para("Your recovery packet", "Heading1")
        para(
            "LOCAL SYNTHETIC DEMONSTRATION - Resident-provided records and AI interpretations. Not an official application, safety assessment, insurance determination or eligibility decision.",
            "SmallSource",
        )
        para("Case " + case["id"], "SmallSource")
        heading("1. What happened - resident-supplied facts")
        para(f"{case['resident_name']} | {case['municipality']}, {case['zip_code']}")
        para(
            f"{case['disaster_type'].title()} | Incident date: {case['incident_date']} | Property: {case['property_situation']}"
        )
        para(case["description"])
        para(
            "Displaced: "
            + ("Yes" if case["displaced"] else "No")
            + ". Immediate needs: "
            + (", ".join(case["immediate_needs"]) or "None reported")
        )
        heading("2. Documentation readiness")
        ready = readiness(case)
        para(f"{ready['percent']}% of documentation checks complete. {ready['meaning']}")
        for check in ready["checks"]:
            para(
                f"{'COMPLETE' if check['complete'] else 'MISSING'}: {check['title']}. "
                + ("" if check["complete"] else check["next_step"])
            )
        heading("3. Damage inventory")
        if not case["damage_items"]:
            para("No damage inventory recorded.")
        for item in case["damage_items"]:
            para(f"{item['item']} - {item['area']} ({item['provenance']})", "Heading3")
            para(item["observation"])
            if item.get("uncertainty"):
                para("Uncertainty: " + item["uncertainty"])
            if item.get("evidence_ids"):
                para("Evidence IDs: " + ", ".join(item["evidence_ids"]), "SmallSource")
        heading("4. Evidence register")
        for d in case["documents"]:
            para(f"{d['name']} | {d['category']} | {d['size']} bytes")
            para("ID: " + d["id"] + " | SHA-256: " + d["sha256"], "SmallSource")
        if not case["documents"]:
            para("No documents uploaded. Original documents are not embedded in this packet.")
        heading("5. Insurance preparation - resident supplied")
        for k, v in case["insurance"].items():
            if v:
                para(k.replace("_", " ").title() + ": " + v)
        para(
            "Confirm policy wording, exclusions, reporting deadlines and coverage with the insurer. No coverage or payment is guaranteed."
        )
        for analysis in case["analyses"]:
            para("Claude interpretation of evidence: " + analysis["document_id"], "Heading3")
            para(analysis["result"]["summary"])
            for uncertainty in analysis["result"]["uncertainties"] + analysis["result"]["missing_details"]:
                para("Verify / missing: " + uncertainty)
            policy = analysis["result"]["policy"]
            para("AI policy identifier: " + policy["policy_identifier"])
            for text in policy["coverage_wording"] + policy["exclusions"] + policy["insurer_questions"]:
                para(text)
            para("AI deductible wording: " + policy["deductible_wording"])
        heading("6. Program prerequisites - never final eligibility")
        for program in match_programs(case, resources):
            para(program["name"] + " - " + program["match_status"], "Heading3")
            for item in program["reasons"] + program["missing_requirements"]:
                para("- " + item)
            para(program["limitations"])
        heading("7. Recovery tasks")
        for task in case["tasks"]:
            para(f"[{task['status'].upper()}] {task['title']} - {task['priority']}", "Heading3")
            para(task["explanation"])
            if task.get("due_date"):
                para("Resident-set target date: " + task["due_date"] + " (not an agency deadline)")
        heading("8. Contact history")
        for contact in case["contacts"]:
            para(f"{contact['contacted_on']} - {contact['organization']}: {contact['notes']}")
        if not case["contacts"]:
            para("No contacts recorded.")
        heading("9. Reference directory")
        for r in resources:
            para(r["name"], "Heading3")
            para(r["description"] + " Contact: " + r["contact"])
            para(r["source_url"], "SmallSource")
            para(
                f"Page checked: {r['verified_at'] or 'Not verified'}. {r['verification']}. {r['limitations']}",
                "SmallSource",
            )

        def footer(canvas, doc):
            canvas.setStrokeColor(colors.HexColor("#dce5df"))
            canvas.line(48, 35, letter[0] - 48, 35)
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(colors.HexColor("#586775"))
            canvas.drawString(48, 23, "Southland RecoveryOS | Private synthetic case packet")
            canvas.drawRightString(letter[0] - 48, 23, str(doc.page))

        doc.build(story, onFirstPage=footer, onLaterPages=footer)
        return stream.getvalue()
