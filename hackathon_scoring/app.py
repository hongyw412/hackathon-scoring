"""곤지암고등학교 여름 AI 해커톤 평가자용 앱."""

from __future__ import annotations

import logging
from html import escape
from typing import Any

import streamlit as st

from config import (
    ALLOW_SCORE_EDIT,
    JUDGES,
    MAX_COMMENT_LENGTH,
    MAX_TOTAL_SCORE,
    MIN_COMMENT_LENGTH,
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
    normalize_member_name,
)
from styles import (
    inject_global_styles,
    render_profile_card,
    render_public_hero,
    render_question_intro,
    render_score_legend,
    render_sidebar_brand,
    render_stage_header,
)

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def initialize_state() -> None:
    defaults: dict[str, Any] = {
        "current_user": None,
        "draft_evaluation": None,
        "submission_success": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_login_state() -> None:
    for key in [
        "current_user",
        "draft_evaluation",
        "submission_success",
    ]:
        st.session_state.pop(key, None)
    initialize_state()


def evaluator_display_name(user: dict[str, Any]) -> str:
    if user.get("user_type") == "team":
        return (
            f"{user.get('team_name', user.get('username', ''))} · "
            f"{user.get('member_name', '')}"
        )
    return str(user.get("username", ""))


@st.dialog("🎉 평가 제출 완료")
def render_submission_success_dialog(target_team: str) -> None:
    st.success(f"{target_team} 팀에 대한 평가가 정상적으로 저장되었습니다.")
    st.write(
        "제출한 평가는 관리자 실시간 집계에 바로 반영됩니다. "
        "다음 발표팀 평가를 계속 진행해주세요."
    )
    if st.button(
        "확인하고 다음 평가하기",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.submission_success = None
        st.rerun()


def render_login(repository: EvaluationRepository) -> None:
    left, center, right = st.columns([0.6, 1.25, 0.6])
    with center:
        with st.container(border=True):
            st.markdown("### 🔐 평가자 로그인")
            st.caption(
                "참가팀은 팀을 선택하고 본인 이름과 팀 인증 코드를 입력해주세요."
            )

            user_type_label = st.selectbox(
                "사용자 유형",
                ["참가팀", "심사위원"],
                key="login_user_type_label",
            )
            user_type = "team" if user_type_label == "참가팀" else "judge"
            names = TEAMS if user_type == "team" else JUDGES

            with st.form(f"login_form_{user_type}"):
                username = st.selectbox(
                    "참가팀" if user_type == "team" else "심사위원",
                    names,
                    key=f"login_username_{user_type}",
                )
                member_name = ""
                if user_type == "team":
                    member_name = st.text_input(
                        "팀원 이름",
                        placeholder="본인의 실제 이름을 입력해주세요.",
                        key="login_member_name",
                    )
                access_code = st.text_input(
                    "인증 코드",
                    type="password",
                    placeholder="예: TEAM-XXXXXXXX 또는 JUDGE-XXXXXXXX",
                    key=f"login_access_code_{user_type}",
                )
                submitted = st.form_submit_button(
                    "평가 시작하기",
                    type="primary",
                    use_container_width=True,
                )

            if not submitted:
                st.caption(
                    "한 팀은 동일한 팀 인증 코드로 팀원 4명이 각각 평가할 수 있습니다."
                )
                return

            if not access_code.strip():
                st.error("인증 코드를 입력해주세요.")
                return

            try:
                normalized_member_name = None
                if user_type == "team":
                    normalized_member_name = normalize_member_name(
                        member_name
                    )

                user = repository.authenticate_user(
                    username=username,
                    user_type=user_type,
                    access_code=access_code,
                )
            except (
                AuthenticationError,
                ValidationError,
                AppDataError,
            ) as error:
                st.error(str(error))
            else:
                if user_type == "team":
                    user["member_name"] = normalized_member_name
                st.session_state.current_user = user
                st.rerun()


def existing_values(
    evaluation: dict[str, Any] | None,
) -> tuple[dict[str, int | None], str, str]:
    if not evaluation:
        return (
            {question["id"]: None for question in QUESTIONS},
            "",
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
        str(evaluation.get("strength_comment", "")),
        str(evaluation.get("improvement_comment", "")),
    )


def render_review(
    repository: EvaluationRepository,
    user: dict[str, Any],
) -> None:
    draft = st.session_state.draft_evaluation
    if not draft:
        return

    st.markdown("## 제출 전 최종 확인")
    st.caption("제출 후에는 평가자가 직접 수정할 수 없습니다.")

    top_left, top_right = st.columns(2)
    with top_left:
        render_profile_card("평가자", evaluator_display_name(user))
    with top_right:
        render_profile_card("평가 대상", str(draft["target_team"]))

    st.markdown("")
    stage_number = 0
    current_stage = None
    for index, question in enumerate(QUESTIONS, start=1):
        if question["stage"] != current_stage:
            current_stage = question["stage"]
            stage_number += 1
            render_stage_header(current_stage, stage_number)

        score = draft["scores"][question["id"]]
        with st.container(border=True):
            left, right = st.columns([4, 1])
            left.markdown(f"**Q{index}. {question['title']}**")
            right.markdown(f"### {score}점")
            st.caption(SCORE_LABELS[score])

    total_score = sum(draft["scores"].values())
    st.metric("총점", f"{total_score} / {MAX_TOTAL_SCORE}점")

    opinion_columns = st.columns(2)
    with opinion_columns[0]:
        st.markdown("**✅ 잘한 점**")
        st.markdown(
            (
                '<div class="gj-review-box gj-strength-box">'
                f'{escape(str(draft["strength_comment"]))}</div>'
            ),
            unsafe_allow_html=True,
        )
    with opinion_columns[1]:
        st.markdown("**🛠️ 보완할 점**")
        st.markdown(
            (
                '<div class="gj-review-box gj-improvement-box">'
                f'{escape(str(draft["improvement_comment"]))}</div>'
            ),
            unsafe_allow_html=True,
        )

    left, right = st.columns(2)
    if left.button("← 평가 내용 수정", use_container_width=True):
        st.session_state.draft_evaluation = None
        st.rerun()

    if right.button(
        "최종 제출하기",
        type="primary",
        use_container_width=True,
    ):
        try:
            repository.save_evaluation(
                user=user,
                target_team=draft["target_team"],
                scores=draft["scores"],
                strength_comment=draft["strength_comment"],
                improvement_comment=draft["improvement_comment"],
                allow_edit=ALLOW_SCORE_EDIT,
            )
        except (
            DuplicateEvaluationError,
            ValidationError,
            AppDataError,
        ) as error:
            st.error(str(error))
        else:
            submitted_team = str(draft["target_team"])
            st.session_state.draft_evaluation = None
            st.session_state.submission_success = {
                "target_team": submitted_team,
            }
            st.rerun()


def render_evaluation(
    repository: EvaluationRepository,
    user: dict[str, Any],
) -> None:
    if st.session_state.draft_evaluation:
        render_review(repository, user)
        return

    member_name = (
        str(user.get("member_name", ""))
        if user.get("user_type") == "team"
        else None
    )
    user_evaluations = repository.get_user_evaluations(
        evaluator_id=str(user["id"]),
        evaluator_type=str(user["user_type"]),
        member_name=member_name,
    )
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
    completed_count = len(completed_targets.intersection(allowed_targets))

    info_columns = st.columns(3)
    with info_columns[0]:
        render_profile_card("로그인 사용자", evaluator_display_name(user))
    with info_columns[1]:
        render_profile_card(
            "평가자 유형",
            "참가팀 팀원"
            if user["user_type"] == "team"
            else "심사위원",
        )
    with info_columns[2]:
        render_profile_card(
            "평가 진행",
            f"{completed_count} / {len(allowed_targets)}팀 완료",
        )

    st.markdown("")
    st.progress(
        completed_count / len(allowed_targets),
        text=(
            f"개인 평가 진행률 · "
            f"{completed_count}/{len(allowed_targets)}"
        ),
    )

    selectable_targets = (
        allowed_targets if ALLOW_SCORE_EDIT else pending_targets
    )
    if not selectable_targets:
        st.balloons()
        st.success(
            "본인이 평가해야 할 모든 팀의 평가를 완료했습니다. "
            "참여해주셔서 감사합니다!"
        )
        return

    with st.container(border=True):
        st.markdown("### 🎯 평가할 발표팀 선택")
        target_team = st.selectbox(
            "평가 대상 팀",
            selectable_targets,
            key="target_team_selector",
            label_visibility="collapsed",
        )
        st.caption(
            "선택한 팀의 발표가 끝난 뒤 충분히 검토하고 평가해주세요."
        )

    existing = repository.get_evaluation(
        evaluator_id=str(user["id"]),
        evaluator_type=str(user["user_type"]),
        target_team=target_team,
        member_name=member_name,
    )
    (
        default_scores,
        default_strength,
        default_improvement,
    ) = existing_values(existing if ALLOW_SCORE_EDIT else None)

    st.markdown(f"## {target_team} 프로젝트 평가")
    st.caption(
        "10개 문항을 각 1~5점으로 평가합니다. "
        "잘한 점과 보완할 점을 모두 작성해야 제출할 수 있습니다."
    )
    render_score_legend(SCORE_LABELS)

    with st.form(f"evaluation_form_{target_team}"):
        selected_scores: dict[str, int | None] = {}
        current_stage = None
        stage_number = 0

        for index, question in enumerate(QUESTIONS, start=1):
            if question["stage"] != current_stage:
                current_stage = question["stage"]
                stage_number += 1
                render_stage_header(current_stage, stage_number)

            with st.container(border=True):
                render_question_intro(
                    index=index,
                    title=question["title"],
                    text=question["text"],
                    checkpoint=question["checkpoint"],
                )
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
                    label_visibility="collapsed",
                )

        render_stage_header("✍️ 최종 의견 (Feedback)", 4)
        opinion_columns = st.columns(2)

        with opinion_columns[0]:
            with st.container(border=True):
                st.markdown("### ✅ 잘한 점")
                st.caption(
                    "발표팀이 특히 잘한 부분을 구체적으로 작성해주세요."
                )
                strength_comment = st.text_area(
                    "잘한 점",
                    value=default_strength,
                    placeholder=(
                        "예: 타겟 사용자가 명확하고 AI가 핵심 문제를 "
                        "해결하는 이유가 설득력 있게 제시되었습니다."
                    ),
                    max_chars=MAX_COMMENT_LENGTH,
                    height=150,
                    label_visibility="collapsed",
                )
                st.caption(
                    f"{MIN_COMMENT_LENGTH}자 이상 · "
                    f"{MAX_COMMENT_LENGTH}자 이하"
                )

        with opinion_columns[1]:
            with st.container(border=True):
                st.markdown("### 🛠️ 보완할 점")
                st.caption(
                    "더 발전하기 위해 보완하면 좋을 부분을 작성해주세요."
                )
                improvement_comment = st.text_area(
                    "보완할 점",
                    value=default_improvement,
                    placeholder=(
                        "예: 실제 사용자 인터뷰와 시장 검증 자료를 "
                        "추가하면 아이디어의 실현 가능성이 더 높아질 것 같습니다."
                    ),
                    max_chars=MAX_COMMENT_LENGTH,
                    height=150,
                    label_visibility="collapsed",
                )
                st.caption(
                    f"{MIN_COMMENT_LENGTH}자 이상 · "
                    f"{MAX_COMMENT_LENGTH}자 이하"
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
            st.metric(
                "현재 선택 총점",
                f"{total} / {MAX_TOTAL_SCORE}점",
            )
        else:
            st.info(
                "아직 선택하지 않은 문항이 있습니다. "
                "Q1~Q10을 모두 확인해주세요."
            )

        review_clicked = st.form_submit_button(
            "제출 내용 검토하기 →",
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

    normalized_strength = " ".join(
        strength_comment.strip().split()
    )
    normalized_improvement = " ".join(
        improvement_comment.strip().split()
    )

    if len(normalized_strength) < MIN_COMMENT_LENGTH:
        st.error(
            f"잘한 점은 {MIN_COMMENT_LENGTH}자 이상 작성해주세요."
        )
        return

    if len(normalized_improvement) < MIN_COMMENT_LENGTH:
        st.error(
            f"보완할 점은 {MIN_COMMENT_LENGTH}자 이상 작성해주세요."
        )
        return

    st.session_state.draft_evaluation = {
        "target_team": target_team,
        "scores": {
            question_id: int(score)
            for question_id, score in selected_scores.items()
            if score is not None
        },
        "strength_comment": normalized_strength,
        "improvement_comment": normalized_improvement,
    }
    st.rerun()


def main() -> None:
    st.set_page_config(
        page_title="곤지암고 여름 AI 해커톤 | 평가",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_global_styles()
    initialize_state()
    render_public_hero()

    try:
        repository = EvaluationRepository()
    except AppDataError as error:
        st.error(str(error))
        st.stop()

    user = st.session_state.current_user
    if not user:
        render_login(repository)
        return

    if st.session_state.submission_success:
        render_submission_success_dialog(
            str(
                st.session_state.submission_success[
                    "target_team"
                ]
            )
        )

    with st.sidebar:
        render_sidebar_brand()
        st.markdown("#### 로그인 정보")
        st.write(f"**사용자**  \n{evaluator_display_name(user)}")
        st.write(
            "**유형**  \n"
            + (
                "참가팀 팀원"
                if user["user_type"] == "team"
                else "심사위원"
            )
        )
        st.divider()
        st.caption("평가는 제출 전 최종 확인 화면을 거칩니다.")
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
