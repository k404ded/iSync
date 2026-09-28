"""
CLI Demo Runner for iSync.
Executes the identical analysis pipeline used by the Streamlit application:
- Loads the SOLIDWORKS 2024 -> 2025 benchmark release notes.
- Loads 5 benchmark course documents (PDF, DOCX, PPTX, CSV, and unaffected PDF).
- Parses documents into content chunks with exact locations.
- Performs hybrid semantic retrieval.
- Classifies impacts into HIGH, MEDIUM, LOW.
- Formulates the Author Action Plan with OLD -> NEW transitions.
- Identifies unaffected documents with explicit explanations.
- Saves multi-format exports (CSV, HTML, PDF) to outputs/.
"""

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.config import SAMPLE_DATA_DIR, SAMPLE_COURSES_DIR, OUTPUT_DIR
from app.parsers import DocumentLoader
from app.analysis import GapAnalysisPipeline
from app.export import CSVExporter, HTMLExporter, PDFExporter


def run_demo():
    print("=" * 75)
    print(" iSync — Intelligent Course Update Gap Analysis Agent (Tata Technologies)")
    print("=" * 75)

    changes_file = SAMPLE_DATA_DIR / "changes.txt"
    if not changes_file.exists():
        from scripts.generate_sample_data import generate_sample_files
        generate_sample_files(root_dir)

    raw_changes = changes_file.read_text(encoding="utf-8")
    course_files = list(SAMPLE_COURSES_DIR.glob("*.*"))

    print(f"\n[1/4] Ingesting {len(course_files)} course documents from {SAMPLE_COURSES_DIR}...")
    loader = DocumentLoader()
    all_chunks = loader.parse_multiple(course_files)
    doc_names = [f.name for f in course_files]
    print(f"  • Extracted {len(all_chunks)} content chunks across {len(doc_names)} documents.")

    print("\n[2/4] Executing Intelligent Gap Analysis Pipeline...")
    pipeline = GapAnalysisPipeline()

    def progress_callback(step: int, msg: str):
        print(f"  [Stage {step}/5] {msg}")

    report = pipeline.run(
        software="SOLIDWORKS",
        current_version="2024",
        new_version="2025",
        change_text=raw_changes,
        all_chunks=all_chunks,
        all_document_names=doc_names,
        progress_cb=progress_callback,
    )

    # 1. Executive Summary
    print("\n" + "=" * 80)
    print(" 1. EXECUTIVE SUMMARY")
    print("=" * 80)
    print(f"Software:             {report.software}")
    print(f"Version:              {report.current_version} → {report.new_version}")
    print(f"Documents Analyzed:   {report.total_documents}")
    print(f"Documents Requiring Action: {report.affected_documents_count}")
    print(f"High Priority:        {report.high_priority_count}")
    print(f"Medium Priority:      {report.medium_priority_count}")
    print(f"Low Priority:         {report.low_priority_count}")

    # 2. Software Change Inventory
    print("\n" + "=" * 80)
    print(" 2. SOFTWARE CHANGE INVENTORY")
    print("=" * 80)
    print(f"{'CHANGE ID':<10} | {'AREA':<22} | {'TYPE':<22} | {'CHANGE TITLE'}")
    print("-" * 80)
    for c in report.changes:
        print(f"{c.change_id:<10} | {c.software_area[:20]:<22} | {c.change_type.value[:20]:<22} | {c.title[:45]}")

    # 3. Document Impact Map
    print("\n" + "=" * 80)
    print(" 3. DOCUMENT IMPACT MAP")
    print("=" * 80)
    print(f"{'DOCUMENT':<32} | {'STATUS':<15} | {'PRIORITY':<8} | {'LOCS':<4} | {'REQUIRED ACTION'}")
    print("-" * 105)
    for d in report.document_summaries:
        pri = d.highest_priority.value if d.highest_priority else "—"
        status_icon = "🔴" if d.status.value == "Affected" else ("🟡" if "Potentially" in d.status.value else ("🔵" if d.status.value == "Reference" else "🟢"))
        print(f"{d.document:<32} | {status_icon} {d.status.value:<12} | {pri:<8} | {d.affected_locations_count:<4} | {d.action_summary[:42]}")

    # 4. Author Action Plan
    print("\n" + "=" * 80)
    print(" 4. AUTHOR ACTION PLAN (What exactly do I need to change?)")
    print("=" * 80)
    for idx, act in enumerate(report.action_plan, 1):
        print(f"\n#{idx} [{act.priority.value.upper()}] {act.action_type} in {act.document}")
        print(f"   Change:   {act.change_title}")
        print(f"   Location: {act.exact_location}")
        if act.old_state and act.new_state:
            print(f"   FROM:     \"{act.old_state}\"")
            print(f"   TO:       \"{act.new_state}\"")
        print(f"   Action:   {act.instructions}")

    # 5. Detailed Findings & Grounded Evidence
    print("\n" + "=" * 80)
    print(" 5. DETAILED FINDINGS & GROUNDED EVIDENCE (Sample)")
    print("=" * 80)
    for f in report.findings[:3]:
        print(f"\n[{f.priority.value.upper()}] {f.finding_id} — {f.software_change or f.change_summary}")
        print(f"   Document:        {f.document}")
        print(f"   Exact Location:  {f.exact_location}")
        print(f"   Course Excerpt:  \"{f.affected_content[:100]}...\"")
        print(f"   Grounded Quote:  \"{f.evidence}\"")
        print(f"   Why Affected:    {f.why_flagged}")
        print(f"   Author Action:   {f.recommended_action}")

    # 6. Verified Unaffected Material
    print("\n" + "=" * 80)
    print(" 6. VERIFIED UNAFFECTED COURSE MATERIAL")
    print("=" * 80)
    for u in report.unaffected_documents:
        print(f"• 🟢 {u.document}: {u.non_impact_reason}")
        print(f"  Author Directive: No changes required.")

    # 7. Current-State Reference Documents
    print("\n" + "=" * 80)
    print(" 7. CURRENT-STATE REFERENCE DOCUMENTS")
    print("=" * 80)
    if report.reference_documents:
        for r in report.reference_documents:
            print(f"• 🔵 {r.document}: Current-state reference used to establish the target software state.")
    else:
        print("• Analysis performed using parsed vendor release change notes.")

    # 8. Traceability Matrix
    print("\n" + "=" * 80)
    print(" 8. TRACEABILITY MATRIX (Sample Links)")
    print("=" * 80)
    print(f"{'TRACE ID':<10} | {'CHANGE ID':<10} | {'DOCUMENT':<28} | {'EXACT LOCATION':<35} | {'PRIORITY'}")
    print("-" * 95)
    for t in report.traceability_matrix[:4]:
        print(f"{t.trace_id:<10} | {t.change_id:<10} | {t.document[:26]:<28} | {t.exact_location[:33]:<35} | {t.priority.value}")

    # Export Reports
    print("\n" + "=" * 80)
    print(" EXPORTING REPORTS")
    print("=" * 80)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    base_name = f"iSync_Report_{report.software}_{report.new_version}_{report.report_id}"

    csv_path = OUTPUT_DIR / f"{base_name}.csv"
    html_path = OUTPUT_DIR / f"{base_name}.html"
    pdf_path = OUTPUT_DIR / f"{base_name}.pdf"

    csv_path.write_bytes(CSVExporter.export(report))
    html_path.write_text(HTMLExporter.export(report), encoding="utf-8")
    pdf_path.write_bytes(PDFExporter.export(report))

    print(f"  • CSV:  {csv_path.name} ({csv_path.stat().st_size} bytes)")
    print(f"  • HTML: {html_path.name} ({html_path.stat().st_size} bytes)")
    print(f"  • PDF:  {pdf_path.name} ({pdf_path.stat().st_size} bytes)")

    print("\n✓ Pipeline execution verified successfully!")
    return report


if __name__ == "__main__":
    run_demo()
