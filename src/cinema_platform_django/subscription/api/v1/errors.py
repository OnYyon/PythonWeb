from rest_framework.response import Response


def make_error(code: int, message: str, details: dict | None = None) -> Response:
    return Response(
        data={"code": code, "message": message, "details": details}, status=code
    )
