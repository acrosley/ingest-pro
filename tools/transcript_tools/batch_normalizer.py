#!/usr/bin/env python3
"""
Batch Transcript Normalizer
Processes files in batches of 10 in a temporary folder to preserve original data
"""

import re
import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime
import tempfile
import os

class BatchTranscriptNormalizer:
    def __init__(self):
        # Speaker normalization mappings
        self.speaker_mappings = {
            'audio': 'System',
            'agent': 'Agent',
            'caller': 'Caller',
            'system': 'System',
            'voicemail': 'System',
            'operator': 'System',
            'receptionist': 'System',
            'nurse': 'Medical Staff',
            'doctor': 'Medical Staff',
            'dr.': 'Medical Staff',
            'dr ': 'Medical Staff',
        }
    
    def normalize_transcript(self, transcript_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize transcript data into consistent format
        
        Args:
            transcript_data: List of transcript segments from JSON
            
        Returns:
            List of normalized transcript segments
        """
        normalized_segments = []
        
        for segment in transcript_data:
            text = segment.get('text', '')
            timestamp = segment.get('timestamp', '')
            speaker = segment.get('speaker', '')
            
            # If already properly structured with all fields, keep as is
            if timestamp and speaker and text and not timestamp.startswith('['):
                normalized_segments.append({
                    'timestamp': timestamp,
                    'speaker': self.normalize_speaker(speaker),
                    'text': text.strip()
                })
            else:
                # Parse the text to extract segments
                parsed_segments = self.parse_transcript_text(text)
                normalized_segments.extend(parsed_segments)
        
        return normalized_segments
    
    def parse_transcript_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse transcript text to extract individual segments
        
        Args:
            text: Raw transcript text
            
        Returns:
            List of parsed segments
        """
        segments = []
        
        # Pattern 1: [timestamp] **Speaker:** text (embedded format)
        # Example: [00:00:01] **Audio:** Hi, and thanks for calling...
        pattern1 = r'\[(\d{2}:\d{2}:\d{2})\] \*\*([^:]+):\*\* (.+?)(?=\[\d{2}:\d{2}:\d{2}\]|\Z)'
        matches1 = re.findall(pattern1, text, re.DOTALL)
        
        if matches1:
            for timestamp, speaker, segment_text in matches1:
                segments.append({
                    'timestamp': timestamp,
                    'speaker': self.normalize_speaker(speaker),
                    'text': segment_text.strip()
                })
            return segments
        
        # Pattern 2: Speaker: [timestamp] text (mixed format)
        # Example: Agent: [00:00:03] Hello. Caller: [00:00:04] Hello Mr. Brown?
        pattern2 = r'([^:]+): \[(\d{2}:\d{2}:\d{2})\] (.+?)(?=[^:]+: \[\d{2}:\d{2}:\d{2}\]|\Z)'
        matches2 = re.findall(pattern2, text, re.DOTALL)
        
        if matches2:
            for speaker, timestamp, segment_text in matches2:
                segments.append({
                    'timestamp': timestamp,
                    'speaker': self.normalize_speaker(speaker),
                    'text': segment_text.strip()
                })
            return segments
        
        # Pattern 3: [timestamp] Speaker: text (simple embedded)
        # Example: [00:00:01] Audio: Hi, and thanks for calling...
        pattern3 = r'\[(\d{2}:\d{2}:\d{2})\] ([^:]+): (.+?)(?=\[\d{2}:\d{2}:\d{2}\]|\Z)'
        matches3 = re.findall(pattern3, text, re.DOTALL)
        
        if matches3:
            for timestamp, speaker, segment_text in matches3:
                segments.append({
                    'timestamp': timestamp,
                    'speaker': self.normalize_speaker(speaker),
                    'text': segment_text.strip()
                })
            return segments
        
        # Pattern 4: Single block with embedded timestamps but no speaker labels
        # Example: [00:00:05] Your call has been forwarded to voicemail... [00:00:17] Good morning...
        pattern4 = r'\[(\d{2}:\d{2}:\d{2})\] (.+?)(?=\[\d{2}:\d{2}:\d{2}\]|\Z)'
        matches4 = re.findall(pattern4, text, re.DOTALL)
        
        if matches4:
            for timestamp, segment_text in matches4:
                # Try to determine speaker from context
                speaker = self.determine_speaker_from_context(segment_text)
                segments.append({
                    'timestamp': timestamp,
                    'speaker': speaker,
                    'text': segment_text.strip()
                })
            return segments
        
        # Fallback: treat as single segment
        segments.append({
            'timestamp': '',
            'speaker': 'Unknown',
            'text': text.strip()
        })
        
        return segments
    
    def determine_speaker_from_context(self, text: str) -> str:
        """
        Determine speaker from text context
        
        Args:
            text: Text segment
            
        Returns:
            Determined speaker
        """
        text_lower = text.lower()
        
        # Check for system messages
        if any(keyword in text_lower for keyword in [
            'voicemail', 'forwarded', 'unavailable', 'tone', 'hang up',
            'thank you for calling', 'office hours', 'fax number'
        ]):
            return 'System'
        
        # Check for agent introductions
        if any(keyword in text_lower for keyword in [
            'crosley law', 'this is', 'how can i help', 'agent'
        ]):
            return 'Agent'
        
        # Check for caller responses
        if any(keyword in text_lower for keyword in [
            'yes ma\'am', 'yes sir', 'i was', 'i had', 'i need'
        ]):
            return 'Caller'
        
        # Default to Unknown if can't determine
        return 'Unknown'
    
    def normalize_speaker(self, speaker: str) -> str:
        """
        Normalize speaker names to consistent format
        
        Args:
            speaker: Raw speaker name
            
        Returns:
            Normalized speaker name
        """
        speaker_lower = speaker.lower().strip()
        
        # Check mappings
        for key, value in self.speaker_mappings.items():
            if key in speaker_lower:
                return value
        
        # Handle common variations
        if 'agent' in speaker_lower:
            return 'Agent'
        elif 'caller' in speaker_lower:
            return 'Caller'
        elif 'audio' in speaker_lower:
            return 'System'
        elif 'system' in speaker_lower:
            return 'System'
        elif 'voicemail' in speaker_lower:
            return 'System'
        
        # Return original if no mapping found
        return speaker.strip()
    
    def process_json_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a single JSON file and normalize its transcript
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Updated JSON data with normalized transcript
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Normalize transcript
            if 'transcript' in data:
                original_transcript = data['transcript']
                normalized_transcript = self.normalize_transcript(original_transcript)
                data['transcript'] = normalized_transcript
                
                # Add normalization metadata
                data['normalization_info'] = {
                    'original_segments': len(original_transcript),
                    'normalized_segments': len(normalized_transcript),
                    'normalized_at': datetime.now().isoformat(),
                    'normalizer_version': '2.0'
                }
            
            return data
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None
    
    def process_batch(self, source_directory: Path, batch_size: int = 10) -> Dict[str, Any]:
        """
        Process files in batches of specified size
        
        Args:
            source_directory: Directory containing JSON files
            batch_size: Number of files to process in each batch
            
        Returns:
            Processing results
        """
        results = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'batches': [],
            'temp_directories': []
        }
        
        # Get all JSON files
        json_files = list(source_directory.glob('*.json'))
        results['total_files'] = len(json_files)
        
        print(f"Found {len(json_files)} JSON files to process")
        print(f"Processing in batches of {batch_size}")
        
        # Process in batches
        for batch_num, i in enumerate(range(0, len(json_files), batch_size), 1):
            batch_files = json_files[i:i + batch_size]
            
            print(f"\n=== BATCH {batch_num} ===")
            print(f"Processing files {i+1}-{min(i+batch_size, len(json_files))} of {len(json_files)}")
            
            # Create temporary directory for this batch
            temp_dir = Path(tempfile.mkdtemp(prefix=f"batch_{batch_num}_"))
            results['temp_directories'].append(str(temp_dir))
            
            batch_results = {
                'batch_number': batch_num,
                'temp_directory': str(temp_dir),
                'files_processed': 0,
                'files_failed': 0,
                'processed_files': [],
                'failed_files': []
            }
            
            # Copy files to temp directory
            for json_file in batch_files:
                temp_file = temp_dir / json_file.name
                shutil.copy2(json_file, temp_file)
                print(f"  Copied: {json_file.name}")
            
            # Process files in temp directory
            for json_file in batch_files:
                temp_file = temp_dir / json_file.name
                print(f"  Processing: {json_file.name}")
                
                normalized_data = self.process_json_file(temp_file)
                
                if normalized_data:
                    # Write normalized data back to temp file
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        json.dump(normalized_data, f, indent=2, ensure_ascii=False)
                    
                    batch_results['files_processed'] += 1
                    batch_results['processed_files'].append(json_file.name)
                    results['processed_files'] += 1
                    print(f"    ✓ Normalized successfully")
                else:
                    batch_results['files_failed'] += 1
                    batch_results['failed_files'].append(json_file.name)
                    results['failed_files'] += 1
                    print(f"    ✗ Failed to normalize")
            
            results['batches'].append(batch_results)
            
            print(f"Batch {batch_num} complete: {batch_results['files_processed']} processed, {batch_results['files_failed']} failed")
            print(f"Temp directory: {temp_dir}")
        
        return results
    
    def cleanup_temp_directories(self, temp_directories: List[str]):
        """
        Clean up temporary directories
        
        Args:
            temp_directories: List of temporary directory paths
        """
        for temp_dir in temp_directories:
            try:
                shutil.rmtree(temp_dir)
                print(f"Cleaned up: {temp_dir}")
            except Exception as e:
                print(f"Failed to clean up {temp_dir}: {e}")
    
    def save_results(self, results: Dict[str, Any], output_file: Path):
        """
        Save processing results to file
        
        Args:
            results: Processing results
            output_file: Path to save results
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to: {output_file}")

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch transcript normalizer')
    parser.add_argument('input_path', help='Input directory containing JSON files')
    parser.add_argument('--batch-size', '-b', type=int, default=10, help='Batch size (default: 10)')
    parser.add_argument('--keep-temp', '-k', action='store_true', help='Keep temporary directories')
    parser.add_argument('--results-file', '-r', help='File to save results (default: batch_results.json)')
    
    args = parser.parse_args()
    
    normalizer = BatchTranscriptNormalizer()
    input_path = Path(args.input_path)
    
    if not input_path.is_dir():
        print(f"Error: {input_path} is not a directory")
        return
    
    # Process batches
    print("Starting batch processing...")
    results = normalizer.process_batch(input_path, args.batch_size)
    
    # Print summary
    print("\n" + "=" * 60)
    print("PROCESSING SUMMARY")
    print("=" * 60)
    print(f"Total files: {results['total_files']}")
    print(f"Successfully processed: {results['processed_files']}")
    print(f"Failed: {results['failed_files']}")
    print(f"Batches: {len(results['batches'])}")
    
    print("\nBatch details:")
    for batch in results['batches']:
        print(f"  Batch {batch['batch_number']}: {batch['files_processed']} processed, {batch['files_failed']} failed")
        print(f"    Temp directory: {batch['temp_directory']}")
    
    # Save results
    results_file = Path(args.results_file) if args.results_file else Path("batch_results.json")
    normalizer.save_results(results, results_file)
    
    # Cleanup
    if not args.keep_temp:
        print("\nCleaning up temporary directories...")
        normalizer.cleanup_temp_directories(results['temp_directories'])
    else:
        print("\nTemporary directories preserved:")
        for temp_dir in results['temp_directories']:
            print(f"  {temp_dir}")
    
    print("\nBatch processing complete!")

if __name__ == "__main__":
    main()
