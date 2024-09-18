import json
from datetime import datetime
import pytz

class ResponseManager:
    def __init__(self):
        self.response = {
            "type":"response",
            "status":"completed",
            "timestamp": datetime.now(pytz.timezone('Asia/Seoul')).replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S'),
            "contexts": []
        }
    def add_contexts(self, step_num, task_name, status, msg, result=None):
        contexts = {
            "step": step_num,
            "task": task_name,
            "status": status,
            "msg": msg,
            "timestamp": datetime.now(pytz.timezone('Asia/Seoul')).replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
        }
        if result is not None:
            contexts['result'] = result
        if status.lower() == "failed":
            self.response['status'] = "failed"      
        self.response['contexts'].append(contexts)
        
    def to_json(self):
        return json.dumps(self.response, ensure_ascii=False, indent=4)
