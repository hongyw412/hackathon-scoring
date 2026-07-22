"""운영진용 실시간 집계 및 데이터 관리 화면."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from calculations import (
    build_ranking,
    build_team_summary,
    get_submission_lists,
    to_korean_columns,
)
from config import (
    ADMIN_REFRESH_SECONDS,
    ADMIN_TITLE,
    EXPECTED_TOTAL_EVALUATIONS,
    MAX_REVIEW_LENGTH,
    QUESTIONS,
    TEAMS,
)
from database import (
    AppDataError,
    ConfigurationError,
    EvaluationRepository,
    get_secret,
)
from security import secure_compare


def initialize_admin_state() -> None:
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False


def render_admin_login() -> bool:
    expected_password = get_secret("ADMIN_PASSWORD")
    if not expected_password:
        raise ConfigurationError("ADMIN_PASSWORD 환경변수가 없습니다.")

    if st.session_state.admin_authenticated:
        return True

    st.title(ADMIN_TITLE)
    with st.form("admin_login_form"):
        password = st.text_input("관리자 비밀번호", type="password")
        submitted = st.form_submit_button(
            "관리자 로그인",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if secure_compare(password, expected_password):
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("관리자 비밀번호가 올바르지 않습니다.")

    return False


def format_datetime_kst(value: Any) -> str:
    if value in (None, ""):
        return "-"
    try:
        timestamp = pd.to_datetime(value, utc=True)
        return timestamp.tz_convert("Asia/Seoul").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    except Exception:
        return str(value)


def evaluation_dataframe(
    evaluations: list[dict[str, Any]],
) -> pd.DataFrame:
    if not evaluations:
        return pd.DataFrame()

    rows = []
    for evaluation in evaluations:
        scores = evaluation.get("scores")
        scores = scores if isinstance(scores, dict) else {}

        row = {
            "평가 ID": evaluation.get("id"),
            "평가자": evaluation.get("evaluator_name"),
            "평가자 유형": (
                "참가팀"
                if evaluation.get("evaluator_type") == "team"
                else "심사위원"
            ),
            "평가자 소속 팀": evaluation.get("evaluator_team"),
            "평가 대상 팀": evaluation.get("target_team"),
        }

        for index, question in enumerate(QUESTIONS, start=1):
            row[f"Q{index}"] = scores.get(question["id"])

        row.update(
            {
                "총점": evaluation.get("total_score"),
                "한 줄 평가": evaluation.get("one_line_review"),
                "제출 시간": format_datetime_kst(
                    evaluation.get("submitted_at")
                ),
                "마지막 수정 시간": format_datetime_kst(
                    evaluation.get("updated_at")
                ),
            }
        )
        rows.append(row)

    return pd.DataFrame(rows)


def render_overview(
    evaluations: list[dict[str, Any]],
    summary: pd.DataFrame,
) -> None:
    total_submissions = len(evaluations)
    progress = (
        total_submissions / EXPECTED_TOTAL_EVALUATIONS
        if EXPECTED_TOTAL_EVALUATIONS
        else 0
    )
    completed_count = int((summary["status"] == "평가 완료").sum())

    complete_rows = summary[summary["final_score"].notna()]
    provisional_rows = summary[summary["provisional_score"].notna()]

    if not complete_rows.empty:
        leader = complete_rows.sort_values(
            "final_score",
            ascending=False,
        ).iloc[0]
        leader_text = f"{leader['team']} ({leader['final_score']:.2f}점)"
    elif not provisional_rows.empty:
        leader = provisional_rows.sort_values(
            "provisional_score",
            ascending=False,
        ).iloc[0]
        leader_text = (
            f"{leader['team']} "
            f"({leader['provisional_score']:.2f}점, 임시)"
        )
    else:
        leader_text = "집계 중"

    last_submission = "-"
    if evaluations:
        latest = max(
            evaluations,
            key=lambda row: str(row.get("submitted_at", "")),
        )
        last_submission = format_datetime_kst(
            latest.get("submitted_at")
        )

    columns = st.columns(3)
    columns[0].metric("전체 제출 수", total_submissions)
    columns[1].metric("예상 전체 제출 수", EXPECTED_TOTAL_EVALUATIONS)
    columns[2].metric("전체 진행률", f"{progress * 100:.1f}%")

    columns = st.columns(3)
    columns[0].metric("평가 완료 팀", f"{completed_count} / {len(TEAMS)}")
    columns[1].metric("현재 1위", leader_text)
    columns[2].metric("마지막 제출", last_submission)

    st.progress(
        min(progress, 1.0),
        text=f"{total_submissions} / {EXPECTED_TOTAL_EVALUATIONS}개 제출",
    )

    status_table = summary[
        [
            "team",
            "judge_count",
            "team_count",
            "total_count",
            "judge_average",
            "team_average",
            "provisional_score",
            "status",
        ]
    ]
    st.dataframe(
        to_korean_columns(status_table),
        use_container_width=True,
        hide_index=True,
    )

    chart_data = (
        summary[["team", "provisional_score"]]
        .dropna()
        .set_index("team")
        .rename(columns={"provisional_score": "현재 점수"})
    )
    if not chart_data.empty:
        st.subheader("팀별 현재 점수")
        st.bar_chart(chart_data)


def render_ranking(summary: pd.DataFrame) -> None:
    ranking = build_ranking(summary)
    columns = [
        "rank",
        "team",
        "team_average",
        "judge_average",
        "provisional_score",
        "final_score",
        "team_count",
        "judge_count",
        "total_count",
        "status",
    ]
    display = to_korean_columns(ranking[columns])
    display["순위"] = display["순위"].apply(
        lambda value: (
            f"{int(value)}위"
            if value is not pd.NA and not pd.isna(value)
            else "집계 중"
        )
    )
    st.dataframe(display, use_container_width=True, hide_index=True)


def render_details(
    evaluations: list[dict[str, Any]],
    summary: pd.DataFrame,
) -> None:
    target_team = st.selectbox(
        "확인할 발표팀",
        TEAMS,
        key="admin_detail_target",
    )
    evaluator_filter = st.selectbox(
        "평가자 유형",
        ["전체", "참가팀", "심사위원"],
        key="admin_detail_type",
    )

    filtered = [
        row for row in evaluations
        if row.get("target_team") == target_team
    ]
    if evaluator_filter != "전체":
        expected_type = (
            "team" if evaluator_filter == "참가팀" else "judge"
        )
        filtered = [
            row for row in filtered
            if row.get("evaluator_type") == expected_type
        ]

    frame = evaluation_dataframe(filtered)
    if frame.empty:
        st.info("조건에 맞는 평가 내역이 없습니다.")
    else:
        st.dataframe(
            frame.drop(columns=["평가 ID"], errors="ignore"),
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("문항별 평균")
    team_summary = summary[summary["team"] == target_team].iloc[0]
    question_rows = []
    for index, question in enumerate(QUESTIONS, start=1):
        value = team_summary[f"{question['id']}_average"]
        question_rows.append(
            {
                "문항": f"Q{index}. {question['title']}",
                "평균": None if pd.isna(value) else round(float(value), 2),
            }
        )
    st.dataframe(
        pd.DataFrame(question_rows),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("제출 및 미제출 현황")
    lists = get_submission_lists(evaluations, target_team)
    left, right = st.columns(2)
    with left:
        st.markdown("**심사위원 완료**")
        st.write(", ".join(lists["completed_judges"]) or "없음")
        st.markdown("**심사위원 미제출**")
        st.write(", ".join(lists["missing_judges"]) or "없음")
    with right:
        st.markdown("**참가팀 완료**")
        st.write(", ".join(lists["completed_teams"]) or "없음")
        st.markdown("**참가팀 미제출**")
        st.write(", ".join(lists["missing_teams"]) or "없음")


def render_downloads(
    evaluations: list[dict[str, Any]],
    summary: pd.DataFrame,
) -> None:
    evaluation_frame = evaluation_dataframe(evaluations)
    ranking_frame = to_korean_columns(build_ranking(summary))

    left, right = st.columns(2)
    left.download_button(
        "전체 평가 결과 CSV",
        evaluation_frame.to_csv(index=False).encode("utf-8-sig"),
        file_name="hackathon_evaluations.csv",
        mime="text/csv",
        use_container_width=True,
    )
    right.download_button(
        "전체 순위 CSV",
        ranking_frame.to_csv(index=False).encode("utf-8-sig"),
        file_name="hackathon_ranking.csv",
        mime="text/csv",
        use_container_width=True,
    )


def render_data_management(
    repository: EvaluationRepository,
    evaluations: list[dict[str, Any]],
) -> None:
    if evaluations:
        option_map = {
            (
                f"{row['target_team']} ← {row['evaluator_name']} "
                f"({row['evaluator_type']}, 총점 {row['total_score']})"
            ): row
            for row in evaluations
        }
        selected_label = st.selectbox(
            "관리할 평가 결과",
            list(option_map.keys()),
        )
        selected = option_map[selected_label]
        selected_scores = selected.get("scores")
        selected_scores = (
            selected_scores
            if isinstance(selected_scores, dict)
            else {}
        )

        with st.form("admin_edit_evaluation_form"):
            scores: dict[str, int] = {}
            for index, question in enumerate(QUESTIONS, start=1):
                scores[question["id"]] = int(
                    st.number_input(
                        f"Q{index}. {question['title']}",
                        min_value=1,
                        max_value=5,
                        value=int(
                            selected_scores.get(question["id"], 3)
                        ),
                        step=1,
                    )
                )

            review = st.text_area(
                "한 줄 평가",
                value=str(selected.get("one_line_review", "")),
                max_chars=MAX_REVIEW_LENGTH,
            )
            confirm_edit = st.checkbox("위 내용으로 수정합니다.")
            edit_submitted = st.form_submit_button(
                "평가 결과 수정",
                use_container_width=True,
            )

        if edit_submitted:
            if not confirm_edit:
                st.error("수정 확인 항목을 선택해주세요.")
            else:
                try:
                    repository.admin_update_evaluation(
                        str(selected["id"]),
                        scores,
                        review,
                    )
                except AppDataError as error:
                    st.error(str(error))
                else:
                    st.success("평가 결과를 수정했습니다.")
                    st.rerun()

        confirm_delete = st.checkbox(
            "선택한 평가 결과를 삭제합니다."
        )
        if st.button(
            "선택한 평가 결과 삭제",
            use_container_width=True,
        ):
            if not confirm_delete:
                st.error("삭제 확인 항목을 선택해주세요.")
            else:
                repository.delete_evaluation(str(selected["id"]))
                st.rerun()
    else:
        st.info("관리할 평가 결과가 없습니다.")

    st.divider()
    st.error(
        "전체 삭제는 평가 결과만 삭제하며 사용자 계정은 유지됩니다."
    )
    phrase = st.text_input('계속하려면 "전체삭제"를 입력하세요.')
    if st.button(
        "전체 평가 데이터 삭제",
        type="primary",
        use_container_width=True,
    ):
        if phrase != "전체삭제":
            st.error('확인 문구 "전체삭제"를 정확히 입력해주세요.')
        else:
            repository.reset_evaluations()
            st.success("전체 평가 데이터를 삭제했습니다.")
            st.rerun()


def render_realtime_dashboard(
    repository: EvaluationRepository,
) -> None:
    evaluations = repository.get_all_evaluations()
    summary = build_team_summary(evaluations)

    overview_tab, ranking_tab, detail_tab = st.tabs(
        ["실시간 현황", "순위표", "상세 및 미제출자"]
    )
    with overview_tab:
        render_overview(evaluations, summary)
    with ranking_tab:
        render_ranking(summary)
    with detail_tab:
        render_details(evaluations, summary)


def main() -> None:
    st.set_page_config(
        page_title=ADMIN_TITLE,
        page_icon="📊",
        layout="wide",
    )
    initialize_admin_state()

    try:
        if not render_admin_login():
            return
        repository = EvaluationRepository()
    except AppDataError as error:
        st.error(str(error))
        return

    st.title(ADMIN_TITLE)
    st.caption(
        f"조회 화면은 {ADMIN_REFRESH_SECONDS}초마다 자동 갱신됩니다."
    )

    left, right = st.sidebar.columns(2)
    if left.button("즉시 새로고침", use_container_width=True):
        st.rerun()
    if right.button("로그아웃", use_container_width=True):
        st.session_state.admin_authenticated = False
        st.rerun()

    @st.fragment(run_every=f"{ADMIN_REFRESH_SECONDS}s")
    def live_fragment() -> None:
        try:
            render_realtime_dashboard(repository)
        except AppDataError as error:
            st.error(str(error))

    live_fragment()

    st.divider()
    evaluations = repository.get_all_evaluations()
    summary = build_team_summary(evaluations)

    download_tab, management_tab = st.tabs(
        ["CSV 다운로드", "데이터 관리"]
    )
    with download_tab:
        render_downloads(evaluations, summary)
    with management_tab:
        render_data_management(repository, evaluations)


if __name__ == "__main__":
    main()
