# CLAUDE.md — heartline-api

> 이 파일은 Claude(및 사람)가 이 레포에서 작업할 때 읽는 프로젝트 가이드입니다.

## 프로젝트 한 줄 요약

모바일 웹앱 기반 **소개팅 MVP 백엔드** (Django + DRF + PostgreSQL).
본인인증 → 프로필 심사 → 추천 → 하트 → 매칭 → 연락처 열람(결제) 흐름.

**이 레포의 목적은 운영이 아니라 "Django/DRF 학습 + 포트폴리오"** 입니다.

## ⚠️ 작업 방식 (가장 중요)

이 프로젝트는 **학습용**입니다. 진행 방식은 **가이드형**으로 합의됨:

- **Claude의 역할**: 단계마다 개념을 설명하고, 초안 코드를 채팅으로 보여주고, *왜* 그렇게 쓰는지 설명한다. 사용자가 친 코드를 리뷰하고 고친다. 학습 문서(`docs/`)를 갱신한다.
- **사용자의 역할**: `config/`, `apps/` 안의 **모든 Django 코드를 직접 타이핑한다.**
- **Claude가 직접 파일을 쓰는 범위**: 학습 문서(`CLAUDE.md`, `docs/*`), 순수 환경/ops 설정(`.gitignore`, `.env.example`, `requirements.txt`)에 한함.
- ❗ **사용자가 명시적으로 요청하지 않는 한, `apps/`·`config/`의 Django 코드를 Claude가 대신 작성하지 않는다.** 막혔을 때 리뷰·수정·힌트만 제공. (예외: 사용자가 인정한 단순 영문 오타는 Claude가 직접 수정 가능)

## 학습자 프로필 & 커뮤니케이션 규칙

- 사용자는 **프론트엔드 개발자** (Next.js / React / TypeScript / SCSS Modules).
- 백엔드 개념 설명 시 **프론트 생태계 비유를 적극 활용**한다 (예: Swagger UI ≈ Storybook, `objects` ≈ Prisma client, settings 상속 ≈ 스프레드 덮어쓰기). 단, **억지 비유는 금지** — 자연스러운 대응이 있을 때만.
- **`docs/` 문서는 문어체로 쓴다.** git에 올라가는 문서에 채팅체("ㅇㅇ", "~임" 등)를 쓰지 않는다. 채팅 대화는 편하게 해도 됨.
- 새로 등장한 개념은 질문-답 파편이 아니라 **전체 그림을 아우르는 정리**로 learning-log에 남긴다.

## 기술 스택 (고정 버전)

| 분류 | 버전 |
|---|---|
| Python | 3.13.14 (uv로 관리) |
| Django | 5.2.x LTS |
| djangorestframework | 3.17.x |
| djangorestframework-simplejwt | 5.5.x (JWT 인증) |
| drf-spectacular | 0.29.x (OpenAPI 문서) |
| django-filter | 25.x |
| psycopg | 3.3.x (PostgreSQL 어댑터) |
| Pillow | 12.x (이미지) |
| django-cors-headers | 4.9.x |
| django-environ | 0.14.x (.env 로딩) |
| PostgreSQL | 17.x (Homebrew) |

## 디렉토리 구조 (목표)

```
heartline-api/
├── manage.py
├── config/                 # 프로젝트 패키지
│   ├── settings/           # base / dev / prod 분리
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/                   # 모든 Django 앱
│   ├── core/               # 공통 추상모델, 권한, 페이지네이션, 유틸
│   ├── accounts/           # User, IdentityVerification
│   ├── profiles/           # DatingProfile, ProfilePhoto, ProfileReviewLog
│   ├── matching/           # DailyRecommendation, Like, Match, ContactReveal
│   ├── payments/           # Payment (Mock)
│   ├── reports/            # Report, Block
│   └── notifications/      # Notification
├── docs/
│   ├── roadmap.md          # 8단계 로드맵 + 진행 체크리스트 + "다음 작업" 포인터
│   ├── learning-log.md     # 배운 것/함정/결정 기록
│   ├── project-structure.md # 폴더/파일 역할 레퍼런스 (Next 비유)
│   ├── setup.md            # 새 컴퓨터/새 클론 환경 재구축 절차
│   └── erd.md              # ERD + 모델 레퍼런스 + 상태머신
├── requirements.txt
├── .env.example
└── .env                    # (git 제외)
```

## 자주 쓰는 명령어

가상환경 활성화부터:
```bash
cd /Users/higgs/workspace/heartline-api
source .venv/bin/activate          # 프롬프트에 (.venv) 표시되면 OK
```

Django 작업:
```bash
python manage.py runserver         # 개발 서버 (http://127.0.0.1:8000)
python manage.py makemigrations     # 모델 변경 → 마이그레이션 파일 생성
python manage.py migrate            # 마이그레이션 DB 반영
python manage.py createsuperuser    # 관리자 계정 (Django Admin용)
python manage.py shell              # 대화형 셸
python manage.py startapp <name> apps/<name>   # 새 앱 생성
```

패키지 관리 (uv):
```bash
uv pip install "<패키지>"           # 설치 (반드시 .venv 활성화 상태에서)
uv pip freeze > requirements.txt    # 잠금
```

PostgreSQL (Homebrew, keg-only라 PATH 필요):
```bash
export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"
brew services start postgresql@17   # 서버 시작
brew services stop  postgresql@17   # 서버 중지
psql -U heartline -h localhost -d heartline   # 접속 (비번: heartline)
```

API 문서 (서버 실행 중):
```
http://127.0.0.1:8000/api/schema/swagger-ui/    # Swagger UI
http://127.0.0.1:8000/api/schema/redoc/          # ReDoc
```

## 핵심 설계 원칙 (절대 어기지 말 것)

1. **민감정보 분리**: 로그인 정보만 `User`. 실명/전화/생년월일/성별은 `IdentityVerification`. 공개 프로필은 `DatingProfile`.
2. **전화번호·실명·이메일·생년월일은 일반 API 응답에 절대 포함하지 않는다.** 연락처는 오직 `ContactReveal` 조회 API(결제한 본인)에서만 반환.
3. **상태로 권한 제어**: 서비스 이용 가능 여부는 `User.status`, 프로필 심사는 `DatingProfile.review_status`.
4. **레이어 분리**: View(요청/응답) ↔ Serializer(검증/직렬화) ↔ Service(비즈니스 로직) ↔ Permission(접근제어). 매칭 생성·결제·연락처 열람 같은 트랜잭션 로직은 `services.py`에.
5. **MVP 범위 엄수**: 채팅/푸시/SMS/실제 PG/프리미엄/위치기반 없음. 결제는 Mock.

## 현재 진행 상태

진행 상태는 [docs/roadmap.md](docs/roadmap.md)의 체크리스트가 **단일 진실 공급원(SSOT)** 입니다. 새 세션은 거기부터 확인하세요. 단계를 완료하거나 다음 안내를 시작할 때마다 roadmap의 체크박스와 상단 "다음 작업" 포인터를 갱신합니다.

새 컴퓨터에서 clone한 경우: [docs/setup.md](docs/setup.md) 절차로 환경(.venv/.env/PostgreSQL)을 먼저 재구축해야 합니다. **DB 데이터는 git에 없으므로** 컴퓨터마다 `migrate` + `createsuperuser`로 새로 만듭니다.
