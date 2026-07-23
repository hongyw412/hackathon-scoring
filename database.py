"""Supabase 연결과 평가 데이터 접근 로직."""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any, Mapping

from dotenv import load_dotenv
from supabase import Client, create_client

from config import (
    MAX_COMMENT_LENGTH,
    MAX_MEMBER_NAME_LENGTH,
    MIN_COMMENT_LENGTH,
    MIN_MEMBER_NAME_LENGTH,
    QUESTION_IDS,
    TEAM_MEMBERS_PER_TEAM,
    TEAMS,
)
from security import verify_access_code

load_dotenv()
LOGGER = logging.getLogger(__name__)


class AppDataError(RuntimeError):
    """사용자에게 안내할 데이터 처리 오류."""


class AuthenticationError(AppDataError):
    """사용자 인증 실패."""


class DuplicateEvaluationError(AppDataError):
    """같은 평가자가 같은 팀을 중복 평가함."""


class ValidationError(AppDataError):
    """입력값 또는 평가 규칙 위반."""


class ConfigurationError(AppDataError):
    """환경변수 또는 앱 설정 누락."""


def get_secret(name: str, default: str | None = None) -> str | None:
    """환경변수를 우선 읽고, 없으면 Streamlit Secrets를 확인합니다."""
    environment_value = os.getenv(name)
    if environment_value not in (None, ""):
        return environment_value

    try:
        import streamlit as st

        if name in st.secrets:
            value = st.secrets[name]
            return str(value) if value is not None else default
    except Exception:
        pass

    return default


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """서버 전용 Supabase 클라이언트를 생성해 재사용합니다."""
    url = get_secret("SUPABASE_URL")
    service_key = (
        get_secret("SUPABASE_SECRET_KEY")
        or get_secret("SUPABASE_SERVICE_ROLE_KEY")
    )

    if not url:
        raise ConfigurationError("SUPABASE_URL 환경변수가 없습니다.")

    if not service_key:
        raise ConfigurationError(
            "SUPABASE_SECRET_KEY 또는 SUPABASE_SERVICE_ROLE_KEY가 없습니다."
        )

    return create_client(url, service_key)


def _extract_data(response: Any) -> list[dict[str, Any]]:
    data = getattr(response, "data", None)
    return list(data) if data is not None else []


def _is_unique_violation(error: Exception) -> bool:
    message = str(error).lower()
    return (
        "23505" in message
        or "duplicate key" in message
        or "evaluations_judge_target_unique" in message
        or "evaluations_team_member_target_unique" in message
    )


def _is_member_limit_violation(error: Exception) -> bool:
    message = str(error).lower()
    return (
        "team member limit exceeded" in message
        or "팀원 4명" in message
    )


def normalize_member_name(member_name: str) -> str:
    """팀원이 입력한 이름을 공백 기준으로 정리하고 검증합니다."""
    normalized = " ".join(str(member_name).strip().split())

    if len(normalized) < MIN_MEMBER_NAME_LENGTH:
        raise ValidationError("참가팀 팀원 이름을 입력해주세요.")

    if len(normalized) > MAX_MEMBER_NAME_LENGTH:
        raise ValidationError(
            f"팀원 이름은 {MAX_MEMBER_NAME_LENGTH}자 이하로 입력해주세요."
        )

    return normalized


def _validate_scores(scores: Mapping[str, int]) -> dict[str, int]:
    if set(scores.keys()) != set(QUESTION_IDS):
        raise ValidationError("모든 평가 문항에 점수를 선택해주세요.")

    normalized: dict[str, int] = {}
    for question_id in QUESTION_IDS:
        score = scores[question_id]
        if isinstance(score, bool) or not isinstance(score, int):
            raise ValidationError("점수는 1부터 5까지의 정수여야 합니다.")
        if score < 1 or score > 5:
            raise ValidationError("점수는 1점부터 5점까지만 입력할 수 있습니다.")
        normalized[question_id] = score

    return normalized


def _validate_comment(comment: str, label: str) -> str:
    normalized = " ".join(str(comment).strip().split())

    if len(normalized) < MIN_COMMENT_LENGTH:
        raise ValidationError(
            f"{label}은(는) {MIN_COMMENT_LENGTH}자 이상 작성해주세요."
        )

    if len(normalized) > MAX_COMMENT_LENGTH:
        raise ValidationError(
            f"{label}은(는) {MAX_COMMENT_LENGTH}자 이하로 작성해주세요."
        )

    return normalized


class EvaluationRepository:
    """평가 시스템 데이터베이스 작업."""

    def __init__(self, client: Client | None = None) -> None:
        self.client = client or get_supabase_client()

    def authenticate_user(
        self,
        username: str,
        user_type: str,
        access_code: str,
    ) -> dict[str, Any]:
        try:
            response = (
                self.client.table("users")
                .select("*")
                .eq("username", username)
                .eq("user_type", user_type)
                .limit(1)
                .execute()
            )
            rows = _extract_data(response)
        except Exception as error:
            LOGGER.exception("User lookup failed: %s", error)
            raise AppDataError(
                "데이터베이스 연결에 실패했습니다. 잠시 후 다시 시도해주세요."
            ) from error

        if not rows:
            raise AuthenticationError("등록되지 않은 사용자입니다.")

        user = rows[0]
        if not user.get("is_active", False):
            raise AuthenticationError("비활성화된 사용자입니다.")

        if not verify_access_code(
            access_code,
            str(user.get("access_code_hash", "")),
        ):
            raise AuthenticationError("인증 코드가 올바르지 않습니다.")

        user.pop("access_code_hash", None)
        return user

    def get_all_users(self) -> list[dict[str, Any]]:
        try:
            response = (
                self.client.table("users")
                .select(
                    "id,username,user_type,team_name,is_active,created_at"
                )
                .order("user_type")
                .order("username")
                .execute()
            )
            return _extract_data(response)
        except Exception as error:
            LOGGER.exception("Fetching users failed: %s", error)
            raise AppDataError("사용자 목록을 불러오지 못했습니다.") from error

    def get_all_evaluations(self) -> list[dict[str, Any]]:
        try:
            response = (
                self.client.table("evaluations")
                .select("*")
                .order("target_team")
                .order("submitted_at")
                .execute()
            )
            return _extract_data(response)
        except Exception as error:
            LOGGER.exception("Fetching evaluations failed: %s", error)
            raise AppDataError("평가 결과를 불러오지 못했습니다.") from error

    def get_team_member_names(self, evaluator_id: str) -> set[str]:
        """해당 참가팀 계정으로 실제 제출한 팀원 이름을 반환합니다."""
        try:
            response = (
                self.client.table("evaluations")
                .select("evaluator_member_name")
                .eq("evaluator_id", evaluator_id)
                .eq("evaluator_type", "team")
                .execute()
            )
            rows = _extract_data(response)
        except Exception as error:
            LOGGER.exception("Fetching team member names failed: %s", error)
            raise AppDataError(
                "팀원 등록 현황을 확인하지 못했습니다."
            ) from error

        return {
            str(row.get("evaluator_member_name", "")).strip()
            for row in rows
            if str(row.get("evaluator_member_name", "")).strip()
        }

    def get_user_evaluations(
        self,
        evaluator_id: str,
        evaluator_type: str,
        member_name: str | None = None,
    ) -> list[dict[str, Any]]:
        try:
            query = (
                self.client.table("evaluations")
                .select("*")
                .eq("evaluator_id", evaluator_id)
            )
            if evaluator_type == "team":
                normalized_name = normalize_member_name(member_name or "")
                query = query.eq(
                    "evaluator_member_name",
                    normalized_name,
                )

            response = query.order("target_team").execute()
            return _extract_data(response)
        except ValidationError:
            raise
        except Exception as error:
            LOGGER.exception("Fetching user evaluations failed: %s", error)
            raise AppDataError(
                "평가 완료 내역을 불러오지 못했습니다."
            ) from error

    def get_evaluation(
        self,
        evaluator_id: str,
        evaluator_type: str,
        target_team: str,
        member_name: str | None = None,
    ) -> dict[str, Any] | None:
        try:
            query = (
                self.client.table("evaluations")
                .select("*")
                .eq("evaluator_id", evaluator_id)
                .eq("target_team", target_team)
            )
            if evaluator_type == "team":
                normalized_name = normalize_member_name(member_name or "")
                query = query.eq(
                    "evaluator_member_name",
                    normalized_name,
                )

            response = query.limit(1).execute()
            rows = _extract_data(response)
            return rows[0] if rows else None
        except ValidationError:
            raise
        except Exception as error:
            LOGGER.exception("Fetching evaluation failed: %s", error)
            raise AppDataError(
                "기존 평가 내역을 확인하지 못했습니다."
            ) from error

    def save_evaluation(
        self,
        user: dict[str, Any],
        target_team: str,
        scores: Mapping[str, int],
        strength_comment: str,
        improvement_comment: str,
        allow_edit: bool,
    ) -> dict[str, Any]:
        normalized_scores = _validate_scores(scores)
        normalized_strength = _validate_comment(
            strength_comment,
            "잘한 점",
        )
        normalized_improvement = _validate_comment(
            improvement_comment,
            "보완할 점",
        )

        if target_team not in TEAMS:
            raise ValidationError("존재하지 않는 평가 대상 팀입니다.")

        evaluator_type = str(user.get("user_type", ""))
        evaluator_team = user.get("team_name")

        if evaluator_type not in {"team", "judge"}:
            raise ValidationError("올바르지 않은 평가자 유형입니다.")

        if evaluator_type == "team" and evaluator_team == target_team:
            raise ValidationError("참가팀은 자기 팀을 평가할 수 없습니다.")

        evaluator_id = str(user.get("id", ""))
        if not evaluator_id:
            raise ValidationError("로그인 정보가 올바르지 않습니다.")

        member_name: str | None = None
        if evaluator_type == "team":
            member_name = normalize_member_name(
                str(user.get("member_name", ""))
            )

        existing = self.get_evaluation(
            evaluator_id=evaluator_id,
            evaluator_type=evaluator_type,
            target_team=target_team,
            member_name=member_name,
        )
        if existing and not allow_edit:
            raise DuplicateEvaluationError(
                "이미 해당 팀에 대한 평가를 제출했습니다."
            )

        if evaluator_type == "team" and not existing:
            known_names = self.get_team_member_names(evaluator_id)
            if (
                member_name not in known_names
                and len(known_names) >= TEAM_MEMBERS_PER_TEAM
            ):
                raise ValidationError(
                    "이 팀 인증 코드로는 팀원 4명까지만 평가할 수 있습니다. "
                    "이름 철자를 확인하거나 운영진에게 문의해주세요."
                )

        payload = {
            "evaluator_id": evaluator_id,
            "evaluator_name": str(user.get("username", "")),
            "evaluator_type": evaluator_type,
            "evaluator_team": evaluator_team,
            "evaluator_member_name": member_name,
            "target_team": target_team,
            "scores": normalized_scores,
            "total_score": sum(normalized_scores.values()),
            "strength_comment": normalized_strength,
            "improvement_comment": normalized_improvement,
        }

        try:
            if existing:
                response = (
                    self.client.table("evaluations")
                    .update(payload)
                    .eq("id", existing["id"])
                    .select("*")
                    .execute()
                )
            else:
                response = (
                    self.client.table("evaluations")
                    .insert(payload)
                    .select("*")
                    .execute()
                )

            rows = _extract_data(response)
            if not rows:
                raise AppDataError("평가 저장 결과를 확인하지 못했습니다.")
            return rows[0]
        except AppDataError:
            raise
        except Exception as error:
            LOGGER.exception("Saving evaluation failed: %s", error)
            if _is_unique_violation(error):
                raise DuplicateEvaluationError(
                    "이미 해당 팀에 대한 평가를 제출했습니다."
                ) from error
            if _is_member_limit_violation(error):
                raise ValidationError(
                    "이 팀 인증 코드로는 팀원 4명까지만 평가할 수 있습니다."
                ) from error
            raise AppDataError(
                "평가 저장에 실패했습니다. 잠시 후 다시 시도해주세요."
            ) from error

    def admin_update_evaluation(
        self,
        evaluation_id: str,
        scores: Mapping[str, int],
        strength_comment: str,
        improvement_comment: str,
    ) -> dict[str, Any]:
        normalized_scores = _validate_scores(scores)
        normalized_strength = _validate_comment(
            strength_comment,
            "잘한 점",
        )
        normalized_improvement = _validate_comment(
            improvement_comment,
            "보완할 점",
        )
        payload = {
            "scores": normalized_scores,
            "total_score": sum(normalized_scores.values()),
            "strength_comment": normalized_strength,
            "improvement_comment": normalized_improvement,
        }

        try:
            response = (
                self.client.table("evaluations")
                .update(payload)
                .eq("id", evaluation_id)
                .select("*")
                .execute()
            )
            rows = _extract_data(response)
            if not rows:
                raise AppDataError("수정할 평가 결과를 찾지 못했습니다.")
            return rows[0]
        except AppDataError:
            raise
        except Exception as error:
            LOGGER.exception("Admin update failed: %s", error)
            raise AppDataError("평가 결과 수정에 실패했습니다.") from error

    def delete_evaluation(self, evaluation_id: str) -> None:
        try:
            self.client.table("evaluations").delete().eq(
                "id",
                evaluation_id,
            ).execute()
        except Exception as error:
            LOGGER.exception("Delete evaluation failed: %s", error)
            raise AppDataError("평가 결과 삭제에 실패했습니다.") from error

    def reset_evaluations(self) -> None:
        try:
            self.client.table("evaluations").delete().not_.is_(
                "id",
                "null",
            ).execute()
        except Exception as error:
            LOGGER.exception("Reset evaluations failed: %s", error)
            raise AppDataError(
                "전체 평가 데이터 초기화에 실패했습니다."
            ) from error
