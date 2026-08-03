import re


def is_valid_email(email: str) -> bool:
    """Basic validation for email format."""
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(email_regex, email))


def is_valid_phone(phone: str) -> bool:
    """Basic validation for international E.164 phone formats."""
    # Matches optional + sign followed by 7 to 15 digits
    phone_regex = r"^\+?[1-9]\d{6,14}$"
    return bool(re.match(phone_regex, phone))
