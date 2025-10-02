#!/usr/bin/env python3
"""
Transcript Normalizer Module
Integrated transcript normalization for the call processing pipeline
"""

import re
from typing import List, Dict, Any
from datetime import datetime


class TranscriptNormalizer:
    """Normalizes transcript data into consistent format"""
    
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
        elif 'operator' in speaker_lower:
            return 'System'
        elif 'receptionist' in speaker_lower:
            return 'System'
        elif any(medical in speaker_lower for medical in ['nurse', 'doctor', 'dr.']):
            return 'Medical Staff'
        
        # Return original if no match found
        return speaker.strip()
    
    def normalize_raw_transcript(self, raw_text: str) -> List[Dict[str, Any]]:
        """
        Normalize raw transcript text directly
        
        Args:
            raw_text: Raw transcript text from file
            
        Returns:
            List of normalized transcript segments
        """
        # First try to parse as structured segments
        segments = self.parse_transcript_text(raw_text)
        
        # Add normalization metadata
        normalization_info = {
            'normalized_at': datetime.now().isoformat(),
            'original_segments': 1,  # Raw text is treated as one segment
            'normalized_segments': len(segments),
            'normalization_method': 'raw_text_parsing'
        }
        
        return segments, normalization_info


# Global instance for use in the processor
transcript_normalizer = TranscriptNormalizer()
