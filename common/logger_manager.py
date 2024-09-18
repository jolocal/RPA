import logging
import logging.config
import os
from datetime import datetime
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
class LoggerManager:
    _logger_initialized = False

    @classmethod
    def setup_logger(cls):
        if cls._logger_initialized:
            return

        # logs 폴더 경로 설정
        base_log_dir = os.getenv('LOG_DIR', 'C:/work/RPA_python3.7_20240824/logs')
        info_dir = os.path.join(base_log_dir, 'info')
        error_dir = os.path.join(base_log_dir, 'error')
        debug_dir = os.path.join(base_log_dir, 'debug')

        # 디렉토리가 없는 경우 생성
        os.makedirs(info_dir, exist_ok=True)
        os.makedirs(error_dir, exist_ok=True)
        os.makedirs(debug_dir, exist_ok=True)

        current_date = datetime.now().strftime('%Y-%m-%d')

        log_config = {
            'version': 1,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s  - %(name)s  -   %(levelname)s   -   %(message)s',
                },
            },
            'handlers': {
                'infoFileHandler': {
                    'class': 'logging.handlers.TimedRotatingFileHandler',
                    'level': 'INFO',
                    'formatter': 'standard',
                    'filename': os.path.join(info_dir, f'log_INFO_{current_date}.log'),  # 파일 경로 설정
                    'when': 'midnight',
                    'interval': 1,
                    'backupCount': 7,
                    'encoding': 'utf-8',
                },
                'errorFileHandler': {
                    'class': 'logging.handlers.TimedRotatingFileHandler',
                    'level': 'ERROR',
                    'formatter': 'standard',
                    'filename': os.path.join(error_dir, f'log_ERROR_{current_date}.log'),  # 파일 경로 설정
                    'when': 'midnight',
                    'interval': 1,
                    'backupCount': 7,
                    'encoding': 'utf-8',
                },
                'debugFileHandler': {
                    'class': 'logging.handlers.TimedRotatingFileHandler',
                    'level': 'DEBUG',
                    'formatter': 'standard',
                    'filename': os.path.join(debug_dir, f'log_DEBUG_{current_date}.log'),  # 파일 경로 설정
                    'when': 'midnight',
                    'interval': 1,
                    'backupCount': 7,
                    'encoding': 'utf-8',
                },
            },
            'root': {
                'handlers': ['infoFileHandler', 'errorFileHandler', 'debugFileHandler'],
                'level': 'DEBUG',
            },
        }

        logging.config.dictConfig(log_config)
        cls._logger_initialized = True

    @classmethod
    def get_logger(cls, name=None):
        cls.setup_logger()
        return logging.getLogger(name)
