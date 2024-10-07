from rest_framework.views import exception_handler


def generic_exception_handler(exc, context):
    response = exception_handler(exc, context)

    payload = {
        "status": "error",
        "code": getattr(exc, "default_code", ""),
        "message": getattr(exc, "default_detail", ""),
        "data": response.data if response else None,
    }

    if response is not None:
        response.data = payload

    return response
