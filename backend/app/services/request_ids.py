import uuid


def build_request_id() -> str:
    return f"req_{uuid.uuid4().hex[:12]}"
