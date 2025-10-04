"""
Cleanup and consolidate review_tools directory.
Organizes files into a cleaner structure.
"""

import shutil
from pathlib import Path

def cleanup_review_tools():
    """Organize review_tools directory."""
    
    review_tools = Path(__file__).parent
    print(f"Cleaning up: {review_tools}")
    
    # Create subdirectories
    archived = review_tools / "archived"
    viewer = review_tools / "viewer"
    
    archived.mkdir(exist_ok=True)
    viewer.mkdir(exist_ok=True)
    
    # Files to archive (old/deprecated versions)
    to_archive = [
        "assemblyai_review_ui.html",  # Old UI (replaced by studio)
        "review_ui.html",  # Even older generic UI
        "launch_assemblyai_review.py",  # Old launcher
        "launch_assemblyai_review.bat",  # Old launcher batch
        "ASSEMBLYAI_REVIEW_README.md",  # Replaced by README.md
    ]
    
    # Files to move to viewer subfolder
    to_viewer = [
        "transcript_viewer.html",
        "transcript_viewer.css",
        "transcript_viewer.js",
    ]
    
    print("\n" + "="*60)
    print("ARCHIVING OLD FILES")
    print("="*60)
    
    for filename in to_archive:
        src = review_tools / filename
        if src.exists():
            dest = archived / filename
            if dest.exists():
                print(f"  [SKIP] Already archived: {filename}")
            else:
                shutil.move(str(src), str(dest))
                print(f"  [OK] Archived: {filename}")
        else:
            print(f"  [--] Not found: {filename}")
    
    print("\n" + "="*60)
    print("MOVING VIEWER FILES")
    print("="*60)
    
    for filename in to_viewer:
        src = review_tools / filename
        if src.exists():
            dest = viewer / filename
            if dest.exists():
                print(f"  [SKIP] Already moved: {filename}")
            else:
                shutil.move(str(src), str(dest))
                print(f"  [OK] Moved: {filename}")
        else:
            print(f"  [--] Not found: {filename}")
    
    print("\n" + "="*60)
    print("CURRENT ACTIVE FILES")
    print("="*60)
    
    # List remaining files (should be the active ones)
    active_files = [
        f.name for f in review_tools.iterdir()
        if f.is_file() and not f.name.startswith('__') and not f.name.endswith('.pyc')
    ]
    
    for filename in sorted(active_files):
        if filename != "cleanup_review_tools.py":
            print(f"  [OK] {filename}")
    
    print("\n" + "="*60)
    print("CLEANUP COMPLETE!")
    print("="*60)
    print(f"\nOrganized structure:")
    print(f"  - Active files: {len(active_files) - 1}")  # -1 for cleanup script
    print(f"  - Archived: {len(list(archived.iterdir()))}")
    print(f"  - Viewer: {len(list(viewer.iterdir()))}")
    print("\nRecommended structure:")
    print("  tools/review_tools/")
    print("    - assemblyai_review_studio.*    (NEW UI)")
    print("    - assemblyai_review_generator.py (AssemblyAI)")
    print("    - review_generator.py            (Google/Gemini)")
    print("    - corrections_db.py              (Database)")
    print("    - launch_review_ui.py            (Main launcher)")
    print("    - launch_review.bat              (Windows shortcut)")
    print("    - launch_with_logging.bat        (With API)")
    print("    - test_assemblyai_review.py      (Testing)")
    print("    - README.md                      (Documentation)")
    print("    - archived/                      (Old versions)")
    print("    - viewer/                        (Transcript viewer)")

if __name__ == "__main__":
    cleanup_review_tools()

