import pandas as pd

from calculations import build_ranking, build_team_summary


def make_evaluation(
    evaluator_name: str,
    evaluator_type: str,
    target_team: str,
    total_seed: int = 3,
):
    scores = [total_seed] * 5
    return {
        "evaluator_name": evaluator_name,
        "evaluator_type": evaluator_type,
        "target_team": target_team,
        "question_1": scores[0],
        "question_2": scores[1],
        "question_3": scores[2],
        "question_4": scores[3],
        "question_5": scores[4],
        "total_score": sum(scores),
    }


def test_equal_group_weight_not_equal_headcount_weight():
    rows = []

    # 심사위원 6명은 모두 5점씩: 평균 총점 25점
    for index in range(6):
        rows.append(
            make_evaluation(
                f"심사위원 {index + 1}",
                "judge",
                "1팀",
                5,
            )
        )

    # 참가팀 5팀은 모두 1점씩: 평균 총점 5점
    for index in range(5):
        rows.append(
            make_evaluation(
                f"{index + 2}팀",
                "team",
                "1팀",
                1,
            )
        )

    summary = build_team_summary(rows)
    team_one = summary[summary["team"] == "1팀"].iloc[0]

    # (25 * 0.5) + (5 * 0.5) = 15
    assert team_one["final_score"] == 15
    assert team_one["status"] == "평가 완료"


def test_incomplete_team_has_provisional_but_no_final_score():
    rows = [
        make_evaluation("심사위원 1", "judge", "2팀", 4),
        make_evaluation("1팀", "team", "2팀", 2),
    ]
    summary = build_team_summary(rows)
    team_two = summary[summary["team"] == "2팀"].iloc[0]

    assert team_two["provisional_score"] == 15
    assert pd.isna(team_two["final_score"])
    assert team_two["status"] == "집계 중"


def test_dense_ranking_for_tie():
    rows = []
    for target_team in ["1팀", "2팀"]:
        for index in range(6):
            rows.append(
                make_evaluation(
                    f"심사위원 {index + 1}",
                    "judge",
                    target_team,
                    4,
                )
            )
        team_number = int(target_team[0])
        eligible = [
            f"{index}팀"
            for index in range(1, 7)
            if index != team_number
        ]
        for team_name in eligible:
            rows.append(
                make_evaluation(
                    team_name,
                    "team",
                    target_team,
                    4,
                )
            )

    ranking = build_ranking(build_team_summary(rows))
    completed = ranking[ranking["final_score"].notna()]

    assert list(completed["rank"].astype(int)) == [1, 1]
