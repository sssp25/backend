import secrets
import string

alphabet = string.ascii_letters + string.digits + '-_'

# 랜덤한 문자열 생성기
def gen_id(length: int) -> str:
    return ''.join(secrets.choice(alphabet) for _ in range(length))