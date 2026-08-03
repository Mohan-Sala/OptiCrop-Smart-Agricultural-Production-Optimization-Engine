import re
from app.utils.exceptions import ValidationException


def validate_password_strength(password: str) -> None:
    """Enforces enterprise password strength rules.

    Rules:
    - Minimum length of 8 characters
    - At least one uppercase character (A-Z)
    - At least one lowercase character (a-z)
    - At least one numeric digit (0-9)
    - At least one special symbol character (!@#$%^&*...)
    """
    if len(password) < 8:
        raise ValidationException("Weak password: must be at least 8 characters long.")
    if not re.search(r"[a-z]", password):
        raise ValidationException("Weak password: must contain at least one lowercase letter.")
    if not re.search(r"[A-Z]", password):
        raise ValidationException("Weak password: must contain at least one uppercase letter.")
    if not re.search(r"\d", password):
        raise ValidationException("Weak password: must contain at least one digit character.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValidationException("Weak password: must contain at least one special symbol.")
