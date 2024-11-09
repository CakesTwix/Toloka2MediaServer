class Config:
    def __init__(
        self,
        args=None,
        logger=None,
        toloka=None,
        client=None,
        app_config=None,
        titles_config=None,
        application_config=None,
        operation_result=None,
    ):
        self.args = args
        self.logger = logger
        self.toloka = toloka
        self.client = client
        self.app_config = app_config
        self.titles_config = titles_config
        self.application_config = application_config
        self.operation_result = operation_result
