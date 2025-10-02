import os
import sys
import time
import logging
import threading
import queue
import json
import re
import configparser
import soundfile as sf
from datetime import datetime, timezone
from pathlib import Path

import keyring
import google.generativeai as genai

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from logging.handlers import RotatingFileHandler

from tools.review_tools.review_generator import (
    ReviewConfig,
    generate_review,
    load_review_config,
)
from tools.review_tools.assemblyai_review_generator import (
    AssemblyAIReviewConfig,
    generate_assemblyai_review,
    load_expected_terms,
)
from tools.transcription_engine import create_transcription_engine, TranscriptionResult


# --- Load expected nouns ----------------------------------------------
NOUNS_FILE = Path(__file__).parent / "config" / "nouns_to_expect.txt"
if NOUNS_FILE.exists():
    with open(NOUNS_FILE, encoding="utf-8") as f:
        EXPECTED_NOUNS_LIST = [line.strip() for line in f if line.strip()]
else:
    EXPECTED_NOUNS_LIST = []
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# 1. Load configuration from call_pipeline.ini
# ----------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = os.path.join(SCRIPT_DIR, "config", "call_pipeline.ini")

if not os.path.exists(CONFIG_FILE_PATH):
    print(f"FATAL: Configuration file '{CONFIG_FILE_PATH}' not found! Exiting.")
    exit(1)

config = configparser.ConfigParser()
try:
    config.read(CONFIG_FILE_PATH)

    # Paths
    TRANSCRIPTS_BASE_DIR = config.get('Paths', 'TranscriptInputDirectory').strip()
    DATABASE_DIRECTORY = config.get('Paths', 'DatabaseDirectory', fallback='').strip()
    PROCESSED_FILES_DB = os.path.join(DATABASE_DIRECTORY or SCRIPT_DIR, "processed_files.json")
    STAFF_MAP_FILE_PATH = config.get('Paths', 'StaffMapFile', fallback='').strip()
    # Support both legacy and new key names for central JSON output directory
    CENTRAL_JSON_DIR = (
        config.get('Paths', 'CentralJsonOutputDirectory', fallback='')
        or config.get('Paths', 'JsonOutputDirectory', fallback='')
    ).strip()
    # Central transcript archive directory
    CENTRAL_TRANSCRIPT_DIR = config.get('Paths', 'CentralTranscriptOutputDirectory', fallback=r"W:\\Staff_Call_Recordings\\_Pipeline_Output\\ALL_TRANSCRIPT_FILES").strip()

    # FileMonitoring (audio)
    CHECK_INTERVAL_SECONDS = config.getint('FileMonitoring', 'CheckIntervalSeconds', fallback=3)
    COMPLETION_THRESHOLD_SECONDS = config.getint('FileMonitoring', 'CompletionThresholdSeconds', fallback=10)
    raw_extensions = config.get('FileMonitoring', 'AllowedExtensions', fallback='.wav').strip()
    ALLOWED_EXTENSIONS = [ext.strip().lower() for ext in raw_extensions.split(',') if ext.strip()]

    # Transcription
    MAX_TRANSCRIPTION_WORKERS = config.getint('Transcription', 'MaxTranscriptionWorkers', fallback=2)
    PROCESS_NEW_AUDIO_ON_START = config.getboolean('Transcription', 'ProcessNewAudioOnStart', fallback=False)
    TRANSCRIPTION_ENGINE = config.get('Transcription', 'TranscriptionEngine', fallback='gemini').strip().lower()
    
    # Gemini STT settings
    GEMINI_STT_MODEL_NAME = config.get('Transcription', 'GeminiModelName', fallback='gemini-2.0-flash').strip()
    GEMINI_STT_TIMEOUT = config.getint('Transcription', 'GeminiApiTimeoutSeconds', fallback=600)
    
    # Google Cloud STT settings
    GOOGLE_CLOUD_STT_LANGUAGE = config.get('Transcription', 'GoogleCloudSTT_LanguageCode', fallback='en-US').strip()
    GOOGLE_CLOUD_STT_MODEL = config.get('Transcription', 'GoogleCloudSTT_Model', fallback='phone_call').strip()
    GOOGLE_CLOUD_STT_USE_ENHANCED = config.getboolean('Transcription', 'GoogleCloudSTT_UseEnhanced', fallback=True)
    GOOGLE_CLOUD_STT_ENCODING = config.get('Transcription', 'GoogleCloudSTT_Encoding', fallback='LINEAR16').strip()
    GOOGLE_CLOUD_STT_SAMPLE_RATE = config.getint('Transcription', 'GoogleCloudSTT_SampleRateHertz', fallback=8000)
    GOOGLE_CLOUD_STT_WORD_CONFIDENCE = config.getboolean('Transcription', 'GoogleCloudSTT_EnableWordConfidence', fallback=True)
    GOOGLE_CLOUD_STT_WORD_TIMESTAMPS = config.getboolean('Transcription', 'GoogleCloudSTT_EnableWordTimeOffsets', fallback=True)
    GOOGLE_CLOUD_STT_AUTO_PUNCTUATION = config.getboolean('Transcription', 'GoogleCloudSTT_EnableAutomaticPunctuation', fallback=True)
    GOOGLE_CLOUD_STT_DIARIZATION = config.getboolean('Transcription', 'GoogleCloudSTT_EnableSpeakerDiarization', fallback=True)
    GOOGLE_CLOUD_STT_SPEAKER_COUNT = config.getint('Transcription', 'GoogleCloudSTT_DiarizationSpeakerCount', fallback=2)
    GOOGLE_CLOUD_STT_SPEECH_ADAPTATION = config.getboolean('Transcription', 'GoogleCloudSTT_EnableSpeechAdaptation', fallback=True)
    GOOGLE_CLOUD_STT_MAX_ALTERNATIVES = config.getint('Transcription', 'GoogleCloudSTT_MaxAlternatives', fallback=3)
    GOOGLE_CLOUD_STT_PROFANITY_FILTER = config.getboolean('Transcription', 'GoogleCloudSTT_ProfanityFilter', fallback=False)
    GOOGLE_CLOUD_STT_INCLUDE_TIMESTAMPS = config.getboolean('Transcription', 'GoogleCloudSTT_IncludeTimestamps', fallback=True)
    
    # AssemblyAI settings
    ASSEMBLYAI_API_KEY = config.get('Transcription', 'AssemblyAI_ApiKey', fallback='').strip()
    ASSEMBLYAI_SPEECH_MODEL = config.get('Transcription', 'AssemblyAI_SpeechModel', fallback='universal').strip()
    ASSEMBLYAI_ENABLE_SPEAKER_LABELS = config.getboolean('Transcription', 'AssemblyAI_EnableSpeakerLabels', fallback=True)
    ASSEMBLYAI_LANGUAGE_CODE = config.get('Transcription', 'AssemblyAI_LanguageCode', fallback='en_us').strip()
    ASSEMBLYAI_INCLUDE_TIMESTAMPS = config.getboolean('Transcription', 'AssemblyAI_IncludeTimestamps', fallback=True)
    ASSEMBLYAI_DUAL_CHANNEL = config.getboolean('Transcription', 'AssemblyAI_DualChannel', fallback=False)
    ASSEMBLYAI_PUNCTUATE = config.getboolean('Transcription', 'AssemblyAI_Punctuate', fallback=True)
    ASSEMBLYAI_FORMAT_TEXT = config.getboolean('Transcription', 'AssemblyAI_FormatText', fallback=True)
    ASSEMBLYAI_DISFLUENCIES_FILTER = config.getboolean('Transcription', 'AssemblyAI_DisfluenciesFilter', fallback=False)
    ASSEMBLYAI_ENABLE_WORD_BOOST = config.getboolean('Transcription', 'AssemblyAI_EnableWordBoost', fallback=True)
    ASSEMBLYAI_WORD_BOOST_PARAM = config.get('Transcription', 'AssemblyAI_WordBoostParam', fallback='default').strip()
    ASSEMBLYAI_REDACT_PII = config.getboolean('Transcription', 'AssemblyAI_RedactPii', fallback=False)
    ASSEMBLYAI_REDACT_PII_AUDIO = config.getboolean('Transcription', 'AssemblyAI_RedactPiiAudio', fallback=False)
    ASSEMBLYAI_REDACT_PII_POLICIES = config.get('Transcription', 'AssemblyAI_RedactPiiPolicies', fallback='').strip()
    ASSEMBLYAI_CONTENT_SAFETY = config.getboolean('Transcription', 'AssemblyAI_ContentSafety', fallback=False)
    ASSEMBLYAI_ENTITY_DETECTION = config.getboolean('Transcription', 'AssemblyAI_EntityDetection', fallback=False)
    ASSEMBLYAI_SENTIMENT_ANALYSIS = config.getboolean('Transcription', 'AssemblyAI_SentimentAnalysis', fallback=False)
    ASSEMBLYAI_AUTO_HIGHLIGHTS = config.getboolean('Transcription', 'AssemblyAI_AutoHighlights', fallback=False)
    ASSEMBLYAI_SUMMARIZATION = config.getboolean('Transcription', 'AssemblyAI_Summarization', fallback=False)
    ASSEMBLYAI_SUMMARY_MODEL = config.get('Transcription', 'AssemblyAI_SummaryModel', fallback='informative').strip()
    ASSEMBLYAI_SUMMARY_TYPE = config.get('Transcription', 'AssemblyAI_SummaryType', fallback='bullets').strip()

    # Analysis
    ANALYSIS_QUEUE_SIZE = config.getint('Analysis', 'QueueSize', fallback=50)
    MAX_ANALYSIS_WORKERS = config.getint('Analysis', 'MaxWorkers', fallback=2)
    MIN_TRANSCRIPT_SIZE = config.getint('Analysis', 'MinTranscriptSize', fallback=100)
    PROCESS_EXISTING_ON_START = config.getboolean('Analysis', 'ProcessExistingOnStart', fallback=True)
    OUTPUT_FORMAT = config.get('Analysis', 'OutputFormat', fallback='both').strip().lower()
    ENABLE_TRANSCRIPT_NORMALIZATION = config.getboolean('Analysis', 'EnableTranscriptNormalization', fallback=True)
    ENABLE_JSON_NORMALIZATION = config.getboolean('Analysis', 'EnableJsonNormalization', fallback=False)
    NORMALIZE_EXISTING_JSON_ON_START = config.getboolean('Analysis', 'NormalizeExistingJsonOnStart', fallback=False)

    # Gemini (for analysis)
    GEMINI_ANALYSIS_MODEL_NAME = config.get('Gemini', 'ModelName').strip()
    GEMINI_ANALYSIS_TIMEOUT = config.getint('Gemini', 'ApiTimeoutSeconds', fallback=600)
    SERVICE_NAME = config.get('Gemini', 'KeyringServiceName').strip()
    USERNAME = config.get('Gemini', 'KeyringUsername').strip()

    # Logging
    LOG_DIRECTORY = config.get('Logging', 'LogDirectory').strip()
    LOG_FILENAME = config.get('Logging', 'LogFilename', fallback='call_pipeline.log').strip()
    LOG_LEVEL_STR = config.get('Logging', 'LogLevel', fallback='INFO').upper().strip()
    LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)
    LOG_MAX_BYTES = config.getint('Logging', 'LogMaxBytes', fallback=10 * 1024 * 1024)
    LOG_BACKUP_COUNT = config.getint('Logging', 'LogBackupCount', fallback=5)

    # Review pipeline
    REVIEW_CONFIG: ReviewConfig = load_review_config(config)
    
    # AssemblyAI-specific review config (uses same settings but optimized for AssemblyAI)
    ASSEMBLYAI_REVIEW_CONFIG = AssemblyAIReviewConfig(
        enabled=REVIEW_CONFIG.enabled,
        output_directory=REVIEW_CONFIG.output_directory,
        low_confidence_threshold=REVIEW_CONFIG.low_confidence_threshold,
        flag_numbers=REVIEW_CONFIG.flag_numbers,
    )

except Exception as e:
    print(f"FATAL: Error loading configuration from '{CONFIG_FILE_PATH}': {e}. Exiting.")
    exit(1)

# ----------------------------------------------------------------------
# 2. Prepare directories and logging
# ----------------------------------------------------------------------
os.makedirs(LOG_DIRECTORY, exist_ok=True)
os.makedirs(Path(PROCESSED_FILES_DB).parent, exist_ok=True)

# Logging setup
logger = logging.getLogger('CallPipeline')
logger.setLevel(LOG_LEVEL)
log_path = os.path.join(LOG_DIRECTORY, LOG_FILENAME)
file_handler = RotatingFileHandler(log_path, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT, encoding='utf-8')
file_formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)
logger.info("=== CallPipeline Starting ===")
logger.info(f"Configuration loaded from: {CONFIG_FILE_PATH}")
logger.info(f"[STT] Transcription engine: {TRANSCRIPTION_ENGINE}")
logger.info(
    "[Review] Review generation %s",
    "enabled" if REVIEW_CONFIG.enabled else "disabled",
)
if REVIEW_CONFIG.enabled and REVIEW_CONFIG.output_directory:
    logger.info("[Review] Output directory: %s", REVIEW_CONFIG.output_directory)

# ----------------------------------------------------------------------
# 3. Gemini API key configuration
# ----------------------------------------------------------------------
try:
    GEMINI_API_KEY = keyring.get_password(SERVICE_NAME, USERNAME)
    if not GEMINI_API_KEY:
        GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        api_key_configured = True
        logger.info("Google AI SDK configured successfully.")
    else:
        api_key_configured = False
        logger.error("API key not found in Keyring or environment. Transcription and analysis will fail.")
except Exception as e:
    api_key_configured = False
    logger.error(f"Failed to configure Google AI SDK: {e}")

# ----------------------------------------------------------------------
# 4. Globals
# ----------------------------------------------------------------------
active_recordings = {}
transcription_queue = queue.Queue(maxsize=200)
analysis_queue = queue.Queue(maxsize=ANALYSIS_QUEUE_SIZE)
processed_files = set()
processed_files_lock = threading.Lock()

# Production enhancements
dead_letter_queue = queue.Queue(maxsize=1000)
failed_items_db = os.path.join(DATABASE_DIRECTORY, "failed_items.json")

# Metrics tracking
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ProcessingMetrics:
    start_time: float
    end_time: float = None
    success: bool = False
    error: str = None
    file_size: int = 0
    api_calls: int = 0
    worker_thread: str = None

class MetricsCollector:
    def __init__(self, max_history=1000):
        self.metrics: List[ProcessingMetrics] = deque(maxlen=max_history)
        self.api_usage = defaultdict(int)
        self.success_rates = defaultdict(list)
        self.processing_times = defaultdict(list)
        
    def record_metric(self, metric: ProcessingMetrics):
        self.metrics.append(metric)
        
        # Track API usage
        if metric.api_calls > 0:
            self.api_usage[metric.worker_thread] += metric.api_calls
        
        # Track success rates
        file_type = self._get_file_type(metric)
        self.success_rates[file_type].append(metric.success)
        
        # Track processing times
        if metric.end_time:
            processing_time = metric.end_time - metric.start_time
            self.processing_times[file_type].append(processing_time)
    
    def get_summary(self) -> Dict:
        total_files = len(self.metrics)
        successful_files = sum(1 for m in self.metrics if m.success)
        
        return {
            "total_files_processed": total_files,
            "success_rate": successful_files / total_files if total_files > 0 else 0,
            "average_processing_time": self._calculate_avg_processing_time(),
            "api_usage_by_worker": dict(self.api_usage),
            "success_rates_by_type": {k: sum(v)/len(v) for k, v in self.success_rates.items()},
            "processing_times_by_type": {k: sum(v)/len(v) for k, v in self.processing_times.items()}
        }
    
    def _get_file_type(self, metric: ProcessingMetrics) -> str:
        # Determine file type from path or other indicators
        return "audio" if "audio" in str(metric) else "transcript"
    
    def _calculate_avg_processing_time(self) -> float:
        times = [m.end_time - m.start_time for m in self.metrics if m.end_time]
        return sum(times) / len(times) if times else 0

# Initialize metrics collector
metrics_collector = MetricsCollector()

# --- Load Staff Map for File Renaming ---
STAFF_MAP = {}
if STAFF_MAP_FILE_PATH:
    try:
        if os.path.exists(STAFF_MAP_FILE_PATH):
            with open(STAFF_MAP_FILE_PATH, 'r', encoding='utf-8') as f:
                next(f, None)  # Skip the header line
                for line in f:
                    parts = [p.strip() for p in re.split(r'\t|\s{2,}', line) if p.strip()]
                    if len(parts) >= 5: # Role, Last, First, Full Name, Email, Phone
                        full_name = parts[2]
                        phone = parts[5]
                        phone_digits = re.findall(r'\d', phone)
                        if len(phone_digits) >= 3:
                            user_id = "".join(phone_digits[-3:])
                            STAFF_MAP[user_id] = full_name
            logger.info(f"Successfully loaded {len(STAFF_MAP)} users from '{STAFF_MAP_FILE_PATH}'.")
            if not STAFF_MAP:
                logger.warning("Staff map was loaded, but no users were parsed. Check file format.")
        else:
            logger.warning(f"Staff map file specified in config not found: '{STAFF_MAP_FILE_PATH}'. Files will not be renamed.")
    except Exception as e:
        logger.error(f"Error loading staff map file from '{STAFF_MAP_FILE_PATH}': {e}")
else:
    logger.warning("StaffMapFile not set in config. Files will not be renamed.")
# ----------------------------------------

# ----------------------------------------------------------------------
# 5. Production Enhancement Functions
# ----------------------------------------------------------------------
def save_failed_item(item_data, error_info, retry_count=0):
    """Save failed item to dead letter queue and persistent storage"""
    failed_item = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "item_data": item_data,
        "error": str(error_info),
        "retry_count": retry_count,
        "worker_thread": threading.current_thread().name
    }
    
    try:
        dead_letter_queue.put(failed_item, block=False)
    except queue.Full:
        logger.error("Dead letter queue full, writing to file directly")
    
    # Persist to file
    try:
        with open(failed_items_db, 'a', encoding='utf-8') as f:
            json.dump(failed_item, f)
            f.write('\n')
    except Exception as e:
        logger.error(f"Failed to save failed item to file: {e}")

def process_dead_letter_queue():
    """Process items from dead letter queue with exponential backoff"""
    while not dead_letter_queue.empty():
        try:
            failed_item = dead_letter_queue.get_nowait()
            
            # Implement retry logic with exponential backoff
            if failed_item['retry_count'] < 3:
                wait_time = 2 ** failed_item['retry_count']  # 1s, 2s, 4s
                time.sleep(wait_time)
                
                # Retry processing
                try:
                    if 'transcript_path' in failed_item['item_data']:
                        process_transcript(failed_item['item_data']['transcript_path'])
                    elif 'audio_path' in failed_item['item_data']:
                        # For audio files, re-queue for transcription
                        transcription_queue.put(failed_item['item_data']['audio_path'], block=False)
                    logger.info(f"Successfully retried failed item: {failed_item['item_data']}")
                except Exception as e:
                    failed_item['retry_count'] += 1
                    save_failed_item(failed_item['item_data'], e, failed_item['retry_count'])
            else:
                logger.error(f"Item permanently failed after 3 retries: {failed_item}")
                
        except queue.Empty:
            break

def report_metrics():
    """Report current metrics to log"""
    summary = metrics_collector.get_summary()
    logger.info(f"Processing Metrics: {json.dumps(summary, indent=2)}")

def metrics_reporter():
    """Periodic metrics reporting thread"""
    while True:
        time.sleep(300)  # Report every 5 minutes
        report_metrics()

# ----------------------------------------------------------------------
# 6. Configuration Validation
# ----------------------------------------------------------------------
class ConfigurationValidator:
    def __init__(self, config: configparser.ConfigParser):
        self.config = config
        self.errors = []
        self.warnings = []
    
    def validate_all(self) -> bool:
        """Validate all configuration sections"""
        self._validate_paths()
        self._validate_file_monitoring()
        self._validate_transcription()
        self._validate_analysis()
        self._validate_gemini()
        self._validate_logging()
        
        if self.errors:
            logger.error("Configuration validation failed:")
            for error in self.errors:
                logger.error(f"  - {error}")
            return False
        
        if self.warnings:
            logger.warning("Configuration warnings:")
            for warning in self.warnings:
                logger.warning(f"  - {warning}")
        
        return True
    
    def _validate_paths(self):
        """Validate path configurations"""
        required_paths = [
            ('Paths', 'TranscriptInputDirectory'),
            ('Paths', 'DatabaseDirectory'),
            ('Logging', 'LogDirectory')
        ]
        
        for section, key in required_paths:
            try:
                path = self.config.get(section, key).strip()
                if not path:
                    self.errors.append(f"{section}.{key} is empty")
                elif not os.path.exists(path):
                    self.warnings.append(f"{section}.{key} path does not exist: {path}")
            except configparser.NoOptionError:
                self.errors.append(f"Missing required configuration: {section}.{key}")
        
        # Validate file extensions
        try:
            extensions = self.config.get('FileMonitoring', 'AllowedExtensions')
            if not extensions:
                self.errors.append("FileMonitoring.AllowedExtensions is empty")
            else:
                ext_list = [ext.strip().lower() for ext in extensions.split(',')]
                if not all(ext.startswith('.') for ext in ext_list):
                    self.errors.append("FileMonitoring.AllowedExtensions must start with '.'")
        except configparser.NoOptionError:
            self.errors.append("Missing FileMonitoring.AllowedExtensions")
    
    def _validate_transcription(self):
        """Validate transcription settings"""
        try:
            workers = self.config.getint('Transcription', 'MaxTranscriptionWorkers')
            if workers < 1 or workers > 10:
                self.warnings.append("MaxTranscriptionWorkers should be between 1-10")
        except (configparser.NoOptionError, ValueError):
            self.errors.append("Invalid MaxTranscriptionWorkers value")
        
        try:
            timeout = self.config.getint('Transcription', 'GeminiApiTimeoutSeconds')
            if timeout < 60 or timeout > 3600:
                self.warnings.append("GeminiApiTimeoutSeconds should be between 60-3600 seconds")
        except (configparser.NoOptionError, ValueError):
            self.errors.append("Invalid GeminiApiTimeoutSeconds value")
    
    def _validate_analysis(self):
        """Validate analysis settings"""
        try:
            queue_size = self.config.getint('Analysis', 'QueueSize')
            if queue_size < 10 or queue_size > 1000:
                self.warnings.append("Analysis.QueueSize should be between 10-1000")
        except (configparser.NoOptionError, ValueError):
            self.errors.append("Invalid Analysis.QueueSize value")
        
        try:
            output_format = self.config.get('Analysis', 'OutputFormat').lower()
            if output_format not in ['json', 'markdown', 'both']:
                self.errors.append("Analysis.OutputFormat must be 'json', 'markdown', or 'both'")
        except configparser.NoOptionError:
            self.errors.append("Missing Analysis.OutputFormat")
        
        # Validate transcript normalization setting
        try:
            self.config.getboolean('Analysis', 'EnableTranscriptNormalization', fallback=True)
        except ValueError:
            self.warnings.append("Invalid EnableTranscriptNormalization value, using default (True)")
        
        # Validate JSON normalization settings
        try:
            self.config.getboolean('Analysis', 'EnableJsonNormalization', fallback=False)
        except ValueError:
            self.warnings.append("Invalid EnableJsonNormalization value, using default (False)")
        
        try:
            self.config.getboolean('Analysis', 'NormalizeExistingJsonOnStart', fallback=False)
        except ValueError:
            self.warnings.append("Invalid NormalizeExistingJsonOnStart value, using default (False)")
    
    def _validate_gemini(self):
        """Validate Gemini API configuration"""
        try:
            model_name = self.config.get('Gemini', 'ModelName')
            if not model_name:
                self.errors.append("Gemini.ModelName is empty")
        except configparser.NoOptionError:
            self.errors.append("Missing Gemini.ModelName")
        
        try:
            service_name = self.config.get('Gemini', 'KeyringServiceName')
            username = self.config.get('Gemini', 'KeyringUsername')
            if not service_name or not username:
                self.errors.append("Gemini KeyringServiceName and KeyringUsername are required")
        except configparser.NoOptionError:
            self.errors.append("Missing Gemini keyring configuration")
    
    def _validate_logging(self):
        """Validate logging configuration"""
        try:
            log_level = self.config.get('Logging', 'LogLevel').upper()
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if log_level not in valid_levels:
                self.errors.append(f"Logging.LogLevel must be one of: {valid_levels}")
        except configparser.NoOptionError:
            self.errors.append("Missing Logging.LogLevel")
    
    def _validate_file_monitoring(self):
        """Validate file monitoring settings"""
        try:
            check_interval = self.config.getint('FileMonitoring', 'CheckIntervalSeconds')
            if check_interval < 1 or check_interval > 60:
                self.warnings.append("CheckIntervalSeconds should be between 1-60 seconds")
        except (configparser.NoOptionError, ValueError):
            self.errors.append("Invalid CheckIntervalSeconds value")

def validate_configuration():
    """Validate configuration before starting the pipeline"""
    validator = ConfigurationValidator(config)
    if not validator.validate_all():
        logger.error("Configuration validation failed. Please fix the errors above.")
        sys.exit(1)
    
    logger.info("Configuration validation passed.")

# ----------------------------------------------------------------------
# 7. Utilities for processed-files persistence
# ----------------------------------------------------------------------
def load_processed_files():
    global processed_files
    if os.path.exists(PROCESSED_FILES_DB):
        try:
            with open(PROCESSED_FILES_DB, 'r', encoding='utf-8') as f:
                data = json.load(f)
                processed_files = set(data.get('processed_files', []))
            logger.info(f"Loaded {len(processed_files)} processed files from '{PROCESSED_FILES_DB}'.")
        except Exception as e:
            logger.error(f"Error loading processed files DB: {e}")
            processed_files = set()

def save_processed_files():
    try:
        with open(PROCESSED_FILES_DB, 'w', encoding='utf-8') as f:
            json.dump({'processed_files': list(processed_files), 'last_updated': datetime.now(timezone.utc).isoformat()}, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving processed files DB: {e}")

# ----------------------------------------------------------------------
# 6. Transcription workflow
# ----------------------------------------------------------------------
class CallMonitorHandler(FileSystemEventHandler):
    def _is_valid_file(self, filepath):
        return any(filepath.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)

    def on_created(self, event):
        if event.is_directory or not self._is_valid_file(event.src_path): return
        path = event.src_path
        if path in active_recordings: return
        try:
            time.sleep(1.0) # Give the file a second to exist before checking
            size = os.path.getsize(path)
            now = time.time()
            active_recordings[path] = {"last_size": size, "first_seen_time": now}
            logger.info(f"New audio detected: {path} (size: {size} bytes)")
        except Exception as e:
            logger.error(f"Error in on_created for {path}: {e}")

    def on_deleted(self, event):
        if event.is_directory: return
        if event.src_path in active_recordings:
            active_recordings.pop(event.src_path, None)

def check_for_completion_and_growth():
    """
    Checks for completed audio files by actively probing for file locks.
    This is more reliable than relying on modification times over a network.
    """
    now = time.time()
    for path in list(active_recordings.keys()):
        try:
            if not os.path.exists(path):
                active_recordings.pop(path, None)
                continue
            
            info = active_recordings[path]
            size = os.path.getsize(path)
            info["last_size"] = size
            
            if now - info["first_seen_time"] < COMPLETION_THRESHOLD_SECONDS:
                continue

            try:
                os.rename(path, path)
                logger.info(f"Audio complete (probe successful): {path} (final size {size})")
                try:
                    transcription_queue.put(path, block=False)
                    active_recordings.pop(path, None)
                except queue.Full:
                    logger.warning(f"Transcription queue full; will retry queuing: {path}")

            except PermissionError:
                logger.debug(f"Probe failed for {path} (still in use), will re-check.")
                continue

        except Exception as e:
            logger.error(f"Error checking file '{path}' for completion: {e}", exc_info=True)
            active_recordings.pop(path, None)

def process_transcription(path):
    """Process transcription using the configured engine (Google Cloud STT or Gemini)."""
    logger.info(f"[STT] Starting transcription with {TRANSCRIPTION_ENGINE} for: {path}")
    
    try:
        # Build engine configuration
        if TRANSCRIPTION_ENGINE == "google_cloud_stt":
            engine_config = {
                "language_code": GOOGLE_CLOUD_STT_LANGUAGE,
                "model": GOOGLE_CLOUD_STT_MODEL,
                "use_enhanced": GOOGLE_CLOUD_STT_USE_ENHANCED,
                "encoding": GOOGLE_CLOUD_STT_ENCODING,
                "sample_rate_hertz": GOOGLE_CLOUD_STT_SAMPLE_RATE,
                "enable_word_confidence": GOOGLE_CLOUD_STT_WORD_CONFIDENCE,
                "enable_word_time_offsets": GOOGLE_CLOUD_STT_WORD_TIMESTAMPS,
                "enable_automatic_punctuation": GOOGLE_CLOUD_STT_AUTO_PUNCTUATION,
                "enable_speaker_diarization": GOOGLE_CLOUD_STT_DIARIZATION,
                "diarization_speaker_count": GOOGLE_CLOUD_STT_SPEAKER_COUNT,
                "enable_speech_adaptation": GOOGLE_CLOUD_STT_SPEECH_ADAPTATION,
                "max_alternatives": GOOGLE_CLOUD_STT_MAX_ALTERNATIVES,
                "profanity_filter": GOOGLE_CLOUD_STT_PROFANITY_FILTER,
                "include_timestamps": GOOGLE_CLOUD_STT_INCLUDE_TIMESTAMPS,
            }
        elif TRANSCRIPTION_ENGINE == "gemini":
            if not api_key_configured:
                logger.error("Gemini API key not configured")
                return
            engine_config = {
                "model_name": GEMINI_STT_MODEL_NAME,
                "timeout": GEMINI_STT_TIMEOUT,
                "expected_nouns": EXPECTED_NOUNS_LIST,
                "keyring_service_name": SERVICE_NAME,
                "keyring_username": USERNAME,
            }
        elif TRANSCRIPTION_ENGINE == "assemblyai":
            if not ASSEMBLYAI_API_KEY:
                logger.error("AssemblyAI API key not configured in call_pipeline.ini")
                return
            engine_config = {
                "api_key": ASSEMBLYAI_API_KEY,
                "speech_model": ASSEMBLYAI_SPEECH_MODEL,
                "enable_speaker_labels": ASSEMBLYAI_ENABLE_SPEAKER_LABELS,
                "language_code": ASSEMBLYAI_LANGUAGE_CODE,
                "include_timestamps": ASSEMBLYAI_INCLUDE_TIMESTAMPS,
                "dual_channel": ASSEMBLYAI_DUAL_CHANNEL,
                "punctuate": ASSEMBLYAI_PUNCTUATE,
                "format_text": ASSEMBLYAI_FORMAT_TEXT,
                "disfluencies_filter": ASSEMBLYAI_DISFLUENCIES_FILTER,
                "enable_word_boost": ASSEMBLYAI_ENABLE_WORD_BOOST,
                "word_boost_param": ASSEMBLYAI_WORD_BOOST_PARAM,
                "redact_pii": ASSEMBLYAI_REDACT_PII,
                "redact_pii_audio": ASSEMBLYAI_REDACT_PII_AUDIO,
                "redact_pii_policies": ASSEMBLYAI_REDACT_PII_POLICIES,
                "content_safety": ASSEMBLYAI_CONTENT_SAFETY,
                "entity_detection": ASSEMBLYAI_ENTITY_DETECTION,
                "sentiment_analysis": ASSEMBLYAI_SENTIMENT_ANALYSIS,
                "auto_highlights": ASSEMBLYAI_AUTO_HIGHLIGHTS,
                "summarization": ASSEMBLYAI_SUMMARIZATION,
                "summary_model": ASSEMBLYAI_SUMMARY_MODEL,
                "summary_type": ASSEMBLYAI_SUMMARY_TYPE,
            }
        else:
            logger.error(f"Unknown transcription engine: {TRANSCRIPTION_ENGINE}")
            return
        
        # Create transcription engine
        engine = create_transcription_engine(TRANSCRIPTION_ENGINE, engine_config)
        
        # Perform transcription
        result: TranscriptionResult = engine.transcribe_file(path)
        
        if not result.transcript.strip():
            logger.warning(f"[STT] Empty transcript for {path}; skipping file write.")
            return
        
        # Save transcript
        audio_path = Path(path)
        user_base_dir = audio_path.parent.parent
        local_output_dir = user_base_dir / "Transcripts"
        os.makedirs(local_output_dir, exist_ok=True)
        transcript_path = local_output_dir / f"{audio_path.stem}.txt"
        
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(result.transcript)
        logger.info(f"[STT] Transcription saved: {transcript_path}")
        
        # Save word-level confidence data if available
        if result.word_confidences:
            confidence_path = local_output_dir / f"{audio_path.stem}.confidence.json"
            confidence_data = {
                "transcript": result.transcript,
                "overall_confidence": result.confidence,
                "word_data": result.word_confidences,
                "metadata": result.metadata,
                "expected_terms": EXPECTED_NOUNS_LIST or []  # Include for review UI
            }
            with open(confidence_path, "w", encoding="utf-8") as f:
                json.dump(confidence_data, f, indent=2, ensure_ascii=False)
            logger.info(f"[STT] Confidence data saved: {confidence_path}")
        
        # Generate review if enabled
        if REVIEW_CONFIG.enabled:
            try:
                # Use AssemblyAI-specific review if using AssemblyAI engine
                if TRANSCRIPTION_ENGINE == "assemblyai" and confidence_path.exists():
                    review_path = generate_assemblyai_review(
                        confidence_json_path=confidence_path,
                        transcript_path=transcript_path,
                        config=ASSEMBLYAI_REVIEW_CONFIG,
                        expected_terms=EXPECTED_NOUNS_LIST or None,
                    )
                    if review_path:
                        logger.info(f"[Review] AssemblyAI review created: {review_path}")
                else:
                    # Use Whisper-based review for Google Cloud STT or Gemini
                    review_path = generate_review(
                        audio_path=audio_path,
                        transcript_path=transcript_path,
                        review_config=REVIEW_CONFIG,
                        expected_terms=EXPECTED_NOUNS_LIST or None,
                    )
                    if review_path:
                        logger.info(f"[Review] Alignment review created: {review_path}")
            except Exception as review_error:
                logger.error(
                    f"[Review] Failed to generate review file for {audio_path.name}: {review_error}",
                    exc_info=True,
                )
        
        # Archive copy to central transcript folder
        try:
            os.makedirs(CENTRAL_TRANSCRIPT_DIR, exist_ok=True)
            central_copy_path = Path(CENTRAL_TRANSCRIPT_DIR) / f"{audio_path.stem}.txt"
            with open(central_copy_path, "w", encoding="utf-8") as cf:
                cf.write(result.transcript)
            logger.info(f"[STT] Archived transcript to: {central_copy_path}")
        except Exception as e:
            logger.warning(f"[STT] Failed to archive transcript to central folder: {e}")
            
    except Exception as e:
        logger.error(f"[STT] Transcription FAILED for {path}: {e}", exc_info=True)
        raise

def transcription_worker():
    while not shutdown_requested.is_set():
        try:
            path = transcription_queue.get(timeout=5)
        except queue.Empty:
            continue
        try:
            if path is None: break
            
            metric = ProcessingMetrics(
                start_time=time.time(),
                worker_thread=threading.current_thread().name,
                file_size=os.path.getsize(path) if os.path.exists(path) else 0
            )
            
            try:
                process_transcription(path)
                metric.end_time = time.time()
                metric.success = True
                metric.api_calls = 1  # Count API calls made
            except Exception as e:
                metric.end_time = time.time()
                metric.success = False
                metric.error = str(e)
                logger.error(f"Transcription failed for {path}: {e}")
                save_failed_item({"audio_path": path}, e)
                raise
            finally:
                metrics_collector.record_metric(metric)
                transcription_queue.task_done()
        except Exception as e:
            logger.error(f"Unexpected error processing transcription item {path}: {e}", exc_info=True)
            transcription_queue.task_done()

# ----------------------------------------------------------------------
# 7. Analysis
# ----------------------------------------------------------------------
PROMPT_FILE_PATH = os.path.join(SCRIPT_DIR, "config", "prompts.txt")
ANALYSIS_PROMPT_TEMPLATE = ""
try:
    with open(PROMPT_FILE_PATH, 'r', encoding='utf-8') as f:
        ANALYSIS_PROMPT_TEMPLATE = f.read()
    logger.info(f"Successfully loaded analysis prompt from '{PROMPT_FILE_PATH}'.")
except Exception as e:
    logger.error(f"Error reading prompt file '{PROMPT_FILE_PATH}': {e}. Analysis will fail.")

def create_markdown_from_data(data: dict, full_transcript: str) -> str:
    # Get analysis data from the nested structure
    analysis = data.get('analysis', {})
    processing_details = data.get('processing_details', {})
    
    md = [f"---\nTranscript File: {processing_details.get('transcript_file', 'N/A')}",
          f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n---",
          "\n**A. Overall Call Summary:**", analysis.get('summary', 'No summary provided.'),
          "\n**B. Sentiments:**", f"1.  Overall Sentiment: **{analysis.get('sentiment', {}).get('overall', 'N/A')}**",
          "2.  Key Sentiment Drivers:"]
    drivers = analysis.get('sentiment', {}).get('drivers', [])
    if not drivers: md.append("    *   N/A")
    for driver in drivers: md.append(f"    *   {driver}")
    md.append("\n**C. Main Topics/Themes:**")
    topics = analysis.get('topics', [])
    if not topics: md.append("*   No topics identified.")
    for i, topic in enumerate(topics, 1): md.append(f"*   Topic {i}: {topic}")
    md.append("\n**D. Named Entity Detection:**")
    entities = analysis.get('entities', {})
    if not entities: md.append("*   No entities identified.")
    else:
        for category, items in entities.items():
            if items and isinstance(items, list):
                display_category = category.upper()
                for item in items:
                    md.append(f"*   {display_category}: {item}")
    md.append("\n**E. Action Items (If Any):**")
    items = analysis.get('action_items', [])
    if not items: md.append("*   No specific action items identified.")
    else:
        for item in items: md.append(f"*   {item}")
    md.extend(["\n\n## Full Transcript\n", full_transcript])
    return "\n".join(md)

# ----------------------------------------------------------------------
# Import transcript normalizer module
# ----------------------------------------------------------------------
try:
    from tools.transcript_tools.transcript_normalizer_module import transcript_normalizer
    TRANSCRIPT_NORMALIZATION_ENABLED = True
except ImportError:
    try:
        from transcript_normalizer_module import transcript_normalizer
        TRANSCRIPT_NORMALIZATION_ENABLED = True
    except ImportError:
        TRANSCRIPT_NORMALIZATION_ENABLED = False
        logger.warning("Transcript normalizer module not found. Using legacy parsing.")

# Import database updater module
# ----------------------------------------------------------------------
try:
    from tools.database_tools.database_updater import DatabaseUpdater
    DATABASE_UPDATER_ENABLED = True
    logger.info("Database updater module found - will auto-update database")
except ImportError:
    DATABASE_UPDATER_ENABLED = False
    logger.warning("Database updater module not found - database will not be auto-updated")

# Import JSON archive and normalizer module
# ----------------------------------------------------------------------
try:
    from tools.database_tools.archive_and_normalize import ArchiveAndNormalizer
    JSON_NORMALIZER_ENABLED = True
    logger.info("JSON archive and normalizer module found - can normalize existing JSON files")
except ImportError:
    JSON_NORMALIZER_ENABLED = False
    logger.warning("JSON archive and normalizer module not found - JSON normalization not available")

# ----------------------------------------------------------------------
# Helper: Parse transcript text into structured segments with normalization
# ----------------------------------------------------------------------
def parse_transcript_segments(raw_text: str):
    """
    Parse transcript text into structured segments with optional normalization
    
    Args:
        raw_text: Raw transcript text
        
    Returns:
        List of transcript segments
    """
    if TRANSCRIPT_NORMALIZATION_ENABLED and ENABLE_TRANSCRIPT_NORMALIZATION:
        # Use the new transcript normalizer
        try:
            normalized_segments, normalization_info = transcript_normalizer.normalize_raw_transcript(raw_text)
            logger.debug(f"Transcript normalized: {normalization_info['original_segments']} -> {normalization_info['normalized_segments']} segments")
            return normalized_segments
        except Exception as e:
            logger.warning(f"Transcript normalization failed, falling back to legacy parsing: {e}")
    
    # Legacy parsing as fallback
    segments = []
    # Match timestamps in square brackets, speaker label, then text
    line_re = re.compile(r"^\s*\[(\d{2}:\d{2}(?::\d{2})?)\]\s*(Agent|Caller)\s*:\s*(.*)\s*$",
                         re.IGNORECASE)
    for raw_line in raw_text.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        m = line_re.match(line)
        if m:
            timestamp = m.group(1)
            speaker_raw = m.group(2)
            text = m.group(3).strip()
            # Normalize speaker to exactly 'Agent' or 'Caller' (no content changes)
            speaker = 'Agent' if speaker_raw.lower() == 'agent' else 'Caller'
            segments.append({
                'timestamp': timestamp,
                'speaker': speaker,
                'text': text,
            })
        else:
            # Non-matching line: append to previous text to avoid losing content
            if segments:
                joiner = '' if segments[-1]['text'].endswith((' ', '-', '\u2014')) else ' '
                segments[-1]['text'] = f"{segments[-1]['text']}{joiner}{line.strip()}"
            else:
                # If transcript starts without a timestamped line, keep it as-is under unknown speaker
                segments.append({'timestamp': '', 'speaker': '', 'text': line.strip()})
    return segments

def extract_text_from_gemini_response(response) -> str:
    """Best-effort text extraction from Google Generative AI response objects across SDK versions."""
    try:
        text = getattr(response, "text", None)
        if isinstance(text, str) and text.strip():
            return text.strip()
    except Exception:
        pass

    # Try candidates -> content -> parts -> text
    texts = []
    try:
        for candidate in getattr(response, "candidates", []) or []:
            content = getattr(candidate, "content", None)
            parts = getattr(content, "parts", []) if content is not None else []
            for part in parts or []:
                part_text = getattr(part, "text", None)
                if isinstance(part_text, str) and part_text.strip():
                    texts.append(part_text.strip())
    except Exception:
        pass
    if texts:
        return "\n".join(texts).strip()
    return ""

def wait_for_file_activation(file_name: str, max_wait_seconds: int = 120) -> bool:
    """Poll the uploaded file until it is ACTIVE, or timeout. Returns True if ACTIVE or unknown, False on explicit failure."""
    start_time = time.time()
    while time.time() - start_time < max_wait_seconds:
        try:
            f = genai.get_file(name=file_name)
            state = getattr(f, "state", None)
            # State may be enum-like or string
            state_str = getattr(state, "name", str(state)) if state is not None else ""
            if state_str.upper() == "ACTIVE":
                return True
            if state_str.upper() == "FAILED":
                return False
        except Exception:
            # On transient errors, keep polling
            pass
        time.sleep(1.0)
    # If we time out waiting, proceed anyway and let generate_content retry logic handle
    return True

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).strip() if name else ""

def format_duration(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    return f"{minutes}m{seconds}s" if minutes > 0 else f"{seconds}s"

def format_mm_ss(total_seconds: float) -> str:
    total_seconds_int = int(round(total_seconds))
    minutes, seconds = divmod(total_seconds_int, 60)
    return f"{minutes:02d}:{seconds:02d}"

def format_call_time_from_hh_mm(hour_24: int, minute: int) -> str:
    period = "AM" if hour_24 < 12 else "PM"
    hour_12 = 12 if hour_24 % 12 == 0 else (hour_24 % 12)
    return f"{hour_12}:{minute:02d} {period}"

def safe_rename(old_path, new_path, retries=5, delay=0.5):
    for i in range(retries):
        try:
            os.rename(old_path, new_path)
            logger.info(f"Renamed file to: {new_path.name}")
            return True
        except PermissionError:
            if i < retries - 1:
                logger.debug(f"Permission error renaming {old_path.name}, retrying in {delay}s...")
                time.sleep(delay)
            else:
                raise
    return False

def rename_pipeline_files(transcript_path: str, structured_data: dict):
    if not STAFF_MAP: return
    try:
        original_stem = Path(transcript_path).stem
        match = re.match(r'x(\d+)_(\d{4}-\d{2}-\d{2})\.(\d{2}-\d{2})\.\d+', original_stem)
        if not match: return
        user_id, date_part, time_part = match.groups()
        agent_name = STAFF_MAP.get(user_id, f"UnknownAgent-{user_id}")
        # Entities may be nested under analysis per schema alignment
        entities = structured_data.get('analysis', {}).get('entities', {}) if 'analysis' in structured_data else structured_data.get('entities', {})
        caller_name = next((p for p in entities.get('persons', []) if agent_name.lower() not in p.lower()), "UnknownCaller")
        org_list = entities.get('organizations', [])
        organization = next((org for org in org_list if 'crosley law' not in org.lower()), '')
        transcript_p = Path(transcript_path)
        user_base_dir = transcript_p.parent.parent
        audio_dir = user_base_dir / "Audio"
        original_audio_path = None
        for i in range(3):
            original_audio_path = next((p for p in [audio_dir / f"{original_stem}{ext}" for ext in ALLOWED_EXTENSIONS] if p.exists()), None)
            if original_audio_path: break
            time.sleep(0.5)
        if not original_audio_path:
            logger.error(f"Could not find original audio file for stem: {original_stem} after retries.")
            return
        duration_str = "0s"
        try:
            with sf.SoundFile(str(original_audio_path)) as f:
                duration = len(f) / f.samplerate
                duration_str = format_duration(duration)
        except Exception as e:
            logger.warning(f"Could not determine audio duration for {original_audio_path.name}: {e}")
        new_base_name_parts = [sanitize_filename(agent_name), date_part, time_part.replace(':', '-'), duration_str,
                                          sanitize_filename(caller_name), sanitize_filename(organization)]
        new_stem = "_".join(part for part in new_base_name_parts if part)
        
        # Update the "renamed to" field in the structured data
        if 'call_details' in structured_data:
            structured_data['call_details']['renamed to'] = f"{new_stem}.wav"
        
        # Do not rename centrally stored JSON; only rename local JSON if present
        if CENTRAL_JSON_DIR:
            json_path = None
        else:
            json_path = user_base_dir / "JSON_Output" / f"{original_stem}.json"
        md_path = user_base_dir / "Summaries" / f"{original_stem}.md"
        
        # Filter out None values to avoid the warning
        files_to_rename = [path for path in [original_audio_path, transcript_p, json_path, md_path] if path is not None]
        for old_path in files_to_rename:
            if old_path.exists():
                new_path = old_path.with_name(f"{new_stem}{old_path.suffix}")
                safe_rename(old_path, new_path)
            else:
                logger.warning(f"Could not find file to rename: {old_path}")
        
        # Update the JSON file with the new "renamed to" field if using central JSON directory
        if CENTRAL_JSON_DIR and 'call_details' in structured_data and structured_data['call_details'].get('renamed to'):
            try:
                json_output_dir = Path(CENTRAL_JSON_DIR)
                json_path = json_output_dir / f"{original_stem}.json"
                if json_path.exists():
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(structured_data, f, indent=2)
                    logger.info(f"Updated JSON file with renamed to: {json_path}")
            except Exception as e:
                logger.error(f"Failed to update JSON file with renamed to field: {e}")
    except Exception as e:
        logger.error(f"Failed during file renaming for '{transcript_path}': {e}", exc_info=True)

def process_transcript(transcript_path):
    global processed_files
    with processed_files_lock:
        if transcript_path in processed_files: return
        processed_files.add(transcript_path)
    try:
        if not api_key_configured: return
        with open(transcript_path, 'r', encoding='utf-8') as f: content = f.read()
        if len(content.strip()) < MIN_TRANSCRIPT_SIZE: return
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(transcript_content=content)
        model = genai.GenerativeModel(model_name=GEMINI_ANALYSIS_MODEL_NAME)
        response = model.generate_content(prompt, request_options={"timeout": GEMINI_ANALYSIS_TIMEOUT})
        cleaned_response = re.sub(r'^```json\s*|\s*```$', '', response.text, flags=re.MULTILINE).strip()
        gemini_data = json.loads(cleaned_response)

        # Derive call_details from filename and audio
        base_name = os.path.basename(transcript_path)
        m_all = re.match(r"x(\d+)_((?:\d{4}-\d{2}-\d{2}))\.(\d{2})-(\d{2})\.\d+", Path(base_name).stem)
        call_date = None
        call_time = None
        agent_name_for_details = None
        if m_all:
            user_id = m_all.group(1)
            call_date = m_all.group(2)
            hh = int(m_all.group(3))
            mm = int(m_all.group(4))
            call_time = format_call_time_from_hh_mm(hh, mm)
            agent_name_for_details = STAFF_MAP.get(user_id)

        # Locate original audio to compute duration
        transcript_file_path = Path(transcript_path)
        user_base_dir = transcript_file_path.parent.parent
        audio_dir = user_base_dir / "Audio"
        audio_path = None
        try:
            for ext in ALLOWED_EXTENSIONS:
                candidate = audio_dir / f"{transcript_file_path.stem}{ext}"
                if candidate.exists():
                    audio_path = candidate
                    break
        except Exception:
            audio_path = None

        call_duration_str = None
        if audio_path and audio_path.exists():
            try:
                with sf.SoundFile(str(audio_path)) as f:
                    duration_seconds = len(f) / f.samplerate
                    call_duration_str = format_mm_ss(duration_seconds)
            except Exception:
                call_duration_str = None

        call_details = {
            "wav_file": f"{transcript_file_path.stem}.wav",
            "renamed to": "",
            "Agent": agent_name_for_details,
            "call_date": call_date,
            "call_time": call_time,
            "call_duration": call_duration_str,
        }

        analysis = {
            "summary": gemini_data.get("summary"),
            "sentiment": gemini_data.get("sentiment"),
            "topics": gemini_data.get("topics"),
            "entities": gemini_data.get("entities"),
            "action_items": gemini_data.get("action_items"),
        }

        processing_details = {
            "transcript_file": os.path.basename(transcript_path),
            "transcript_path": str(Path(transcript_path).resolve()),
            "analysis_timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "model_used": GEMINI_ANALYSIS_MODEL_NAME,
        }

        # Parse and normalize transcript
        transcript_segments = parse_transcript_segments(content)
        
        # Add normalization metadata if normalization was used
        normalization_info = None
        if TRANSCRIPT_NORMALIZATION_ENABLED and ENABLE_TRANSCRIPT_NORMALIZATION:
            try:
                # Get normalization info from the normalizer
                _, norm_info = transcript_normalizer.normalize_raw_transcript(content)
                normalization_info = norm_info
            except Exception as e:
                logger.warning(f"Could not get normalization info: {e}")
        
        structured_data = {
            "call_details": call_details,
            "analysis": analysis,
            "processing_details": processing_details,
            # Include transcript in a structured, non-hallucinated format: list of {timestamp, speaker, text}
            "transcript": transcript_segments,
        }
        
        # Add normalization info if available
        if normalization_info:
            structured_data["normalization_info"] = normalization_info
        transcript_file_path = Path(transcript_path)
        user_base_dir = transcript_file_path.parent.parent
        if OUTPUT_FORMAT in ('json', 'both'):
            if CENTRAL_JSON_DIR:
                json_output_dir = Path(CENTRAL_JSON_DIR)
            else:
                json_output_dir = user_base_dir / "JSON_Output"
            os.makedirs(json_output_dir, exist_ok=True)
            json_path = json_output_dir / f"{transcript_file_path.stem}.json"
            with open(json_path, 'w', encoding='utf-8') as f: json.dump(structured_data, f, indent=2)
            logger.info(f"[Analysis] Saved JSON to: {json_path}")
            
            # Normalize newly created JSON file if enabled
            if JSON_NORMALIZER_ENABLED and ENABLE_JSON_NORMALIZATION and CENTRAL_JSON_DIR:
                try:
                    normalizer = ArchiveAndNormalizer(
                        source_dir=CENTRAL_JSON_DIR,
                        backup_dir=CENTRAL_JSON_DIR + "_BACKUP"
                    )
                    
                    # Normalize just this specific file
                    single_file_result = normalizer._normalize_single_file(json_path)
                    if single_file_result.get("success"):
                        logger.debug(f"[JSON Normalization] Normalized new file: {json_path.name}")
                    else:
                        logger.warning(f"[JSON Normalization] Failed to normalize new file {json_path.name}: {single_file_result.get('error')}")
                except Exception as e:
                    logger.warning(f"[JSON Normalization] Error normalizing new file {json_path.name}: {e}")
            
            # Auto-update database if enabled
            if DATABASE_UPDATER_ENABLED:
                try:
                    updater = DatabaseUpdater(str(CENTRAL_JSON_DIR), "call_recordings.db")
                    results = updater.update_database()
                    if results['processed'] > 0:
                        logger.info(f"[Database] Auto-updated database: {results['processed']} new calls added")
                    elif results['skipped'] > 0:
                        logger.debug(f"[Database] Database already up to date: {results['skipped']} existing calls")
                except Exception as e:
                    logger.warning(f"[Database] Failed to auto-update database: {e}")
        if OUTPUT_FORMAT in ('markdown', 'both'):
            md_path = user_base_dir / "Summaries" / f"{transcript_file_path.stem}.md"
            os.makedirs(md_path.parent, exist_ok=True)
            with open(md_path, 'w', encoding='utf-8') as f: f.write(create_markdown_from_data(structured_data, content))
            logger.info(f"[Analysis] Saved Markdown to: {md_path}")
        rename_pipeline_files(transcript_path, structured_data)
        save_processed_files()
    except Exception as e:
        logger.error(f"Error in process_transcript('{transcript_path}'): {e}", exc_info=True)
        with processed_files_lock:
            processed_files.discard(transcript_path)

def scan_existing_transcripts():
    count = 0
    for root, _, files in os.walk(TRANSCRIPTS_BASE_DIR):
        if any(d in Path(root).parts for d in ["Summaries", "Audio", "JSON_Output"]): continue
        for fname in files:
            if fname.lower().endswith(".txt"):
                full = os.path.join(root, fname)
                if "Transcripts" in Path(full).parts and full not in processed_files:
                    try:
                        analysis_queue.put(full, block=False)
                        count += 1
                    except queue.Full:
                        logger.warning("[Analysis] Queue full; stopping scan.")
                        return count
    logger.info(f"[Analysis] Queued {count} existing transcripts for analysis.")

def scan_existing_audio_files():
    """Scan for audio files that don't have corresponding transcripts and queue them for transcription"""
    count = 0
    if not os.path.isdir(TRANSCRIPTS_BASE_DIR):
        logger.warning(f"[Transcription] Base directory not found: {TRANSCRIPTS_BASE_DIR}")
        return count
    
    for item in os.scandir(TRANSCRIPTS_BASE_DIR):
        if item.is_dir() and not item.name.startswith(('_', '.')):
            audio_dir_path = os.path.join(item.path, 'Audio')
            transcripts_dir_path = os.path.join(item.path, 'Transcripts')
            
            if not os.path.isdir(audio_dir_path):
                continue
            
            # Get list of existing transcripts (without extension)
            existing_transcripts = set()
            if os.path.isdir(transcripts_dir_path):
                for transcript_file in os.listdir(transcripts_dir_path):
                    if transcript_file.lower().endswith('.txt'):
                        existing_transcripts.add(Path(transcript_file).stem)
            
            # Check each audio file
            for audio_file in os.listdir(audio_dir_path):
                audio_path = os.path.join(audio_dir_path, audio_file)
                if not os.path.isfile(audio_path):
                    continue
                
                # Check if it's an allowed audio extension
                if not any(audio_file.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
                    continue
                
                # Check if transcript exists
                audio_stem = Path(audio_file).stem
                if audio_stem not in existing_transcripts:
                    try:
                        # Check if file is accessible (not locked)
                        try:
                            os.rename(audio_path, audio_path)
                        except PermissionError:
                            logger.debug(f"[Transcription] Skipping locked file: {audio_file}")
                            continue
                        
                        transcription_queue.put(audio_path, block=False)
                        count += 1
                        logger.info(f"[Transcription] Queued unprocessed audio: {audio_file}")
                    except queue.Full:
                        logger.warning("[Transcription] Queue full; stopping audio scan.")
                        return count
    
    logger.info(f"[Transcription] Queued {count} unprocessed audio files for transcription.")
    return count

def normalize_existing_json_files():
    """Normalize existing JSON files on startup if enabled"""
    if not JSON_NORMALIZER_ENABLED or not NORMALIZE_EXISTING_JSON_ON_START:
        return
    
    if not CENTRAL_JSON_DIR:
        logger.warning("[JSON Normalization] Central JSON directory not configured - skipping normalization")
        return
    
    try:
        logger.info("[JSON Normalization] Starting normalization of existing JSON files...")
        
        # Initialize the normalizer
        normalizer = ArchiveAndNormalizer(
            source_dir=CENTRAL_JSON_DIR,
            backup_dir=CENTRAL_JSON_DIR + "_BACKUP"
        )
        
        # Run normalization in safe mode (with backup protection)
        results = normalizer.archive_and_normalize(dry_run=False, force_overwrite=False)
        
        if results["success"]:
            logger.info(f"[JSON Normalization] Successfully processed {results['normalized_files']} files")
            logger.info(f"[JSON Normalization] Archived: {results['archived_files']}, "
                       f"Skipped: {results['skipped_files']}, Failed: {results['failed_files']}")
            
            if results["errors"]:
                logger.warning(f"[JSON Normalization] {len(results['errors'])} files had errors:")
                for error in results["errors"][:5]:  # Log first 5 errors
                    logger.warning(f"  - {error}")
                if len(results["errors"]) > 5:
                    logger.warning(f"  ... and {len(results['errors']) - 5} more errors")
        else:
            logger.error(f"[JSON Normalization] Failed: {results.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"[JSON Normalization] Unexpected error during startup normalization: {e}", exc_info=True)

class TranscriptFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.lower().endswith(".txt"): return
        path = event.src_path
        if "Transcripts" in Path(path).parts:
            logger.info(f"[Analysis] New transcript detected: {path}")
            time.sleep(1)
            analysis_queue.put(path, block=False)

def analysis_worker():
    while not shutdown_requested.is_set():
        try:
            path = analysis_queue.get(timeout=5)
        except queue.Empty:
            continue
        try:
            if path is None: break
            
            metric = ProcessingMetrics(
                start_time=time.time(),
                worker_thread=threading.current_thread().name,
                file_size=os.path.getsize(path) if os.path.exists(path) else 0
            )
            
            try:
                process_transcript(path)
                metric.end_time = time.time()
                metric.success = True
                metric.api_calls = 1  # Count API calls made
            except Exception as e:
                metric.end_time = time.time()
                metric.success = False
                metric.error = str(e)
                logger.error(f"Analysis failed for {path}: {e}")
                save_failed_item({"transcript_path": path}, e)
                raise
            finally:
                metrics_collector.record_metric(metric)
                analysis_queue.task_done()
        except Exception as e:
            logger.error(f"Unexpected error in analysis worker for item {path}: {e}", exc_info=True)
            analysis_queue.task_done()

# ----------------------------------------------------------------------
# 8. Main
# ----------------------------------------------------------------------
# Global shutdown flag for graceful worker termination
shutdown_requested = threading.Event()

def main():
    # Validate configuration first
    validate_configuration()
    
    load_processed_files()
    threads = []
    for i in range(MAX_TRANSCRIPTION_WORKERS):
        t = threading.Thread(target=transcription_worker, name=f"Transcriber-{i+1}", daemon=True)
        t.start()
        threads.append(t)
    for i in range(MAX_ANALYSIS_WORKERS):
        t = threading.Thread(target=analysis_worker, name=f"Analyzer-{i+1}", daemon=True)
        t.start()
        threads.append(t)
    
    # Start production enhancement threads
    metrics_thread = threading.Thread(target=metrics_reporter, name="MetricsReporter", daemon=True)
    metrics_thread.start()
    threads.append(metrics_thread)
    
    dead_letter_thread = threading.Thread(target=process_dead_letter_queue, name="DeadLetterProcessor", daemon=True)
    dead_letter_thread.start()
    threads.append(dead_letter_thread)
    
    logger.info(f"Started {len(threads)} worker threads.")
    
    # Normalize existing JSON files if enabled
    if NORMALIZE_EXISTING_JSON_ON_START:
        normalize_existing_json_files()
    
    # Process new audio files that don't have transcripts
    if PROCESS_NEW_AUDIO_ON_START:
        scan_existing_audio_files()
    
    if PROCESS_EXISTING_ON_START:
        scan_existing_transcripts()
    
    observer = Observer()
    logger.info(f"Discovering user audio directories to watch inside: {TRANSCRIPTS_BASE_DIR}")
    discovered_audio_dirs = []
    if os.path.isdir(TRANSCRIPTS_BASE_DIR):
        for item in os.scandir(TRANSCRIPTS_BASE_DIR):
            if item.is_dir() and not item.name.startswith(('_', '.')):
                audio_dir_path = os.path.join(item.path, 'Audio')
                if os.path.isdir(audio_dir_path):
                    discovered_audio_dirs.append(audio_dir_path)
                    logger.info(f"  + Found and will watch: {audio_dir_path}")
    else:
        logger.error(f"Base directory for watching not found: {TRANSCRIPTS_BASE_DIR}. Cannot watch for new audio.")
    
    audio_handler = CallMonitorHandler()
    for d in discovered_audio_dirs:
        observer.schedule(audio_handler, d, recursive=False)

    if os.path.isdir(TRANSCRIPTS_BASE_DIR):
        observer.schedule(TranscriptFileHandler(), TRANSCRIPTS_BASE_DIR, recursive=True)
    
    observer.start()
    logger.info("Watchdog observers started. Press Ctrl+C to exit.")

    try:
        while observer.is_alive():
            check_for_completion_and_growth()
            time.sleep(CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        logger.info("Shutdown requested.")
    finally:
        # Signal workers to stop gracefully
        shutdown_requested.set()
        
        observer.stop()
        observer.join()
        for _ in range(MAX_TRANSCRIPTION_WORKERS): transcription_queue.put(None)
        for _ in range(MAX_ANALYSIS_WORKERS): analysis_queue.put(None)
        logger.info(f"Waiting for {transcription_queue.qsize() + analysis_queue.qsize()} tasks to complete...")
        
        # Add timeout to prevent indefinite hanging during shutdown
        def wait_for_queue_with_timeout(queue, timeout=30):
            """Wait for queue to empty with timeout to prevent shutdown hanging"""
            start_time = time.time()
            while not queue.empty() and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            return queue.empty()
        
        # Wait for queues with timeout
        transcription_complete = wait_for_queue_with_timeout(transcription_queue, timeout=30)
        analysis_complete = wait_for_queue_with_timeout(analysis_queue, timeout=30)
        
        if not transcription_complete:
            logger.warning("Transcription queue did not complete within timeout - forcing shutdown")
        if not analysis_complete:
            logger.warning("Analysis queue did not complete within timeout - forcing shutdown")
            
        logger.info("=== CallPipeline Shutdown Complete ====")

if __name__ == "__main__":
    main()