import pyautogui
import cv2
import numpy as np
import time
import pytesseract

from common.logger_manager import LoggerManager
from common.utils.pre_processing import ImageProcessing

# 로거 설정
logger = LoggerManager.get_logger(__name__)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class OCRUtils:
    @staticmethod
    def take_screenshot(region=None):
        screenshot = pyautogui.screenshot(region=region)
        screenshot = np.array(screenshot)  # PIL 이미지를 numpy 배열로 변환
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)  # 색상 변환
        return screenshot

    
    @staticmethod
    def detect_popup_txt(screenshot, target_txts) :
        """+======================================      
        OCR로 팝업 이미지의 텍스트를 인식하고, target_txt가 포함되어 있는지 확인하는 함수.
        
        :param screenshot: OCR 대상 이미지
        :param target_txt: 찾고자 하는 텍스트
        :return: 감지된 텍스트가 있으면 해당 텍스트, 없으면 None
        ========================================+"""
        try:
            # 이미지 전처리
            processed_image = ImageProcessing.preprocess_image(screenshot)
            logger.info(" 이미지 전처리 완료 ")
            
            time.sleep(1)
            
            # OCR 설정 최적화 / OCR로 텍스트 출력
            custom_oem_psm_config = r'--oem 3 --psm 6'
            result  = pytesseract.image_to_string(processed_image, config=custom_oem_psm_config, lang='kor+eng')
            logger.info(f"OCR로 인식한 텍스트: {result}")
            
            # 타겟 텍스트 감지
            for target_txt in target_txts:
                # 팝업 창의 텍스트가 포함되어 있는지 확인
                if target_txt in result :
                    logger.info("타겟 텍스트 발견: %s", target_txt)
                    return target_txt, True  # 감지된 텍스트와 True 반환
                    
            logger.info("타겟 텍스트 미발견")
            return None, False # 감지된 텍스트가 없으면 None 반환
                
        except Exception as e:
            logger.error("Error during OCR processing: %s",str(e))
            return None, False # 예외가 발생한 경우에도 None 반환
    
    @staticmethod
    def capture_screen(region = None) :
        """ ============================================================================
        주어진 영역(region)을 캡처하고, BGR 형식으로 변환하는 함수.
        
        :param region: 캡처할 영역의 좌표와 크기  (x, y, width, height) 형태의 튜플
        :return: BGR 형식의 이미지
        ============================================================================ """
        try:
        
            screenshot = pyautogui.screenshot(region = region)
            # RGB 배열을 numpy 배열로 변환
            img = np.array(screenshot)
            
            # BGR 형식으로 변환
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            logger.info("스크린샷을 BGR로 변환 완료")
            
            # # 캡처한 이미지 저장
            # cv2.imwrite("captured_image.png", img_bgr)
            # # 캡처한 이미지 표시
            # cv2.imshow("Captured Image", img_bgr)
            # cv2.waitKey(0)  # 키 입력을 기다림
            # cv2.destroyAllWindows()  # 모든 창 닫기
            
            # 해상도 조정
            img_bgr = ImageProcessing.adjust_resolution(img_bgr)
            
            return img_bgr
        
        except Exception as e:
            logger.error("화면 캡처 중 오류 발생: %s", str(e))
            return None
    
    @staticmethod
    def detect_popup_in_region(region):
        """+======================================  
        주어진 영역에서 팝업(popup)이 존재하는지 판단하는 함수.
        
        :param region: 캡처할 영역의 좌표와 크기  (x, y, width, height) 형태의 튜플
        :return: True: 팝업 존재, False: 팝업 없음
        ======================================+"""   
        screenshot = OCRUtils.capture_screen(region=region)
        txt = pytesseract.image_to_string(screenshot, lang='kor+eng')
        return bool(txt.strip())
    


    @staticmethod
    def find_and_click_confirm_btn(region):
        """+==========================================
        창 내에서 특정 버튼을 찾아 클리릭하는 함수.
        :param region: 버튼의 x, y, width, height
        :return: None
        ===========================================+"""
        try:
            # region이 (x, y, width, height) 형식인지 확인
            if len(region) == 4 and region[2] > 0 and region[3] > 0:
                # 중심 좌표 계산
                x_center = region[0] + region[2] // 2
                y_center = region[1] + region[3] // 2
                
                # 중심 좌표로 이동 및 클릭
                pyautogui.moveTo(x_center, y_center)
                pyautogui.click(x_center, y_center)
                
                logger.info("확인 버튼 클릭됨: x=%d, y=%d", x_center, y_center)
            else:
                raise ValueError("region의 width와 height는 양수여야 합니다.")
        except Exception as e:
            logger.error("확인 버튼을 클릭하는 동안 오류 발생: %s", str(e))
            
            
    # @staticmethod
    # def extract_number_from_txt(x, y, width, height):
    #     region = (x, y, width, height)
    #     attempt = 0
    #     max_attempts = 5
    #     extract_handled = False
        
    #     while attempt < max_attempts and not extract_handled:
    #         attempt += 1
            
    #         # 캡처된 이미지
    #         screenshot = OCRUtils.take_screenshot(region)
        
    #         if screenshot is not None:
    #             # 이미지 전처리
    #             processed_image = ImageProcessing.txt_preprocess_image(screenshot)
                
    #             # OCR을 사용하여 텍스트 추출
    #             custom_oem_psm_config = r'--oem 3 --psm 6'
    #             ocr_text = pytesseract.image_to_string(processed_image, config=custom_oem_psm_config, lang='kor')
    #             logger.info(f"OCR 텍스트 추출 결과: {ocr_text}")
                
    #             # "건"이라는 단어가 포함된 문자열에서 그 앞에 위치한 숫자 추출
    #             match = re.search(r'(\d+)\s*건', ocr_text)
    #             if match:
    #                 extracted_number = int(match.group(1))  # 첫 번째 그룹이 숫자를 포함
    #                 logger.info(f"추출된 숫자: {extracted_number}")
                    
    #                 extract_handled = True
    #                 return extracted_number
    #             else:
    #                 logger.info("숫자를 찾을 수 없습니다.")
    #         else:
    #             logger.error("스크린샷을 캡처하지 못했습니다.")
            
    #         time.sleep(0.1)  # 0.1초 간격으로 재시도
        
    #     if not extract_handled:
    #         logger.error("숫자 추출에 실패했습니다.")
    #         raise Exception("숫자 추출에 실패했습니다.")  