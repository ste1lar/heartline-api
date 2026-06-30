# heartline-api

모바일 웹앱 기반 **소개팅 MVP 백엔드** — Django + DRF + PostgreSQL 학습 프로젝트.

본인인증 → 프로필 심사 → 매일 추천 → 하트 → 상호 하트 매칭 → 3일 내 연락처 열람(Mock 결제) 흐름.

## 빠른 시작

```bash
# 1) 가상환경
source .venv/bin/activate

# 2) 환경변수
cp .env.example .env        # 그리고 SECRET_KEY 채우기

# 3) DB (이미 설치/생성됨)
export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"
brew services start postgresql@17

# 4) Django
python manage.py migrate
python manage.py runserver
```

## 문서

- [CLAUDE.md](CLAUDE.md) — 프로젝트 가이드 / 작업 방식 / 명령어
- [docs/roadmap.md](docs/roadmap.md) — 8단계 로드맵 + 진행 체크리스트 (SSOT)
- [docs/erd.md](docs/erd.md) — ERD / 모델 / 상태머신 / 제약
- [docs/learning-log.md](docs/learning-log.md) — 배운 것 / 함정 / 결정 기록

## 스택

Python 3.13 · Django 5.2 LTS · DRF 3.17 · SimpleJWT · drf-spectacular · PostgreSQL 17
