# 학습 로그 (learning-log)

> 배운 개념, 빠졌던 함정, 내린 결정을 시간순으로 남깁니다.
> 새 항목은 **맨 아래에 추가**. 형식:
>
> ```
> ## [날짜] 주제
> - **무엇을**: ...
> - **왜**: ...
> - **함정/주의**: ...
> ```

---

## [2026-06-30] Phase 0 — 환경 세팅

- **무엇을**: uv로 Python 3.13 가상환경 생성 → Django 5.2 LTS 스택 설치 → PostgreSQL 17 설치 후 `heartline` DB/role 생성.
- **왜 uv?**: 기존 시스템 Python이 3.8(EOL)이라 최신 Django를 못 돌림. uv는 Python 버전 설치 + venv를 빠르게 처리. 워크플로는 전통적 `pip + requirements.txt`와 동일하게 유지(Django 학습에 집중하려고 uv 고유 개념은 최소화).
- **함정**: `uv pip install`이 기존에 활성화돼 있던 옛 venv(3.8)를 자동으로 잡아갔다. → `uv pip install --python /…/.venv/bin/python` 으로 **대상 인터프리터를 명시**해서 해결. 교훈: venv가 여러 개면 어떤 파이썬에 깔리는지 항상 확인.
- **함정**: Homebrew PostgreSQL은 **keg-only**라 `psql` 등이 기본 PATH에 없다. → `export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"` 필요.
- **결정**: DB는 학습 초기부터 실서비스와 동일하게 PostgreSQL 사용 (SQLite 미사용). 인증은 모바일 웹앱 API라서 JWT(simplejwt).
- **결정**: Django는 6.0(최신) 대신 **5.2 LTS** — 자료가 가장 풍부하고 2028까지 지원되어 학습 중 검색이 쉬움.

---

## 자주 헷갈리는 개념 메모 (수시 추가)

- **`makemigrations` vs `migrate`**: 전자는 모델→마이그레이션 파일 생성(설계도), 후자는 그 설계도를 실제 DB에 적용(시공).
- **Custom User는 첫 migrate 전에 정해야 한다**: 이미 `auth.User`로 마이그레이트한 뒤 바꾸면 매우 번거로움. 그래서 Phase 1에서 가장 먼저 만든다.
