"""팀원 4명 방식의 10문항 테스트 데이터를 생성합니다."""

from __future__ import annotations

import argparse
import random

from config import QUESTIONS, TEAM_MEMBERS_PER_TEAM, TEAMS
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


def member_names(team_name: str) -> list[str]:
    return [
        f"{team_name} 팀원 {index}"
        for index in range(1, TEAM_MEMBERS_PER_TEAM + 1)
    ]


def main() -> None:
    args = parse_args()
    repository = EvaluationRepository()

    if args.clear_first:
        repository.reset_evaluations()

    users = repository.get_all_users()
    team_users = [
        user
        for user in users
        if user.get("user_type") == "team"
        and user.get("is_active")
    ]
    judge_users = [
        user
        for user in users
        if user.get("user_type") == "judge"
        and user.get("is_active")
    ]

    if len(team_users) < 6 or len(judge_users) < 6:
        raise RuntimeError(
            "참가팀 6개와 심사위원 6명이 먼저 생성되어 있어야 합니다."
        )

    generator = random.Random(20260723)
    saved_count = 0

    for target_team in TEAMS:
        eligible_team_users = [
            user
            for user in team_users
            if user.get("team_name") != target_team
        ]

        selected_judges = (
            judge_users[:3]
            if args.mode == "partial"
            else judge_users
        )
        selected_team_users = (
            eligible_team_users[:2]
            if args.mode == "partial"
            else eligible_team_users
        )
        members_per_selected_team = (
            2
            if args.mode == "partial"
            else TEAM_MEMBERS_PER_TEAM
        )

        for judge in selected_judges:
            scores = {
                question["id"]: generator.randint(2, 5)
                for question in QUESTIONS
            }
            repository.save_evaluation(
                user=judge,
                target_team=target_team,
                scores=scores,
                strength_comment=(
                    "문제 정의와 AI 활용의 연결이 명확하고 "
                    "발표 흐름이 이해하기 쉬웠습니다."
                ),
                improvement_comment=(
                    "실제 사용자 검증 자료와 시장 규모 근거를 "
                    "조금 더 구체적으로 제시하면 좋겠습니다."
                ),
                allow_edit=True,
            )
            saved_count += 1

        for team_user in selected_team_users:
            team_name = str(team_user.get("team_name"))
            for name in member_names(team_name)[
                :members_per_selected_team
            ]:
                member_user = dict(team_user)
                member_user["member_name"] = name
                scores = {
                    question["id"]: generator.randint(2, 5)
                    for question in QUESTIONS
                }
                repository.save_evaluation(
                    user=member_user,
                    target_team=target_team,
                    scores=scores,
                    strength_comment=(
                        "서비스의 대상 사용자가 명확하고 "
                        "아이디어의 공익적 가치가 잘 드러났습니다."
                    ),
                    improvement_comment=(
                        "구현 일정과 사용자 확보 방법을 더 자세히 "
                        "설명하면 실현 가능성이 높아질 것 같습니다."
                    ),
                    allow_edit=True,
                )
                saved_count += 1

    print(
        f"테스트 평가 {saved_count}개를 생성하거나 갱신했습니다."
    )


if __name__ == "__main__":
    main()
