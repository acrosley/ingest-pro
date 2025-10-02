#!/usr/bin/env python3
"""
Test script for integrated transcript normalization
"""

import json
from transcript_normalizer_module import transcript_normalizer

def test_normalization():
    """Test the integrated transcript normalizer"""
    
    print("=== Testing Integrated Transcript Normalization ===\n")
    
    # Test case 1: Embedded format with **Speaker:**
    test_text_1 = """[00:00:01] **Audio:** Hi, and thanks for calling Crosley Law Group. Your call has been forwarded to voicemail. [00:00:05] Good morning, this is John from Crosley Law Group. How can I help you today?"""
    
    print("Test 1: Embedded format with **Speaker:**")
    print(f"Input: {test_text_1[:100]}...")
    
    segments, info = transcript_normalizer.normalize_raw_transcript(test_text_1)
    print(f"Output: {len(segments)} segments")
    for i, segment in enumerate(segments, 1):
        print(f"  Segment {i}: [{segment['timestamp']}] {segment['speaker']}: {segment['text'][:50]}...")
    print(f"Normalization info: {info}")
    print()
    
    # Test case 2: Mixed format with Speaker: [timestamp]
    test_text_2 = """Agent: [00:00:03] Hello, this is Crosley Law Group. Caller: [00:00:04] Hello, I need to speak with someone about my case."""
    
    print("Test 2: Mixed format with Speaker: [timestamp]")
    print(f"Input: {test_text_2}")
    
    segments, info = transcript_normalizer.normalize_raw_transcript(test_text_2)
    print(f"Output: {len(segments)} segments")
    for i, segment in enumerate(segments, 1):
        print(f"  Segment {i}: [{segment['timestamp']}] {segment['speaker']}: {segment['text']}")
    print(f"Normalization info: {info}")
    print()
    
    # Test case 3: Simple embedded format
    test_text_3 = """[00:00:01] Audio: Thank you for calling. [00:00:03] Agent: How can I help you? [00:00:05] Caller: I have a question about my case."""
    
    print("Test 3: Simple embedded format")
    print(f"Input: {test_text_3}")
    
    segments, info = transcript_normalizer.normalize_raw_transcript(test_text_3)
    print(f"Output: {len(segments)} segments")
    for i, segment in enumerate(segments, 1):
        print(f"  Segment {i}: [{segment['timestamp']}] {segment['speaker']}: {segment['text']}")
    print(f"Normalization info: {info}")
    print()
    
    # Test case 4: Timestamps only (context-based speaker detection)
    test_text_4 = """[00:00:05] Your call has been forwarded to voicemail. [00:00:17] Good morning, this is Crosley Law Group. [00:00:20] Yes ma'am, I need help with my case."""
    
    print("Test 4: Timestamps only (context-based detection)")
    print(f"Input: {test_text_4}")
    
    segments, info = transcript_normalizer.normalize_raw_transcript(test_text_4)
    print(f"Output: {len(segments)} segments")
    for i, segment in enumerate(segments, 1):
        print(f"  Segment {i}: [{segment['timestamp']}] {segment['speaker']}: {segment['text']}")
    print(f"Normalization info: {info}")
    print()
    
    print("=== All tests completed ===")

def test_speaker_normalization():
    """Test speaker normalization mappings"""
    
    print("\n=== Testing Speaker Normalization ===\n")
    
    test_speakers = [
        'audio', 'Audio:', 'AUDIO', 'agent', 'Agent:', 'AGENT',
        'caller', 'Caller:', 'CALLER', 'system', 'System:', 'SYSTEM',
        'voicemail', 'Voicemail:', 'VOICEMAIL', 'operator', 'Operator:',
        'receptionist', 'Receptionist:', 'nurse', 'Nurse:', 'doctor', 'Dr.'
    ]
    
    for speaker in test_speakers:
        normalized = transcript_normalizer.normalize_speaker(speaker)
        print(f"'{speaker}' -> '{normalized}'")
    
    print("\n=== Speaker normalization completed ===")

if __name__ == "__main__":
    test_normalization()
    test_speaker_normalization()
