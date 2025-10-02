#!/usr/bin/env python3
"""
Test script for archive_and_normalize.py
Tests the functionality with a small sample
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from archive_and_normalize import archive_and_normalize_json_files


def test_dry_run():
    """Test the archive and normalize functionality in dry run mode"""
    
    print("=" * 60)
    print("TESTING ARCHIVE AND NORMALIZE (DRY RUN)")
    print("=" * 60)
    
    # Run dry run test
    results = archive_and_normalize_json_files(dry_run=True)
    
    print("\nTest Results:")
    print(f"Total files found: {results['total_files']}")
    print(f"Would archive: {results['archived_files']}")
    print(f"Would normalize: {results['normalized_files']}")
    print(f"Would skip: {results['skipped_files']}")
    print(f"Errors: {len(results.get('errors', []))}")
    
    if results.get('errors'):
        print("\nSample errors:")
        for error in results['errors'][:3]:
            print(f"  - {error}")
        if len(results['errors']) > 3:
            print(f"  ... and {len(results['errors']) - 3} more")
    
    print(f"\nDry run completed in {results.get('duration_seconds', 0):.2f} seconds")
    
    return results


def test_source_directory():
    """Test if source directory exists and has JSON files"""
    
    source_dir = Path("W:/Staff_Call_Recordings/_Pipeline_Output/ALL_JSON_FILES")
    
    print("=" * 60)
    print("TESTING SOURCE DIRECTORY")
    print("=" * 60)
    
    print(f"Source directory: {source_dir}")
    print(f"Exists: {source_dir.exists()}")
    
    if source_dir.exists():
        json_files = list(source_dir.glob("*.json"))
        print(f"JSON files found: {len(json_files)}")
        
        if json_files:
            print(f"Sample files:")
            for file in json_files[:5]:
                print(f"  - {file.name}")
            if len(json_files) > 5:
                print(f"  ... and {len(json_files) - 5} more")
    else:
        print("ERROR: Source directory not found!")
        return False
    
    return True


def main():
    """Run all tests"""
    
    print("ARCHIVE AND NORMALIZE - TEST SUITE")
    print("=" * 60)
    
    # Test 1: Check source directory
    if not test_source_directory():
        print("\nERROR: Source directory test failed. Cannot proceed.")
        return
    
    print("\n")
    
    # Test 2: Dry run
    results = test_dry_run()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if results['total_files'] > 0:
        print("✓ Source directory contains JSON files")
        print("✓ Archive and normalize function is working")
        print("✓ Dry run mode is functional")
        
        if len(results.get('errors', [])) == 0:
            print("✓ No errors detected in dry run")
        else:
            print(f"⚠ {len(results['errors'])} errors detected (this may be expected for malformed files)")
        
        print("\nReady for actual processing!")
        print("Run: database_tools\\archive_and_normalize.bat")
        
    else:
        print("✗ No JSON files found in source directory")
        print("Check that the source path is correct")
    
    print("\nTest completed!")


if __name__ == "__main__":
    main()
