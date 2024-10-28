import re 


def duplicate_error(error_message: str) -> str | None:
    """
    Cắt key unique của dữ liệu lỗi từ mongoengine.errors.NotUniqueError
    """
    match = re.search(r"dup key: { (.+) },", error_message)
    if match:
        return match.group(1)
    return None