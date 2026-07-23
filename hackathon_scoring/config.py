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
            "제안하는 문제가 사회적 또는 필요로 하는 사람에게 "
            "명확한 가치(공익성)를 제공하는가?"
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
            "타겟 고객의 페인포인트(Pain Point)와 해결하고자 하는 "
            "최종 목표가 구체적인 상황이나 지표로 명확히 정의되었는가?"
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
            "제시한 아이디어가 정의한 문제를 해결하는 데 있어 논리적인 "
            "비약이 없으며, 비용·시간 대비 효율적인 타당한 해결책인가?"
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
            "기존 시장에 이미 존재하는 유사 솔루션과 비교했을 때, "
            "이 팀만의 확실한 우위나 독창적인 접근 방식이 존재하는가?"
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
            "AI가 문제의 핵심 병목을 해결하며, 규칙 기반 시스템이나 "
            "일반 소프트웨어보다 명확한 이점을 제공하는가?"
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
            "현존하는 IT 기술 수준과 시장 환경을 고려했을 때 실제 "
            "상용화 프로덕트로 구현 가능한가? 문제의 실재성을 "
            "뒷받침하는 인터뷰·통계·관찰·사용자 반응 등의 근거가 있는가?"
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
            "문제 제기, 원인 분석, 솔루션 제시, 기대효과로 이어지는 "
            "기획의 전체 흐름이 빈틈없이 탄탄하게 구조화되어 있는가?"
        ),
        "checkpoint": (
            "심사위원이 중간에 길을 잃지 않고 논리적으로 따라올 수 있는가"
        ),
    },
    {
        "id": "q8",
        "stage": "🗣️ 3단계: 논리 구조 및 전달력 (Execution & Pitching)",
        "title": "아이디어의 파급력 및 확장성",
        "text": (
            "아이디어가 구현되었을 때 사회에 미치는 긍정적 영향력에 "
            "대한 예측이 잘 드러나 있고 납득 가능한가?"
        ),
        "checkpoint": (
            "일회성에 그치지 않고 지속 가능하게 성장할 수 있는 모델인가"
        ),
    },
    {
        "id": "q9",
        "stage": "🗣️ 3단계: 논리 구조 및 전달력 (Execution & Pitching)",
        "title": "발표 완성도",
        "text": (
            "발표 자료의 시각적 완성도가 높고, 발표자가 팀의 비전과 "
            "서비스 핵심을 제한 시간 내에 설득력 있게 전달했는가?"
        ),
        "checkpoint": (
            "핵심 텍스트와 도식을 적절히 활용해 청중의 이목을 집중시키는가"
        ),
    },
    {
        "id": "q10",
        "stage": "🤝 4단계: 창업가적 태도 (Attitude & Team Fit)",
        "title": "태도 및 디펜스 능력",
        "text": (
            "날카로운 질문이나 비판에 감정적으로 방어하지 않고 논리적으로 "
            "수용·답변하며, 타 팀을 존중하고 적극적으로 질문해 발전을 "
            "도모하는 성숙한 커뮤니케이션 능력을 보여주는가?"
        ),
        "checkpoint": (
            "'내가 틀릴 수도 있다'는 유연함과 피드백 수용 능력이 있는가"
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
