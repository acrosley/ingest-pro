"""
Transcription Engine Module

Supports multiple transcription services:
- Google Cloud Speech-to-Text (with word-level confidence scores)
- Google Gemini API
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

import keyring

# Conditional imports
try:
    from google.cloud import speech
    GOOGLE_CLOUD_STT_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_STT_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import assemblyai as aai
    ASSEMBLYAI_AVAILABLE = True
except ImportError:
    ASSEMBLYAI_AVAILABLE = False


logger = logging.getLogger(__name__)


class TranscriptionResult:
    """Container for transcription results with metadata."""
    
    def __init__(
        self,
        transcript: str,
        confidence: float = None,
        word_timestamps: List[Dict] = None,
        word_confidences: List[Dict] = None,
        metadata: Dict[str, Any] = None
    ):
        self.transcript = transcript
        self.confidence = confidence
        self.word_timestamps = word_timestamps or []
        self.word_confidences = word_confidences or []
        self.metadata = metadata or {}
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "transcript": self.transcript,
            "confidence": self.confidence,
            "word_timestamps": self.word_timestamps,
            "word_confidences": self.word_confidences,
            "metadata": self.metadata
        }


class GoogleCloudSTT:
    """Google Cloud Speech-to-Text transcription engine."""
    
    def __init__(self, config: Dict[str, Any]):
        if not GOOGLE_CLOUD_STT_AVAILABLE:
            raise ImportError("google-cloud-speech is not installed. Run: pip install google-cloud-speech")
        
        self.config = config
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Google Cloud Speech client with credentials."""
        # Get credentials path from keyring
        creds_path = keyring.get_password("GoogleCloudSTT", "credentials_path")
        
        if not creds_path:
            raise ValueError(
                "Google Cloud credentials not found. Run config/set_google_cloud_credentials.py"
            )
        
        if not os.path.exists(creds_path):
            raise FileNotFoundError(
                f"Google Cloud credentials file not found: {creds_path}"
            )
        
        # Set environment variable for authentication
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
        
        # Initialize client
        self.client = speech.SpeechClient()
        logger.info("Google Cloud Speech-to-Text client initialized")
    
    def transcribe_file(self, audio_path: str) -> TranscriptionResult:
        """
        Transcribe an audio file using Google Cloud Speech-to-Text.
        
        Automatically uses long_running_recognize for files >60 seconds.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            TranscriptionResult with transcript and word-level confidence scores
        """
        logger.info(f"[Google Cloud STT] Starting transcription for: {audio_path}")
        
        # Read audio file
        with open(audio_path, "rb") as audio_file:
            content = audio_file.read()
        
        # Determine audio duration to choose appropriate method
        audio_duration = self._estimate_audio_duration(audio_path, len(content))
        
        # Google Cloud STT synchronous recognize() has a 1-minute limit
        # Use long_running_recognize() for longer files
        use_long_running = audio_duration > 59  # Use 59 seconds as threshold for safety
        
        if use_long_running:
            logger.info(f"[Google Cloud STT] Audio is ~{audio_duration:.1f}s, using long_running_recognize()")
        
        # Configure recognition
        audio = speech.RecognitionAudio(content=content)
        
        # Get configuration from settings
        language_code = self.config.get("language_code", "en-US")
        enable_word_confidence = self.config.get("enable_word_confidence", True)
        enable_word_time_offsets = self.config.get("enable_word_time_offsets", True)
        enable_automatic_punctuation = self.config.get("enable_automatic_punctuation", True)
        enable_speaker_diarization = self.config.get("enable_speaker_diarization", True)
        diarization_speaker_count = self.config.get("diarization_speaker_count", 2)
        model = self.config.get("model", "phone_call")
        use_enhanced = self.config.get("use_enhanced", True)
        
        # Audio encoding parameters (CRITICAL for accuracy)
        encoding = self.config.get("encoding", "LINEAR16")
        sample_rate_hertz = self.config.get("sample_rate_hertz", 8000)
        
        # Additional accuracy parameters
        max_alternatives = self.config.get("max_alternatives", 1)
        profanity_filter = self.config.get("profanity_filter", False)
        enable_speech_adaptation = self.config.get("enable_speech_adaptation", True)
        
        # Map encoding string to enum
        encoding_map = {
            "LINEAR16": speech.RecognitionConfig.AudioEncoding.LINEAR16,
            "FLAC": speech.RecognitionConfig.AudioEncoding.FLAC,
            "MULAW": speech.RecognitionConfig.AudioEncoding.MULAW,
            "AMR": speech.RecognitionConfig.AudioEncoding.AMR,
            "AMR_WB": speech.RecognitionConfig.AudioEncoding.AMR_WB,
            "OGG_OPUS": speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            "SPEEX_WITH_HEADER_BYTE": speech.RecognitionConfig.AudioEncoding.SPEEX_WITH_HEADER_BYTE,
            "MP3": speech.RecognitionConfig.AudioEncoding.MP3,
        }
        audio_encoding = encoding_map.get(encoding.upper(), speech.RecognitionConfig.AudioEncoding.LINEAR16)
        
        # Build configuration
        config_params = {
            "encoding": audio_encoding,
            "sample_rate_hertz": sample_rate_hertz,
            "language_code": language_code,
            "enable_word_confidence": enable_word_confidence,
            "enable_word_time_offsets": enable_word_time_offsets,
            "enable_automatic_punctuation": enable_automatic_punctuation,
            "model": model,
            "use_enhanced": use_enhanced,
            "max_alternatives": max_alternatives,
            "profanity_filter": profanity_filter,
        }
        
        # Add speaker diarization if enabled
        if enable_speaker_diarization:
            diarization_config = speech.SpeakerDiarizationConfig(
                enable_speaker_diarization=True,
                min_speaker_count=2,
                max_speaker_count=diarization_speaker_count,
            )
            config_params["diarization_config"] = diarization_config
        
        # Add speech adaptation (phrase hints) if enabled
        if enable_speech_adaptation:
            speech_contexts = self._build_speech_contexts()
            if speech_contexts:
                config_params["speech_contexts"] = speech_contexts
        
        config = speech.RecognitionConfig(**config_params)
        
        # Perform transcription
        try:
            if use_long_running:
                # Use long-running operation for audio > 1 minute
                operation = self.client.long_running_recognize(config=config, audio=audio)
                logger.info("[Google Cloud STT] Waiting for long-running operation to complete...")
                response = operation.result(timeout=600)  # Wait up to 10 minutes
            else:
                # Use synchronous recognition for short audio
                response = self.client.recognize(config=config, audio=audio)
        except Exception as e:
            logger.error(f"Google Cloud STT API error: {e}", exc_info=True)
            raise
        
        # Process results
        if not response.results:
            logger.warning(f"No transcription results for {audio_path}")
            return TranscriptionResult(
                transcript="",
                confidence=0.0,
                metadata={"error": "No transcription results"}
            )
        
        # Collect all alternatives (usually just one, the best)
        full_transcript = []
        word_confidences = []
        word_timestamps = []
        overall_confidences = []
        
        for result in response.results:
            alternative = result.alternatives[0]
            full_transcript.append(alternative.transcript)
            overall_confidences.append(alternative.confidence)
            
            # Extract word-level information
            for word_info in alternative.words:
                word_data = {
                    "word": word_info.word,
                    "confidence": word_info.confidence if hasattr(word_info, 'confidence') else None,
                    "start_time": word_info.start_time.total_seconds() if hasattr(word_info, 'start_time') else None,
                    "end_time": word_info.end_time.total_seconds() if hasattr(word_info, 'start_time') else None,
                }
                
                # Add speaker tag if available
                if hasattr(word_info, 'speaker_tag'):
                    word_data["speaker_tag"] = word_info.speaker_tag
                
                word_confidences.append(word_data)
                word_timestamps.append(word_data)
        
        transcript_text = " ".join(full_transcript)
        avg_confidence = sum(overall_confidences) / len(overall_confidences) if overall_confidences else 0.0
        
        # Format transcript with speaker labels if diarization was used
        if enable_speaker_diarization and word_confidences:
            include_timestamps = self.config.get("include_timestamps", True)
            transcript_text = self._format_with_speakers(word_confidences, include_timestamps)
        
        result = TranscriptionResult(
            transcript=transcript_text,
            confidence=avg_confidence,
            word_timestamps=word_timestamps,
            word_confidences=word_confidences,
            metadata={
                "service": "google_cloud_stt",
                "language_code": language_code,
                "model": model,
                "num_results": len(response.results),
            }
        )
        
        logger.info(f"[Google Cloud STT] Transcription complete. Confidence: {avg_confidence:.2f}")
        return result
    
    def _estimate_audio_duration(self, audio_path: str, file_size: int) -> float:
        """
        Estimate audio duration in seconds.
        
        Args:
            audio_path: Path to audio file
            file_size: File size in bytes
            
        Returns:
            Estimated duration in seconds
        """
        # Try to read WAV header for accurate duration
        try:
            import wave
            with wave.open(str(audio_path), 'rb') as wav:
                frames = wav.getnframes()
                rate = wav.getframerate()
                duration = frames / float(rate)
                return duration
        except:
            pass
        
        # Fallback: Estimate based on file size
        # For MULAW 8kHz mono: ~8000 bytes per second
        # For LINEAR16 8kHz mono: ~16000 bytes per second
        encoding = self.config.get("encoding", "LINEAR16")
        sample_rate = self.config.get("sample_rate_hertz", 8000)
        
        if encoding == "MULAW":
            # 8-bit samples
            bytes_per_second = sample_rate * 1  # 1 byte per sample
        elif encoding == "LINEAR16":
            # 16-bit samples
            bytes_per_second = sample_rate * 2  # 2 bytes per sample
        else:
            # Default estimate
            bytes_per_second = sample_rate * 2
        
        # WAV files have ~44 byte header
        data_size = max(file_size - 44, 0)
        estimated_duration = data_size / bytes_per_second
        
        return estimated_duration
    
    def _build_speech_contexts(self) -> List[speech.SpeechContext]:
        """
        Build speech contexts from nouns_to_expect.txt and staff_map.txt for better accuracy.
        
        Returns:
            List of SpeechContext objects with phrase hints
        """
        phrases = []
        
        # Load expected nouns
        nouns_file = Path("config/nouns_to_expect.txt")
        if nouns_file.exists():
            try:
                with open(nouns_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            phrases.append(line)
                logger.info(f"Loaded {len(phrases)} phrase hints from nouns_to_expect.txt")
            except Exception as e:
                logger.warning(f"Could not read nouns_to_expect.txt: {e}")
        
        # Load staff names from staff_map.txt
        staff_file = Path("config/staff_map.txt")
        staff_count = 0
        if staff_file.exists():
            try:
                with open(staff_file, "r", encoding="utf-8") as f:
                    for idx, line in enumerate(f):
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        
                        # Skip header row
                        if idx == 0 and ("Role" in line or "Full Name" in line):
                            continue
                        
                        # Try tab-separated format (TSV)
                        if "\t" in line:
                            parts = line.split("\t")
                            # Assuming columns: Role, Last, First, Full Name, Email, Phone
                            if len(parts) >= 4:
                                full_name = parts[3].strip()
                                first_name = parts[2].strip()
                                last_name = parts[1].strip()
                                if full_name:
                                    phrases.append(full_name)
                                    staff_count += 1
                                # Also add first and last names separately
                                if first_name:
                                    phrases.append(first_name)
                                if last_name:
                                    phrases.append(last_name)
                        # Fallback: Parse lines like "x123 = John Doe"
                        elif "=" in line:
                            parts = line.split("=", 1)
                            if len(parts) == 2:
                                name = parts[1].strip()
                                if name:
                                    phrases.append(name)
                                    staff_count += 1
                logger.info(f"Added {staff_count} staff names from staff_map.txt")
            except Exception as e:
                logger.warning(f"Could not read staff_map.txt: {e}")
        
        # Add common legal/business terms that might be misheard
        phrases.extend([
            "liability", "settlement", "plaintiff", "defendant", "attorney",
            "deposition", "affidavit", "subpoena", "litigation", "arbitration",
            "negligence", "malpractice", "insurance", "claim", "coverage"
        ])
        
        if not phrases:
            return []
        
        # Google Cloud STT has a limit of 500 phrases per context
        # and boost values from 0-20 (higher = stronger hint)
        return [speech.SpeechContext(
            phrases=phrases[:500],  # Limit to 500 phrases
            boost=15.0  # Strong boost for accuracy with domain terms
        )]
    
    def _format_with_speakers(self, word_data: List[Dict], include_timestamps: bool = True) -> str:
        """Format transcript with speaker labels (Agent/Caller) and optional timestamps."""
        if not word_data:
            return ""
        
        lines = []
        current_speaker = None
        current_line = []
        line_start_time = None
        
        for word_info in word_data:
            speaker_tag = word_info.get("speaker_tag")
            word = word_info.get("word", "")
            start_time = word_info.get("start_time")
            
            if speaker_tag != current_speaker:
                # New speaker
                if current_line:
                    speaker_label = "Agent:" if current_speaker == 1 else "Caller:"
                    if include_timestamps and line_start_time is not None:
                        timestamp = self._format_timestamp(line_start_time)
                        lines.append(f"[{timestamp}] {speaker_label} {' '.join(current_line)}")
                    else:
                        lines.append(f"{speaker_label} {' '.join(current_line)}")
                    current_line = []
                    line_start_time = None
                current_speaker = speaker_tag
            
            # Track start time of the line
            if line_start_time is None and start_time is not None:
                line_start_time = start_time
            
            current_line.append(word)
        
        # Add final line
        if current_line:
            speaker_label = "Agent:" if current_speaker == 1 else "Caller:"
            if include_timestamps and line_start_time is not None:
                timestamp = self._format_timestamp(line_start_time)
                lines.append(f"[{timestamp}] {speaker_label} {' '.join(current_line)}")
            else:
                lines.append(f"{speaker_label} {' '.join(current_line)}")
        
        return "\n".join(lines)
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds as MM:SS or HH:MM:SS."""
        if seconds is None:
            return "00:00"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"


class GeminiSTT:
    """Google Gemini API transcription engine."""
    
    def __init__(self, config: Dict[str, Any]):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai is not installed")
        
        self.config = config
        self.model_name = config.get("model_name", "gemini-2.0-flash")
        self.timeout = config.get("timeout", 600)
        self.expected_nouns = config.get("expected_nouns", [])
        
        # Initialize API key from keyring
        service_name = config.get("keyring_service_name", "MyGeminiApp")
        username = config.get("keyring_username", "gemini_api_key_user")
        
        api_key = keyring.get_password(service_name, username)
        if not api_key:
            raise ValueError(f"Gemini API key not found in keyring: {service_name}/{username}")
        
        # Configure Gemini with custom vocabulary if available
        config_options = {"api_key": api_key}
        
        # Build custom spelling dictionary from expected nouns
        if self.expected_nouns and len(self.expected_nouns) > 0:
            # Gemini's custom vocabulary feature helps with proper nouns
            # Each word/phrase gets mapped to itself to reinforce correct spelling
            custom_vocab = {noun: noun for noun in self.expected_nouns[:100]}  # Limit to 100 terms
            if custom_vocab:
                logger.info(f"[Gemini] Configuring {len(custom_vocab)} custom vocabulary terms")
                # Note: This feature may not be available in all Gemini versions
                # Falls back gracefully if not supported
        
        genai.configure(**config_options)
        logger.info("Gemini API configured")
    
    def transcribe_file(self, audio_path: str) -> TranscriptionResult:
        """
        Transcribe an audio file using Gemini API.
        
        Note: Gemini does not provide word-level confidence scores.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            TranscriptionResult with transcript (no confidence scores)
        """
        logger.info(f"[Gemini STT] Starting transcription for: {audio_path}")
        
        # Upload file
        display_name = f"call-rec-{os.path.basename(audio_path)}-{int(time.time())}"
        uploaded_file_info = genai.upload_file(path=audio_path, display_name=display_name)
        
        # Wait for file to be ready
        if uploaded_file_info and getattr(uploaded_file_info, 'name', None):
            self._wait_for_file_activation(uploaded_file_info.name, max_wait_seconds=180)
        
        # Build prompt with vocabulary guidance
        noun_guidance = ""
        if self.expected_nouns:
            # Create a more explicit vocabulary list for better recognition
            vocab_list = "\n".join(f"- {noun}" for noun in self.expected_nouns[:50])  # Limit to 50 for prompt size
            noun_guidance = (
                f"\n\nIMPORTANT VOCABULARY to transcribe accurately (use exact spellings):\n"
                f"{vocab_list}\n"
            )
        
        system_instr = (
            "You are an expert transcription assistant. Accurately transcribe this audio, "
            "label speakers as 'Agent:' and 'Caller:'. Include timestamps [HH:MM:SS]." + 
            noun_guidance
        )
        user_prompt = "Please transcribe the uploaded call audio."
        
        # Generate transcription
        model = genai.GenerativeModel(model_name=self.model_name, system_instruction=system_instr)
        response = model.generate_content(
            [user_prompt, uploaded_file_info],
            request_options={"timeout": self.timeout}
        )
        
        transcript = self._extract_text_from_response(response)
        
        # Retry once if empty
        if not transcript.strip():
            time.sleep(1.5)
            response = model.generate_content(
                [user_prompt, uploaded_file_info],
                request_options={"timeout": self.timeout}
            )
            transcript = self._extract_text_from_response(response)
        
        # Clean up uploaded file
        try:
            genai.delete_file(uploaded_file_info.name)
        except Exception as e:
            logger.warning(f"Failed to delete uploaded file: {e}")
        
        result = TranscriptionResult(
            transcript=transcript,
            confidence=None,  # Gemini doesn't provide confidence scores
            metadata={
                "service": "gemini",
                "model": self.model_name,
            }
        )
        
        logger.info(f"[Gemini STT] Transcription complete")
        return result
    
    def _wait_for_file_activation(self, file_name: str, max_wait_seconds: int = 180):
        """Wait for uploaded file to be ready."""
        start_time = time.time()
        while True:
            file_info = genai.get_file(file_name)
            if file_info.state.name == "ACTIVE":
                logger.info(f"File {file_name} is ready")
                break
            if time.time() - start_time > max_wait_seconds:
                logger.warning(f"File {file_name} not ready after {max_wait_seconds}s")
                break
            time.sleep(2)
    
    def _extract_text_from_response(self, response) -> str:
        """Extract text from Gemini response."""
        if hasattr(response, 'text'):
            return response.text
        if hasattr(response, 'parts'):
            return "".join(part.text for part in response.parts if hasattr(part, 'text'))
        return ""


def create_transcription_engine(engine_type: str, config: Dict[str, Any]):
    """
    Factory function to create a transcription engine.
    
    Args:
        engine_type: Type of engine ("google_cloud_stt", "gemini", or "assemblyai")
        config: Configuration dictionary for the engine
        
    Returns:
        Transcription engine instance
    """
    engine_type = engine_type.lower()
    
    if engine_type == "google_cloud_stt":
        return GoogleCloudSTT(config)
    elif engine_type == "gemini":
        return GeminiSTT(config)
    elif engine_type == "assemblyai":
        return AssemblyAISTT(config)
    else:
        raise ValueError(f"Unknown transcription engine: {engine_type}")


class AssemblyAISTT:
    """AssemblyAI transcription engine with word-level confidence."""
    
    def __init__(self, config: Dict[str, Any]):
        if not ASSEMBLYAI_AVAILABLE:
            raise ImportError("assemblyai is not installed. Run: pip install assemblyai")
        
        self.config = config
        
        # Get API key
        api_key = config.get("api_key")
        if not api_key:
            # Try keyring as fallback
            api_key = keyring.get_password("AssemblyAI", "api_key")
        
        if not api_key:
            raise ValueError("AssemblyAI API key not found. Set in config or keyring.")
        
        # Configure SDK
        aai.settings.api_key = api_key
        
        # Build word boost list from nouns_to_expect.txt
        word_boost_list = None
        if config.get("enable_word_boost", True):
            word_boost_list = self._load_word_boost_list()
        
        # Build transcription config with all options
        config_params = {
            "speaker_labels": config.get("enable_speaker_labels", True),
            "language_code": config.get("language_code", "en_us"),
            "punctuate": config.get("punctuate", True),
            "format_text": config.get("format_text", True),
            "disfluencies": config.get("disfluencies_filter", False),
        }
        
        # Add speech model if specified
        speech_model_str = config.get("speech_model", "universal").lower()
        is_slam_1 = False
        if speech_model_str == "universal":
            config_params["speech_model"] = aai.SpeechModel.universal
        elif speech_model_str == "slam_1":
            config_params["speech_model"] = aai.SpeechModel.slam_1
            is_slam_1 = True
        else:
            logger.warning(f"Unknown speech model '{speech_model_str}', defaulting to universal")
            config_params["speech_model"] = aai.SpeechModel.universal
        
        # Add dual channel if enabled
        if config.get("dual_channel", False):
            config_params["multichannel"] = True
        
        # Add word boost or keyterms based on model
        # slam_1 uses keyterms_prompt, universal uses word_boost
        if word_boost_list:
            if is_slam_1:
                # slam_1 requires keyterms_prompt instead of word_boost
                config_params["keyterms_prompt"] = word_boost_list
                logger.info(f"[AssemblyAI] Using keyterms_prompt with {len(word_boost_list)} terms for slam_1 model")
            else:
                # universal model uses word_boost
                config_params["word_boost"] = word_boost_list
                config_params["boost_param"] = config.get("word_boost_param", "default")
                logger.info(f"[AssemblyAI] Using word_boost with {len(word_boost_list)} words for universal model")
        
        # PII Redaction
        if config.get("redact_pii", False):
            config_params["redact_pii"] = True
            config_params["redact_pii_audio"] = config.get("redact_pii_audio", False)
            
            # Parse PII policies
            pii_policies_str = config.get("redact_pii_policies", "")
            if pii_policies_str:
                # Convert comma-separated string to list of enums
                policy_mapping = {
                    "medical_process": aai.PIIRedactionPolicy.medical_process,
                    "medical_condition": aai.PIIRedactionPolicy.medical_condition,
                    "injury": aai.PIIRedactionPolicy.injury,
                    "blood_type": aai.PIIRedactionPolicy.blood_type,
                    "drug": aai.PIIRedactionPolicy.drug,
                    "date_of_birth": aai.PIIRedactionPolicy.date_of_birth,
                    "drivers_license": aai.PIIRedactionPolicy.drivers_license,
                    "email_address": aai.PIIRedactionPolicy.email_address,
                    "location": aai.PIIRedactionPolicy.location,
                    "money_amount": aai.PIIRedactionPolicy.money_amount,
                    "person_name": aai.PIIRedactionPolicy.person_name,
                    "phone_number": aai.PIIRedactionPolicy.phone_number,
                    "credit_card_number": aai.PIIRedactionPolicy.credit_card_number,
                    "credit_card_cvv": aai.PIIRedactionPolicy.credit_card_cvv,
                    "credit_card_expiration": aai.PIIRedactionPolicy.credit_card_expiration,
                    "ssn": aai.PIIRedactionPolicy.ssn,
                }
                pii_policies = []
                for policy in pii_policies_str.split(","):
                    policy = policy.strip()
                    if policy in policy_mapping:
                        pii_policies.append(policy_mapping[policy])
                
                if pii_policies:
                    config_params["redact_pii_policies"] = pii_policies
        
        # Content Safety
        if config.get("content_safety", False):
            config_params["content_safety"] = True
        
        # Entity Detection
        if config.get("entity_detection", False):
            config_params["entity_detection"] = True
        
        # Sentiment Analysis
        if config.get("sentiment_analysis", False):
            config_params["sentiment_analysis"] = True
        
        # Auto Highlights
        if config.get("auto_highlights", False):
            config_params["auto_highlights"] = True
        
        # Summarization
        if config.get("summarization", False):
            config_params["summarization"] = True
            config_params["summary_model"] = config.get("summary_model", "informative")
            config_params["summary_type"] = config.get("summary_type", "bullets")
        
        self.aai_config = aai.TranscriptionConfig(**config_params)
        self.transcriber = aai.Transcriber(config=self.aai_config)
        logger.info("AssemblyAI transcription engine initialized")
    
    def transcribe_file(self, audio_path: str) -> TranscriptionResult:
        """
        Transcribe an audio file using AssemblyAI.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            TranscriptionResult with transcript and word-level confidence scores
        """
        logger.info(f"[AssemblyAI] Starting transcription for: {audio_path}")
        
        try:
            # Transcribe
            transcript = self.transcriber.transcribe(audio_path)
            
            if transcript.status == aai.TranscriptStatus.error:
                logger.error(f"[AssemblyAI] Transcription error: {transcript.error}")
                return TranscriptionResult(
                    transcript="",
                    confidence=0.0,
                    metadata={"error": transcript.error, "service": "assemblyai"}
                )
            
            # Extract word-level data
            word_confidences = []
            word_timestamps = []
            
            if transcript.words:
                for word in transcript.words:
                    word_data = {
                        "word": word.text,
                        "confidence": word.confidence,
                        "start_time": word.start / 1000.0,  # Convert ms to seconds
                        "end_time": word.end / 1000.0,
                        "speaker_tag": getattr(word, 'speaker', None)
                    }
                    word_confidences.append(word_data)
                    word_timestamps.append(word_data)
            
            # Format transcript with speakers if available
            transcript_text = transcript.text
            if transcript.utterances:
                include_timestamps = self.config.get("include_timestamps", True)
                transcript_text = self._format_with_speakers(transcript.utterances, include_timestamps)
            
            result = TranscriptionResult(
                transcript=transcript_text,
                confidence=transcript.confidence,
                word_timestamps=word_timestamps,
                word_confidences=word_confidences,
                metadata={
                    "service": "assemblyai",
                    "language_code": getattr(transcript, "language_code", None),
                    "audio_duration": transcript.audio_duration / 1000.0 if transcript.audio_duration else None,
                    "num_words": len(transcript.words) if transcript.words else 0,
                }
            )
            
            logger.info(f"[AssemblyAI] Transcription complete. Confidence: {transcript.confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"[AssemblyAI] Transcription failed: {e}", exc_info=True)
            raise
    
    def _load_word_boost_list(self) -> list:
        """Load words from nouns_to_expect.txt for word boosting."""
        words = []
        nouns_file = Path("config/nouns_to_expect.txt")
        
        if nouns_file.exists():
            try:
                with open(nouns_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            words.append(line)
                
                if words:
                    logger.info(f"[AssemblyAI] Loaded {len(words)} words for boosting")
                    return words
            except Exception as e:
                logger.warning(f"[AssemblyAI] Could not read nouns_to_expect.txt: {e}")
        
        return []
    
    def _format_with_speakers(self, utterances, include_timestamps: bool = True) -> str:
        """Format transcript with speaker labels and optional timestamps."""
        if not utterances:
            return ""
        
        lines = []
        for utterance in utterances:
            speaker_label = f"Speaker {utterance.speaker}:"
            
            if include_timestamps:
                # Format timestamp as MM:SS
                start_seconds = utterance.start / 1000.0
                minutes = int(start_seconds // 60)
                seconds = int(start_seconds % 60)
                timestamp = f"[{minutes:02d}:{seconds:02d}]"
                lines.append(f"{timestamp} {speaker_label} {utterance.text}")
            else:
                lines.append(f"{speaker_label} {utterance.text}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Simple test
    print("Transcription Engine Module")
    print(f"Google Cloud STT available: {GOOGLE_CLOUD_STT_AVAILABLE}")
    print(f"Gemini available: {GEMINI_AVAILABLE}")
    print(f"AssemblyAI available: {ASSEMBLYAI_AVAILABLE}")

