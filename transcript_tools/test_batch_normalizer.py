#!/usr/bin/env python3
"""
Test script for batch transcript normalizer
Tests the normalizer with a small sample of files
"""

from batch_normalizer import BatchTranscriptNormalizer
from pathlib import Path
import json

def test_batch_normalizer():
    """Test the batch normalizer with a small sample"""
    
    print("=== BATCH NORMALIZER TEST ===\n")
    
    # Create test normalizer
    normalizer = BatchTranscriptNormalizer()
    
    # Test with a small batch size
    source_dir = Path("W:/Staff_Call_Recordings/_Pipeline_Output/ALL_JSON_FILES")
    
    if not source_dir.exists():
        print(f"Error: Source directory not found: {source_dir}")
        return
    
    # Count files
    json_files = list(source_dir.glob('*.json'))
    print(f"Found {len(json_files)} JSON files in source directory")
    
    if len(json_files) == 0:
        print("No JSON files found to process")
        return
    
    # Test with first 5 files
    test_batch_size = 5
    print(f"Testing with batch size of {test_batch_size}")
    
    # Process test batch
    results = normalizer.process_batch(source_dir, test_batch_size)
    
    # Print results
    print("\n=== TEST RESULTS ===")
    print(f"Total files: {results['total_files']}")
    print(f"Processed: {results['processed_files']}")
    print(f"Failed: {results['failed_files']}")
    print(f"Batches: {len(results['batches'])}")
    
    print("\nBatch details:")
    for batch in results['batches']:
        print(f"  Batch {batch['batch_number']}:")
        print(f"    Files processed: {batch['files_processed']}")
        print(f"    Files failed: {batch['files_failed']}")
        print(f"    Temp directory: {batch['temp_directory']}")
        
        if batch['processed_files']:
            print(f"    Successfully processed:")
            for file_name in batch['processed_files']:
                print(f"      - {file_name}")
        
        if batch['failed_files']:
            print(f"    Failed to process:")
            for file_name in batch['failed_files']:
                print(f"      - {file_name}")
    
    # Save test results
               test_results_file = Path("../batch_results/test_batch_results.json")
    normalizer.save_results(results, test_results_file)
    
    # Keep temp directories for inspection
    print(f"\nTemp directories preserved for inspection:")
    for temp_dir in results['temp_directories']:
        print(f"  {temp_dir}")
    
    print(f"\nTest results saved to: {test_results_file}")
    print("Test completed!")

def test_single_file_normalization():
    """Test normalization of a single file"""
    
    print("\n=== SINGLE FILE NORMALIZATION TEST ===\n")
    
    normalizer = BatchTranscriptNormalizer()
    
    # Test with a known file
    test_file = Path("W:/Staff_Call_Recordings/_Pipeline_Output/ALL_JSON_FILES/x542_2025-08-21.10-10.007.json")
    
    if not test_file.exists():
        print(f"Test file not found: {test_file}")
        return
    
    print(f"Testing normalization of: {test_file.name}")
    
    # Process the file
    normalized_data = normalizer.process_json_file(test_file)
    
    if normalized_data:
        print("✓ File processed successfully")
        
        # Show normalization info
        if 'normalization_info' in normalized_data:
            info = normalized_data['normalization_info']
            print(f"  Original segments: {info['original_segments']}")
            print(f"  Normalized segments: {info['normalized_segments']}")
            print(f"  Normalized at: {info['normalized_at']}")
        
        # Show sample of normalized transcript
        if 'transcript' in normalized_data:
            transcript = normalized_data['transcript']
            print(f"\nSample of normalized transcript ({len(transcript)} segments):")
            
            for i, segment in enumerate(transcript[:3], 1):  # Show first 3 segments
                print(f"  Segment {i}:")
                print(f"    Timestamp: {segment['timestamp']}")
                print(f"    Speaker: {segment['speaker']}")
                print(f"    Text: {segment['text'][:100]}...")
                print()
            
            if len(transcript) > 3:
                print(f"  ... and {len(transcript) - 3} more segments")
    else:
        print("✗ File processing failed")

if __name__ == "__main__":
    test_single_file_normalization()
    test_batch_normalizer()
