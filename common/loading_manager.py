import time
import pyautogui
import os
import cv2
import numpy as np
import os
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from PIL import ImageGrab

from PIL import Image, ImageChops, ImageGrab

from common.logger_manager import LoggerManager
from common.utils.path_utils import PathHelper


class LoadingIconManager:
    def __init__(self, threshold=0.8, check_interval=0.1, max_wait_time=900, disappearance_check_time=10, center_search_size=(200, 200)):
        self.logger = LoggerManager.get_logger(__name__)
        self.search_center = True
        self.threshold = threshold
        self.check_interval = check_interval
        self.max_wait_time = max_wait_time
        self.disappearance_check_time = disappearance_check_time
        self.center_search_size = center_search_size
        
        # 이미지 경로를 config.json에서 불러옴
        self.template_paths = PathHelper.get_image_path("loading_icon_image")
        
        # 템플릿 파일들이 모두 존재하는지 확인
        for template_path in self.template_paths:
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"not found template path: {template_path}")

    def _get_center_region(self):
        """
        화면 중앙에 대해 주어진 크기의 영역을 계산하여 반환하는 메서드.
        """
        screen_width, screen_height = pyautogui.size()
        center_x = screen_width // 2
        center_y = screen_height // 2
        region_width, region_height = self.center_search_size

        return (
            center_x - region_width // 2,
            center_y - region_height // 2,
            region_width,
            region_height
        )

    def get_average_similarity(self, num_samples=5):
        """
        여러 번의 템플릿 매칭 시도를 통해 평균 유사도를 계산하여 반환하는 메서드.
        
        Parameters:
        - num_samples: 유사도 계산을 위한 샘플링 횟수.
        
        Returns:
        - 평균 유사도 (float)
        """
        similarities = []
        for _ in range(num_samples):
            search_region = self._get_center_region()
            
            for template_path in self.template_paths:
                template = cv2.imread(template_path, 0)
                screenshot = pyautogui.screenshot(region=search_region)
                screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)
                
                match = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(match)
                similarities.append(max_val)
            time.sleep(self.check_interval)
        return sum(similarities) / len(similarities)

    def is_loading_icon_present(self):
        """
        현재 로딩 아이콘이 화면에 존재하는지 확인하는 메서드
        Returns:
        - 로딩 아이콘이 존재하면 True, 아니면 False
        """
        average_similarity = self.get_average_similarity()
        if average_similarity >= self.threshold:
            self.logger.info(f"Loading icon detected with average similarity: {average_similarity:.4f}")
            return True
        else:
            self.logger.info(f"Loading icon not detected. Average similarity: {average_similarity:.4f}")
            return False

    def wait_until_condition(self, condition_fn, timeout, check_interval):
        
        start_time = time.time()
        while True:
            condition_met = condition_fn()
            if condition_met:
                return True
            if time.time() - start_time > timeout:
                return False
            time.sleep(check_interval)
            
    def wait_for_loading_to_complete(self):
        """
        로딩 아이콘이 사라질 때 까지 대기하는 메서드
        최대 5분까지 대기하며, 로딩 아이콘이 5초 이상 감지되지 않으면 로딩이 완료된것으로 간주함.
        
        Returns:
        - 로딩이 완료되면 True, 타임아웃이 발생하면 False
        """
        start_time = time.time()  # 시작 시간 기록
        consecutive_absent_time = 0
        icon_disappeared_start_time = None  # 로딩 아이콘이 사라진 시간을 기록하기 위한 변수
        
        while time.time() - start_time < self.max_wait_time:  # 최대(15분) 대기 시간까지 반복
            
            if self.is_loading_icon_present():
                self.logger.debug("로딩 아이콘 감지됨, 로딩이 사라질 때까지 대기 중...")
                consecutive_absent_time = 0  # 리셋
                icon_disappeared_start_time = None  # 아이콘 사라짐 시간 초기화
            else:
                if icon_disappeared_start_time is None:
                    icon_disappeared_start_time = time.time()
                    self.logger.debug("로딩 아이콘이 사라짐, 재등장 여부 확인 중...")

                consecutive_absent_time = time.time() - icon_disappeared_start_time

                if consecutive_absent_time >= self.disappearance_check_time:  # 로딩 아이콘이 사라진 후 10초 동안 재등장하지 않으면 로딩 완료로 간주
                    self.logger.debug("로딩 완료로 간주됨.")
                    return True

                self.logger.debug("로딩 아이콘이 감지되지 않음, 다시 확인 중...")

            time.sleep(self.check_interval)

        self.logger.error("최대 대기 시간 초과. 시스템 문제 가능성 있음.")
        return False  # 타임아웃 초과 시 로딩 실패로 간주


    def capture_screen(self, region):
        """
        주어진 영역(region)을 캡처하고 이미지를 반환하는 메서드.
        Parameters:
        - region: (x, y, width, height) 형식의 튜플
        Returns:
        - 캡처한 이미지 (PIL 이미지 객체)
        """
        x, y, width, height = region
        return ImageGrab.grab(bbox=(x, y, x + width, y + height))
    
    def save_empty_table_image(self, region, filepath=None):
        """
        빈 테이블 상태의 이미지를 캡처하고 저장하는 메서드
        Parameters:
        - region: (x, y, width, height) 형식의 튜플
        - filepath: 저장할 파일 경로
        """
        if filepath is None:
            filepath = PathHelper.get_image_path("empty_table_image")
        
        empty_table_image = self.capture_screen(region)
        empty_table_image.save(filepath)
        self.logger.debug(f"Empty table image saved at: {filepath}")

    def compare_table_image(self, region, image_key="empty_table_image"):
        """
        저장된 이미지와 현재 이미지를 비교하여 변화가 있는지 확인하는 메서드.
        Parameters:
        - region: (x, y, width, height) 형식의 튜플
        - image_key: config.json에서 사용할 이미지 경로의 키.
        Returns:
        - 이미지가 다르면 True, 같으면 False
        """
        empty_image_path = PathHelper.get_image_path(image_key)
        
        if not os.path.exists(empty_image_path):
            self.logger.error(f"Image not found at: {empty_image_path}")
            raise FileNotFoundError(f"Image not found at: {empty_image_path}")
        
        empty_image = Image.open(empty_image_path)
        current_image = self.capture_screen(region)

        # 동적으로 이미지를 크기 조정
        if empty_image.size != current_image.size:
            self.logger.debug(f"Resizing current image from {current_image.size} to {empty_image.size}")
            current_image = current_image.resize(empty_image.size, Image.ANTIALIAS)

        # 이미지 비교
        diff = ImageChops.difference(empty_image, current_image)
        if diff.getbbox() is not None:
            self.logger.debug("Change detected in table. Data might have been loaded.")
            self.logger.info("Loading complete.")
            return True
        else:
            self.logger.info("No changes detected in the table. Still waiting for data to load.")
            return False
        
    def wait_for_table_load(self, region, image_key="empty_table_image", max_attempts=5, check_interval=3):
        """
        테이블이 로드될 때까지 저장된 이미지와 현재 테이블 이미지를 반복적으로 비교하며 대기합니다.
        매개변수:
        - region: 캡처할 영역을 지정하는 (x, y, width, height) 형식의 튜플.
        - image_key: config.json에서 사용할 이미지 경로의 키.
        - max_attempts: 테이블이 로드되었는지 확인할 최대 시도 횟수.
        - check_interval: 각 확인 사이의 대기 시간 (초 단위).
        반환값:
        - 테이블이 지정된 시도 내에 로드되면 True, 그렇지 않으면 False.
        """
        attempt = 0
        
        while attempt < max_attempts:
            if self.compare_table_image(region, image_key):
                self.logger.info(f"Table loaded successfully on attempt {attempt + 1}.")
                return True
            
            attempt += 1
            self.logger.info(f"Table not loaded yet. Attempt {attempt}/{max_attempts}. Waiting for {check_interval} seconds before next check.")
            time.sleep(check_interval)
    
        self.logger.error("Table did not load within the given attempts.")
        return False