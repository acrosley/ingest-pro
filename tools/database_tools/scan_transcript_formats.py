#!/usr/bin/env python3
"""
Scan JSON files to identify different transcript formats
Helps identify edge cases for the normalizer
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

def scan_json_files(directory_path: str, sample_size: int = 100):
    """
    Scan JSON files to identify transcript format patterns
    
    Args:
        directory_path: Path to directory containing JSON files
        sample_size: Number of files to sample
    """
    
    directory = Path(directory_path)
    json_files = list(directory.glob("*.json"))
    
    # Sample files if too many
    if len(json_files) > sample_size:
        json_files = json_files[:sample_size]
    
    results = {
        "total_files": len(json_files),
        "transcript_formats": defaultdict(list),
        "missing_transcript": [],
        "errors": [],
        "sample_data": {}
    }
    
    print(f"Scanning {len(json_files)} JSON files...")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'transcript' not in data:
                results["missing_transcript"].append(json_file.name)
                continue
            
            transcript = data['transcript']
            format_type = type(transcript).__name__
            
            if format_type == "str":
                # String transcript - check format
                if transcript.startswith("["):
                    results["transcript_formats"]["string_timestamped"].append(json_file.name)
                    if len(results["sample_data"]) < 3:
                        results["sample_data"][f"string_timestamped_{len(results['sample_data'])}"] = transcript[:200] + "..."
                else:
                    results["transcript_formats"]["string_plain"].append(json_file.name)
                    if len(results["sample_data"]) < 3:
                        results["sample_data"][f"string_plain_{len(results['sample_data'])}"] = transcript[:200] + "..."
                        
            elif format_type == "list":
                # List transcript - check structure
                if transcript and isinstance(transcript[0], dict):
                    # Check if it has proper structure
                    first_segment = transcript[0]
                    if 'timestamp' in first_segment and 'speaker' in first_segment and 'text' in first_segment:
                        results["transcript_formats"]["list_structured"].append(json_file.name)
                    else:
                        results["transcript_formats"]["list_unstructured"].append(json_file.name)
                        if len(results["sample_data"]) < 3:
                            results["sample_data"][f"list_unstructured_{len(results['sample_data'])}"] = str(first_segment)
                else:
                    results["transcript_formats"]["list_empty_or_invalid"].append(json_file.name)
            else:
                results["transcript_formats"]["other_type"].append(json_file.name)
                if len(results["sample_data"]) < 3:
                    results["sample_data"][f"other_{len(results['sample_data'])}"] = str(transcript)[:200] + "..."
                    
        except Exception as e:
            results["errors"].append(f"{json_file.name}: {str(e)}")
    
    return results

def print_results(results):
    """Print scan results in a readable format"""
    
    print("\n" + "=" * 60)
    print("TRANSCRIPT FORMAT SCAN RESULTS")
    print("=" * 60)
    
    print(f"Total files scanned: {results['total_files']}")
    print(f"Files with errors: {len(results['errors'])}")
    print(f"Files missing transcript: {len(results['missing_transcript'])}")
    
    print(f"\nTRANSCRIPT FORMATS FOUND:")
    for format_type, files in results['transcript_formats'].items():
        print(f"  {format_type}: {len(files)} files")
        if files and len(files) <= 5:
            print(f"    Examples: {files}")
        elif files:
            print(f"    Examples: {files[:3]} (and {len(files)-3} more)")
    
    if results['missing_transcript']:
        print(f"\nFILES WITHOUT TRANSCRIPT:")
        for file in results['missing_transcript'][:10]:
            print(f"  - {file}")
        if len(results['missing_transcript']) > 10:
            print(f"  ... and {len(results['missing_transcript']) - 10} more")
    
    if results['sample_data']:
        print(f"\nSAMPLE DATA:")
        for format_name, sample in results['sample_data'].items():
            print(f"\n{format_name}:")
            print(f"  {sample}")
    
    if results['errors']:
        print(f"\nERRORS:")
        for error in results['errors'][:5]:
            print(f"  - {error}")
        if len(results['errors']) > 5:
            print(f"  ... and {len(results['errors']) - 5} more errors")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = "W:/Staff_Call_Recordings/_Pipeline_Output/ALL_JSON_FILES"
    
    sample_size = 200  # Check more files
    
    print(f"Scanning JSON files in: {directory}")
    print(f"Sample size: {sample_size}")
    
    results = scan_json_files(directory, sample_size)
    print_results(results)
    
    # Generate recommendations
    print(f"\n" + "=" * 60)
    print("NORMALIZER RECOMMENDATIONS")
    print("=" * 60)
    
    total_problematic = (
        len(results['missing_transcript']) + 
        len(results['transcript_formats']['string_timestamped']) +
        len(results['transcript_formats']['string_plain']) +
        len(results['transcript_formats']['list_unstructured']) +
        len(results['transcript_formats']['list_empty_or_invalid']) +
        len(results['transcript_formats']['other_type'])
    )
    
    print(f"Files needing normalization: {total_problematic}")
    print(f"Files already normalized: {len(results['transcript_formats']['list_structured'])}")
    
    if results['missing_transcript']:
        print(f"\n⚠️  {len(results['missing_transcript'])} files are missing transcript data entirely")
        print("   These may need to be reprocessed or have transcript files restored")
    
    if results['transcript_formats']['string_timestamped']:
        print(f"\n✅ {len(results['transcript_formats']['string_timestamped'])} files have string transcripts with timestamps")
        print("   These can be normalized using existing patterns")
    
    if results['transcript_formats']['string_plain']:
        print(f"\n⚠️  {len(results['transcript_formats']['string_plain'])} files have plain string transcripts")
        print("   These need basic string-to-segment conversion")

if __name__ == "__main__":
    main()
