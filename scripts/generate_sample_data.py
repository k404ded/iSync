"""
Sample Data Generator for iSync.
Creates realistic benchmark test curriculum:
- Sketching_Fundamentals.pdf (Affected by UI change - Toolbar screenshot)
- Advanced_Parts_Assembly.docx (Affected by Terminology, Deprecation, Enhancement)
- Constraints_and_Mates.pptx (Affected by Workflow change - Relocated panel)
- Feature_Glossary_Index.csv (Affected by Terminology and Deprecation)
- Introduction_and_Overview.pdf (Unaffected introductory material - Demonstrates Not Affected status)
"""

from pathlib import Path
import pandas as pd
from docx import Document
from pptx import Presentation
from pptx.util import Inches
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors


def generate_sample_files(base_dir: Path):
    sample_dir = base_dir / "sample_data"
    courses_dir = sample_dir / "course_files"
    courses_dir.mkdir(parents=True, exist_ok=True)

    # 1. Changes text
    changes_text = """SOLIDWORKS 2025 Release Notes & Software Delta:

CHANGE 1:
Sketch toolbar redesigned with updated icon arrangement and unified palette grouping.

CHANGE 2:
Constraints panel moved from the floating window directly into the docked Left FeatureManager design tree.

CHANGE 3:
Mate Controller has been renamed to Kinematic Assembly Controller to reflect modern multi-body simulation standards.

CHANGE 4:
Legacy 2D Drawing Export has been deprecated in favor of native MBD workflows.

CHANGE 5:
AI-Assisted Hole Wizard introduced for automatic fastener sizing and intelligent hole positioning."""

    (sample_dir / "changes.txt").write_text(changes_text.strip(), encoding="utf-8")

    # 2. PDF: Sketching_Fundamentals.pdf
    pdf_path = courses_dir / "Sketching_Fundamentals.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter

    # Page 1
    c.setFont("Helvetica-Bold", 16)
    c.drawString(54, height - 54, "Module 1: Getting Started with 3D CAD")
    c.setFont("Helvetica", 11)
    c.drawString(54, height - 80, "Lesson 1: Welcome and System Orientation")
    c.drawString(54, height - 110, "Welcome to 3D CAD Modeling. In this course you will learn core solid modeling workflows.")
    c.drawString(54, height - 130, "Save the completed model to your project workspace before continuing to the next exercise.")
    c.showPage()

    # Page 2
    c.setFont("Helvetica-Bold", 16)
    c.drawString(54, height - 54, "Module 1: Getting Started with 3D CAD")
    c.setFont("Helvetica", 11)
    c.drawString(54, height - 80, "Lesson 2: Sketch Plane Selection")
    c.drawString(54, height - 110, "Select Front Plane, Top Plane, or Right Plane from the design tree to establish a 2D sketch plane.")
    c.drawString(54, height - 130, "Ensure grid snap settings match your engineering tolerance requirements.")
    c.showPage()

    # Page 3: Sketch Toolbar & Screenshot (Directly affected by CHANGE 1)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(54, height - 54, "Module 2: Sketching Fundamentals")
    c.setFont("Helvetica-Bold", 13)
    c.drawString(54, height - 80, "Lesson 3: The Sketch Environment & Toolbar")
    c.setFont("Helvetica", 11)
    c.drawString(54, height - 105, "Open Sketch and select the Sketch toolbar shown in Figure 2-1 below.")
    c.drawString(54, height - 125, "The Sketch toolbar contains essential drawing commands such as Line, Circle, Rectangle, and Spline.")
    c.drawString(54, height - 145, "Click the Sketch toolbar button to initiate profile creation and observe tool parameters.")

    # Screenshot simulation
    c.setStrokeColor(colors.HexColor("#0284c7"))
    c.setFillColor(colors.HexColor("#f0f9ff"))
    c.rect(54, height - 280, 500, 110, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#0369a1"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(70, height - 200, "[Screenshot / Figure 2-1: Sketch Toolbar Layout (SOLIDWORKS 2024 UI)]")
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(70, height - 220, "Visual capture illustrating old Sketch toolbar icons, button arrangements, and floating command ribbon.")

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    c.drawString(54, height - 310, "Caption: Figure 2-1 shows the standard Sketch toolbar layout for drawing entities.")
    c.drawString(54, height - 330, "Notice how the drawing tools are grouped together for rapid access during sketching.")
    c.showPage()
    c.save()

    # 3. PPTX: Constraints_and_Mates.pptx (Affected by CHANGE 2)
    pptx_path = courses_dir / "Constraints_and_Mates.pptx"
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(5.625)

    # Slide 1: Intro
    s1 = prs.slides.add_slide(prs.slide_layouts[1])
    s1.shapes.title.text = "Module 3: Parametric Assembly Basics"
    b1 = s1.shapes.placeholders[1].text_frame
    b1.text = "Parametric modeling uses dimensional constraints to control geometry."
    p = b1.add_paragraph()
    p.text = "Always anchor the base component to origin coordinates."

    # Slide 2: Workflow for Constraints (Affected by CHANGE 2)
    s2 = prs.slides.add_slide(prs.slide_layouts[1])
    s2.shapes.title.text = "Lesson 2: Applying Assembly Constraints"
    b2 = s2.shapes.placeholders[1].text_frame
    b2.text = "Workflow for assembling mechanical components:"
    p1 = b2.add_paragraph()
    p1.text = "Step 1: Open the Constraints window and select the Constraints panel to define relationships."
    p2 = b2.add_paragraph()
    p2.text = "Step 2: Navigate through the floating Constraints panel options to assign coincident or parallel mates between component faces."
    p3 = b2.add_paragraph()
    p3.text = "Step 3: Confirm alignment and verify degrees of freedom."

    # Slide 3: Summary
    s3 = prs.slides.add_slide(prs.slide_layouts[1])
    s3.shapes.title.text = "Lesson 3: Verification & Mating Principles"
    b3 = s3.shapes.placeholders[1].text_frame
    b3.text = "Always test full range of motion after applying mates to ensure parts do not collide."

    prs.save(str(pptx_path))

    # 4. DOCX: Advanced_Parts_Assembly.docx (Affected by CHANGE 3, 4, 5)
    docx_path = courses_dir / "Advanced_Parts_Assembly.docx"
    doc = Document()
    doc.add_heading("Module 4: Advanced Solid Modeling and Assembly Procedures", level=1)

    # Section 1: Mate Controller
    doc.add_heading("Lesson 1: Kinematic Position Management", level=2)
    doc.add_paragraph(
        "In this lesson, we study kinematic positions. Select the Mate Controller from the assembly tree "
        "to record positions and evaluate kinematic clearance. The Mate Controller provides precise joint angles "
        "and coordinates across all defined assembly states."
    )

    # Section 2: Deprecated Feature
    doc.add_heading("Lesson 2: Drawing Production and Documentation", level=2)
    doc.add_paragraph(
        "To export traditional draft sheets, run the Legacy 2D Drawing Export utility from the Tools menu. "
        "Follow the step-by-step export wizard to produce flat files for archive. Note that Legacy 2D Drawing Export "
        "is used for legacy machine shops requiring DXF format."
    )

    # Section 3: Hole Wizard enhancement
    doc.add_heading("Lesson 3: Standard Fastener Placement & Holes", level=2)
    doc.add_paragraph(
        "Standard fasteners require properly sized clearance holes. When creating mounting bosses, manually calculate "
        "fastener clearance and thread depth according to standard machinery handbooks before selecting hole diameter."
    )

    doc.save(str(docx_path))

    # 5. CSV: Feature_Glossary_Index.csv
    csv_path = courses_dir / "Feature_Glossary_Index.csv"
    data = [
        {
            "Module": "Assembly",
            "Lesson": "Kinematics",
            "Section": "Terminology",
            "Page": 14,
            "Term": "Mate Controller",
            "Definition": "Interactive tool to manipulate degrees of freedom across mates.",
            "Notes": "Reference Mate Controller in all kinematic mechanism exercises.",
        },
        {
            "Module": "Drafting",
            "Lesson": "Export",
            "Section": "Archiving",
            "Page": 28,
            "Term": "Legacy 2D Drawing Export",
            "Definition": "Command to output outdated flat 2D representations.",
            "Notes": "Scheduled for deprecation in future versions.",
        },
    ]
    pd.DataFrame(data).to_csv(csv_path, index=False)

    # 6. PDF: Introduction_and_Overview.pdf (UNAFFECTED DOCUMENT)
    unaffected_pdf = courses_dir / "Introduction_and_Overview.pdf"
    c_un = canvas.Canvas(str(unaffected_pdf), pagesize=letter)
    c_un.setFont("Helvetica-Bold", 16)
    c_un.drawString(54, height - 54, "Course Syllabus: Introduction to Engineering Design")
    c_un.setFont("Helvetica", 11)
    c_un.drawString(54, height - 85, "Instructor Office Hours and Grading Policy.")
    c_un.drawString(54, height - 110, "Students are expected to attend laboratory sessions on time and review standard safety protocols.")
    c_un.drawString(54, height - 130, "Textbook references: Shigley's Mechanical Engineering Design 11th Edition.")
    c_un.showPage()
    c_un.save()

    print("All sample benchmark documents generated successfully!")


if __name__ == "__main__":
    generate_sample_files(Path(__file__).resolve().parent.parent)
