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

## [2026-06-30] Phase 1 시작 — 프로젝트 골격 + 첫 커밋

- **무엇을**: `django-admin startproject config .` 로 `config/` 패키지와 `manage.py` 생성, `apps/` 아래 7개 앱 생성. `runserver`로 로켓 화면 확인. 첫 커밋 후 `git push -u origin main`.
- **`startproject config .` 의 `.`**: "현재 폴더에" 생성하라는 뜻. 안 찍으면 `config/config/`로 한 겹 더 깊어진다.
- **`apps/__init__.py`**: 이게 있어야 `apps`가 패키지가 되어 `apps.accounts`로 import 가능.
- **절대 커밋하면 안 되는 것**: `.venv/`(가상환경 — 용량 크고 OS 종속), `.env`(비밀키/DB 비번), `__pycache__/`, `db.sqlite3`. → `.gitignore`가 막아준다. 커밋 전 `git status`로 staged 목록을 꼭 눈으로 확인하는 습관.
- **함정 예방**: 아직 `migrate` 안 함. Custom User를 먼저 만들고 첫 migrate를 해야 나중에 안 꼬인다.

---

## [2026-06-30] Phase 1 개념 정리 — base.py 설정들 / Swagger / drf-spectacular

> "설정인 건 알겠는데 이름만 보고 추측했던" 것들을 하나씩 제대로. (프론트 Next/React/TS 비유 포함)

### A. settings를 base / dev / prod 로 쪼갠다는 것
- 거대한 설정 파일 하나 대신 **공통(base) + 환경별 차이(dev/prod)** 로 나눈다.
- `dev.py`의 `from .base import *` = "base의 모든 설정을 가져온 뒤, 아래에서 몇 개만 덮어쓴다".
  - **JS 비유**: `const devConfig = { ...baseConfig, DEBUG: true }` (스프레드 후 덮어쓰기).
  - **Next 비유**: `.env` / `.env.development` / `.env.production` 를 환경마다 자동으로 갈아끼우는 발상과 같음.

### B. `.env` + django-environ
- 비밀값·환경값을 코드가 아니라 `.env` 에 두고 `env("KEY")` 로 읽는다. ≈ `process.env.KEY`.
- **차이**: Next의 `NEXT_PUBLIC_*` 는 브라우저 번들에 실려 나가지만, 백엔드 env는 **항상 서버에만** 남는다(클라 노출 0). 그래서 SECRET_KEY·DB 비번을 여기 둔다.

### C. base.py 설정 블록 — 하나씩 무슨 일을 하나
| 설정 | 하는 일 | 프론트 비유 / 메모 |
|---|---|---|
| `BASE_DIR` | 프로젝트 루트 절대경로. `.env`·`media` 등 다른 경로의 기준점 | 경로 계산 기준(cwd 느낌) |
| `SECRET_KEY` | 세션·CSRF·JWT 서명에 쓰는 **마스터 키**. 유출되면 보안 붕괴 | 서버 전용 시크릿 |
| `DEBUG` | `True`면 에러 시 상세 디버그 페이지 노출(개발용). **운영은 반드시 False** | `NODE_ENV` 개발/운영 갈림 |
| `ALLOWED_HOSTS` | 이 서버가 응답해 줄 도메인 화이트리스트 (Host 헤더 위조 방어) | — |
| `INSTALLED_APPS` | **켤 기능(앱) 목록.** 기본(admin/auth)+서드파티(DRF 등)+우리 앱 7개. 여기 없으면 그 앱의 모델·admin·명령이 전부 죽어 있음 | package.json deps를 "실제 등록"까지 |
| `MIDDLEWARE` | 모든 요청이 뷰에 닿기 전(응답은 역순) 순서대로 통과하는 **파이프라인**: 보안헤더→세션→CORS→CSRF→인증… | Next/Express 미들웨어 체인 |
| `ROOT_URLCONF` | URL 라우팅의 시작 모듈 = `config/urls.py` | 라우터 루트 |
| `TEMPLATES` | 서버사이드 HTML 템플릿 엔진. 우린 API 위주라 거의 안 쓰지만 **Django Admin이 사용** | SSR 템플릿 엔진 |
| `WSGI_APPLICATION` | 운영 웹서버(gunicorn 등)가 앱을 찾는 진입점 | 서버 엔트리포인트 |
| `DATABASES` | DB 연결정보. `env.db()` 가 `DATABASE_URL` 을 파싱 → psycopg3로 PostgreSQL 연결 | DB 커넥션 설정 |
| `AUTH_PASSWORD_VALIDATORS` | 회원가입 시 비번 규칙 검사(너무 짧음/흔함/숫자만/개인정보 유사) | 폼 validation 규칙 모음 |
| `LANGUAGE_CODE`·`TIME_ZONE`·`USE_TZ` | 언어(ko-kr)·시간대(Asia/Seoul). `USE_TZ=True`면 **DB엔 UTC 저장, 표시할 때 현지시간 변환** | dayjs/Intl로 tz 다루기 |
| `STATIC_URL` vs `MEDIA_URL`/`MEDIA_ROOT` | static=개발자 자산(css/js/admin), **media=사용자 업로드(프로필 사진)** | `public/` vs 업로드 스토리지 |
| `DEFAULT_AUTO_FIELD` | 모델 PK 기본 타입 = BigAutoField(64bit 자동증가 정수) | auto-increment id |
| `REST_FRAMEWORK` | DRF 전역 기본값 뭉치: 인증=JWT, 기본권한=로그인필수, 스키마=spectacular, 페이지 20, 필터 | 라우터/클라이언트 전역 기본설정 |
| `SIMPLE_JWT` | JWT 토큰 수명: access 짧게(30분)/refresh 길게(7일) | 토큰 만료 정책 |
| `SPECTACULAR_SETTINGS` | 자동 생성될 API 문서의 메타(제목·설명·버전) | 아래 D 참고 |
| `CORS_ALLOWED_ORIGINS` | 브라우저에서 **다른 출처(프론트 :3000)** 가 이 API를 부를 수 있게 허용 | 바로 그 CORS |

> 한 줄 요약: base.py = **"이 서버가 어떻게 동작할지에 대한 규칙 전부"**. 각 대문자 상수는 Django/DRF가 정해둔 "약속된 이름"이라, 철자가 정확해야 인식된다.

### D. Swagger 3형제 — OpenAPI / drf-spectacular / Swagger UI
헷갈리는 세 단어가 사실 **역할이 다른 3단 구조**다:

1. **OpenAPI** = *규격(계약서)*. "이 API엔 이런 엔드포인트가 있고, 뭘 받고 뭘 돌려준다"를 JSON/YAML로 적은 **표준 명세**. → GraphQL 스키마나 프론트-백이 공유하는 TS 타입 같은 "계약서".
2. **drf-spectacular** (스펙타쿨러) = *자동 생성기*. 이 명세를 손으로 안 쓰고, **우리 DRF 코드(뷰·시리얼라이저)를 스캔해 OpenAPI 문서를 자동 생성**. → codegen. 코드 바뀌면 문서도 자동 갱신.
3. **Swagger UI / ReDoc** = *뷰어*. 그 명세를 브라우저에서 보기 좋게 렌더링. 특히 Swagger UI는 **"Try it out" 버튼으로 실제 호출**까지 된다.
   → **프론트 비유 = Storybook.** 컴포넌트를 브라우저에서 골라 조작하듯, Swagger UI는 API 엔드포인트를 골라 눌러본다.

**왜 좋냐**: 프론트(너)가 백엔드 코드를 안 열어봐도 API 계약을 한눈에 보고 바로 테스트. 코드만 짜면 문서가 공짜로 따라오고 항상 코드와 일치.

> 곁다리 개념: 에디터의 빨간/회색 줄(정적 분석)과 실제 실행 결과는 별개다. 최종 판단은 `python manage.py check`·실행으로. (TS 빨간 줄 떠도 런타임은 되던 경험과 같은 결.)

---

## 자주 헷갈리는 개념 메모 (수시 추가)

- **`makemigrations` vs `migrate`**: 전자는 모델→마이그레이션 파일 생성(설계도), 후자는 그 설계도를 실제 DB에 적용(시공).
- **Custom User는 첫 migrate 전에 정해야 한다**: 이미 `auth.User`로 마이그레이트한 뒤 바꾸면 매우 번거로움. 그래서 Phase 1에서 가장 먼저 만든다.
