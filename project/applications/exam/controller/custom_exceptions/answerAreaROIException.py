from dataExtractionException import DataExtractionException


class AnswerAreaROIException(DataExtractionException):
    def __init__(self, *args, **kwargs):
        DataExtractionException.__init__(self, *args, **kwargs)

