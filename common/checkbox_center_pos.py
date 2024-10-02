import pyautogui
import matplotlib.pyplot as plt
from PIL import Image
import cv2 
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
import numpy as np
import time
import sys
import os
import pyautogui
import pandas as pd

# 현재 파일의 디렉토리 기준으로 src 폴더 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(src_path)

# PathHelper import
from common.utils.path_utils import PathHelper
from common.utils.helper import PyAutoGuiHelper

def print_invoice_and_details(index_value_pairs):
            
            PyAutoGuiHelper.perform_click((328,522)) #328,522
            # 시작위치로 이동
            pyautogui.hotkey('shift', 'tab')

            time.sleep(1)
            current_index = 0 # 초기 시작 인덱스를 0으로 가정
            # 리스트의 총 개수만큼 반복
            for index, value in index_value_pairs: #12번 반복 (0~11)
                print(f"{index}")
                time.sleep(0.5) 

                # 현재 인덱스에서 목표 인덱스로 이동
                PyAutoGuiHelper.move_to_index(current_index, index)

                # 현재 체크박스를 체크
                pyautogui.press('space')
                time.sleep(0.5)

                current_index = index

            time.sleep(1)

index_value_pairs = [(0, 'K249P0000O81J'), (1, 'K249P0000O81K'), (2, 'K249P0000O81L'), (3, 'K249P0000O81M'), (4, 'K249P0000O81N'), (5, 'K249P0000O81O'), (6, 'K249P0000O81P'), (7, 'K249P0000O81Q'), (8, 'K249P0000O81R'), (9, 'K249P0000O81S'), (11, 'K249P0000O81T'), (12, 'K249P0000O81U')]
print_invoice_and_details(index_value_pairs)

# def print_invoice_and_details(total_count):
#     time.sleep(3)

#     # 모든 matches에 대해 작업이 완료된 후 거래명세서 발행 작업 수행
#     PyAutoGuiHelper.perform_click((328,522)) #328,522 # pallet 번호
#     time.sleep(0.5)
#     pyautogui.hotkey('shift', 'tab')

#     for i in range(total_count):
#         time.sleep(0.5)
 
#         pyautogui.press('space')
#         time.sleep(0.5)
        
#         # 현재 항목이 마지막이 아니라면 'down'키 눌러 다음 항목으로 포커스 이동
#         if i < total_count - 1:
#             pyautogui.press('down')
#             time.sleep(0.5)

    
# print_invoice_and_details(13)


# def excel_text():
#                 # 엑셀 아이콘 클릭
#             PyAutoGuiHelper.perform_click((1793,459)) 
            
#             PyAutoGuiHelper.perform_click((920,584))

#             # 로딩
#             time.sleep(5)

#             # [파일 디렉토리+파일이름+날짜+시간] 엑셀 저장
#             file_directory = PathHelper.get_abs_path('reports','직납직사급납품예약')
#             filename = PyAutoGuiHelper.generate_filename("직납_직사급_납품예약", "xlsx")
        
#             time.sleep(1)
#             reserv_filepath = os.path.join(file_directory, filename)

#             time.sleep(1)
#             PyAutoGuiHelper.save_file_with_name(reserv_filepath)

#             # 파일 저장중........
#             time.sleep(5)   

#             # 파일 존재 확인
#             if not os.path.exists(reserv_filepath):
#                 time.sleep(1) 
#                 return False, f"Excel file not found at: {reserv_filepath}"

#             #! 엑셀파일 읽어서 행 갯수 구하기
#             df = pd.read_excel(reserv_filepath, header=0, engine='openpyxl')
#             print(f"엑셀데이터: \n{df}")
            
#             #! palle번호 열에서 중복된 인덱스 제거
#             unique_df = df.drop_duplicates(subset=['Pallet번호'], keep='first')
#             print(f"Unique rows based on Pallet번호 obtained: {len(unique_df)}")
            
            
#             # 고유한 인덱스와 Pallet번호 값을 튜플로 묶어 리스트 생성
#             unique_indices = unique_df.index.tolist()
#             unique_pallet_numbers = unique_df['Pallet번호'].tolist()

#             # 인덱스와 Pallet번호 값을 튜플로 묶기
#             index_value_pairs = list(zip(unique_indices, unique_pallet_numbers))
#             print(f"Index-Value pairs of unique Pallet번호: {index_value_pairs}")

# def process(loop_cnt):
#     current_index = 0 # 시작인덱스 초기화
#     loop_index = 9
#     while loop_index < loop_cnt:
#                 print(f"loop index: {loop_index}")
#                 time.sleep(1)
#                 # 시작위치로 이동 (첫번째 pallet번호 셀 중심)
#                 # PyAutoGuiHelper.perform_click(step.pos_start)
#                 PyAutoGuiHelper.perform_click((325, 524)) 
                
#                 # 현재 인덱스에서 목표 인덱스로 이동
#                 PyAutoGuiHelper.move_to_index(current_index, index)
                
#                 # 체크박스로 이동
#                 pyautogui.hotkey('shift', 'tab')
    
#                 time.sleep(1)
                
#                 start_pallet_pos = (325, 524)
#                 # 해당 행의 체크박스 처리
#                 checked = check_checkbox_state(current_index, start_pallet_pos)
                
#                 if checked:
#                     # 체크박스가 체크된 상태
#                     index += 2 
#                 else:
#                     # 체크박스가 체크되지 않은 상태
#                     pyautogui.press('space')
#                     index += 1
                    
#                 time.sleep(1)


# def check_checkbox_state(row_index, start_pallet_pos):
        
#         # 현재 행의 pallet번호 중심 좌표 계산 
#         pallet_center_x = start_pallet_pos[0]
#         pallet_center_y = start_pallet_pos[1] + row_index * 22 # y 좌표만 인덱스와 높이로 계산
#         print(f"현재 셀의 좌표: {(pallet_center_x, pallet_center_y)}")
        
#         # 현재 행의 체크박스의 중심 좌표 계산
#         checkbox_center_x = pallet_center_x - 62
#         checkbox_center_y = pallet_center_y
        
#         # 로그로 좌표 확인
#         print(f"Calculated Checkbox Center: ({checkbox_center_x}, {checkbox_center_y})")
#         # 체크박스 영역 정의 (체크박스 전체를 포함하도록 설정)
#         checkbox_region = (
#             int(checkbox_center_x - 11),  # 중심에서 좌측 상단으로 이동
#             int(checkbox_center_y - 11.5),  # 중심에서 좌측 상단으로 이동
#             22,  # 체크박스의 너비
#             23  # 체크박스의 높이
#         )
        
#         time.sleep(1)
        
#         # 체크박스 위치에서 스크린샷 캡처
#         screenshot = pyautogui.screenshot(region=checkbox_region)
#         # 스크린샷을 즉시 화면에 표시
#         screenshot_np = np.array(screenshot)
#         plt.imshow(screenshot_np)
#         plt.title(f"Checkbox Screenshot at Row {row_index}")
#         plt.axis('off')
#         plt.show()
#         print(f"Step: Saved screenshot of checkbox at row {row_index}")

#         time.sleep(1)
        
#         # 체크된 상태와 체크되지 않은 상태의 이미지 비교를 통해 상태 확인
#         checkbox_images = PathHelper.get_image_path('checkbox_state_image')
#         if checkbox_images and isinstance(checkbox_images, list) and len(checkbox_images) >= 2:
#             unchecked_image = cv2.imread(checkbox_images[0], cv2.IMREAD_GRAYSCALE)
#             checked_image = cv2.imread(checkbox_images[1], cv2.IMREAD_GRAYSCALE)

#             print(f"Images loaded successfully: {checkbox_images}")
            
            
#             # 스크린샷을 GRAYSCALE로 변환
#             screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

#             # 템플릿 매칭으로 유사도 비교
#             result_checked = cv2.matchTemplate(screenshot_cv, checked_image, cv2.TM_CCOEFF_NORMED)
#             result_unchecked = cv2.matchTemplate(screenshot_cv, unchecked_image, cv2.TM_CCOEFF_NORMED)

#             max_val_checked = cv2.minMaxLoc(result_checked)[1]
#             max_val_unchecked = cv2.minMaxLoc(result_unchecked)[1]

#             print(f"Max similarity checked: {max_val_checked}, unchecked: {max_val_unchecked}")

#             # 유사도가 0.8 이상일 경우 체크된 것으로 간주
#             if max_val_checked > 0.8:
#                 print(f"체크박스가 체크된 상태입니다.")
#                 return True
#             elif max_val_unchecked > 0.8:
#                 print(f"체크박스가 체크되지 않은 상태입니다.")
#                 return False
#             else:
#                 print(f"체크박스 상태를 확인할 수 없습니다.")
#                 return False

#         else:
#             print(f"이미지 경로 로드 실패 또는 이미지 파일 부족")
#             return False

# def get_center_position():
#     # 첫번째 PALLET번호 셀 중심
#     pyautogui.moveTo(325.5, 524.5)
#     pyautogui.click()
    
#     # # 첫번째 체크박스 셀 중심
#     pyautogui.moveTo(264.0, 524.5)
#     pyautogui.click()


#     print("셀의 좌측 상단 위치를 마우스로 가리키고 Enter를 누르세요.")
#     keyboard.wait('enter')
#     pos = pyautogui.position()  # 현재 마우스 위치 가져오기
#     print(f"좌표: {pos}")

#     # 예를 들어, Pallet번호 셀의 너비가 101, 높이가 20-21이라면:
#     # pallet번호 w*h
#     # width = 101
#     # height = 23

#     # 체크박스 w*h
#     width = 22
#     height = 23
#     # 평균 높이 사용

#     # 중심 좌표 계산
#     center_x = pos[0] + width / 2
#     center_y = pos[1] + height / 2
#     print(f"중심 좌표: ({center_x}, {center_y})")

# # 실행 코드
# excel_text()
# # pallet_cnt = 12
# # loop_cnt = pallet_cnt
# # process(loop_cnt)
# # check_checkbox_state()
# # get_center_position()


# #! 여기 확인!!
# def check_checkbox_state(self, row_index, start_pallet_pos):
        
#         # 현재 행의 pallet번호 중심 좌표 계산 
#         pallet_center_x = start_pallet_pos[0]
#         pallet_center_y = start_pallet_pos[1] + row_index * 22 # y 좌표만 인덱스와 높이로 계산

#         # 현재 행의 체크박스의 중심 좌표 계산
#         checkbox_center_x = pallet_center_x - 62
#         checkbox_center_y = pallet_center_y
        
#             # 로그로 좌표 확인
#         self.logger.debug(f"Calculated Checkbox Center: ({checkbox_center_x}, {checkbox_center_y})")
        
#         # 체크박스 영역 정의 (체크박스 전체를 포함하도록 설정)
#         checkbox_region = (
#             int(checkbox_center_x - 11),  # 중심에서 좌측 상단으로 이동
#             int(checkbox_center_y - 11.5),  # 중심에서 좌측 상단으로 이동
#             22,  # 체크박스의 너비
#             23  # 체크박스의 높이
#         )
        
#         try: 
#             # 체크박스 위치에서 스크린샷 캡처
#             screenshot = pyautogui.screenshot(region=checkbox_region)
#             # 스크린샷을 즉시 화면에 표시
#             screenshot_np = np.array(screenshot)
#             plt.imshow(screenshot_np)
#             plt.title(f"Checkbox Screenshot at Row {row_index}")
#             plt.axis('off')
#             plt.show()
#             self.logger.debug(f"Step: Saved screenshot of checkbox at row {row_index}")
            
#             # 체크된 상태와 체크되지 않은 상태의 이미지 비교를 통해 상태 확인
#             checkbox_images = PathHelper.get_image_path('checkbox_state_image')
#             if checkbox_images and isinstance(checkbox_images, list) and len(checkbox_images) >= 2:
#                 unchecked_image = cv2.imread(checkbox_images[0], cv2.IMREAD_GRAYSCALE)
#                 checked_image = cv2.imread(checkbox_images[1], cv2.IMREAD_GRAYSCALE)
#                 self.logger.debug(f"Images loaded successfully: {checkbox_images}")
                
#                 # 스크린샷을 GRAYSCALE로 변환
#                 screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

#                 # 템플릿 매칭으로 유사도 비교
#                 result_checked = cv2.matchTemplate(screenshot_cv, checked_image, cv2.TM_CCOEFF_NORMED)
#                 result_unchecked = cv2.matchTemplate(screenshot_cv, unchecked_image, cv2.TM_CCOEFF_NORMED)

#                 max_val_checked = cv2.minMaxLoc(result_checked)[1]
#                 max_val_unchecked = cv2.minMaxLoc(result_unchecked)[1]

#                 self.logger.debug(f"Max similarity checked: {max_val_checked}, unchecked: {max_val_unchecked}")

#                 # 유사도가 0.8 이상일 경우 체크된 것으로 간주
#                 if max_val_checked > 0.8:
#                     self.logger.info("체크박스가 체크된 상태입니다.")
#                     return True
#                 elif max_val_unchecked > 0.8:
#                     self.logger.debug("체크박스가 체크되지 않은 상태입니다.")
#                     return False
#                 else:
#                     self.logger.debug("체크박스 상태를 확인할 수 없습니다.")
#                     return False

#             else:
#                 self.logger.error("이미지 경로 로드 실패 또는 이미지 파일 부족")
#                 return False

#         except Exception as e:
#             error_message = f"reserve_delivery failed: {str(e)}"
#             self.logger.error(error_message)
#             return False, error_message  # 작업이 실패한 경우 False와 오류 메시지 반환
