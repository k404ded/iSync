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
    print("\n" + "=" * 75)
    print(" 1. GAP ANALYSIS SUMMARY")
    print("=" * 75)
    print(f"Software:             {report.software}")
    print(f"Version:              {report.current_version} → {report.new_version}")
    print(f"Documents Analyzed:   {report.total_documents}")
    print(f"Documents Affected:   {report.affected_documents_count}")
    print(f"High Priority:        {report.high_priority_count}")
    print(f"Medium Priority:      {report.medium_priority_count}")
    print(f"Low Priority:         {report.low_priority_count}")

    # 2. Document Impact Map
    print("\n" + "=" * 75)
    print(" 2. DOCUMENT IMPACT MAP")
    print("=" * 75)
    print(f"{'DOCUMENT':<32} | {'STATUS':<12} | {'PRIORITY':<8} | {'LOCS':<4} | {'REQUIRED ACTION'}")
    print("-" * 105)
    for d in report.document_summaries:
        pri = d.highest_priority.value if d.highest_priority else "—"
        print(f"{d.document:<32} | {d.status.value:<12} | {pri:<8} | {d.affected_locations_count:<4} | {d.action_summary[:42]}")

    # 3. Author Action Plan
    print("\n" + "=" * 75)
    print(" 3. AUTHOR ACTION PLAN (What exactly do I need to change?)")
    print("=" * 75)
    for idx, act in enumerate(report.action_plan, 1):
        print(f"\n#{idx} [{act.priority.value.upper()}] {act.action_type} in {act.document}")
        print(f"   Change:   {act.change_title}")
        print(f"   Location: {act.exact_location}")
        if act.old_state and act.new_state:
            print(f"   FROM:     \"{act.old_state}\"")
            print(f"   TO:       \"{act.new_state}\"")
        print(f"   Action:   {act.instructions}")

    # 4. Verified Unaffected Documents
    print("\n" + "=" * 75)
    print(" 4. VERIFIED UNAFFECTED MATERIAL")
    print("=" * 75)
    for u in report.unaffected_documents:
        print(f"• {u.document}: {u.non_impact_reason}")

    # 5. Export Reports
    print("\n" + "=" * 75)
    print(" 5. EXPORTING REPORTS")
    print("=" * 75)
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
