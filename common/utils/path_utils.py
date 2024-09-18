import os
import json
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
class PathHelper:
    CONFIG = None

    @staticmethod
    def load_config():
        """
        설정 파일에서 설정을 로드하는 함수
        """
        # 현재 파일의 디렉토리 기준으로 두 단계 위로 올라간 후 'configs/config.json' 파일을 찾음
        config_path = os.path.join(os.path.dirname(__file__), '../../configs/config.json')
        with open(config_path, 'r') as f:
            PathHelper.CONFIG = json.load(f)
        
        # # 설정 파일이 제대로 로드되었는지 확인하는 로그 추가
        # print(f"Config loaded: {PathHelper.CONFIG}")


    @staticmethod
    def get_abs_path(*path_parts):
        """
        주어진 경로 부분들을 조합하여 절대 경로를 반환하는 함수.
        설정 파일로 설정된 루트 디렉토리를 기준으로 동작합니다.
        
        Args:
            *path_parts: 경로의 각 부분들을 나열 (예: 'src', 'templates', 'btn', 'close_btn.png')
            *path_parts: 경로의 각 부분들을 나열 (예: 'reports', '변경납기관리', '파일명.xlsx')
        Returns:
            str: 절대 경로 문자열
        """
        if PathHelper.CONFIG is None:
            PathHelper.load_config()

        # 루트 디렉토리를 절대 경로로 변환
        root_dir = os.path.abspath(PathHelper.CONFIG.get('root_dir', r'C:\work\RPA_python3.7_20240824'))

        # 경로 구분자를 일관되게 처리
        norm_path_parts = [os.path.normpath(part) for part in path_parts]

        return os.path.join(root_dir, *norm_path_parts)
    
    @staticmethod
    def get_config_value(key, default=None):
        """
        설정 파일에서 특정 키의 값을 가져오는 함수.
        Args:
            key: 설정 파일에서 가져올 키.
            default: 키가 없을 경우 반환할 기본 값.
        Returns:
            설정된 값 또는 기본 값.
        """
        if PathHelper.CONFIG is None:
            PathHelper.load_config()

        
        value = PathHelper.CONFIG.get(key, default)
        return value
    
    @staticmethod
    def get_image_path(image_key):
        """
        설정 파일에서 특정 이미지 키에 해당하는 경로를 가져오는 함수.
        Args:
            image_key: 이미지 경로를 가져올 키 (예: 'empty_table_image').
        Returns:
            설정된 이미지 경로 또는 None.
        """
        image_paths = PathHelper.get_config_value("image_paths", {})
        return image_paths.get(image_key, None)