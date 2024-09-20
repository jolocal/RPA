import cv2
import numpy as np
import pyautogui
import pytesseract
import time
import re
import gc

from common.logger_manager import LoggerManager


# 로거 설정
logger = LoggerManager.get_logger(__name__)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class PopupManager:
    
    # 캐시 딕셔너리 추가
    cache = {}
    
    """
    extract_text_from_popup:
    팝업창의 텍스트를 추출한 후, 정규화 과정을 거쳐 잘못된 인식을 수정합니다.
    
    analyze_and_click:
    추출된 텍스트에 타겟 텍스트가 포함되어 있는지 확인한 후, "예" 또는 "아니오" 버튼이 있는지를 추가로 확인합니다.
    버튼이 확인되면, 해당 좌표(pos_yes_btn)를 클릭합니다.
    
    normalize_text:
    OCR이 잘못 인식한 텍스트를 정규화하여 올바른 텍스트로 교정합니다.
    
    extract_text_and_buttons:
    정규화된 텍스트에서 "예", "아니오", "확인" 버튼의 존재 여부를 확인합니다.
    
    process_popup:
    팝업 감지 및 텍스트 추출, 분석, 버튼 클릭의 전체 과정을 담당합니다.
    
    """
    
    
    # 팝업 감지 영역의 기본 값을 클래스 속성으로 설정
    REGION_X_START = 800
    REGION_Y_START = 450
    REGION_X_END = 1350
    REGION_Y_END = 650

    @staticmethod
    def take_screenshot():
        """스크린샷을 찍고 OpenCV 이미지로 변환"""
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        logger.debug("Screenshot taken and converted to OpenCV format.")
        return screenshot

    @staticmethod
    def detect_popup(image):
        """특정 영역에서 팝업창을 감지"""
        # 팝업 영역 추출
        region_of_interest = image[PopupManager.REGION_Y_START:PopupManager.REGION_Y_END, PopupManager.REGION_X_START:PopupManager.REGION_X_END]
        
        # 그레이스케일로 변환
        gray = cv2.cvtColor(region_of_interest, cv2.COLOR_BGR2GRAY)
        
        # 가우시안 블러 적용 (노이즈 감소)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 경계선 검출
        edged = cv2.Canny(blurred, 50, 150)
        
        # 외곽선(컨투어) 찾기
        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # 가장 큰 외곽선을 팝업창으로 가정
            popup_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(popup_contour)
            
            # 팝업창의 위치를 원래 이미지 좌표로 변환
            x += PopupManager.REGION_X_START
            y += PopupManager.REGION_Y_START
            
            # 팝업 영역만 잘라서 반환
            popup_region = image[y:y+h, x:x+w]
            
            # 디버깅용: 팝업창 영역에 사각형 그리기
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            logger.info(f"Popup detected at position ({x}, {y}) with size ({w}, {h}).")
            return image, popup_region
        
        else:
            print("팝업창을 찾을 수 없습니다.")
            logger.info("No popup detected in the specified region.")
            return image, None

    @staticmethod
    def extract_text_from_popup(popup_region):
        """OCR을 통해 팝업창 텍스트를 추출"""
        # 팝업 영역 해시 생성 (이미지를 고유하게 식별)
        hash_value = hash(popup_region.tobytes())
        
        # 캐시 확인: 이미 처리된 이미지라면 캐시된 결과를 반환
        if hash_value in PopupManager.cache:
            logger.debug("Using cached OCR result.")
            return PopupManager.cache[hash_value]
        
        # 이미지 전처리: 그레이스케일, 이진화, 대비 조정
        gray = cv2.cvtColor(popup_region, cv2.COLOR_BGR2GRAY)
        _, binary_image = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 이미지 확대 (텍스트가 작을 경우)
        scale_factor = 2
        enlarged_image = cv2.resize(binary_image, (0, 0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)
        
        # Tesseract 설정
        custom_config = r'--oem 3 --psm 6'
        
        # OCR을 통해 텍스트 추출
        text = pytesseract.image_to_string(enlarged_image, lang='kor+eng', config=custom_config)
        
        # logger.debug(f"Extracted text: {text.strip()}")
        
        #! 정규화 단계에서 잘못 인식된 텍스트 수정
        normalized_text = PopupManager.normalize_text(text)
        logger.debug(f"Normalized text: {normalized_text.strip()}")
        
        # 캐시에 결과 저장
        PopupManager.cache[hash_value] = normalized_text
        logger.debug(f"Text cached with hash: {hash_value}")
        
        return normalized_text
    
    @staticmethod
    def normalize_text(text):
        """
        OCR이 잘못 인식한 텍스트를 정규화하여 보정합니다.
        : param text: 원본 추출된 텍스트
        : return: 정규화된 텍스트
        """
        
        # Success
        text = re.sub(r'히터생성', 'Pallet생성', text)
        text = re.sub(r'a', '예', text)
        text = re.sub(r'마니모', '아니오', text)
        text = re.sub(r'9인','확인',text)
        
        # Failed    
        text = re.sub(r'대상미', '대상이', text)
        text = re.sub(r'미(가)', '이(가)', text)
        text = re.sub(r'존재하지 많습니다.','존재하지 않습니다.',text)
        
        # CG) 미미 『헤하 번호가 생성된 데미터 입니다,
        text = re.sub(r'미미.','이미',text)
        text = re.sub(r'데미터.','데이터',text)

        
        return text


    @staticmethod
    def analyze_and_click(detected_text, success_texts, failure_texts, pos_yes_btn):
        """
        추출된 텍스트를 분석하여 성공 또는 실패 여부를 판단한 후, 버튼 클릭
        :param detected_text: 팝업에서 추출된 텍스트
        :param success_texts: 성공 텍스트 리스트
        :param failure_texts: 실패 텍스트 리스트
        :param pos_yes_btn: 성공 시 클릭할 좌표 (예: '예' 버튼)
        :return: 성공 여부 (True/False), 감지된 텍스트
        """
        
        # 성공 텍스트 감지
        for target_txt in success_texts:
            # 팝업 창의 텍스트가 포함되어 있는지 확인
            if target_txt in detected_text:
                logger.info(f"Success: Detected text contains success criteria. target_txt: {target_txt}")
                # 버튼 텍스트 유무 확인 (2차검증)
                yes_btn, no_btn = PopupManager.extract_text_and_buttons(detected_text)
                
                if yes_btn or no_btn:
                    logger.info(f"Success: Detected 'Yes' or 'No' button.")
                    time.sleep(1)
                    logger.info(f"Clicking 'Yes' button at {pos_yes_btn}.")
                    pyautogui.click(*pos_yes_btn)
                    return True, target_txt # 성공 텍스트 감지 시 True 반환
        
        # 실패 텍스트 감지
        for failure_txt in failure_texts:
            if failure_txt in detected_text:
                logger.error(f"Failure: Detected failure text: {failure_txt}")
                return False, failure_txt  # 실패 텍스트 감지 시 False 반환
            
        logger.info("No success or failure criteria met in detected text.")
        return False, None  # 성공 및 실패 텍스트를 모두 감지하지 못한 경우 False 반환

    
    #! 2차 검증 버튼 이미지 내 "예", "아니오", "확인" 등의 텍스트 유무 확인
    @staticmethod
    def extract_text_and_buttons(normalized_text):
        """ 정규화된 텍스트에서 버튼의 존재 여부를 확인 """
        # 예, 아니오, 확인 버튼 텍스트 존재 여부 확인
        yes_btn = "예" in normalized_text
        no_btn = "아니오" in normalized_text
        # confirm_btn = "확인" in normalized_text
        
        return yes_btn, no_btn
        

    @staticmethod
    def process_popup(master_mode, success_texts, failure_texts, pos_yes_btn, max_attempts=10, delay_between_attempts=0.5):
        """
        팝업 감지부터 버튼 클릭까지의 전체 프로세스
        :param success_texts: 성공 텍스트 리스트
        :param success_coords: 성공 시 클릭할 좌표 (예: '예' 버튼)
        :param max_attempts: 최대 시도 횟수
        :param delay_between_attempts: 시도 사이의 지연 시간 (초)
        :return: (성공 여부, 추출된 텍스트) 튜플
        """
        attempts = 0
        detected_text = ""  # 초기화

        while attempts < max_attempts:
            screenshot = PopupManager.take_screenshot()
            image_with_popup, popup_region = PopupManager.detect_popup(screenshot)
            
            if popup_region is not None:
                # 팝업창 영역에서 텍스트 추출
                detected_text = PopupManager.extract_text_from_popup(popup_region)
                print("추출된 텍스트:", detected_text)
                
                # 텍스트 분석 및 버튼 클릭
                success, matched_text = PopupManager.analyze_and_click(detected_text, success_texts, failure_texts, pos_yes_btn)
                
                # 성공 텍스트 감지 시 처리
                if success:
                    logger.info(f"Popup processed successfully on attempt {attempts + 1}.")
                    return True, matched_text  # 성공적으로 처리되었음을 반환
                
                if not success:
                    logger.info(f"실패텍스트 감지")
                    return False, matched_text  # 성공적으로 처리되었음을 반환


            else:
                logger.debug(f"Popup not detected on attempt {attempts + 1}")
                print("팝업창이 감지되지 않았습니다.")

            # 시도 후 지연 시간 대기
            attempts += 1
            time.sleep(delay_between_attempts)
        
            # 메모리 해제
            gc.collect() 
            

        # 모든 시도가 실패한 경우
        print(f"최대 {max_attempts}번 시도 후에도 팝업을 처리하지 못했습니다.")
        logger.error(f"{attempts}/{max_attempts} attempts failed: {detected_text}")

        return False, detected_text



