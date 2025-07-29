# Supabase 설정 가이드

## 📋 개요
이 가이드는 Flask 카페 주문 관리 시스템을 Supabase와 연동하는 방법을 설명합니다.

## 🚀 1단계: Supabase 프로젝트 생성

### 1.1 Supabase 계정 생성
1. [Supabase](https://supabase.com)에 접속
2. GitHub 계정으로 로그인
3. "New Project" 클릭

### 1.2 프로젝트 설정
1. **Organization**: 선택 또는 생성
2. **Name**: `cafe-order-system` (원하는 이름)
3. **Database Password**: 안전한 비밀번호 설정 (기억해두세요!)
4. **Region**: 가까운 지역 선택 (예: `Northeast Asia (Tokyo)`)
5. **Pricing Plan**: Free tier 선택
6. "Create new project" 클릭

## 🗄️ 2단계: 데이터베이스 스키마 설정

### 2.1 SQL Editor 접속
1. 프로젝트 대시보드에서 "SQL Editor" 클릭
2. "New query" 클릭

### 2.2 스키마 실행
1. `supabase_schema.sql` 파일의 내용을 복사
2. SQL Editor에 붙여넣기
3. "Run" 클릭하여 실행

### 2.3 확인사항
- Tables 탭에서 다음 테이블들이 생성되었는지 확인:
  - `cafe_menu`
  - `cafe_order`
  - `cafe_order_item`

## 🔑 3단계: API 키 및 URL 확인

### 3.1 프로젝트 설정 접속
1. 프로젝트 대시보드에서 "Settings" 클릭
2. "API" 탭 클릭

### 3.2 필요한 정보 복사
- **Project URL**: `https://[project-id].supabase.co`
- **anon public key**: `eyJ...`로 시작하는 긴 문자열
- **service_role key**: `eyJ...`로 시작하는 긴 문자열 (관리자용)

## ⚙️ 4단계: 환경 변수 설정

### 4.1 .env 파일 생성
프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가:

```env
# Supabase 설정
SUPABASE_URL=https://[your-project-id].supabase.co
SUPABASE_ANON_KEY=eyJ[your-anon-key]
SUPABASE_SERVICE_ROLE_KEY=eyJ[your-service-role-key]

# 관리자 계정 설정
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Flask 설정
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

### 4.2 실제 값으로 교체
- `[your-project-id]`: 실제 프로젝트 ID
- `eyJ[your-anon-key]`: 실제 anon key
- `eyJ[your-service-role-key]`: 실제 service role key
- `your-secret-key-here`: 안전한 시크릿 키

## 📦 5단계: Python 패키지 설치

### 5.1 가상환경 활성화
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 5.2 패키지 설치
```bash
pip install -r requirements.txt
```

## 🧪 6단계: 연결 테스트

### 6.1 애플리케이션 실행
```bash
python app.py
```

### 6.2 연결 확인
콘솔에서 다음 메시지 확인:
```
✅ Supabase 연결 성공
```

### 6.3 데이터베이스 초기화
1. 브라우저에서 `http://localhost:4011` 접속
2. "데이터베이스 초기화" 링크 클릭
3. 성공 메시지 확인

## 🔧 7단계: 고급 설정

### 7.1 Row Level Security (RLS)
스키마에서 RLS가 자동으로 설정됩니다:
- 모든 사용자가 메뉴를 읽을 수 있음
- 관리자만 데이터를 수정할 수 있음

### 7.2 실시간 기능 (선택사항)
Supabase의 실시간 기능을 활용하려면:
1. 프로젝트 설정에서 "Realtime" 활성화
2. 클라이언트 코드에 실시간 구독 추가

### 7.3 스토리지 설정 (이미지 업로드)
메뉴 이미지 업로드를 위해:
1. "Storage" 탭에서 새 버킷 생성: `menu-images`
2. RLS 정책 설정
3. 업로드 권한 설정

## 🚨 문제 해결

### 연결 오류
```
❌ Supabase 연결 실패
```
**해결방법:**
1. 환경 변수 확인
2. 프로젝트 URL과 API 키 재확인
3. 네트워크 연결 확인

### 인증 오류
```
401 Unauthorized
```
**해결방법:**
1. API 키가 올바른지 확인
2. 프로젝트가 활성 상태인지 확인

### 테이블 오류
```
relation "cafe_menu" does not exist
```
**해결방법:**
1. SQL Editor에서 스키마 재실행
2. 테이블이 생성되었는지 확인

## 📊 모니터링

### 7.1 Supabase 대시보드
- **Database**: 테이블, 쿼리, 성능 모니터링
- **Auth**: 사용자 인증 관리
- **Storage**: 파일 업로드 관리
- **Logs**: 실시간 로그 확인

### 7.2 애플리케이션 로그
Flask 애플리케이션의 로그를 확인하여 오류 추적

## 🔒 보안 고려사항

### 7.1 환경 변수
- `.env` 파일을 `.gitignore`에 추가
- 프로덕션에서는 환경 변수 사용

### 7.2 API 키 관리
- `anon key`는 공개 가능
- `service_role key`는 절대 공개하지 마세요

### 7.3 RLS 정책
- 필요한 최소 권한만 부여
- 정기적으로 정책 검토

## 📈 성능 최적화

### 7.1 인덱스
스키마에 자동으로 인덱스가 생성됩니다:
- 카테고리별 검색
- 주문 날짜별 검색
- 상태별 검색

### 7.2 쿼리 최적화
- 필요한 컬럼만 선택
- 적절한 WHERE 조건 사용
- 페이지네이션 구현

## 🎯 다음 단계

1. **실시간 기능 추가**: 주문 상태 실시간 업데이트
2. **이미지 스토리지**: Supabase Storage 활용
3. **사용자 인증**: Supabase Auth 통합
4. **백업 설정**: 자동 백업 구성
5. **모니터링**: 성능 모니터링 설정

## 📞 지원

문제가 발생하면:
1. Supabase 문서 확인
2. GitHub Issues 검색
3. 커뮤니티 포럼 활용
4. Supabase 지원팀 문의

---

**참고**: 이 가이드는 Supabase의 최신 기능을 반영하고 있습니다. Supabase가 업데이트되면 일부 내용이 변경될 수 있습니다. 