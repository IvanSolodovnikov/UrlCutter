import string
from secrets import choice


ALPHABET = string.ascii_letters + string.digits

def generate_slug() -> str:
    slug = ""
    for _ in range(6):
        slug += choice(ALPHABET)
    return slug