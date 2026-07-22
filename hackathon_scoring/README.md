# 해커톤 실시간 평가 시스템

6개 참가팀과 6명의 심사위원이 스마트폰 또는 노트북으로 접속하여 평가하고,
운영진이 실시간으로 제출 현황과 순위를 확인하는 Streamlit + Supabase 프로젝트입니다.

## 핵심 계산 규칙

각 발표팀은 다음 11개 평가를 받습니다.

- 심사위원 6명
- 발표팀을 제외한 참가팀 5팀

평가자 수가 6명과 5명으로 다르므로 11개 점수를 한꺼번에 평균 내지 않습니다.

```text
최종 점수
= 심사위원 평균 총점 × 0.5
+ 참가팀 평균 총점 × 0.5
```

심사위원 평가 6개와 참가팀 평가 5개가 모두 제출된 팀만 최종 순위가 확정됩니다.
그 전에는 현재까지의 50:50 계산값을 임시 점수로 표시합니다.

## 폴더 구조

```text
hackathon_scoring/
├─ app.py
├─ admin.py
├─ calculations.py
├─ config.py
├─ database.py
├─ security.py
├─ schema.sql
├─ seed_users.py
├─ seed_test_data.py
├─ requirements.txt
├─ .env.example
├─ .gitignore
├─ .streamlit/
│  ├─ config.toml
│  └─ secrets.toml.example
├─ pages/
│  └─ 1_관리자.py
└─ tests/
   ├─ test_calculations.py
   └─ test_security.py
```

## 1. Python 확인

Python 3.10 이상을 권장합니다.

```powershell
python --version
```

Windows에서 `python`이 실행되지 않으면 다음도 확인합니다.

```powershell
py --version
```

## 2. 가상환경 생성

### Windows PowerShell

```powershell
cd hackathon_scoring
py -m venv .venv
.venv\Scripts\Activate.ps1
```

PowerShell 실행 정책 오류가 나면 현재 창에서만 다음 명령을 먼저 실행합니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### macOS 또는 Linux

```bash
cd hackathon_scoring
python3 -m venv .venv
source .venv/bin/activate
```

## 3. 패키지 설치

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Supabase 프로젝트 및 테이블 생성

1. Supabase에서 새 프로젝트를 생성합니다.
2. 프로젝트의 **SQL Editor**를 엽니다.
3. 이 프로젝트의 `schema.sql` 전체를 붙여넣고 실행합니다.
4. Project Settings의 API Keys에서 서버 전용 Secret key 또는 레거시 service_role key를 확인합니다.

서버 전용 키는 데이터 전체에 접근할 수 있으므로 공개 저장소, 화면, 브라우저 코드에
절대로 노출하지 마세요.

## 5. 로컬 환경변수 설정

`.env.example`을 복사하여 `.env` 파일을 만듭니다.

### Windows

```powershell
Copy-Item .env.example .env
```

### macOS 또는 Linux

```bash
cp .env.example .env
```

`.env`에서 다음 값을 실제 값으로 바꿉니다.

```text
SUPABASE_URL=https://프로젝트주소.supabase.co
SUPABASE_SECRET_KEY=서버전용키
ADMIN_PASSWORD=운영진만아는비밀번호
```

레거시 service_role 키를 사용하는 프로젝트라면
`SUPABASE_SERVICE_ROLE_KEY`에 입력해도 됩니다.

## 6. 사용자 12명과 인증 코드 생성

```powershell
python seed_users.py
```

터미널에 참가팀 6개와 심사위원 6명의 임시 인증 코드가 한 번 출력됩니다.
코드는 안전한 곳에 복사한 뒤 각 평가자에게 개별 전달합니다. 데이터베이스에는 PBKDF2-SHA256 해시만 저장됩니다.

`seed_users.py`를 다시 실행하면 새로운 코드로 기존 해시가 갱신되므로,
행사 직전 실수로 재실행하지 않도록 주의하세요.

## 7. 로컬 실행

### 평가자 화면

```powershell
streamlit run app.py
```

브라우저에서 일반적으로 다음 주소가 열립니다.

```text
http://localhost:8501
```

`pages/1_관리자.py`가 포함되어 있으므로 사이드바의 관리자 페이지에서도
운영진 화면에 들어갈 수 있습니다. 관리자 비밀번호 입력 전에는 평가 결과가 보이지 않습니다.

### 관리자 화면만 별도로 실행

```powershell
streamlit run admin.py
```

## 8. 테스트 데이터 생성

일부 제출만 생성:

```powershell
python seed_test_data.py --mode partial
```

전체 66개 제출 생성:

```powershell
python seed_test_data.py --mode complete --clear-first
```

실제 행사 전에 테스트 데이터를 반드시 초기화하세요.
관리자 화면에서 `전체삭제`를 입력하거나 다음 명령을 사용할 수 있습니다.

```powershell
python seed_test_data.py --mode partial --clear-first
```

위 명령은 삭제 후 다시 테스트 데이터를 넣으므로, 완전히 비우려면 관리자 화면의
전체 삭제 기능을 사용하세요.

## 9. 자동 테스트

Supabase 연결 없이 점수 계산과 인증 코드 해시 기능을 검사합니다.

```powershell
pytest -q
```

## 10. Streamlit Community Cloud 배포

1. 이 폴더를 GitHub 비공개 저장소에 업로드합니다.
2. `.env`와 `.streamlit/secrets.toml`이 Git에 포함되지 않았는지 확인합니다.
3. Streamlit Community Cloud에서 **Create app**을 선택합니다.
4. 저장소, 브랜치, 진입 파일 `app.py`를 선택합니다.
5. Advanced settings의 Secrets에 다음 형식으로 입력합니다.

```toml
SUPABASE_URL = "https://프로젝트주소.supabase.co"
SUPABASE_SECRET_KEY = "서버전용키"
SUPABASE_SERVICE_ROLE_KEY = ""
SUPABASE_ANON_KEY = ""
ADMIN_PASSWORD = "운영진만아는강력한비밀번호"
```

6. 배포 후 평가자 주소를 공유합니다.
7. 관리자 페이지는 앱의 사이드바에서 들어갈 수 있으며 비밀번호로 보호됩니다.

## 11. 동시 접속 점검

행사 전에 다음 항목을 순서대로 확인합니다.

1. Chrome 일반 창과 시크릿 창에서 서로 다른 사용자로 로그인
2. 스마트폰과 노트북에서 동시에 접속
3. 여러 사용자가 같은 발표팀을 동시에 평가
4. 같은 사용자가 같은 팀을 중복 제출
5. 참가팀 계정에서 자기 팀이 평가 대상에 나타나지 않는지 확인
6. 일부 제출 상태에서 관리자 화면에 `집계 중` 표시 확인
7. 전체 11개 제출 후 `평가 완료`와 순위 표시 확인
8. 관리자 화면이 설정된 주기로 자동 갱신되는지 확인
9. CSV 파일이 한글이 깨지지 않고 열리는지 확인
10. 네트워크를 잠시 끊었을 때 사용자 친화적 오류가 표시되는지 확인

## 12. 행사 직전 체크리스트

- `config.py`의 실제 팀명과 심사위원명 수정
- 평가 문항 5개의 실제 문구 수정
- `JUDGE_WEIGHT = 0.5`, `TEAM_WEIGHT = 0.5` 확인
- 점수 수정 허용 여부 `ALLOW_SCORE_EDIT` 확인
- `python seed_users.py` 실행 후 인증 코드 안전하게 전달
- 테스트 데이터 전체 삭제
- 관리자 비밀번호 변경
- 서비스 역할/Secret 키가 GitHub에 올라가지 않았는지 확인
- 스마트폰 화면과 관리자 실시간 갱신 테스트
- CSV 다운로드 테스트

## 주요 오류

### `SUPABASE_URL 환경변수가 없습니다`

`.env` 또는 Streamlit Secrets에 주소가 없는 상태입니다.

### `relation public.users does not exist`

Supabase SQL Editor에서 `schema.sql`을 아직 실행하지 않은 상태입니다.

### `인증 코드가 올바르지 않습니다`

사용자가 잘못 입력했거나 `seed_users.py`를 다시 실행하여 인증 코드가 바뀐 경우입니다.

### `이미 해당 팀에 대한 평가를 제출했습니다`

중복 제출 방지 기능이 정상 작동한 것입니다. 수정을 허용하려면
`config.py`의 `ALLOW_SCORE_EDIT = True`로 바꿉니다.

### 관리자 화면이 갱신되지 않음

`requirements.txt`를 다시 설치하고 Streamlit 버전을 확인합니다.

```powershell
pip install -r requirements.txt --upgrade
streamlit version
```
