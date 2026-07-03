# 프로젝트 구조 — 뭐가 어디 있고 무슨 역할인가

> "코드 보면 대강은 알겠는데 자세히는 모르겠다" 상태를 위한 레퍼런스.
> 프론트(Next/React/TS) 경험 기준 비유 포함.

---

## 0. 큰 그림: 요청 하나가 흐르는 길

`POST /api/v1/auth/register/` 요청이 들어오면:

```
브라우저/프론트
   │
   ▼
MIDDLEWARE (settings의 그 목록. CORS → 보안 → 세션 → 인증 … 순서대로 통과)
   │
   ▼
config/urls.py ─── "api/v1/auth/ 는 accounts 앱 담당" ──▶ apps/accounts/urls.py
   │                                                       │
   ▼                                                       ▼
apps/accounts/views.py      요청 접수/응답 반환 (컨트롤러)
   │        │
   │        ├─▶ permissions.py   "이 사람이 이걸 해도 되나?" (문지기)
   │        ├─▶ serializers.py   입력 검증 + 파이썬 객체 ↔ JSON 변환
   │        └─▶ services.py      비즈니스 로직 (여러 모델 건드리는 트랜잭션)
   ▼
apps/accounts/models.py      DB 테이블 정의 (ORM)
   │
   ▼
PostgreSQL
```

**Next 비유**: `미들웨어 → 라우팅 → route handler → zod 검증 → 비즈니스 로직 → Prisma → DB` 흐름과 1:1로 대응됨.

---

## 1. 루트 파일들

| 파일/폴더 | 역할 | 프론트 비유 |
|---|---|---|
| `manage.py` | Django 명령 진입점. `runserver`, `migrate`, `shell` 등 전부 이걸 통해 실행 | `package.json`의 scripts + CLI |
| `.venv/` | 이 프로젝트 전용 파이썬+패키지 격리 공간 | `node_modules` (단, 파이썬 인터프리터까지 포함) |
| `requirements.txt` | 의존성 버전 잠금 | `package.json` + lockfile 합친 것 |
| `.env` | 비밀값 (git 제외) | `.env.local` |
| `.env.example` | .env 의 견본 (커밋됨) | `.env.example` 그대로 |
| `docs/` | 학습/설계 문서 | — |

---

## 2. `config/` — 프로젝트 전역 설정 패키지

앱이 아니라 **프로젝트 그 자체**. "서버 전체가 어떻게 도는가"만 담당.

| 파일 | 역할 |
|---|---|
| `settings/base.py` | 공통 설정 전부 (앱 목록, DB, DRF, JWT, CORS…) |
| `settings/dev.py` | 개발용 오버라이드 (`from .base import *` 후 덮어씀) |
| `settings/prod.py` | 운영용 오버라이드 (보안 강화) |
| `urls.py` | **최상위 라우팅 테이블.** 여기서 각 앱의 urls.py로 위임 |
| `wsgi.py` / `asgi.py` | 운영 웹서버(gunicorn 등)가 앱을 물고 시작하는 진입점. 직접 만질 일 거의 없음 |

**Next 비유**: `next.config.js` + 루트 라우팅 + 서버 엔트리를 합친 폴더.

---

## 3. `apps/<앱>/` — 기능 단위 모듈

Django의 "앱" = **도메인 단위로 쪼갠 기능 모듈**. Next 모노레포의 feature 패키지나, 도메인별로 나눈 `features/` 폴더와 같은 발상.

### Django가 만들어준 파일 (모든 앱 공통)

| 파일 | 역할 | 프론트 비유 |
|---|---|---|
| `models.py` | **DB 테이블 정의 (ORM).** 클래스 = 테이블, 속성 = 컬럼 | `schema.prisma` |
| `migrations/` | 모델 변경 이력 (자동 생성됨, 직접 수정 X) | `prisma/migrations/` |
| `admin.py` | 이 앱 모델을 Django Admin(관리자 화면)에 등록 | 공짜로 주는 admin 대시보드 설정 |
| `apps.py` | 앱 메타정보 (`name = "apps.accounts"`) | 패키지 매니페스트 |
| `views.py` | HTTP 요청 받고 응답 돌려주는 층 (컨트롤러) | `app/api/*/route.ts` |
| `tests.py` | 테스트 | `*.test.ts` |

### 우리가 추가할 파일 (DRF 레이어 분리 — Phase 2부터)

| 파일 | 역할 | 프론트 비유 |
|---|---|---|
| `serializers.py` | 입력 검증 + 모델 ↔ JSON 변환. **"무엇을 노출할지"도 여기서 결정** (보안 요충지) | zod 스키마 + DTO 변환 |
| `urls.py` | 이 앱의 URL 라우팅 (config/urls.py가 include) | 폴더 라우팅을 수동 선언으로 |
| `permissions.py` | 접근 제어 규칙 (IsActiveUser 등) | 라우트 가드 / 미들웨어 auth 체크 |
| `services.py` | 여러 모델을 한 번에 다루는 비즈니스 로직 (매칭 생성, 결제 처리) | 서버 액션/서비스 레이어 |

### "어디에 뭘 쓰지?" 결정 가이드

```
DB에 저장할 데이터 구조?            → models.py
요청 데이터가 유효한지? 뭘 보여줄지? → serializers.py
누가 접근 가능한지?                → permissions.py
URL을 어디에 연결할지?             → urls.py
여러 테이블 건드리는 로직?          → services.py
위 전부를 조립해서 요청에 응답?      → views.py
```

---

## 4. 우리 앱 7개의 도메인 분담

| 앱 | 담당 | 모델 |
|---|---|---|
| `core` | 공통 부품 (추상모델·공통권한·페이지네이션) — **테이블 없음** | TimeStamped/SoftDelete (추상) |
| `accounts` | 계정·로그인·본인인증 | User, IdentityVerification |
| `profiles` | 공개 프로필·사진·심사 | DatingProfile, ProfilePhoto, ProfileReviewLog |
| `matching` | 추천·하트·매칭·연락처열람 | DailyRecommendation, Like, Match, ContactReveal |
| `payments` | 결제 (Mock) | Payment |
| `reports` | 신고·차단 | Report, Block |
| `notifications` | 앱 내부 알림 | Notification |

의존 방향은 대체로 한쪽으로만: `core ← accounts ← profiles ← matching ← payments`. (matching이 accounts를 참조하는 건 OK, 역방향은 피함)

---

## 5. 헷갈리기 쉬운 것 정리

- **`config` vs `apps`**: config는 "서버 전체 설정", apps는 "기능". 비즈니스 코드는 항상 apps에.
- **앱마다 urls.py가 또 있는 이유**: config/urls.py 하나에 다 쓰면 수백 줄 됨. 앱별로 쪼개고 config는 `include()`로 위임만.
- **migrations/를 직접 수정하지 않는 이유**: `makemigrations`가 모델 변화를 diff 떠서 자동 생성. 손대면 이력이 꼬임. (git 커밋은 해야 함! — 팀원/서버가 같은 DB 구조를 재현하는 수단)
- **admin.py가 공짜인 이유**: Django가 모델 정의만 보고 CRUD 화면을 자동 생성. 등록(`admin.site.register`)만 하면 됨. 우리 프로젝트에선 "운영자 프로필 심사"를 여기서 함.
