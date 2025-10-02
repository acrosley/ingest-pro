"""
Audio Format Detection Script

Helps determine the correct encoding and sample rate for Google Cloud STT configuration.
"""

import sys
import wave
import struct
from pathlib import Path


def detect_wav_format(file_path):
    """Detect format of a WAV file."""
    try:
        # Try the wave module first
        with wave.open(str(file_path), 'rb') as wav:
            params = wav.getparams()
            
            nchannels = params.nchannels
            sampwidth = params.sampwidth
            framerate = params.framerate
            nframes = params.nframes
            comptype = params.comptype
            compname = params.compname
            
            duration = nframes / float(framerate)
            
            # Determine encoding
            if comptype == 'NONE':
                if sampwidth == 2:
                    encoding = 'LINEAR16'
                elif sampwidth == 1:
                    encoding = 'LINEAR16'  # 8-bit PCM, can still use LINEAR16
                else:
                    encoding = 'LINEAR16'  # Default to LINEAR16 for uncompressed
            else:
                encoding = 'UNKNOWN'
            
            return {
                'encoding': encoding,
                'sample_rate': framerate,
                'channels': nchannels,
                'duration': duration,
                'bit_depth': sampwidth * 8,
                'frames': nframes,
                'format_name': compname.decode('utf-8') if isinstance(compname, bytes) else compname
            }
    except Exception as e:
        # If wave module fails, try reading raw WAV header
        try:
            with open(file_path, 'rb') as f:
                # Read RIFF header
                riff = f.read(12)
                if riff[:4] != b'RIFF' or riff[8:12] != b'WAVE':
                    return {'error': 'Not a valid WAV file'}
                
                # Find fmt chunk
                while True:
                    chunk_header = f.read(8)
                    if len(chunk_header) < 8:
                        break
                    chunk_id = chunk_header[:4]
                    chunk_size = struct.unpack('<I', chunk_header[4:8])[0]
                    
                    if chunk_id == b'fmt ':
                        fmt_data = f.read(chunk_size)
                        audio_format = struct.unpack('<H', fmt_data[0:2])[0]
                        num_channels = struct.unpack('<H', fmt_data[2:4])[0]
                        sample_rate = struct.unpack('<I', fmt_data[4:8])[0]
                        bits_per_sample = struct.unpack('<H', fmt_data[14:16])[0] if len(fmt_data) >= 16 else 16
                        
                        # Map audio format codes
                        format_map = {
                            1: 'LINEAR16',  # PCM
                            6: 'LINEAR16',  # A-law (use LINEAR16)
                            7: 'MULAW',     # mu-law
                            85: 'MP3',      # MPEG Layer 3
                        }
                        
                        encoding = format_map.get(audio_format, 'LINEAR16')
                        
                        return {
                            'encoding': encoding,
                            'sample_rate': sample_rate,
                            'channels': num_channels,
                            'bit_depth': bits_per_sample,
                            'audio_format_code': audio_format,
                            'note': 'Detected using raw header parsing'
                        }
                    else:
                        # Skip this chunk
                        f.seek(chunk_size, 1)
                
                return {'error': 'Could not find fmt chunk in WAV file'}
        except Exception as e2:
            return {'error': f'Wave module error: {str(e)}, Raw parsing error: {str(e2)}'}


def detect_mp3_format(file_path):
    """Detect format of an MP3 file (basic detection)."""
    try:
        # Read first few bytes to detect MP3
        with open(file_path, 'rb') as f:
            header = f.read(3)
            if header[:2] == b'\xff\xfb' or header[:3] == b'ID3':
                return {
                    'encoding': 'MP3',
                    'sample_rate': 'UNKNOWN (use 44100 or 48000)',
                    'note': 'MP3 detection is limited. Use ffprobe for accurate info.'
                }
    except Exception as e:
        return {'error': str(e)}
    
    return {'error': 'Not a valid MP3 file'}


def print_results(info, file_path):
    """Print detection results and configuration recommendations."""
    print("\n" + "="*70)
    print(f"Audio File: {file_path}")
    print("="*70)
    
    if 'error' in info:
        print(f"\n[ERROR] {info['error']}")
        return
    
    print("\n[DETECTED PROPERTIES]")
    print("-"*70)
    for key, value in info.items():
        print(f"  {key.replace('_', ' ').title():20s}: {value}")
    
    print("\n[CONFIGURATION RECOMMENDATION]")
    print("-"*70)
    
    encoding = info.get('encoding', 'LINEAR16')
    sample_rate = info.get('sample_rate', 8000)
    
    print(f"\n  In config/call_pipeline.ini, set:\n")
    print(f"  GoogleCloudSTT_Encoding = {encoding}")
    print(f"  GoogleCloudSTT_SampleRateHertz = {sample_rate}")
    
    # Model recommendation based on sample rate
    if isinstance(sample_rate, int):
        if sample_rate <= 8000:
            model = "phone_call"
            print(f"  GoogleCloudSTT_Model = {model}  # Optimized for telephone audio")
        elif sample_rate <= 16000:
            model = "phone_call"
            print(f"  GoogleCloudSTT_Model = {model}  # Good for HD voice calls")
        else:
            model = "latest_long"
            print(f"  GoogleCloudSTT_Model = {model}  # High quality audio")
    
    print("\n[TIPS]")
    print("-"*70)
    
    channels = info.get('channels')
    if channels and channels > 1:
        print("  [WARNING] Your audio has multiple channels (stereo).")
        print("            Google Cloud STT works best with mono audio.")
        print("            Consider converting to mono for better accuracy.")
    
    duration = info.get('duration')
    if duration:
        if duration < 10:
            print("  [INFO] Short audio file. Consider using 'latest_short' model.")
        elif duration > 300:
            print("  [INFO] Long audio file. 'latest_long' or 'phone_call' model is good.")
    
    print("\n" + "="*70 + "\n")


def main():
    if len(sys.argv) < 2:
        print("\nUsage: python detect_audio_format.py <audio_file>")
        print("\nExample:")
        print("  python detect_audio_format.py demo/Audio/test.wav")
        print("  python detect_audio_format.py \"C:/path/to/your/audio.wav\"")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    
    if not file_path.exists():
        print(f"\n[ERROR] File not found: {file_path}")
        sys.exit(1)
    
    # Detect based on extension
    extension = file_path.suffix.lower()
    
    if extension == '.wav':
        info = detect_wav_format(file_path)
    elif extension == '.mp3':
        info = detect_mp3_format(file_path)
    else:
        info = {
            'error': f'Unsupported file type: {extension}',
            'note': 'Supported types: .wav, .mp3'
        }
    
    print_results(info, file_path)


if __name__ == '__main__':
    main()

