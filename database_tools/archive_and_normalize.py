#!/usr/bin/env python3
"""
Archive and Normalize JSON Files
Single method to safely archive original JSON files and normalize working copies
"""

import json
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
import os

# Add transcript_tools to path for normalizer import
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'transcript_tools'))

try:
    from transcript_normalizer_module import TranscriptNormalizer
except ImportError:
    print("Warning: transcript_normalizer_module not found. Normalization will be limited.")
    TranscriptNormalizer = None


class ArchiveAndNormalizer:
    """Handles archiving original files and normalizing working copies"""
    
    def __init__(self, 
                 source_dir: str = "W:/Staff_Call_Recordings/_Pipeline_Output/ALL_JSON_FILES",
                 backup_dir: str = "W:/Staff_Call_Recordings/_Pipeline_Output/ALL_JSON_FILES_BACKUP"):
        """
        Initialize the archive and normalizer
        
        Args:
            source_dir: Directory containing JSON files to process
            backup_dir: Directory to store archived original files
        """
        self.source_dir = Path(source_dir)
        self.backup_dir = Path(backup_dir)
        self.normalizer = TranscriptNormalizer() if TranscriptNormalizer else None
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path(__file__).parent.parent / "Logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "archive_and_normalize.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def archive_and_normalize_files(self, 
                                   force_backup: bool = False,
                                   dry_run: bool = False) -> Dict[str, Any]:
        """
        Single method to archive original JSON files and normalize working copies
        
        Args:
            force_backup: If True, overwrite existing backup files
            dry_run: If True, show what would be done without making changes
            
        Returns:
            Dictionary with processing results and statistics
        """
        
        results = {
            "start_time": datetime.now().isoformat(),
            "source_directory": str(self.source_dir),
            "backup_directory": str(self.backup_dir),
            "dry_run": dry_run,
            "total_files": 0,
            "archived_files": 0,
            "normalized_files": 0,
            "skipped_files": 0,
            "failed_files": 0,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Validate source directory
            if not self.source_dir.exists():
                raise FileNotFoundError(f"Source directory not found: {self.source_dir}")
            
            # Create backup directory if it doesn't exist
            if not dry_run:
                self.backup_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Backup directory: {self.backup_dir}")
            
            # Get all JSON files
            json_files = list(self.source_dir.glob("*.json"))
            results["total_files"] = len(json_files)
            
            self.logger.info(f"Found {len(json_files)} JSON files to process")
            self.logger.info(f"Dry run mode: {dry_run}")
            
            if dry_run:
                self.logger.info("=== DRY RUN MODE - No files will be modified ===")
            
            # Process each file
            for json_file in json_files:
                try:
                    self._process_file(json_file, results, force_backup, dry_run)
                except Exception as e:
                    error_msg = f"Failed to process {json_file.name}: {str(e)}"
                    self.logger.error(error_msg)
                    results["failed_files"] += 1
                    results["errors"].append(error_msg)
            
            # Final summary
            results["end_time"] = datetime.now().isoformat()
            results["duration_seconds"] = (
                datetime.fromisoformat(results["end_time"]) - 
                datetime.fromisoformat(results["start_time"])
            ).total_seconds()
            
            self._log_summary(results)
            
        except Exception as e:
            error_msg = f"Critical error in archive_and_normalize_files: {str(e)}"
            self.logger.error(error_msg)
            results["errors"].append(error_msg)
            results["end_time"] = datetime.now().isoformat()
        
        return results
    
    def _process_file(self, json_file: Path, results: Dict[str, Any], 
                     force_backup: bool, dry_run: bool) -> None:
        """
        Process a single JSON file: archive original and normalize working copy
        
        Args:
            json_file: Path to the JSON file to process
            results: Results dictionary to update
            force_backup: Whether to overwrite existing backup files
            dry_run: Whether this is a dry run
        """
        backup_file = self.backup_dir / json_file.name
        
        # Check if backup already exists
        if backup_file.exists() and not force_backup:
            self.logger.debug(f"Backup already exists, skipping: {json_file.name}")
            results["skipped_files"] += 1
            return
        
        # Load and validate JSON file
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            error_msg = f"Failed to read {json_file.name}: {str(e)}"
            self.logger.error(error_msg)
            results["errors"].append(error_msg)
            results["failed_files"] += 1
            return
        
        # Archive original file
        if not dry_run:
            try:
                shutil.copy2(json_file, backup_file)
                self.logger.debug(f"Archived: {json_file.name}")
                results["archived_files"] += 1
            except Exception as e:
                error_msg = f"Failed to archive {json_file.name}: {str(e)}"
                self.logger.error(error_msg)
                results["errors"].append(error_msg)
                results["failed_files"] += 1
                return
        else:
            self.logger.info(f"[DRY RUN] Would archive: {json_file.name}")
            results["archived_files"] += 1
        
        # Normalize the working copy
        try:
            normalized_data = self._normalize_json_data(data)
            
            if not dry_run:
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(normalized_data, f, indent=2, ensure_ascii=False)
                self.logger.debug(f"Normalized: {json_file.name}")
            else:
                self.logger.info(f"[DRY RUN] Would normalize: {json_file.name}")
            
            results["normalized_files"] += 1
            
        except Exception as e:
            error_msg = f"Failed to normalize {json_file.name}: {str(e)}"
            self.logger.error(error_msg)
            results["errors"].append(error_msg)
            results["failed_files"] += 1
    
    def _normalize_json_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize JSON data structure, particularly transcript data
        
        Args:
            data: Original JSON data
            
        Returns:
            Normalized JSON data
        """
        # Create a copy to avoid modifying original
        normalized_data = data.copy()
        
        # Handle missing transcript field
        if 'transcript' not in data:
            self.logger.warning(f"File missing transcript field - attempting to recover from transcript_file")
            
            # Try to recover from transcript_file path if available
            transcript_file = data.get('transcript_file')
            transcript_path = data.get('transcript_path')
            
            if transcript_file or transcript_path:
                # Attempt to read transcript from file
                file_path = transcript_path if transcript_path else transcript_file
                if file_path and Path(file_path).exists():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            raw_transcript = f.read()
                        
                        if self.normalizer:
                            normalized_transcript = self.normalizer.normalize_raw_transcript(raw_transcript)[0]
                        else:
                            normalized_transcript = [{
                                'timestamp': '',
                                'speaker': 'Unknown',
                                'text': raw_transcript.strip()
                            }]
                        
                        normalized_data['transcript'] = normalized_transcript
                        normalized_data['normalization_info'] = {
                            'normalized_at': datetime.now().isoformat(),
                            'method': 'recovered_from_file',
                            'source_file': file_path,
                            'original_format': 'file_recovery',
                            'normalized_segments': len(normalized_transcript),
                            'normalizer_version': '2.0'
                        }
                        
                        self.logger.info(f"Successfully recovered transcript from file: {file_path}")
                        
                    except Exception as e:
                        self.logger.error(f"Failed to recover transcript from file {file_path}: {e}")
                        # Create placeholder transcript
                        normalized_data['transcript'] = [{
                            'timestamp': '',
                            'speaker': 'Unknown',
                            'text': 'Transcript data unavailable - file recovery failed'
                        }]
                        normalized_data['normalization_info'] = {
                            'normalized_at': datetime.now().isoformat(),
                            'method': 'placeholder_created',
                            'error': str(e),
                            'normalizer_version': '2.0'
                        }
                else:
                    # Create placeholder transcript when file doesn't exist
                    normalized_data['transcript'] = [{
                        'timestamp': '',
                        'speaker': 'Unknown',
                        'text': 'Transcript data unavailable - source file not found'
                    }]
                    normalized_data['normalization_info'] = {
                        'normalized_at': datetime.now().isoformat(),
                        'method': 'placeholder_created',
                        'note': f'Source file not found: {file_path}',
                        'normalizer_version': '2.0'
                    }
            else:
                # No transcript file reference - create minimal placeholder
                normalized_data['transcript'] = [{
                    'timestamp': '',
                    'speaker': 'Unknown',
                    'text': 'Transcript data unavailable'
                }]
                normalized_data['normalization_info'] = {
                    'normalized_at': datetime.now().isoformat(),
                    'method': 'placeholder_created',
                    'note': 'No transcript field or file reference found',
                    'normalizer_version': '2.0'
                }
            
            return normalized_data
        
        # Handle existing transcript field
        original_transcript = data['transcript']
        
        # Skip if already normalized (has normalization_info)
        if 'normalization_info' in data:
            self.logger.debug("File already normalized, skipping")
            return normalized_data
        
        # Normalize transcript based on type
        if self.normalizer:
            if isinstance(original_transcript, str):
                # String transcript - parse it
                normalized_transcript, norm_info = self.normalizer.normalize_raw_transcript(original_transcript)
                normalized_data['transcript'] = normalized_transcript
                
                # Merge normalization info
                normalized_data['normalization_info'] = {
                    'normalized_at': datetime.now().isoformat(),
                    'original_format': 'string',
                    'original_segments': norm_info.get('original_segments', 1),
                    'normalized_segments': len(normalized_transcript),
                    'normalization_method': norm_info.get('normalization_method', 'string_parsing'),
                    'normalizer_version': '2.0'
                }
                
            elif isinstance(original_transcript, list):
                # List transcript - normalize structure
                normalized_transcript = self.normalizer.normalize_transcript(original_transcript)
                normalized_data['transcript'] = normalized_transcript
                
                normalized_data['normalization_info'] = {
                    'normalized_at': datetime.now().isoformat(),
                    'original_format': 'list',
                    'original_segments': len(original_transcript),
                    'normalized_segments': len(normalized_transcript),
                    'normalization_method': 'list_structure_normalization',
                    'normalizer_version': '2.0'
                }
                
            else:
                # Unexpected format - convert to string and process
                str_transcript = str(original_transcript)
                normalized_transcript, norm_info = self.normalizer.normalize_raw_transcript(str_transcript)
                normalized_data['transcript'] = normalized_transcript
                
                normalized_data['normalization_info'] = {
                    'normalized_at': datetime.now().isoformat(),
                    'original_format': type(original_transcript).__name__,
                    'original_segments': 1,
                    'normalized_segments': len(normalized_transcript),
                    'normalization_method': 'unknown_type_conversion',
                    'normalizer_version': '2.0',
                    'note': f'Converted {type(original_transcript).__name__} to string for processing'
                }
        
        else:
            # Fallback normalization without full normalizer
            if isinstance(original_transcript, str):
                normalized_data['transcript'] = [{
                    'timestamp': '',
                    'speaker': 'Unknown',
                    'text': original_transcript.strip()
                }]
            elif isinstance(original_transcript, list):
                # Assume it's properly structured
                normalized_data['transcript'] = original_transcript
            else:
                normalized_data['transcript'] = [{
                    'timestamp': '',
                    'speaker': 'Unknown',
                    'text': str(original_transcript)
                }]
            
            normalized_data['normalization_info'] = {
                'normalized_at': datetime.now().isoformat(),
                'method': 'basic_fallback_normalization',
                'note': 'Full normalizer not available',
                'normalizer_version': '2.0'
            }
        
        return normalized_data
    
    def _normalize_single_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Normalize a single JSON file without archiving
        
        Args:
            file_path: Path to the JSON file to normalize
            
        Returns:
            Dict with success status and any error information
        """
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if already normalized
            if 'normalization_info' in data:
                return {"success": True, "message": "File already normalized"}
            
            # Normalize the data
            normalized_data = self._normalize_json_data(data)
            
            # Write back normalized data
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(normalized_data, f, indent=2)
            
            return {"success": True, "message": "File normalized successfully"}
            
        except Exception as e:
            error_msg = f"Failed to normalize {file_path.name}: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _log_summary(self, results: Dict[str, Any]) -> None:
        """Log processing summary"""
        self.logger.info("=" * 60)
        self.logger.info("ARCHIVE AND NORMALIZE SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Source Directory: {results['source_directory']}")
        self.logger.info(f"Backup Directory: {results['backup_directory']}")
        self.logger.info(f"Dry Run Mode: {results['dry_run']}")
        self.logger.info(f"Duration: {results.get('duration_seconds', 0):.2f} seconds")
        self.logger.info("")
        self.logger.info(f"Total files found: {results['total_files']}")
        self.logger.info(f"Files archived: {results['archived_files']}")
        self.logger.info(f"Files normalized: {results['normalized_files']}")
        self.logger.info(f"Files skipped: {results['skipped_files']}")
        self.logger.info(f"Files failed: {results['failed_files']}")
        self.logger.info("")
        
        if results['errors']:
            self.logger.info("ERRORS:")
            for error in results['errors'][-10:]:  # Show last 10 errors
                self.logger.info(f"  - {error}")
            if len(results['errors']) > 10:
                self.logger.info(f"  ... and {len(results['errors']) - 10} more errors")
        
        if results['warnings']:
            self.logger.info("WARNINGS:")
            for warning in results['warnings'][-10:]:  # Show last 10 warnings
                self.logger.info(f"  - {warning}")
        
        self.logger.info("=" * 60)


def archive_and_normalize_json_files(source_dir: Optional[str] = None,
                                    backup_dir: Optional[str] = None,
                                    force_backup: bool = False,
                                    dry_run: bool = False) -> Dict[str, Any]:
    """
    Convenience function to archive and normalize JSON files
    
    Args:
        source_dir: Directory containing JSON files (default: ALL_JSON_FILES)
        backup_dir: Directory to store backups (default: ALL_JSON_FILES_BACKUP)
        force_backup: Overwrite existing backup files
        dry_run: Show what would be done without making changes
        
    Returns:
        Dictionary with processing results
    """
    # Use default paths if not provided
    if source_dir is None:
        source_dir = "W:/Staff_Call_Recordings/_Pipeline_Output/ALL_JSON_FILES"
    if backup_dir is None:
        backup_dir = "W:/Staff_Call_Recordings/_Pipeline_Output/ALL_JSON_FILES_BACKUP"
    
    processor = ArchiveAndNormalizer(source_dir, backup_dir)
    return processor.archive_and_normalize_files(force_backup=force_backup, dry_run=dry_run)


def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Archive and normalize JSON files')
    parser.add_argument('--source', '-s', 
                       default="W:/Staff_Call_Recordings/_Pipeline_Output/ALL_JSON_FILES",
                       help='Source directory containing JSON files')
    parser.add_argument('--backup', '-b',
                       default="W:/Staff_Call_Recordings/_Pipeline_Output/ALL_JSON_FILES_BACKUP", 
                       help='Backup directory for archived files')
    parser.add_argument('--force', '-f', action='store_true',
                       help='Overwrite existing backup files')
    parser.add_argument('--dry-run', '-d', action='store_true',
                       help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("ARCHIVE AND NORMALIZE JSON FILES")
    print("=" * 60)
    print(f"Source: {args.source}")
    print(f"Backup: {args.backup}")
    print(f"Force overwrite: {args.force}")
    print(f"Dry run: {args.dry_run}")
    print("=" * 60)
    
    if not args.dry_run:
        response = input("\nContinue with processing? (y/N): ").lower()
        if response != 'y':
            print("Operation cancelled.")
            return
    
    # Process files
    results = archive_and_normalize_json_files(
        source_dir=args.source,
        backup_dir=args.backup,
        force_backup=args.force,
        dry_run=args.dry_run
    )
    
    # Show final results
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Total files: {results['total_files']}")
    print(f"Successfully processed: {results['archived_files']}")
    print(f"Failed: {results['failed_files']}")
    print(f"Skipped: {results['skipped_files']}")
    
    if results['errors']:
        print(f"\nErrors encountered: {len(results['errors'])}")
        print("Check the log file for details.")
    
    print(f"\nProcessing completed in {results.get('duration_seconds', 0):.2f} seconds")


if __name__ == "__main__":
    main()
