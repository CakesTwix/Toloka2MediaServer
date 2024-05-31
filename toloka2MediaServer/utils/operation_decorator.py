from datetime import datetime
from functools import wraps

from toloka2MediaServer.models.operation_result import OperationResult, ResponseCode

def operation_tracker(operation_type):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            operation_result = OperationResult()
            operation_result.operation_type = operation_type
            operation_result.start_time = datetime.now()
            operation_result.response_code = ResponseCode.PARTIAL  # Assume partial unless completed
            
            try:
                result = func(*args, **kwargs, operation_result=operation_result)
                operation_result.response_code = ResponseCode.SUCCESS
            except Exception as e:
                operation_result.response_code = ResponseCode.FAILURE
                operation_result.operation_logs.append(str(e))
            
            operation_result.end_time = datetime.now()
            return operation_result
        
        return wrapper
    return decorator