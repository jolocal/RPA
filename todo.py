# 1. OCR 인식X 문제 해결 - 환경변수?
# 2. PALLET 생성 X 케이스
# - 이미 생성된 PALLET 번호 입니다.
# 3. 경로 지정 자동화 구현
# 4. time.sleep 줄이기
# 5. 파이썬 에러발생시 스크립트 종료
# 6. 강제종료 트리거 - 특정 버튼을 누르면 강제 종료
# 7. 중앙창고 파라미터 정리
# - 승인 전 
# - 승인 후


#? 수정사항
#? 1. 예외를 execute_task 에서 관리
#?    하위 메서드에서 예외가 발생하면 execute_task에서 처리함
#?    이후, execute_sg_start_login에서 응답을 랩뷰에게 수신하고 프로그램 강제 종료

#? 2. 동적 경로 모듈 추가 (from common.utils import get_abs_path)
#?    절대경로(C:\work\RPA_python3.7_20240824) / config.json
#?    주어진 경로 부분들을 조합하여 절대 경로를 반환하는 함수.
#?    설정 파일로 설정된 루트 디렉토리를 기준으로 동작합니다.


# 2024/08/30
# config.json 파일에 여러 이미지 경로를 설정하고, 필요할 때마다 동적으로 사용할 수 있도록 수정했습니다.
# PathHelper 클래스를 통해 config.json에서 특정 이미지 경로를 가져올 수 있습니다.
# LoadingIconManager 클래스에서 동적으로 여러 이미지 경로를 사용해 테이블 로드 여부를 판단할 수 있습니다.

#20240831
# sciprt_4 파라미터 정리
# script_3 엑셀 읽을때 시트 인덱스 확인하기
# 1. 예약리스트 PO와 S-GIPS 데이터 불일치로 인한 테스트 불가능
# 상황: 새로 받은 예약리스트의 PO 번호가 S-GIPS 데이터와 일치하지 않아 테스트를 진행할 수 없었음.
# 해결 방안: 배포 환경에서 사용되는 예약리스트는 자재번호가 누락되지 않고, PALLET이 생성되었으며, 납품예약 거래명세서 출력이 완료된 완전한 데이터여야 함.

# 2. 오류 원인:
# Tesseract 미설치 및 시스템 환경변수 설정 문제: Tesseract가 설치되지 않았고, 시스템 환경변수 설정이 제대로 되어 있지 않아 발생한 문제로 확인됨.
# 추가 문제: 납품예약리스트의 PO 번호가 이미 PALLET 생성, 납품예약, 거래명세서 출력 등이 완료된 상태일 경우 테스트를 진행하기 어려움.

# script_2
# inbound_data 입력 시 tab으로 이동후 20240830 을 타이핑 함 -> 끝자리까지 모두 타이핑하지 않음
# tab으로 이동후 복사붙여넣기 방식 사용

# 팝업창 감지 로직
# 팝업창의 위치와 크기를 자동으로 감지하고, 해당 영역만을 대상으로 ocr을 수행
# ocr로 텍스트 추출시 일부 텍스트를 기반이 인식하는데에 더 유연함.

# 변경 사항:

# 성공 처리:
# execute_task 함수 내부에서 작업이 성공적으로 완료된 경우, self.res.add_contexts를 통해 성공 응답을 생성하여 LabVIEW에 전달합니다.
# 예외 처리:
# execute_task 함수와 execute_hn_delv_proc 함수에서 예외가 발생하면, 해당 예외를 처리하고 LabVIEW에 예외 발생 정보를 응답합니다. 이후, 10초 대기 후 스크립트를 종료하도록 설계되었습니다.
# 실패 처리 로직 추가:
# 팝업 처리 실패 시(PopupManager.detect_popup_proc의 반환 값이 False일 경우), 실패 로그를 기록하고 self.res.add_contexts를 통해 실패 응답을 생성하여 LabVIEW에 전달합니다.
# 실패 시에도 성공 처리와 마찬가지로 10초 대기 후 스크립트를 종료하도록 로직을 변경했습니다.


20240901
# task_map에서 호출되는 각 함수에서 성공여부와 메시지를 반환하도록 변경
# 작업함수가 실패할 경우 success = False와 함께 실패 메시지 반환

# 실패 시 즉시 반환
# task_map에서 반환된 결과를 확인하여 실패한 경우 즉시 실패 메시지를 반환하고, 스크립트를 중단
# 성공한 경우에는 None을 반환하여 이후 스텝이 계속 실행되도록 합니다.
# 예외 발생 시 handle_task_exception 메서드가 호출되며, 예외 메시지를 반환합니다

20240902

# success_texts = ["하시겠습니까?"] 

# success, detected_text = PopupManager.process_popup(
#                             success_texts,
#                             step.pos_yes_btn
#                         )
# if success:
#     self.logger.info(f"Step {step_num}: 팝업 처리 성공 - 텍스트: {detected_text}.")

# else:
#     self.logger.warning(f"Step {step_num}: 팝업 처리 실패 - 텍스트: {detected_text}.")
#     self.logger.info(f"Step {step_num}: 팝업 처리 실패 - 텍스트: {detected_text}. / yes btn 클릭")
#     PyAutoGuiHelper.perform_click(step.pos_yes_btn)

20240903
# popup처리:
#     1.단일 텍스트라도 감지되면 즉시 성공으로 판단
#     2.OCR이 자주 잘못 인식하는 특정 패턴을 식별하고, 이를 보정하는 규칙을 적용 ("히터생성"을 "Pallet 생성"으로 정규화)
#     3.2차검증: 성공 팝업의 경우 "예"와 "아니오"버튼이 있으며, 실패 팝업의 경우 "확인" 버튼이 있음 이 버튼의 존재 여부를 확인함으로써 2차 검증을 수행