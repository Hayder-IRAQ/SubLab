# utils/file_processor.py
import threading
import queue
import logging
from pathlib import Path
from typing import List, Dict, Optional, Callable
from audio.extractor import AudioExtractor
from utils.export import Exporter
from utils.config import Config

logger = logging.getLogger(__name__)


class FileProcessor:
    """Threaded File Processor to process audio/video files"""

    def __init__(self, config: Config, status_callback: Callable, progress_callback: Callable):
        self.file_queue = queue.Queue()
        self.audio_extractor = AudioExtractor()
        self.exporter = Exporter()
        self.status_callback = status_callback
        self.progress_callback = progress_callback
        self.config = config
        self.is_running = False
        self.thread = None

    def add_files(self, files: List[str]):
        """Add files to the queue"""
        for file in files:
            self.file_queue.put(file)

    def process_files(self):
        """Start processing files in a separate thread"""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._process)
            self.thread.start()

    def _process(self):
        """Internal process handling"""
        while not self.file_queue.empty():
            file_path = self.file_queue.get()
            self.status_callback(f"Processing: {file_path}")
            try:
                success = self._process_file(file_path)
                if success:
                    self.status_callback(f"Completed: {file_path}")
                else:
                    self.status_callback(f"Failed to process: {file_path}")
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                self.status_callback(f"Error: {e}")
        self.is_running = False

    def stop_processing(self):
        """Stop processing files"""
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()