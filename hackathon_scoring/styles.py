"""곤지암고등학교 여름 AI 해커톤 공통 UI 스타일."""

from __future__ import annotations

from html import escape

import streamlit as st


GLOBAL_CSS = r"""
<style>
:root {
    --gj-navy: #102A43;
    --gj-blue: #1677FF;
    --gj-cyan: #18B6D9;
    --gj-purple: #6C5CE7;
    --gj-green: #18A875;
    --gj-orange: #F59E0B;
    --gj-red: #E45858;
    --gj-ink: #172033;
    --gj-muted: #667085;
    --gj-line: #E6EAF0;
    --gj-card: rgba(255, 255, 255, 0.94);
}

html, body, [class*="css"] {
    font-family: Pretendard, "Noto Sans KR", "Apple SD Gothic Neo", Arial, sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 9% 4%, rgba(24, 182, 217, 0.13), transparent 28%),
        radial-gradient(circle at 91% 2%, rgba(108, 92, 231, 0.11), transparent 28%),
        linear-gradient(180deg, #F7FBFF 0%, #F8FAFC 42%, #F5F7FB 100%);
    color: var(--gj-ink);
}

[data-testid="stHeader"] {
    background: rgba(247, 251, 255, 0.76);
    backdrop-filter: blur(12px);
}

[data-testid="stAppViewContainer"] > .main .block-container {
    max-width: 1120px;
    padding-top: 1.35rem;
    padding-bottom: 4rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #F8FBFF 0%, #F3F6FB 100%);
    border-right: 1px solid var(--gj-line);
}

[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem;
}

.gj-hero {
    position: relative;
    overflow: hidden;
    padding: 2.25rem 2.35rem;
    margin: 0 0 1.4rem 0;
    border-radius: 26px;
    color: white;
    background:
        linear-gradient(120deg, rgba(16,42,67,.98), rgba(22,119,255,.93) 55%, rgba(24,182,217,.90));
    box-shadow: 0 18px 50px rgba(22, 64, 112, 0.20);
}

.gj-hero::before,
.gj-hero::after {
    content: "";
    position: absolute;
    border-radius: 999px;
    background: rgba(255,255,255,.10);
}

.gj-hero::before {
    width: 260px;
    height: 260px;
    right: -75px;
    top: -120px;
}

.gj-hero::after {
    width: 150px;
    height: 150px;
    right: 125px;
    bottom: -105px;
}

.gj-hero-kicker {
    display: inline-flex;
    align-items: center;
    gap: .45rem;
    padding: .42rem .75rem;
    border: 1px solid rgba(255,255,255,.28);
    border-radius: 999px;
    background: rgba(255,255,255,.12);
    font-size: .82rem;
    font-weight: 750;
    letter-spacing: .02em;
}

.gj-hero h1 {
    position: relative;
    margin: .85rem 0 .45rem 0;
    color: white;
    font-size: clamp(1.8rem, 4vw, 3.05rem);
    line-height: 1.12;
    letter-spacing: -.04em;
}

.gj-hero p {
    position: relative;
    margin: 0;
    color: rgba(255,255,255,.86);
    font-size: 1rem;
    line-height: 1.65;
}

.gj-mini-brand {
    padding: 1rem 1.05rem;
    border-radius: 18px;
    background: linear-gradient(145deg, #102A43, #1677FF);
    color: white;
    margin-bottom: 1rem;
}

.gj-mini-brand strong {
    display: block;
    font-size: 1rem;
    margin-bottom: .15rem;
}

.gj-mini-brand span {
    color: rgba(255,255,255,.76);
    font-size: .82rem;
}

.gj-section-label {
    display: flex;
    align-items: center;
    gap: .65rem;
    padding: .82rem 1rem;
    margin: 1.15rem 0 .8rem 0;
    border-radius: 15px;
    font-size: 1rem;
    font-weight: 800;
    letter-spacing: -.015em;
}

.gj-stage-1 { background: #EAF4FF; color: #0B63CE; border: 1px solid #CAE2FF; }
.gj-stage-2 { background: #F1EDFF; color: #5B43D6; border: 1px solid #DDD4FF; }
.gj-stage-3 { background: #FFF5E4; color: #B96D00; border: 1px solid #FFE2B3; }
.gj-stage-4 { background: #EAF9F2; color: #117D58; border: 1px solid #C8EEDD; }

.gj-question-head {
    margin-bottom: .35rem;
}

.gj-question-number {
    display: inline-block;
    margin-right: .45rem;
    padding: .28rem .55rem;
    border-radius: 9px;
    background: #EDF4FF;
    color: #126AD5;
    font-size: .78rem;
    font-weight: 850;
}

.gj-question-title {
    font-size: 1.08rem;
    font-weight: 850;
    color: var(--gj-ink);
    letter-spacing: -.02em;
}

.gj-question-text {
    margin: .55rem 0 .7rem 0;
    color: #344054;
    line-height: 1.68;
    font-size: .96rem;
}

.gj-checkpoint {
    margin: 0 0 .65rem 0;
    padding: .7rem .82rem;
    border-radius: 12px;
    background: #F8FAFC;
    border: 1px dashed #C9D2DF;
    color: #536174;
    font-size: .88rem;
    line-height: 1.55;
}

.gj-score-legend {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: .45rem;
    margin: .8rem 0 1rem;
}

.gj-score-chip {
    padding: .58rem .3rem;
    text-align: center;
    border-radius: 12px;
    border: 1px solid #DCE4EF;
    background: white;
    color: #526174;
    font-size: .78rem;
    font-weight: 700;
}

.gj-score-chip b {
    color: #176FD1;
    font-size: .96rem;
}

.gj-profile-card {
    padding: 1rem 1.1rem;
    border: 1px solid var(--gj-line);
    border-radius: 16px;
    background: rgba(255,255,255,.86);
    min-height: 92px;
}

.gj-profile-label {
    color: var(--gj-muted);
    font-size: .78rem;
    font-weight: 700;
    margin-bottom: .35rem;
}

.gj-profile-value {
    color: var(--gj-ink);
    font-size: 1.08rem;
    font-weight: 850;
}

.gj-review-box {
    padding: 1rem 1.1rem;
    margin: .65rem 0;
    border-left: 4px solid var(--gj-blue);
    border-radius: 0 14px 14px 0;
    background: #F7FAFF;
    color: #344054;
    line-height: 1.65;
}

.gj-team-card {
    padding: 1.05rem 1.05rem .95rem;
    min-height: 170px;
    border: 1px solid var(--gj-line);
    border-radius: 18px;
    background: rgba(255,255,255,.94);
    box-shadow: 0 8px 24px rgba(16, 42, 67, 0.06);
    margin-bottom: .8rem;
}

.gj-team-card h4 {
    margin: 0 0 .55rem 0;
    color: var(--gj-ink);
    font-size: 1.03rem;
}

.gj-team-score {
    font-size: 1.45rem;
    font-weight: 900;
    color: var(--gj-blue);
    margin-bottom: .38rem;
}

.gj-team-meta {
    color: var(--gj-muted);
    font-size: .82rem;
    line-height: 1.65;
}

.gj-status {
    display: inline-block;
    margin-top: .55rem;
    padding: .25rem .58rem;
    border-radius: 999px;
    font-size: .74rem;
    font-weight: 800;
}

.gj-status-done { background: #E6F8F0; color: #087A52; }
.gj-status-live { background: #EEF4FF; color: #185DB2; }

.gj-danger-note {
    padding: .85rem 1rem;
    border: 1px solid #FFD1D1;
    border-radius: 14px;
    background: #FFF5F5;
    color: #A23A3A;
    font-size: .88rem;
    line-height: 1.55;
}

/* Native Streamlit components */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: var(--gj-line) !important;
    border-radius: 18px !important;
    background: var(--gj-card);
    box-shadow: 0 8px 28px rgba(16, 42, 67, 0.055);
}

[data-testid="stMetric"] {
    background: rgba(255,255,255,.94);
    border: 1px solid var(--gj-line);
    border-radius: 16px;
    padding: .95rem 1rem;
    box-shadow: 0 7px 22px rgba(16,42,67,.05);
}

[data-testid="stMetricLabel"] {
    color: var(--gj-muted);
}

[data-testid="stMetricValue"] {
    color: var(--gj-navy);
    font-weight: 850;
}

.stButton > button,
.stDownloadButton > button,
[data-testid="stFormSubmitButton"] > button {
    min-height: 2.85rem;
    border-radius: 12px;
    border: 1px solid #D6DFEB;
    font-weight: 800;
    transition: transform .12s ease, box-shadow .12s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 18px rgba(16, 72, 140, .12);
}

button[kind="primary"],
[data-testid="stFormSubmitButton"] button[kind="primary"] {
    border: 0 !important;
    color: white !important;
    background: linear-gradient(110deg, var(--gj-blue), var(--gj-cyan)) !important;
    box-shadow: 0 9px 22px rgba(22,119,255,.23) !important;
}

[data-baseweb="select"] > div,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
    border-radius: 12px !important;
}

[data-testid="stRadio"] [role="radiogroup"] {
    gap: .45rem;
}

[data-testid="stRadio"] label {
    padding: .44rem .65rem;
    border-radius: 10px;
    border: 1px solid #DFE6EF;
    background: white;
}

[data-testid="stRadio"] label:hover {
    border-color: #9FC7F7;
    background: #F6FAFF;
}

[data-testid="stProgress"] > div > div > div > div {
    background: linear-gradient(90deg, var(--gj-blue), var(--gj-cyan));
}

.stTabs [data-baseweb="tab-list"] {
    gap: .45rem;
    padding: .35rem;
    border-radius: 14px;
    background: #EDF2F8;
}

.stTabs [data-baseweb="tab"] {
    height: 2.65rem;
    border-radius: 10px;
    font-weight: 750;
}

.stTabs [aria-selected="true"] {
    background: white;
    box-shadow: 0 4px 12px rgba(16,42,67,.08);
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--gj-line);
    border-radius: 14px;
    overflow: hidden;
}

@media (max-width: 760px) {
    [data-testid="stAppViewContainer"] > .main .block-container {
        padding-left: .85rem;
        padding-right: .85rem;
        padding-top: .75rem;
    }

    .gj-hero {
        padding: 1.45rem 1.2rem;
        border-radius: 20px;
    }

    .gj-hero h1 {
        font-size: 1.78rem;
    }

    .gj-score-legend {
        grid-template-columns: repeat(2, 1fr);
    }

    [data-testid="stRadio"] [role="radiogroup"] {
        flex-direction: column;
        align-items: stretch;
    }

    [data-testid="stRadio"] label {
        width: 100%;
    }
}
</style>
"""


def inject_global_styles() -> None:
    """모든 페이지에서 공통 CSS를 적용합니다."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_public_hero() -> None:
    st.markdown(
        """
        <section class="gj-hero">
          <div class="gj-hero-kicker">☀️ GONJIAM HIGH SCHOOL · SUMMER 2026</div>
          <h1>곤지암고등학교 여름 AI 해커톤</h1>
          <p>아이디어의 가치와 AI 기술의 가능성을 함께 평가하는 프로젝트 심사 시스템</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_admin_hero() -> None:
    st.markdown(
        """
        <section class="gj-hero">
          <div class="gj-hero-kicker">📊 LIVE OPERATIONS DASHBOARD</div>
          <h1>여름 AI 해커톤 실시간 집계</h1>
          <p>곤지암고등학교 운영진 전용 · 제출 현황, 순위, 평가 의견을 한 화면에서 확인합니다.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand() -> None:
    st.markdown(
        """
        <div class="gj-mini-brand">
          <strong>곤지암고등학교</strong>
          <span>2026 Summer AI Hackathon</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stage_header(stage: str, stage_number: int) -> None:
    safe_stage = escape(stage)
    st.markdown(
        f'<div class="gj-section-label gj-stage-{stage_number}">{safe_stage}</div>',
        unsafe_allow_html=True,
    )


def render_question_intro(
    index: int,
    title: str,
    text: str,
    checkpoint: str,
) -> None:
    st.markdown(
        f"""
        <div class="gj-question-head">
          <span class="gj-question-number">Q{index}</span>
          <span class="gj-question-title">{escape(title)}</span>
        </div>
        <div class="gj-question-text">{escape(text)}</div>
        <div class="gj-checkpoint"><b>CHECK POINT</b> · {escape(checkpoint)}</div>
        """,
        unsafe_allow_html=True,
    )


def render_score_legend(score_labels: dict[int, str]) -> None:
    chips = "".join(
        f'<div class="gj-score-chip"><b>{score}점</b><br>{escape(label)}</div>'
        for score, label in score_labels.items()
    )
    st.markdown(
        f'<div class="gj-score-legend">{chips}</div>',
        unsafe_allow_html=True,
    )


def render_profile_card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="gj-profile-card">
          <div class="gj-profile-label">{escape(label)}</div>
          <div class="gj-profile-value">{escape(value)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_team_card(
    team: str,
    score: float | None,
    judge_count: int,
    team_count: int,
    status: str,
) -> None:
    score_text = f"{score:.2f}점" if score is not None else "집계 전"
    status_class = "gj-status-done" if status == "평가 완료" else "gj-status-live"
    st.markdown(
        f"""
        <div class="gj-team-card">
          <h4>{escape(team)}</h4>
          <div class="gj-team-score">{escape(score_text)}</div>
          <div class="gj-team-meta">
            심사위원 {judge_count}/6<br>
            참가팀 {team_count}/5
          </div>
          <span class="gj-status {status_class}">{escape(status)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
