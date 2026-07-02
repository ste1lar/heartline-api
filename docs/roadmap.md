# 개발 로드맵 & 진행 체크리스트

> 이 파일이 진행 상태의 **단일 진실 공급원(SSOT)** 입니다.
> 항목을 끝낼 때마다 `[ ]` → `[x]` 로 바꾸세요.

범례: `[ ]` 할 일 · `[~]` 진행 중 · `[x]` 완료

---

## Phase 0 — 환경 세팅 (Claude가 수행, 설명만)

- [x] uv로 Python 3.13 설치
- [x] `.venv` 가상환경 생성
- [x] Django 스택 설치 + `requirements.txt` 고정
- [x] PostgreSQL 17 설치 + `heartline` DB/role 생성 + 연결 확인
- [x] `.gitignore`, `.env.example`, 학습 문서(`CLAUDE.md`, `docs/*`) 작성

## Phase 1 — 프로젝트 세팅 (여기부터 사용자가 타이핑)

- [x] `django-admin startproject config .` 로 프로젝트 골격 생성
- [x] `apps/` 디렉토리 + 7개 앱 생성 (core, accounts, profiles, matching, payments, reports, notifications)
- [x] 초기 scaffolding 커밋 + origin/main 푸시
- [x] settings 분리: `config/settings/{base,dev,prod}.py`
- [x] django-environ로 `.env` 로딩, PostgreSQL 연결
- [x] INSTALLED_APPS 등록 + 각 앱 `apps.py`의 `name` 수정
- [x] DRF / SimpleJWT / drf-spectacular / CORS 설정
- [ ] `core` 앱: `TimeStampedModel`, `SoftDeleteModel` 추상모델
- [ ] **Custom User 모델** (`AUTH_USER_MODEL`) — 마이그레이션 *전에* 반드시 먼저!
- [ ] 첫 `migrate` + `createsuperuser` + `runserver` 동작 확인
- [ ] Swagger UI 접속 확인

## Phase 2 — accounts

- [ ] User 모델 + `UserStatus` (REGISTERED…WITHDRAWN)
- [ ] 커스텀 UserManager (email 기반)
- [ ] IdentityVerification 모델 (1:1, PII 분리)
- [ ] 회원가입 / 로그인(JWT) / 로그아웃 API
- [ ] `GET /users/me/`
- [ ] `POST /auth/mock-verify/` → status VERIFIED 전이
- [ ] Django Admin 등록

## Phase 3 — profiles

- [ ] DatingProfile (review_status, MBTI 등)
- [ ] ProfilePhoto (최대 3장, 대표 1장, 썸네일)
- [ ] ProfileReviewLog (심사 이력)
- [ ] 프로필 생성/수정 API + 사진 업로드 API
- [ ] 프로필 제출 API (DRAFT→PENDING, User.status→PROFILE_PENDING)
- [ ] 관리자 승인/반려 API (+Notification, +ReviewLog)
- [ ] Django Admin 심사 액션

## Phase 4 — matching (추천 + 하트)

- [ ] DailyRecommendation (user+recommended_user+date unique)
- [ ] 오늘의 추천 조회 API (없으면 4명 자동 생성, services.py)
- [ ] 추천 view/dismiss 처리
- [ ] Like 모델 (from_user+to_user unique)
- [ ] 하트 보내기 API + 상호 하트 시 Match 생성 (services.py)
- [ ] 받은/보낸 하트 목록 API

## Phase 5 — matches / contact reveal

- [ ] Match 모델 (작은 id=user_a 규칙, expires_at=+3일)
- [ ] Match 목록/상세 API (조회 시 만료 자동 처리)
- [ ] Match 수동 만료 API
- [ ] ContactReveal 모델 (match+viewer unique)
- [ ] 연락처 열람 권한 로직 (IsContactRevealViewer)

## Phase 6 — payments

- [ ] Payment 모델 (READY…REFUNDED, MOCK provider)
- [ ] 연락처 열람 결제 생성 API (status=READY, 5000원)
- [ ] Mock 결제 완료 API → ContactReveal 생성 + Match=REVEALED + Notification
- [ ] ContactReveal 조회 API (결제자만 전화번호 반환)

## Phase 7 — reports / blocks / notifications

- [ ] Report 모델 + 신고 생성/내 신고 API
- [ ] Block 모델 + 차단/해제 API (+ 추천/하트/매칭에 반영)
- [ ] Notification 모델 + 목록/읽음/전체읽음 API

## Phase 8 — 테스트 / 정리

- [ ] 모델 테스트 (제약/상태전이)
- [ ] Serializer validation 테스트
- [ ] Permission 테스트
- [ ] 매칭 생성 / 연락처 열람 / 신고·차단 테스트
- [ ] Swagger 문서 정리
- [ ] seed data 스크립트
