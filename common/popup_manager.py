import time
import cv2
import pyautogui
import numpy as np
import pytesseract
import gc

from common.utils.ocr_utils import OCRUtils
from common.logger_manager import LoggerManager

# 로거 설정
logger = LoggerManager.get_logger(__name__)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class PopupManager:
    
    # 캐시 저장소
    cache = {}
    
    @staticmethod    
    # 스크린샷을 찍고 이미지로 변환
    def take_screenshot():
        try:
            # 스크린샷을 찍는다
            screenshot = pyautogui.screenshot()
            
            if screenshot is None:
                raise ValueError("Failed to take screenshot: Screenshot is None.")
            
            # 스크린샷을 numpy 배열로 변환
            screenshot_np = np.array(screenshot)
            
            # 변환된 numpy 배열이 비어있는지 확인
            if screenshot_np.size == 0:
                raise ValueError("The screenshot is empty or not captured correctly.")
            
            # 스크린샷을 OpenCV 이미지로 변환
            screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            return screenshot_bgr
        
        except Exception as e:
            print(f"An error occurred while taking screenshot: {e}")
            raise
    
    @staticmethod    
    # 특정 영역에서 팝업창을 감지하는 함수
    def detect_popup_in_region(image, region=None):
        """
        특정 영역에서 팝업창을 감지하는 함수.
        region 인자가 주어지지 않으면 디폴트 영역을 사용함.
        region: (x_start, y_start, x_end, y_end)
        """
        
        if region is None:
            # 팝업창이 자주 나타나는 디폴트 영역
            region = (800, 450, 1350, 650)
        
        region_x_start, region_y_start, region_x_end, region_y_end = region
        
        # 해당 영역을 추출
        region_of_interest = image[region_y_start:region_y_end, region_x_start:region_x_end]
        
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
            x += region_x_start
            y += region_y_start
            
            # 팝업창 영역에 사각형 그리기 (디버깅용)
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # 팝업 영역만 잘라서 반환
            popup_region = image[y:y+h, x:x+w]
            
            return image, popup_region
        else:
            print("팝업창을 찾을 수 없습니다.")
            return image, None
        
    @staticmethod    
    # OCR을 통해 텍스트를 추출하는 함수
    def extract_text_from_popup(popup_region):
        
        # 캐시 키 생성 (이미지 해시를 사용)
        hash_value = hash(popup_region.tobytes())
        
        # 캐시에 저장된 텍스트가 있으면 사용
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
        detected_text = pytesseract.image_to_string(enlarged_image, lang='kor+eng', config=custom_config)
        return detected_text
    
    @staticmethod
    def analyze_and_click(region_popup_btn, text, success_texts, failure_texts):
        """추출된 텍스트를 분석하여 성공/실패 여부 판단 및 버튼 클릭"""
        # 성공 텍스트들이 모두 포함되어 있는지 확인
        if all(success_text in text for success_text in success_texts):
            print("성공: 버튼을 클릭합니다.")
            OCRUtils.find_and_click_confirm_btn(region_popup_btn)
            return True
        
        # 실패 텍스트가 하나라도 포함된 경우 즉시 실패로 간주
        elif any(failure_text in text for failure_text in failure_texts):
            print("실패 텍스트 감지: 재시도 중...")
            return False
        
        else:
            print("결과를 알 수 없습니다.")
            return False
    
    @staticmethod
    def detect_popup_proc(region_popup_btn, success_texts, failure_texts, max_attempts=10, region=None):
        
        attempts = 0
        detected_text = ""  # 초기화
        
        while attempts < max_attempts:
            
            screenshot = PopupManager.take_screenshot()
            # image_with_popup, popup_region = PopupManager.detect_popup_in_region(screenshot, region=region)
            popup_region = PopupManager.detect_popup_in_region(screenshot, region=region)
            
            if popup_region is not None:
                #?#?#?#?#?#?#?#? 디버깅용 #?#?#?#?#?#?#?#?#?#?#?#?
                # # 팝업창이 감지된 전체 화면을 표시
                # cv2.imshow("Detected Popup", image_with_popup)
                # # 'q' 키를 누르면 창이 닫힙니다.
                # while True:
                #     if cv2.waitKey(1) & 0xFF == ord('q'):
                #         break
                # cv2.destroyAllWindows()
                #?#?#?#?#?#?#?#?#?#?#?#?#?#?#?#?#?#?#?#?#?#?#?#?#?#
                
                # 팝업창 영역에서 텍스트 추출
                detected_text = PopupManager.extract_text_from_popup(popup_region)
                logger.debug(f"Extracted text: {detected_text.strip()}")
                print("추출된 텍스트:", detected_text)
                
                # 텍스트 분석 및 버튼 클릭 시도
                if PopupManager.analyze_and_click(region_popup_btn, detected_text, success_texts, failure_texts):
                    return True, detected_text  # 성공 시 True와 추출된 텍스트 반환
            
            else:
                logger.debug(f"Popup not detected on attempt {attempts + 1}")
            
            attempts += 1
            time.sleep(0.5)
        
            # 시도 후 메모리 해제
            gc.collect()
        
        # 실패하거나 텍스트가 감지되지 않으면 False 반환
        logger.error(f"{attempts}/{max_attempts} attempts failed: {detected_text}")
        print(f"{attempts}/{max_attempts} 시도 후 실패: {detected_text}")
        return False, detected_text

    #?#######################################################################################################################  
    @staticmethod
    def detect_and_close_popup(close_button_image, region=None, max_attempts=5, sleep_time=0.5):
        """
        화면에서 특정 닫기 버튼을 감지하고 클릭하는 메서드
        - 최대 max_attempts 번 시도
        - target_closes 횟수만큼 팝업을 성공적으로 닫으면 종료
        - target_closes에 도달하지 않아도 실패로 간주하지 않음
        """
        attempts = 0  # 시도 횟수 초기화
        successful_closes = 0  # 성공적으로 닫은 팝업 수

        while attempts < max_attempts:
            try:
                # 닫기 버튼을 감지
                button_location = pyautogui.locateOnScreen(close_button_image, confidence=0.7, region=region)

                if button_location is not None:
                    logger.info(f"Attempt {attempts + 1}: Popup detected!")
                    button_point = pyautogui.center(button_location) # 닫기 버튼의 중앙으로 마우스를 이동하고 클릭합니다
                    pyautogui.click(button_point)
                    logger.info(f"Popup closed! ({successful_closes + 1})")
                    successful_closes += 1  # 성공적으로 닫기 버튼을 클릭한 경우 카운트 증가
                    time.sleep(1)  # 팝업이 다시 뜨는 것을 방지하기 위해 잠시 대기
                    attempts = 0  # 닫기 버튼을 찾았으므로 시도 횟수 초기화

                else:
                    attempts += 1
                    logger.debug(f"Attempt {attempts}: Popup not detected. Retrying...")

                time.sleep(sleep_time)  # 짧은 간격으로 반복 실행

            except Exception as e:
                # logger.error(f"Error occurred: {e}")
                attempts += 1  # 오류 발생 시에도 시도 횟수는 증가시킵니다.
                time.sleep(sleep_time)

        if successful_closes == 0:
            logger.error(f"{max_attempts}번 시도 후에도 팝업을 닫지 못했습니다.")
            return False, f"No popups closed after {max_attempts} attempts"
        
        logger.info(f"최대 시도 횟수에 도달했습니다. 총 닫은 팝업 수: {successful_closes}")
        return True, f"Popup detection finished. Total popups closed: {successful_closes}."

    @staticmethod
    def detect_and_handle_popup_with_ocr(master_mode, region_popup, region_btn, target_texts, failure_texts, max_attempts):
        """ 
        특정 위치에서 팝업 창이 감지되었는지 확인하고
        OCR을 통해 텍스트를 추출하여 프로세스 성공 여부 판단 
        
        return : True/ False , 명시적인 오류 메시지를 반환
        
        사용 로직 
        - 로그인 팝업 감지
        - pallet 생성
        
        """
        attempt = 0
        popup_handled = False
        
        while attempt < max_attempts and not popup_handled:
            attempt += 1
            
            screenshot  = OCRUtils.capture_screen(region_popup)
            if screenshot  is not None:
                logger.info(f"Attempt {attempt}/{max_attempts}: Screenshot captured successfully.")
                
                # 실패 텍스트 감지
                detected_failure_text, failure_detected  = OCRUtils.detect_popup_txt(screenshot, failure_texts)
                if failure_detected:
                    error_message = f"Popup handling failed: '{detected_failure_text}' text detected in the popup."
                    logger.error(error_message)
                    return False, error_message # 실패 텍스트가 발견되면 False와 오류 메시지 반환
                    
                # 성공 텍스트 감지
                detected_text, success_detected = OCRUtils.detect_popup_txt(screenshot, target_texts)
                if success_detected:
                    logger.info(f"Popup detected with texts: {detected_text}")
                    OCRUtils.find_and_click_confirm_btn(region_btn)
                    popup_handled = True
                    break
                else:
                    logger.info("Popup text not detected.")
            else:
                logger.error("Failed to capture screenshot.")
            
        time.sleep(0.5) # 0.5초 간격으로 재시도
        
        # 시도 후 메모리 해제
        gc.collect()
        
        if not popup_handled:
            if master_mode:
                logger.info(f"Popup detection failed, clicking fallback coordinates.")
                time.sleep(1)
                OCRUtils.find_and_click_confirm_btn(region_btn)
                time.sleep(1)
            else:
                error_message = "Failed to detect or handle popup after maximum attempts."
                logger.error(error_message)
                return False, error_message # 실패 시 False와 오류 메시지 반환
        
        return True, "Popup handled successfully"

    @staticmethod
    def detect_popup(region_popup, region_confirm_btn, max_attempts):
        """ 단순히 특정 위치에서 팝업 감지 및 버튼 클릭 """
        attempt = 0
        popup_handled = False
        
        while attempt < max_attempts and not popup_handled:
            attempt += 1
            
            logger.info(f"Attempting to detect popup, attempt {attempt}")
            
            if OCRUtils.detect_popup_in_region(region_popup):
                logger.info("Popup detected successfully")
                time.sleep(1)
                OCRUtils.find_and_click_confirm_btn(region_confirm_btn)
                popup_handled = True
                break
            
            time.sleep(0.1) # 0.1초 간격으로 재시도
            
        if not popup_handled:
            logger.error("Failed to detect or close popup after maximum attempts.")
            raise Exception("Failed to detect or close popup.")
        
        logger.info("Popup closed successfully.")
        return popup_handled