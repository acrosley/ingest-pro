#!/usr/bin/env python3
"""
Apply Normalized Files
Copies normalized files from temp directories back to the original folder
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict, Any
import argparse

def load_batch_results(results_file: Path) -> Dict[str, Any]:
    """Load batch processing results from JSON file"""
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading results file: {e}")
        return None

def apply_normalized_files(results_file: Path, source_directory: Path, backup: bool = True) -> bool:
    """
    Apply normalized files from temp directories to original folder
    
    Args:
        results_file: Path to batch_results.json file
        source_directory: Original directory containing JSON files
        backup: Whether to create a backup before applying changes
        
    Returns:
        True if successful, False otherwise
    """
    
    # Load batch results
    print("Loading batch results...")
    results = load_batch_results(results_file)
    if not results:
        return False
    
    print(f"Found {len(results['batches'])} batches with {results['processed_files']} processed files")
    
    # Create backup if requested
    if backup:
        backup_dir = source_directory.parent / f"{source_directory.name}_BACKUP"
        print(f"Creating backup at: {backup_dir}")
        
        if backup_dir.exists():
            print(f"Warning: Backup directory already exists: {backup_dir}")
            response = input("Continue anyway? (y/N): ").lower()
            if response != 'y':
                print("Operation cancelled.")
                return False
        
        try:
            shutil.copytree(source_directory, backup_dir)
            print(f"✓ Backup created successfully")
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    # Process each batch
    total_copied = 0
    total_failed = 0
    
    for batch in results['batches']:
        temp_dir = Path(batch['temp_directory'])
        
        if not temp_dir.exists():
            print(f"Warning: Temp directory not found: {temp_dir}")
            continue
        
        print(f"\nProcessing batch {batch['batch_number']}: {temp_dir}")
        
        # Copy each processed file from temp directory to original
        for file_name in batch['processed_files']:
            temp_file = temp_dir / file_name
            original_file = source_directory / file_name
            
            if temp_file.exists():
                try:
                    shutil.copy2(temp_file, original_file)
                    print(f"  ✓ Copied: {file_name}")
                    total_copied += 1
                except Exception as e:
                    print(f"  ✗ Failed to copy {file_name}: {e}")
                    total_failed += 1
            else:
                print(f"  ⚠️  Temp file not found: {temp_file}")
                total_failed += 1
    
    # Summary
    print(f"\n" + "=" * 60)
    print("APPLICATION SUMMARY")
    print("=" * 60)
    print(f"Total files copied: {total_copied}")
    print(f"Total files failed: {total_failed}")
    print(f"Original directory: {source_directory}")
    
    if backup:
        print(f"Backup directory: {backup_dir}")
    
    if total_copied > 0:
        print(f"\n✓ Successfully applied {total_copied} normalized files!")
        print("Your original files now contain normalized transcripts.")
    else:
        print(f"\n✗ No files were applied successfully.")
    
    return total_copied > 0

def cleanup_temp_directories(results_file: Path) -> bool:
    """
    Clean up temporary directories after applying changes
    
    Args:
        results_file: Path to batch_results.json file
        
    Returns:
        True if successful, False otherwise
    """
    
    results = load_batch_results(results_file)
    if not results:
        return False
    
    print("\nCleaning up temporary directories...")
    
    cleaned = 0
    failed = 0
    
    for temp_dir_str in results['temp_directories']:
        temp_dir = Path(temp_dir_str)
        if temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
                print(f"  ✓ Cleaned: {temp_dir}")
                cleaned += 1
            except Exception as e:
                print(f"  ✗ Failed to clean {temp_dir}: {e}")
                failed += 1
        else:
            print(f"  ⚠️  Temp directory not found: {temp_dir}")
    
    print(f"\nCleanup complete: {cleaned} cleaned, {failed} failed")
    return failed == 0

def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description='Apply normalized files to original directory')
    parser.add_argument('results_file', help='Path to batch_results.json file')
    parser.add_argument('source_directory', help='Original directory containing JSON files')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backup')
    parser.add_argument('--cleanup', action='store_true', help='Clean up temp directories after applying')
    
    args = parser.parse_args()
    
    results_file = Path(args.results_file)
    source_directory = Path(args.source_directory)
    
    if not results_file.exists():
        print(f"Error: Results file not found: {results_file}")
        return
    
    if not source_directory.exists():
        print(f"Error: Source directory not found: {source_directory}")
        return
    
    print("=" * 60)
    print("APPLY NORMALIZED FILES")
    print("=" * 60)
    print(f"Results file: {results_file}")
    print(f"Source directory: {source_directory}")
    print(f"Create backup: {not args.no_backup}")
    print(f"Cleanup temp dirs: {args.cleanup}")
    print("=" * 60)
    
    # Confirm action
    print("\n⚠️  WARNING: This will modify files in the original directory!")
    if not args.no_backup:
        print("A backup will be created before applying changes.")
    else:
        print("No backup will be created - proceed with caution!")
    
    response = input("\nContinue? (y/N): ").lower()
    if response != 'y':
        print("Operation cancelled.")
        return
    
    # Apply normalized files
    success = apply_normalized_files(
        results_file, 
        source_directory, 
        backup=not args.no_backup
    )
    
    # Cleanup if requested
    if success and args.cleanup:
        cleanup_temp_directories(results_file)
    
    print("\nOperation complete!")

if __name__ == "__main__":
    main()
