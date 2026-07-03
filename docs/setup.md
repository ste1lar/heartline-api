# 환경 재구축 가이드 (새 컴퓨터 / 새 클론)

> 이 레포를 새 컴퓨터에 clone했거나 로컬 환경이 깨졌을 때, 개발 가능한 상태까지 복원하는 절차.
> **코드·문서는 git으로 따라오지만, 아래 세 가지는 컴퓨터마다 새로 만들어야 한다:**
>
> | 안 따라오는 것 | 복원 방법 |
> |---|---|
> | `.venv/` (파이썬 환경) | 2번 — requirements.txt로 재설치 |
> | `.env` (비밀값) | 3번 — .env.example 복사 후 채움 |
> | PostgreSQL 서버 + **DB 데이터** | 4~5번 — 서버 설치, DB 생성, migrate로 스키마 재생성 |
>
> ⚠️ **DB 안의 데이터(가입한 유저 등)는 git에 없다.** 다른 컴퓨터에는 스키마만 재생성되고 데이터는 비어 있는 게 정상. 계정은 `createsuperuser`로 다시 만들면 된다.

macOS 기준. (다른 OS는 PostgreSQL/uv 설치 방법만 다르고 이후 절차는 동일)

## 1. 클론 & 사전 도구

```bash
git clone https://github.com/ste1lar/heartline-api.git
cd heartline-api

# uv가 없다면 (파이썬 버전/가상환경 관리자)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 2. 파이썬 환경

```bash
uv python install 3.13
uv venv --python 3.13
source .venv/bin/activate            # 프롬프트에 (.venv) 표시 확인
uv pip install -r requirements.txt
```

## 3. 환경변수

```bash
cp .env.example .env
# SECRET_KEY 생성 후 .env의 DJANGO_SECRET_KEY에 붙여넣기
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 4. PostgreSQL 설치 & 기동

```bash
brew install postgresql@17
brew services start postgresql@17    # launchd 등록 — 이후 로그인 시 자동 시작
export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"   # keg-only라 PATH 필요
```

## 5. DB 계정/데이터베이스 생성

`.env`의 `DATABASE_URL`(기본: `postgres://heartline:heartline@localhost:5432/heartline`)과 일치해야 한다.

```bash
psql postgres -c "CREATE ROLE heartline WITH LOGIN PASSWORD 'heartline' CREATEDB;"
createdb -O heartline heartline
```

## 6. 스키마 반영 & 관리자 계정

```bash
python manage.py migrate             # 마이그레이션으로 테이블 재생성
python manage.py createsuperuser     # 예: admin@heartline.test
```

## 7. 동작 확인

```bash
python manage.py check               # 이상 없음이어야 함
python manage.py runserver
```

- http://127.0.0.1:8000/admin/ — 관리자 로그인
- http://127.0.0.1:8000/api/schema/swagger-ui/ — API 문서

## 8. (Claude와 이어서 학습할 때)

새 세션/새 컴퓨터의 Claude는 이 레포의 `CLAUDE.md`를 자동으로 읽는다. 진행 위치는 [roadmap.md](roadmap.md)의 체크리스트와 상단 "다음 작업" 포인터가 알려준다. 대화 기록 자체는 이어지지 않으므로, **세션을 넘길 가치가 있는 결정·개념은 반드시 docs/에 남기는 것**이 이 프로젝트의 운영 원칙이다.
