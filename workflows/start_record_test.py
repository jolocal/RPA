import json
import os
import sys

# 루트 디렉토리 경로 설정 (src 경로로 설정)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(root_dir)

from workflows.start_record import execute_start_record
from common.logger_manager import LoggerManager
from common.utils.path_utils import PathHelper

def main():
    # 설정 파일 로드
    PathHelper.load_config()
    logger = LoggerManager.get_logger(__name__)
    
    # 테스트용 JSON 데이터 생성
    test_data = {
        "contexts": {
            "step_1": {
                "task": "start_recording",
                "bdcam_path": r"C:\Program Files\Bandicam\bdcam.exe",  # 필요한 경우 경로 변경
                "record_key": "f12"  # 필요한 경우 다른 키로 변경 가능
            }
        }
    }
    
    # JSON 데이터를 문자열로 변환
    json_data = json.dumps(test_data)
    
    try:
        logger.info("반디캠 실행 및 녹화 시작 테스트를 시작합니다.")
        print("반디캠 실행 및 녹화 시작 테스트를 시작합니다.")
        
        # execute_sg_start_record 함수 실행
        result = execute_start_record(json_data)
        
        # 결과 출력
        logger.info(f"테스트 결과: {result}")
        print(f"테스트 결과: {result}")
        
    except Exception as e:
        logger.error(f"테스트 중 오류 발생: {str(e)}")
        print(f"테스트 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()
