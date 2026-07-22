"""참가팀 6개와 심사위원 6명의 계정 및 임시 인증 코드를 생성합니다."""

from __future__ import annotations

import secrets
import string

from config import JUDGES, TEAMS
from database import EvaluationRepository
from security import hash_access_code


ALPHABET = string.ascii_uppercase + string.digits


def generate_code(prefix: str) -> str:
    random_part = "".join(secrets.choice(ALPHABET) for _ in range(8))
    return f"{prefix}-{random_part}"


def main() -> None:
    repository = EvaluationRepository()
    credentials: list[tuple[str, str, str]] = []

    for team in TEAMS:
        access_code = generate_code("TEAM")
        repository.upsert_user(
            username=team,
            user_type="team",
            team_name=team,
            access_code_hash=hash_access_code(access_code),
        )
        credentials.append(("참가팀", team, access_code))

    for judge in JUDGES:
        access_code = generate_code("JUDGE")
        repository.upsert_user(
            username=judge,
            user_type="judge",
            team_name=None,
            access_code_hash=hash_access_code(access_code),
        )
        credentials.append(("심사위원", judge, access_code))

    print("\n사용자 생성이 완료되었습니다.")
    print("아래 인증 코드는 데이터베이스에 평문으로 저장되지 않습니다.")
    print("이 터미널 출력을 안전한 장소에 한 번만 복사해 보관하세요.\n")
    print(f"{'유형':<10} {'사용자':<20} 인증 코드")
    print("-" * 55)
    for user_type, username, access_code in credentials:
        print(f"{user_type:<10} {username:<20} {access_code}")


if __name__ == "__main__":
    main()
