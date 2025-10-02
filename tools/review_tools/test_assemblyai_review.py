"""
Test script for AssemblyAI Review Generator

Generates a sample review from existing AssemblyAI confidence data.
"""

import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.review_tools.assemblyai_review_generator import (
    AssemblyAIReviewConfig,
    generate_assemblyai_review,
    load_expected_terms,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("=" * 70)
    print("AssemblyAI Review Generator Test")
    print("=" * 70)
    
    # Look for demo files
    demo_dir = Path("demo/Transcripts")
    
    if not demo_dir.exists():
        print(f"\nError: Demo directory not found: {demo_dir}")
        print("Please run this script from the project root directory.")
        return 1
    
    # Find confidence JSON files
    confidence_files = list(demo_dir.glob("*.confidence.json"))
    
    if not confidence_files:
        print(f"\nNo confidence.json files found in {demo_dir}")
        print("Please generate some transcripts first using AssemblyAI.")
        return 1
    
    print(f"\nFound {len(confidence_files)} confidence file(s):")
    for i, f in enumerate(confidence_files, 1):
        print(f"  {i}. {f.name}")
    
    # Process the first one as a test
    test_file = confidence_files[0]
    transcript_file = test_file.parent / test_file.name.replace(".confidence.json", ".txt")
    
    if not transcript_file.exists():
        print(f"\nError: Transcript file not found: {transcript_file}")
        return 1
    
    print(f"\nTesting with: {test_file.name}")
    print(f"Transcript: {transcript_file.name}")
    
    # Create review config
    config = AssemblyAIReviewConfig(
        enabled=True,
        output_directory="demo/Transcripts",
        low_confidence_threshold=0.70,
        flag_phone_numbers=True,
        flag_case_numbers=True,
        flag_money_amounts=True,
        flag_dates=True,
        flag_times=True,
        flag_names=True,
        flag_numbers=True,
    )
    
    print("\nReview Configuration:")
    print(f"  - Low confidence threshold: {config.low_confidence_threshold}")
    print(f"  - Flag phone numbers: {config.flag_phone_numbers}")
    print(f"  - Flag names: {config.flag_names}")
    print(f"  - Output directory: {config.output_directory}")
    
    # Load expected terms
    expected_terms_file = Path("config/nouns_to_expect.txt")
    expected_terms = load_expected_terms(expected_terms_file) if expected_terms_file.exists() else []
    
    if expected_terms:
        print(f"\nLoaded {len(expected_terms)} expected terms")
    
    # Generate review
    print("\nGenerating review...")
    try:
        review_path = generate_assemblyai_review(
            confidence_json_path=test_file,
            transcript_path=transcript_file,
            config=config,
            expected_terms=expected_terms
        )
        
        if review_path:
            print(f"\n✓ Success! Review generated: {review_path}")
            print(f"\nYou can now:")
            print(f"  1. Open the review UI: python launch_assemblyai_review.py")
            print(f"  2. Load the review file: {review_path}")
            print(f"  3. Start reviewing and correcting flagged words")
            return 0
        else:
            print("\n✗ Review generation returned None (check logs)")
            return 1
            
    except Exception as e:
        print(f"\n✗ Error generating review: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())

