from utils import APIException

class NotAllowedError(APIException):

    def __init__(self, message="not allowed", status_code=None, payload=None): #statu_code
        APIException.__init__(self,message, status_code, payload)

