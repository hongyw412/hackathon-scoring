"""평가자용 Streamlit 애플리케이션."""

from __future__ import annotations

import logging
from typing import Any

import streamlit as st

from config import (
    ALLOW_SCORE_EDIT,
    APP_TITLE,
    JUDGES,
    MAX_REVIEW_LENGTH,
    MAX_TOTAL_SCORE,
    MIN_REVIEW_LENGTH,
    QUESTIONS,
    SCORE_LABELS,
    TEAMS,
)
from database import (
    AppDataError,
    AuthenticationError,
    DuplicateEvaluationError,
    EvaluationRepository,
    ValidationError,
)

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def initialize_state() -> None:
    defaults: dict[str, Any] = {
        "current_user": None,
        "draft_evaluation": None,
        "flash_message": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_login_state() -> None:
    for key in ["current_user", "draft_evaluation", "flash_message"]:
        st.session_state.pop(key, None)
    initialize_state()


def render_login(repository: EvaluationRepository) -> None:
    st.subheader("평가자 로그인")

    user_type_label = st.selectbox(
        "사용자 유형",
        ["참가팀", "심사위원"],
        key="login_user_type_label",
    )
    user_type = "team" if user_type_label == "참가팀" else "judge"
    names = TEAMS if user_type == "team" else JUDGES

    with st.form(f"login_form_{user_type}"):
        username = st.selectbox(
            "팀명 또는 심사위원 이름",
            names,
            key=f"login_username_{user_type}",
        )
        access_code = st.text_input(
            "개인 인증 코드",
            type="password",
            placeholder="운영진에게 받은 인증 코드를 입력하세요.",
            key=f"login_access_code_{user_type}",
        )
        submitted = st.form_submit_button(
            "로그인",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    if not access_code.strip():
        st.error("개인 인증 코드를 입력해주세요.")
        return

    try:
        user = repository.authenticate_user(
            username=username,
            user_type=user_type,
            access_code=access_code,
        )
    except (AuthenticationError, AppDataError) as error:
        st.error(str(error))
    else:
        st.session_state.current_user = user
        st.session_state.flash_message = "로그인되었습니다."
        st.rerun()


def existing_values(
    evaluation: dict[str, Any] | None,
) -> tuple[dict[str, int | None], str]:
    if not evaluation:
        return (
            {question["id"]: None for question in QUESTIONS},
            "",
        )

    raw_scores = evaluation.get("scores")
    scores = raw_scores if isinstance(raw_scores, dict) else {}
    return (
        {
            question["id"]: (
                int(scores[question["id"]])
                if question["id"] in scores
                else None
            )
            for question in QUESTIONS
        },
        str(evaluation.get("one_line_review", "")),
    )


def render_review(
    repository: EvaluationRepository,
    user: dict[str, Any],
) -> None:
    draft = st.session_state.draft_evaluation
    if not draft:
        return

    st.subheader("제출 전 확인")
    st.warning("평가 대상 팀과 점수를 다시 확인해주세요.")
    st.write(f"**평가자:** {user['username']}")
    st.write(f"**평가 대상 팀:** {draft['target_team']}")

    for index, question in enumerate(QUESTIONS, start=1):
        score = draft["scores"][question["id"]]
        st.write(
            f"**Q{index}. {question['title']}** — "
            f"{score}점 · {SCORE_LABELS[score]}"
        )

    st.metric(
        "총점",
        f"{sum(draft['scores'].values())} / {MAX_TOTAL_SCORE}점",
    )
    st.write("**한 줄 평가**")
    st.info(draft["one_line_review"])

    left, right = st.columns(2)
    if left.button("평가 내용 수정", use_container_width=True):
        st.session_state.draft_evaluation = None
        st.rerun()

    if right.button(
        "최종 제출",
        type="primary",
        use_container_width=True,
    ):
        try:
            repository.save_evaluation(
                user=user,
                target_team=draft["target_team"],
                scores=draft["scores"],
                one_line_review=draft["one_line_review"],
                allow_edit=ALLOW_SCORE_EDIT,
            )
        except (DuplicateEvaluationError, ValidationError, AppDataError) as error:
            st.error(str(error))
        else:
            st.session_state.draft_evaluation = None
            st.session_state.flash_message = (
                "평가가 정상적으로 제출되었습니다."
            )
            st.rerun()


def render_evaluation(
    repository: EvaluationRepository,
    user: dict[str, Any],
) -> None:
    if st.session_state.draft_evaluation:
        render_review(repository, user)
        return

    user_evaluations = repository.get_user_evaluations(str(user["id"]))
    completed_targets = {
        str(evaluation["target_team"])
        for evaluation in user_evaluations
    }

    allowed_targets = list(TEAMS)
    if user["user_type"] == "team":
        allowed_targets = [
            team for team in TEAMS
            if team != user.get("team_name")
        ]

    pending_targets = [
        team for team in allowed_targets
        if team not in completed_targets
    ]

    st.subheader("내 평가 현황")
    completed_count = len(completed_targets.intersection(allowed_targets))
    st.progress(
        completed_count / len(allowed_targets),
        text=f"{completed_count} / {len(allowed_targets)}개 팀 평가 완료",
    )

    selectable_targets = (
        allowed_targets if ALLOW_SCORE_EDIT else pending_targets
    )
    if not selectable_targets:
        st.success("평가해야 할 모든 팀의 평가를 완료했습니다.")
        return

    target_team = st.selectbox(
        "평가 대상 팀",
        selectable_targets,
        key="target_team_selector",
    )
    existing = repository.get_evaluation(str(user["id"]), target_team)
    default_scores, default_review = existing_values(
        existing if ALLOW_SCORE_EDIT else None
    )

    st.divider()
    st.header(f"{target_team} 평가")
    st.caption(
        "각 문항은 1~5점이며 총점은 50점입니다. "
        "마지막 한 줄 평가까지 작성해야 제출할 수 있습니다."
    )
    st.info(
        " · ".join(
            f"{score}점: {label}"
            for score, label in SCORE_LABELS.items()
        )
    )

    with st.form(f"evaluation_form_{target_team}"):
        selected_scores: dict[str, int | None] = {}
        current_stage = None

        for index, question in enumerate(QUESTIONS, start=1):
            if question["stage"] != current_stage:
                current_stage = question["stage"]
                st.markdown(f"## {current_stage}")

            st.markdown(f"### Q{index}. [{question['title']}]")
            st.write(question["text"])
            st.caption(f"체크 포인트: {question['checkpoint']}")

            default = default_scores[question["id"]]
            selected_scores[question["id"]] = st.radio(
                f"Q{index} 점수",
                options=list(SCORE_LABELS.keys()),
                format_func=lambda value: (
                    f"{value}점 · {SCORE_LABELS[value]}"
                ),
                index=(default - 1) if default is not None else None,
                horizontal=True,
                key=f"score_{target_team}_{question['id']}",
            )
            st.divider()

        st.markdown("## ✍️ 한 줄 평가")
        st.write(
            "발표팀의 **가장 강한 점 1가지**와 "
            "**가장 보완해야 할 점 1가지**를 함께 작성해주세요."
        )
        one_line_review = st.text_area(
            "한 줄 평가",
            value=default_review,
            placeholder=(
                "예: 강점은 타겟 사용자가 명확하고 AI 활용 이유가 "
                "설득력 있다는 점이며, 보완점은 실제 사용자 검증 자료가 "
                "부족하다는 점입니다."
            ),
            max_chars=MAX_REVIEW_LENGTH,
            height=120,
        )
        st.caption(
            f"{MIN_REVIEW_LENGTH}자 이상, "
            f"{MAX_REVIEW_LENGTH}자 이하로 작성해주세요."
        )

        all_selected = all(
            score is not None
            for score in selected_scores.values()
        )
        if all_selected:
            total = sum(
                int(score)
                for score in selected_scores.values()
                if score is not None
            )
            st.metric("현재 선택 총점", f"{total} / {MAX_TOTAL_SCORE}점")
        else:
            st.info("모든 문항을 선택하면 총점이 표시됩니다.")

        review_clicked = st.form_submit_button(
            "제출 내용 검토하기",
            type="primary",
            use_container_width=True,
        )

    if not review_clicked:
        return

    if not all(
        score is not None
        for score in selected_scores.values()
    ):
        st.error("모든 평가 문항에 점수를 선택해주세요.")
        return

    normalized_review = " ".join(one_line_review.strip().split())
    if len(normalized_review) < MIN_REVIEW_LENGTH:
        st.error(
            f"한 줄 평가는 {MIN_REVIEW_LENGTH}자 이상 작성해주세요."
        )
        return

    st.session_state.draft_evaluation = {
        "target_team": target_team,
        "scores": {
            question_id: int(score)
            for question_id, score in selected_scores.items()
            if score is not None
        },
        "one_line_review": normalized_review,
    }
    st.rerun()


def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🏆",
        layout="centered",
    )
    initialize_state()
    st.title(APP_TITLE)
    st.caption(
        "발표팀을 제외한 참가팀 5팀과 심사위원 6명이 각 팀을 평가합니다."
    )

    try:
        repository = EvaluationRepository()
    except AppDataError as error:
        st.error(str(error))
        st.stop()

    user = st.session_state.current_user
    if not user:
        render_login(repository)
        return

    if st.session_state.flash_message:
        st.success(st.session_state.flash_message)
        st.session_state.flash_message = None

    with st.sidebar:
        st.subheader("로그인 정보")
        st.write(f"**사용자:** {user['username']}")
        st.write(
            "**유형:** "
            + ("참가팀" if user["user_type"] == "team" else "심사위원")
        )
        if st.button("로그아웃", use_container_width=True):
            clear_login_state()
            st.rerun()

    try:
        render_evaluation(repository, user)
    except AppDataError as error:
        LOGGER.exception("Evaluator screen error")
        st.error(str(error))


if __name__ == "__main__":
    main()
