"""곤지암고등학교 여름 AI 해커톤 행사 설정."""

from __future__ import annotations

import math

APP_TITLE = "곤지암고등학교 여름 AI 해커톤 평가"
ADMIN_TITLE = "곤지암고등학교 여름 AI 해커톤 실시간 집계"

TEAMS = [
    "석가모니",
    "제우스",
    "띵콩땅콩",
    "아름다운",
    "포세이돈",
    "라이온킹",
]

JUDGES = [
    "한아름 선생님",
    "정재우 선생님",
    "이재도 선생님",
    "박지원 멘토",
    "송민성 멘토",
    "홍연우 멘토",
]

QUESTIONS = [
    {
        "id": "q1",
        "stage": "🔍 1단계: 문제 정의 (Problem & Market)",
        "title": "문제 발견의 적절성 및 공익성",
        "text": (
            "발견한 문제가 사회적으로 의미 있고, "
            "공익에 얼마나 기여하는가?"
        ),
        "checkpoint": (
            "'누가 진짜 이 문제로 고통받고 있는가?'가 명확히 보이는가"
        ),
    },
    {
        "id": "q2",
        "stage": "🔍 1단계: 문제 정의 (Problem & Market)",
        "title": "목표의 구체성",
        "text": (
            "해결하고자 하는 문제를 명확하게 제시하고, "
            "구체적인 목표가 서술되었는가?"
        ),
        "checkpoint": (
            "추상적인 슬로건이 아닌, 뾰족하게 타겟팅된 목표가 있는가"
        ),
    },
    {
        "id": "q3",
        "stage": "🛠️ 2단계: 솔루션 및 기술 (Solution & Technology)",
        "title": "문제 해결 과정의 적합성",
        "text": (
            "제안한 문제를 해결하는데 제시한 아이디어는 "
            "얼마나 적절한가?"
        ),
        "checkpoint": (
            "'굳이 이렇게까지 풀어야 하나?'라는 의문이 들지 않는가"
        ),
    },
    {
        "id": "q4",
        "stage": "🛠️ 2단계: 솔루션 및 기술 (Solution & Technology)",
        "title": "문제 해결 과정의 참신성",
        "text": (
            "기존의 아이디어와 차별화된 점을 "
            "확실하게 보이는가?"
        ),
        "checkpoint": (
            "단순 카피캣이 아닌, 기존 한계를 극복할 '한 끗'이 있는가"
        ),
    },
    {
        "id": "q5",
        "stage": "🛠️ 2단계: 솔루션 및 기술 (Solution & Technology)",
        "title": "AI 기술 활용의 적절성",
        "text": (
            "문제 해결 아이디어(해결 과정)에 대한 설명이 "
            "구체적이고 논리적으로 잘 되어 있는가?"
        ),
        "checkpoint": (
            "AI를 빼면 아이디어의 가치가 확 떨어지는 핵심 코어인가"
        ),
    },
    {
        "id": "q6",
        "stage": "🛠️ 2단계: 솔루션 및 기술 (Solution & Technology)",
        "title": "현실적 실현 가능성",
        "text": (
            "제안한 해결 방안이 현재 기술 수준에서, "
            "현실적 예산범위 안에서 실제 구현 가능한가?"
        ),
        "checkpoint": (
            "이상향만 그리는 것이 아니라 기술적으로 납득 가능한 기획인가"
        ),
    },
    {
        "id": "q7",
        "stage": "🗣️ 3단계: 논리 구조 및 전달력 (Execution & Pitching)",
        "title": "문제 해결 과정의 구조적 완성도",
        "text": (
            "발표 자료(PPT)와 전달 방식(말하기, 흐름 등)의 "
            "완성도는 어떠한가?"
        ),
        "checkpoint": (
            "심사위원이 중간에 길을 잃지 않고 논리적으로 따라올 수 있는가"
        ),
    },
    {
        "id": "q8",
        "stage": "🗣️ 3단계: 논리 구조 및 전달력 (Execution & Pitching)",
        "title": "적극성",
        "text": (
            "3일간 다른 사람이 발표하는가? 다른 팀 발표에 "
            "적절한 질문을(모둠원 모두가 3일 중 1번 이상) 하는가?"
        ),
        "checkpoint": (
            "팀원 모두가 발표에 열심히 참여하는가?"
        ),
    },
    {
        "id": "q9",
        "stage": "🗣️ 3단계: 논리 구조 및 전달력 (Execution & Pitching)",
        "title": "발표 완성도",
        "text": (
            "발표 후 질의응답에 책임감있고 적절하게 답변하는가?"
        ),
        "checkpoint": (
            "모둠원들이 질의응답에 서로 서포트를 잘 해주는가?"
        ),
    },
    {
        "id": "q10",
        "stage": "🤝 4단계: 창업가적 태도 (Attitude & Team Fit)",
        "title": "태도 및 디펜스 능력",
        "text": (
            "다른 팀 발표를 경청하는가? 질문이나 의견을 "
            "말할 때 공격적이거나 무례하지 않은가?"
        ),
        "checkpoint": (
            "태도를 보기 위한 질문입니다!"
        ),
    },
]

SCORE_LABELS = {
    1: "매우 부족",
    2: "부족",
    3: "보통",
    4: "우수",
    5: "매우 우수",
}

JUDGE_WEIGHT = 0.5
TEAM_WEIGHT = 0.5

TEAM_MEMBERS_PER_TEAM = 4
MIN_MEMBER_NAME_LENGTH = 1
MAX_MEMBER_NAME_LENGTH = 30

ALLOW_SCORE_EDIT = False
ADMIN_REFRESH_SECONDS = 5
APP_TIMEZONE = "Asia/Seoul"

MIN_COMMENT_LENGTH = 10
MAX_COMMENT_LENGTH = 500

QUESTION_IDS = [question["id"] for question in QUESTIONS]
MAX_TOTAL_SCORE = len(QUESTIONS) * 5

EXPECTED_JUDGE_COUNT_PER_TEAM = len(JUDGES)
EXPECTED_TEAM_MEMBER_COUNT_PER_TEAM = (
    (len(TEAMS) - 1) * TEAM_MEMBERS_PER_TEAM
)
EXPECTED_EVALUATIONS_PER_TEAM = (
    EXPECTED_JUDGE_COUNT_PER_TEAM
    + EXPECTED_TEAM_MEMBER_COUNT_PER_TEAM
)
EXPECTED_TOTAL_EVALUATIONS = (
    len(TEAMS) * EXPECTED_EVALUATIONS_PER_TEAM
)


def validate_config() -> None:
    """설정 오류를 프로그램 시작 시 확인합니다."""
    if len(TEAMS) != 6:
        raise ValueError("현재 행사는 참가팀 6개로 설정되어야 합니다.")

    if len(JUDGES) != 6:
        raise ValueError("현재 행사는 심사위원 6명으로 설정되어야 합니다.")

    if TEAM_MEMBERS_PER_TEAM < 1:
        raise ValueError("팀원 수는 1명 이상이어야 합니다.")

    if not QUESTIONS:
        raise ValueError("평가 문항은 한 개 이상이어야 합니다.")

    if len(set(QUESTION_IDS)) != len(QUESTION_IDS):
        raise ValueError("평가 문항 ID가 중복되어 있습니다.")

    required_fields = {"id", "stage", "title", "text", "checkpoint"}
    for question in QUESTIONS:
        if not required_fields.issubset(question):
            raise ValueError("평가 문항 설정에 필수 항목이 누락되었습니다.")

    if len(set(TEAMS)) != len(TEAMS):
        raise ValueError("팀 이름이 중복되어 있습니다.")

    if len(set(JUDGES)) != len(JUDGES):
        raise ValueError("심사위원 이름이 중복되어 있습니다.")

    if not math.isclose(
        JUDGE_WEIGHT + TEAM_WEIGHT,
        1.0,
        rel_tol=1e-9,
        abs_tol=1e-9,
    ):
        raise ValueError("심사위원과 참가자 가중치의 합은 1이어야 합니다.")

    if MIN_COMMENT_LENGTH < 1:
        raise ValueError("평가 의견 최소 글자 수는 1자 이상이어야 합니다.")

    if MAX_COMMENT_LENGTH < MIN_COMMENT_LENGTH:
        raise ValueError("평가 의견 최대 글자 수 설정이 올바르지 않습니다.")

    if MAX_MEMBER_NAME_LENGTH < MIN_MEMBER_NAME_LENGTH:
        raise ValueError("팀원 이름 글자 수 설정이 올바르지 않습니다.")


validate_config()
