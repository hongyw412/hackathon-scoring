"""평가 집계, 순위, 미제출자 계산."""

from __future__ import annotations

from typing import Any

import pandas as pd

from config import (
    EXPECTED_EVALUATIONS_PER_TEAM,
    EXPECTED_JUDGE_COUNT_PER_TEAM,
    EXPECTED_TEAM_COUNT_PER_TEAM,
    JUDGES,
    JUDGE_WEIGHT,
    QUESTIONS,
    TEAMS,
    TEAM_WEIGHT,
)


QUESTION_AVERAGE_COLUMNS = [
    f"{question['id']}_average"
    for question in QUESTIONS
]


def _mean_or_none(series: pd.Series) -> float | None:
    if series.empty:
        return None
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if numeric.empty:
        return None
    return float(numeric.mean())


def _score_value(row: dict[str, Any], question_id: str) -> int | None:
    scores = row.get("scores")
    if not isinstance(scores, dict):
        return None
    value = scores.get(question_id)
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def build_team_summary(
    evaluations: list[dict[str, Any]],
) -> pd.DataFrame:
    """팀별 평가 수, 집단별 평균, 50:50 최종점수를 계산합니다."""
    rows: list[dict[str, Any]] = []

    for team in TEAMS:
        team_rows = [
            row
            for row in evaluations
            if row.get("target_team") == team
        ]
        judge_rows = [
            row for row in team_rows
            if row.get("evaluator_type") == "judge"
        ]
        peer_rows = [
            row for row in team_rows
            if row.get("evaluator_type") == "team"
        ]

        judge_count = len(judge_rows)
        team_count = len(peer_rows)
        total_count = len(team_rows)

        judge_average = _mean_or_none(
            pd.Series(
                [row.get("total_score") for row in judge_rows],
                dtype="float64",
            )
        )
        team_average = _mean_or_none(
            pd.Series(
                [row.get("total_score") for row in peer_rows],
                dtype="float64",
            )
        )

        provisional_score = None
        if judge_average is not None and team_average is not None:
            provisional_score = (
                judge_average * JUDGE_WEIGHT
                + team_average * TEAM_WEIGHT
            )

        is_complete = (
            judge_count == EXPECTED_JUDGE_COUNT_PER_TEAM
            and team_count == EXPECTED_TEAM_COUNT_PER_TEAM
            and total_count == EXPECTED_EVALUATIONS_PER_TEAM
        )

        row: dict[str, Any] = {
            "team": team,
            "judge_count": judge_count,
            "team_count": team_count,
            "total_count": total_count,
            "judge_average": judge_average,
            "team_average": team_average,
            "provisional_score": provisional_score,
            "final_score": provisional_score if is_complete else None,
            "status": "평가 완료" if is_complete else "집계 중",
        }

        for question in QUESTIONS:
            values = [
                _score_value(evaluation, question["id"])
                for evaluation in team_rows
            ]
            valid_values = [value for value in values if value is not None]
            row[f"{question['id']}_average"] = (
                sum(valid_values) / len(valid_values)
                if valid_values
                else None
            )

        rows.append(row)

    return pd.DataFrame(rows)


def build_ranking(summary: pd.DataFrame) -> pd.DataFrame:
    ranking = summary.copy()
    ranking["rank"] = pd.NA

    complete_mask = ranking["final_score"].notna()
    if complete_mask.any():
        ranking.loc[complete_mask, "rank"] = (
            ranking.loc[complete_mask, "final_score"]
            .rank(method="dense", ascending=False)
            .astype("Int64")
        )

    ranking["_sort_complete"] = complete_mask.astype(int)
    ranking["_sort_score"] = pd.to_numeric(
        ranking["provisional_score"],
        errors="coerce",
    ).fillna(-1)

    ranking = ranking.sort_values(
        ["_sort_complete", "_sort_score", "team"],
        ascending=[False, False, True],
    ).drop(columns=["_sort_complete", "_sort_score"])

    return ranking.reset_index(drop=True)


def get_submission_lists(
    evaluations: list[dict[str, Any]],
    target_team: str,
) -> dict[str, list[str]]:
    target_rows = [
        row for row in evaluations
        if row.get("target_team") == target_team
    ]

    completed_judges = sorted(
        {
            str(row.get("evaluator_name"))
            for row in target_rows
            if row.get("evaluator_type") == "judge"
        }
    )
    completed_teams = sorted(
        {
            str(row.get("evaluator_name"))
            for row in target_rows
            if row.get("evaluator_type") == "team"
        }
    )

    eligible_teams = [team for team in TEAMS if team != target_team]

    return {
        "completed_judges": completed_judges,
        "missing_judges": [
            judge for judge in JUDGES if judge not in completed_judges
        ],
        "completed_teams": completed_teams,
        "missing_teams": [
            team for team in eligible_teams if team not in completed_teams
        ],
    }


def to_korean_columns(summary: pd.DataFrame) -> pd.DataFrame:
    display = summary.copy()
    rename_map = {
        "team": "팀 이름",
        "judge_count": "심사위원 제출 수",
        "team_count": "참가팀 제출 수",
        "total_count": "전체 제출 수",
        "judge_average": "심사위원 평균",
        "team_average": "참가팀 평균",
        "provisional_score": "현재 점수",
        "final_score": "확정 최종 점수",
        "status": "평가 상태",
        "rank": "순위",
    }

    for index, question in enumerate(QUESTIONS, start=1):
        rename_map[f"{question['id']}_average"] = f"문항 {index} 평균"

    display = display.rename(columns=rename_map)

    numeric_columns = [
        "심사위원 평균",
        "참가팀 평균",
        "현재 점수",
        "확정 최종 점수",
        *[
            f"문항 {index} 평균"
            for index in range(1, len(QUESTIONS) + 1)
        ],
    ]
    for column in numeric_columns:
        if column in display.columns:
            display[column] = pd.to_numeric(
                display[column],
                errors="coerce",
            ).round(2)

    return display
