import time
import pyautogui
import os
import cv2
import numpy as np
import os
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from PIL import ImageGrab
import sys
import os
from PIL import Image, ImageChops, ImageGrab

# 현재 파일의 디렉토리 기준으로 src 폴더 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(src_path)

from common.logger_manager import LoggerManager
from common.utils.path_utils import PathHelper

class SuperLoadingManager:
    def __init__(self, threshold=0.8, check_interval=0.1, max_wait_time=900, disappearance_check_time=10, center_search_size=(200, 200)):
        self.logger = LoggerManager.get_logger(__name__)

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
        average_similarity = self.get_average_similarity()
        if average_similarity >= self.threshold:
            print(f"Loading icon detected with average similarity: {average_similarity:.4f}")
            return True
        else:
            print(f"Loading icon not detected. Average similarity: {average_similarity:.4f}")
            return False
    def wait_for_loading_to_complete(self):
        """
        로딩 아이콘이 사라질 때까지 대기하는 메서드.
        로딩 아이콘이 감지되지 않으면 5초 추가로 대기하여 재등장 여부를 확인.
        5초 동안 재감지되지 않으면 로딩 완료로 간주.

        Returns:
        - (bool, str): 로딩이 완료되면 (True, "로딩 완료"), 그렇지 않으면 (False, "오류 메시지")
        """
        start_time = time.time()  # 전체 감지 시작 시간
        icon_present_start_time = None  # 로딩 아이콘이 감지된 시간을 기록
        icon_disappeared_start_time = None  # 로딩 아이콘이 사라진 시간을 기록
        similarity_threshold = 0.4  # 로딩 아이콘이 사라졌다고 판단하는 임계값
        consecutive_no_icon_count = 0  # 연속으로 로딩 아이콘이 감지되지 않은 횟수
        required_no_icon_count = 5  # 로딩 아이콘이 사라졌다고 판단하기 위한 연속 감지 실패 횟수

        self.logger.debug("Starting wait_for_loading_to_complete...")

        while time.time() - start_time < 300:  # 최대 5분(300초) 대기
            average_similarity = self.get_average_similarity()  # 평균 유사도 계산
            self.logger.debug(f"Current average similarity: {average_similarity:.4f}")

            if average_similarity >= similarity_threshold:
                # 로딩 아이콘이 감지되는 경우
                if icon_present_start_time is None:
                    icon_present_start_time = time.time()
                    self.logger.debug(f"Loading icon detected at {icon_present_start_time:.2f}. Waiting for it to disappear...")
                    print("로딩 아이콘 감지됨, 로딩이 사라질 때까지 대기 중...")

                # 로딩 아이콘이 3분(180초) 이상 지속적으로 감지되면 시스템 오류로 간주
                if time.time() - icon_present_start_time >= 180:
                    self.logger.error("Loading icon detected for over 120 seconds. System error assumed.")
                    print("로딩 아이콘이 180초 이상 지속적으로 감지됨. 시스템 오류로 간주합니다.")
                    return False, "로딩 아이콘이 180초 이상 지속적으로 감지됨. 시스템 오류로 간주합니다."

                # 로딩 아이콘이 감지되었으므로 사라진 시간 및 연속 실패 횟수 초기화
                icon_disappeared_start_time = None
                consecutive_no_icon_count = 0
                self.logger.debug("Loading icon is still present. Resetting disappearance count.")


            else:
                # 로딩 아이콘이 감지되지 않는 경우 
                # 연속 실패 횟수 증가
                consecutive_no_icon_count += 1
                print(f"로딩 아이콘 감지 시도 횟수: {consecutive_no_icon_count}")
                self.logger.debug(f"Loading icon not detected. Consecutive no-icon count: {consecutive_no_icon_count}")


                # 로딩 아이콘이 일정 횟수 이상 감지되지 않으면 사라짐으로 간주
                if consecutive_no_icon_count >= required_no_icon_count:
                    if icon_disappeared_start_time is None:
                        icon_disappeared_start_time = time.time()
                        self.logger.debug(f"Loading icon disappeared at {icon_disappeared_start_time:.2f}. Waiting 5 more seconds to confirm.")
                        print("로딩 아이콘이 사라짐, 추가 5초 대기 중...")
                        icon_present_start_time = None  # 아이콘 감지 시간을 초기화

                    # 로딩 아이콘이 사라진 후 추가 5초 대기
                    time.sleep(5)
                    average_similarity = self.get_average_similarity()  # 추가 대기 후 유사도 재평가
                    self.logger.debug(f"Post-wait average similarity: {average_similarity:.4f}")

                    if average_similarity < similarity_threshold:
                        self.logger.info("Loading icon did not reappear within 5 seconds. Loading complete.")
                        print("로딩 아이콘이 5초 내에 재감지되지 않음, 로딩이 완전히 완료됨.")
                        return True, "로딩 완료"
                    else:
                        # 로딩 아이콘이 추가 대기 중 재감지된 경우
                        self.logger.debug("Loading icon reappeared during additional wait. Resetting wait process.")
                        print("로딩 아이콘이 추가 5초 대기 중 다시 감지됨, 다시 대기 시작.")
                        icon_present_start_time = time.time()
                        consecutive_no_icon_count = 0

            time.sleep(self.check_interval)
        
        self.logger.error("Maximum wait time exceeded. System issue possible.")
        print("최대 대기 시간 초과. 시스템 문제 가능성 있음.")
        return False, "최대 대기 시간 초과. 시스템 문제 가능성 있음."

