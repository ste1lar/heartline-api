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
- **차이**: Next의 `NEXT_PUBLIC_*` 는 브라우저 번들에 실려 나가지만, 백엔드 env는 **항상 서버에만** 남는다(클라이언트 노출 0). 그래서 SECRET_KEY·DB 비밀번호를 여기 둔다.

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
| `AUTH_PASSWORD_VALIDATORS` | 회원가입 시 비밀번호 규칙 검사(너무 짧음/흔함/숫자만/개인정보 유사) | 폼 validation 규칙 모음 |
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

**장점**: 프론트 개발자가 백엔드 코드를 열어보지 않아도 API 계약을 한눈에 확인하고 바로 테스트할 수 있다. 코드만 짜면 문서가 자동으로 따라오고 항상 코드와 일치한다.

> 곁다리 개념: 에디터의 빨간/회색 줄(정적 분석)과 실제 실행 결과는 별개다. 최종 판단은 `python manage.py check`·실행으로. (TS 빨간 줄이 떠도 런타임은 정상이던 경험과 같은 결.)

---

## [2026-07-03] Phase 1 개념 정리 — 추상모델 & Custom User

### A. 추상모델 (`abstract = True`)
- 공통 필드 묶음(`created_at` 등)을 만들어 상속시키는 것. `abstract = True`면 **자기 테이블은 안 만들고** 상속받는 모델에 컬럼이 복사됨.
- **TS 비유**: `interface Timestamped` 를 extends — 단, 타입만이 아니라 실제 DB 컬럼+동작까지 딸려옴.
- `auto_now_add`(생성 시 1회) vs `auto_now`(저장할 때마다 갱신).
- `null=True`(DB에 NULL 허용) vs `blank=True`(검증 층에서 빈 값 허용) — **층이 다르다.**

### B. Custom User = 완성품 상속이 아니라 부품 조립
```python
class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
```
- `AbstractBaseUser` = 비밀번호/last_login 등 **로그인 뼈대만**
- `PermissionsMixin` = is_superuser·권한/그룹 (Admin에 필요)
- `TimeStampedModel` = 우리가 만든 시각 필드
- **프론트 비유**: 완성된 `<LoginForm>` 상속이 아니라 **headless 프리미티브(Radix류) 조합**. 파이썬은 다중 상속으로 mixin 여러 개를 섞는다.
- `is_active`(Django: 로그인 가능 스위치) vs `status`(우리: 비즈니스 상태머신) — 역할이 다르다. 탈퇴 시 둘 다 세팅.

### C. 이 파일의 이름들은 3부류다 (모르는 이름을 만났을 때 판별법)
1. **Django가 주는 것** (호출만): `normalize_email`, `set_password`(평문→해시! 직접 대입 금지), `save()`, 각종 `models.*Field`
2. **Django가 요구하는 계약** (이름 고정, 내용은 우리가): `create_user`/`create_superuser`(createsuperuser 명령이 이 이름을 찾음), `USERNAME_FIELD`, `REQUIRED_FIELDS`, `objects`(쿼리 진입점 ≈ Prisma client), `class Meta`(모델 설정 객체)
   → TS 비유: **인터페이스 구현** — 메서드명은 정해져 있고 몸통만 내가 채움
3. **순수 우리 것** (이름 자유): `UserStatus`, `status`, `_create_user` (`_` 접두사 = private **관례**, TS `#`처럼 강제 아님)

### D. 파이썬 문법 ↔ TS 대응표
| Python | TS/JS |
|---|---|
| `self` (첫 인자로 명시) | `this` (암묵적) |
| `**extra_fields` | `...rest` |
| `dict.setdefault(k, v)` | `obj.k ??= v` |
| `TextChoices` 의 `X = "DB값", "라벨"` 튜플 | union 타입 + 라벨 매핑. DB값/표시용 분리 |
| `__str__` | `toString()` (Admin 목록 표시 등) |
| `raise ValueError(...)` | `throw new Error(...)` |

### E. 이번에 겪은 함정
- `AUTH_USER_MODEL = "accounts.User"` — 앱이 `apps/accounts` 에 있어도 **app_label은 마지막 조각**. `"apps.accounts.User"` 아님.
- `WIDHDRAWN = "WITHDRAWN", ...` 오타 — **DB값은 맞는데 파이썬 속성명이 틀린** 케이스. 당장은 멀쩡하다가 `UserStatus.WITHDRAWN` 참조하는 순간 AttributeError. enum 키 오타는 린터가 못 잡으니 값·키 둘 다 확인.

---

## [2026-07-03] 전체 그림 — 이 맥에서 데이터베이스는 어떻게 존재하고 움직이는가

> DBeaver 접속, db.sqlite3, brew, "heartline이 뭐지?"까지 — 흩어져 있던 질문들을 하나의 그림으로 정리한다.

### 1. 등장인물 정리

| 이름 | 정체 | 언제 생겼나 | 적용 범위 |
|---|---|---|---|
| **Homebrew (brew)** | 맥용 패키지 매니저 (npm의 맥 버전) | 예전에 사용자가 설치 | 맥 전체 |
| **PostgreSQL 17** | DB를 관리하는 **소프트웨어**(DBMS) | 6/30 Phase 0에서 `brew install` | **맥 전체** (프로젝트 한정 아님) |
| **PostgreSQL 서버 프로세스** | 위 소프트웨어가 5432 포트에 상시 실행 중인 것 | 6/30 `brew services start` 이후 계속 | 맥 전체 |
| **`heartline` (계정)** | PostgreSQL **내부의** 사용자 계정 | 6/30 `CREATE ROLE` 명령으로 생성 | Postgres 서버 안 |
| **`heartline` (데이터베이스)** | 그 서버가 담고 있는 DB 하나 | 6/30 `createdb` 명령으로 생성 | 이 프로젝트용 |
| **`db.sqlite3`** | SQLite용으로 생겼던 **빈 파일** (삭제됨) | 6/30 첫 runserver 부산물 | — |
| **`.venv/`** | 이 프로젝트 전용 파이썬 환경 | 6/30 | **이 프로젝트만** (대조용) |

핵심: **PostgreSQL(소프트웨어)과 heartline(그 안의 데이터베이스)은 포토샵과 .psd 파일의 관계**다. "DB"라는 단어가 이 둘 모두에 쓰이기 때문에 헷갈린다.

### 2. PostgreSQL은 언제 어떻게 이 맥에 들어왔고, 왜 프로젝트 한정이 아닌가

- Phase 0 환경 세팅 때(6/30) `brew install postgresql@17`로 설치됐다. 이는 **맥 전역 설치**다 — `.venv`처럼 프로젝트 폴더 안에 들어있는 것이 아니라, 맥에 하나 깔린 서버 프로그램이다.
- 한 대의 PostgreSQL 서버는 **여러 데이터베이스를 동시에 담을 수 있다.** 다음 프로젝트를 시작하면 서버를 새로 깔 필요 없이 `createdb`로 데이터베이스만 하나 더 만들면 된다. (지금도 서버 안에는 `heartline` 외에 관리용 기본 DB인 `postgres` 등이 함께 들어 있다.)
- 응용 프로그램 폴더/Launchpad에 안 보이는 이유: 그 목록은 **GUI 앱(.app)만** 보여준다. brew는 CLI 프로그램을 `/opt/homebrew/Cellar/`에 설치하고 실행 파일을 `/opt/homebrew/bin/`에 연결한다. `npm i -g typescript`로 설치한 tsc가 응용 프로그램 폴더에 안 보이는 것과 같다. brew로 설치된 목록은 `brew list`로 본다.
- **brew 없이도 PostgreSQL은 쓸 수 있다.** brew는 여러 설치 경로 중 하나일 뿐이다:
  - 공식 GUI 인스톨러 (윈도우 사용자는 주로 이걸 쓴다 — 윈도우에도 winget/chocolatey라는 brew 대응물이 있긴 하다)
  - **Postgres.app** — 진짜 .app 형태의 맥 앱. 이걸로 설치하면 응용 프로그램 폴더에 보인다
  - Docker 컨테이너
  - 아예 로컬 설치 없이 클라우드 DB 사용 (AWS RDS, Supabase, Neon 등)

### 3. brew가 "실행 관리"까지 하는 것처럼 보이는 이유

정확한 직관이었다 — 패키지 매니저의 본업은 설치/삭제이지 프로세스 실행 관리가 아니다. 실체는 이렇다:

- 맥에는 **launchd**라는 진짜 서비스 관리자가 OS 차원에 존재한다 (부팅/로그인 시 백그라운드 프로그램을 띄우고 유지하는 역할).
- `brew services start postgresql@17`는 **launchd에 등록을 대행**해주는 편의 명령일 뿐이다. 실제로 `~/Library/LaunchAgents/homebrew.mxcl.postgresql@17.plist`라는 등록 파일을 만들어 넣고, 이후 프로세스를 띄우고 유지하는 주체는 launchd(OS)다.
- 즉 "brew가 OS처럼 군다"가 아니라 "**brew가 OS 기능을 빌려 쓰기 쉽게 포장**해준다"가 맞다. Node 생태계로 치면 pm2가 하는 일을 OS에 위임하는 셈.

### 4. 계정이 세 층으로 존재한다 — "heartline은 내가 설정한 적 없는데?"

이 시스템에는 서로 **완전히 독립적인 계정 체계가 세 층** 있다:

| 층 | 계정 | 만든 주체/시점 | 용도 |
|---|---|---|---|
| macOS | `higgs` | 맥 살 때 | 컴퓨터 로그인 |
| **PostgreSQL 내부** | **`heartline` / 비밀번호 `heartline`** | **6/30 Phase 0 세팅 때 Claude가 `CREATE ROLE heartline WITH LOGIN PASSWORD 'heartline'` 실행** | DB 서버 접속 (Django·DBeaver가 사용) |
| 우리 서비스 | `admin@heartline.test` | 7/3 `createsuperuser` | Django Admin 로그인 |

- PostgreSQL은 **자체 계정 시스템**을 갖고 있다. 우리가 만드는 서비스가 자체 User 테이블을 갖는 것과 정확히 같은 구조 — DB 서버 입장에서 Django와 DBeaver는 "로그인해서 들어오는 클라이언트"다.
- 같은 세팅 때 데이터베이스도 `createdb -O heartline heartline`으로 만들어졌다. 즉 **계정명 = 비밀번호 = DB명이 전부 "heartline"** 인데, 학습용이라 단순하게 통일한 것이다(실서비스라면 셋은 서로 달라야 하고 비밀번호는 무작위여야 한다). 세 가지가 같은 단어라 "이게 뭐지?"가 된 것.
- 이 정보가 기록된 곳이 바로 `.env`의 접속 문자열이다:

```
DATABASE_URL = postgres://heartline:heartline@localhost:5432/heartline
                          └계정명   └비밀번호  └호스트    └포트  └DB명
```

Django는 이 한 줄을 파싱해 접속하고, DBeaver에 입력하는 값도 정확히 이 다섯 조각이다.

### 5. 파일형 DB vs 서버형 DB — db.sqlite3의 정체

- **SQLite = 파일형 DB.** DB 엔진이 라이브러리로 앱 안에 포함되고, 데이터는 파일 하나(`db.sqlite3`)에 저장된다. 별도 서버가 없다. 질문에 답하면: 맞다, **db.sqlite3는 "로컬 파일형 DB"가 될 뻔한 파일**이었다. 다만 우리 것은 0바이트 빈 껍데기였다 — 6/30 첫 runserver 때(설정 분리 전, Django 기본 설정이 SQLite였던 시점) 연결 시도만으로 생성됐고, 이후 PostgreSQL로 전환되며 버려졌다(삭제 완료).
- **PostgreSQL = 서버형 DB.** 별도 프로세스가 5432 포트에서 상시 대기하고, 모든 클라이언트는 네트워크로 접속한다.
- 구분 축은 "로컬 vs 배포"가 아니라 **"파일 직접 접근 vs 서버 경유"** 다. 지금 우리 PostgreSQL도 로컬(내 맥)에 있다. `localhost:5432`의 Postgres는 `localhost:3000`의 Next dev 서버와 같은 부류 — 서버지만 배포된 것은 아니다.

서버 3개의 생명주기 비교:

| 프로세스 | 뜨는 시점 | 죽는 시점 | 포트 |
|---|---|---|---|
| Next dev | `npm run dev` | Ctrl+C | 3000 |
| Django | `python manage.py runserver` | Ctrl+C | 8000 |
| **PostgreSQL** | `brew services start` 한 번 → 이후 맥 로그인 시 자동(launchd) | `brew services stop` 해야만 | 5432 |

```
[Django :8000] ──┐
[DBeaver]────────┼──▶ [PostgreSQL 서버 :5432] ──▶ /opt/homebrew/var/postgresql@17/ (내부 바이너리 파일)
[psql]───────────┘      (셋은 서로 독립적인 클라이언트)
```

- Django는 PostgreSQL의 클라이언트 중 하나일 뿐이므로, **runserver를 꺼도 DBeaver 접속에는 아무 영향이 없다.** 반대로 PostgreSQL을 끄면 Django·DBeaver 모두 접속에 실패한다.

파일이 어차피 내 맥에 있는데 왜 서버를 거치는가:
1. **동시성 조정** — Django, DBeaver, psql이 동시에 같은 데이터를 읽고 쓸 때 잠금·트랜잭션을 조정할 심판이 필요하다. 각자 파일을 직접 열면 서로 덮어써서 데이터가 깨진다. (엑셀 파일 돌려쓰기 vs Google Sheets)
2. **내부 포맷** — 인덱스, WAL(장애 복구 로그) 등 복잡한 바이너리 구조라 서버만 안전하게 다룰 수 있다.
3. **배포 시 무변경** — 대화가 네트워크 기반이므로 운영에서 DB가 다른 머신으로 가도 host만 바꾸면 된다. 로컬 개발과 운영이 같은 방식이 된다.

### 6. 데이터의 물리적 실체와 보호

- 데이터 파일은 결국 이 맥의 `/opt/homebrew/var/postgresql@17/`에 있고, 소유자가 본인이므로 `rm -rf` 한 번이면 (sudo 없이도) 전부 사라진다. **DB 서버는 자물쇠가 아니라 교통정리 역할**이다 — 네트워크(5432)로 오는 요청은 비밀번호로 통제하지만, 파일시스템 접근은 막지 못한다.
- 이는 PostgreSQL의 결함이 아니라 모든 소프트웨어의 공통 조건이다. node_modules도, git 저장소도, OS 파일도 소유자의 삭제 명령 앞에서는 동일하다.
- **운영 DB가 보호되는 실제 방식**: 아무도 셸 접근을 할 수 없는 별도 머신에 두고, 외부에는 5432 포트(+비밀번호+방화벽)만 연다. 삭제 명령을 입력할 경로 자체가 차단되는 것이다. 보안의 본질은 서버 프로그램이 아니라 **머신 접근 통제**이고, 최후의 방어선은 백업(`pg_dump`)이다.
- 로컬 학습 DB는 날아가도 `migrate` + 시드 데이터로 재생 가능하므로 부담 없이 실험해도 된다.

---

## 📌 별도 레퍼런스 문서

- **[project-structure.md](project-structure.md)** — 폴더/파일별 역할, 요청이 흐르는 길, "어디에 뭘 쓰지?" 가이드 (Next 비유 포함). 구조가 헷갈릴 때 여기부터.

---

## 자주 헷갈리는 개념 메모 (수시 추가)

- **`makemigrations` vs `migrate`**: 전자는 모델→마이그레이션 파일 생성(설계도), 후자는 그 설계도를 실제 DB에 적용(시공).
- **Custom User는 첫 migrate 전에 정해야 한다**: 이미 `auth.User`로 마이그레이트한 뒤 바꾸면 매우 번거로움. 그래서 Phase 1에서 가장 먼저 만든다.
