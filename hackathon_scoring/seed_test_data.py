"""10개 문항 및 한 줄 평가 테스트 데이터를 생성합니다."""

from __future__ import annotations

import argparse
import random

from config import QUESTIONS, TEAMS
from database import EvaluationRepository


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["partial", "complete"],
        default="partial",
    )
    parser.add_argument("--clear-first", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repository = EvaluationRepository()

    if args.clear_first:
        repository.reset_evaluations()

    users = repository.get_all_users()
    team_users = [
        user for user in users
        if user.get("user_type") == "team" and user.get("is_active")
    ]
    judge_users = [
        user for user in users
        if user.get("user_type") == "judge" and user.get("is_active")
    ]

    if len(team_users) < 6 or len(judge_users) < 6:
        raise RuntimeError("사용자 12명이 먼저 생성되어 있어야 합니다.")

    generator = random.Random(20260723)
    saved_count = 0

    for target_team in TEAMS:
        eligible_teams = [
            user for user in team_users
            if user.get("team_name") != target_team
        ]

        selected_judges = (
            judge_users[:3] if args.mode == "partial" else judge_users
        )
        selected_teams = (
            eligible_teams[:2] if args.mode == "partial" else eligible_teams
        )

        for user in [*selected_judges, *selected_teams]:
            scores = {
                question["id"]: generator.randint(2, 5)
                for question in QUESTIONS
            }
            review = (
                "강점은 문제 정의와 기술 활용의 연결이 명확하다는 점이며, "
                "보완점은 실제 사용자 검증과 시장 근거를 더 제시해야 한다는 점입니다."
            )
            repository.save_evaluation(
                user=user,
                target_team=target_team,
                scores=scores,
                one_line_review=review,
                allow_edit=True,
            )
            saved_count += 1

    print(f"테스트 평가 {saved_count}개를 생성하거나 갱신했습니다.")


if __name__ == "__main__":
    main()
