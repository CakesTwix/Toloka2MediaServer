from datetime import datetime
from functools import wraps

from toloka2MediaServer.models.operation_result import OperationResult, ResponseCode


def operation_tracker(operation_type):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Assume first argument is always Config object
            config = args[0]

            # Initialize OperationResult if it doesn't exist in Config
            if (
                not hasattr(config, "operation_result")
                or config.operation_result is None
            ):
                config.operation_result = OperationResult()

            # Set operation details
            config.operation_result.operation_type = operation_type
            config.operation_result.start_time = datetime.now()
            config.operation_result.response_code = (
                ResponseCode.PARTIAL
            )  # Assume partial unless completed

            try:
                config.operation_result = func(*args, **kwargs)
                config.operation_result.response_code = ResponseCode.SUCCESS
            except Exception as e:
                config.operation_result.response_code = ResponseCode.FAILURE
                if not hasattr(config.operation_result, "operation_logs"):
                    config.operation_result.operation_logs = []
                config.operation_result.operation_logs.append(str(e))
            finally:
                config.operation_result.end_time = datetime.now()

            return config.operation_result

        return wrapper

    return decorator
