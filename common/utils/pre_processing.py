import cv2
import numpy as np
from matplotlib import pyplot as plt
import pytesseract
from common.logger_manager import LoggerManager
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# 로거 설정
logger = LoggerManager.get_logger(__name__)

class ImageProcessing:
    @staticmethod
    def preprocess_image(screenshot) :
        """ =======================
        OCR을 위한 이미지 전처리
        - 그레이스케일 변환
        - 대비 
        - 이진화
        - 노이즈 제거
        ======================= """
        try:
            logger.info("이미지 전처리 시작")
            
            # 그레이스케일 변환
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            logger.info("이미지를 그레이스케일 변환 완료")

            # 대비를 높이기 위해 CLAHE 적용
            clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(8, 8))
            cl1 = clahe.apply(gray)
            logger.info("CLAHE 적용 완료")

            # 이진화
            _, binary = cv2.threshold(cl1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            logger.info("이진화 완료")

            # 모폴로지 연산 (노이즈 제거)
            kernel = np.ones((1, 1), np.uint8)
            morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            logger.info("모폴로지 연산 완료")

            # # 전처리된 이미지 저장 및 표시 (디버깅용)
            # cv2.imwrite("preprocessed_image.png", morph)
            # cv2.imshow("Preprocessed Image", morph)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            
            return morph
        except Exception as e:
            logger.error("이미지 전처리 중 오류 발생: %s", str(e))
            return None
        
    def adjust_resolution(image, min_height=600, min_width=600):
        """이미지의 해상도를 확인하고, 최소 해상도에 맞추어 조정하는 함수."""
        height, width = image.shape[:2]
        if height < min_height or width < min_width:
            scale = max(min_height / height, min_width / width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
            logger.info(f"이미지 해상도를 {new_width}x{new_height}로 조정 완료")
            return resized_image
        return image

    @staticmethod
    def txt_preprocess_image(image):
        try:
            # 그레이스케일 변환
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # # 이미지 리사이즈 (더 크게 확대)
            height, width = gray.shape[:2]
            scale_factor = 3
            gray = cv2.resize(gray, (width * scale_factor, height * scale_factor), interpolation=cv2.INTER_LINEAR)
            
            # 이진화
            _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
            
            # 팽창 (Dilation) - 글씨를 더 굵게
            kernel = np.ones((2, 2), np.uint8)
            dilated = cv2.dilate(binary, kernel, iterations=1)
            
            # 컨트라스트 조정
            alpha = 2.0  # Contrast control (1.0-3.0)
            beta = 0     # Brightness control (-100 to 100)
            adjusted = cv2.convertScaleAbs(dilated, alpha=alpha, beta=beta)
            
            # 노이즈 제거
            kernel = np.ones((1, 1), np.uint8)
            processed_image = cv2.morphologyEx(adjusted, cv2.MORPH_CLOSE, kernel)
            
            # 샤프닝 필터 적용
            sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            processed_image = cv2.filter2D(processed_image, -1, sharpen_kernel)
            
            # 중간 블러 적용
            processed_image = cv2.medianBlur(processed_image, 3)
            
            # # 전처리된 이미지 저장 (디버깅 용도)
            # cv2.imwrite('processed_image.png', processed_image)
            
            # # 전처리된 이미지 출력
            # plt.figure(figsize=(10, 10))
            # plt.imshow(processed_image, cmap='gray')
            # plt.title('Processed Image')
            # plt.axis('off')
            # plt.show()
            
            return processed_image
        except Exception as e:
            logger.error(f"텍스트 전처리 중 오류 발생: {str(e)}")
            raise