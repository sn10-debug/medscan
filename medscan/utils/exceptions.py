from rest_framework.exceptions import APIException


class MissingImageException(APIException):
    status_code = 400
    default_detail = "Missing image. Please upload an image."
    default_code = "missing_image"


class MissingModelException(APIException):
    status_code = 400
    default_detail = "Missing model. Please configure a model version."
    default_code = "missing_model"


class MissingKitIDException(APIException):
    status_code = 400
    default_detail = "Missing kit_id. Please provide a kit_id."
    default_code = "missing_kit_id"
