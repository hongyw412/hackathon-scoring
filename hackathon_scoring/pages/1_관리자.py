"""평가자 앱과 함께 배포할 때 사용하는 관리자 멀티페이지 진입점."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from admin import main  # noqa: E402

main()
