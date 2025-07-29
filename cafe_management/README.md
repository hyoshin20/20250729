# 카페 주문 관리 시스템 (Supabase 연동)

Flask 기반의 카페 주문 관리 시스템입니다. Supabase를 사용하여 클라우드 데이터베이스와 연동하며, 사용자 주문과 관리자 메뉴 관리 기능을 제공하는 웹 애플리케이션입니다.

## 주요 기능

### 사용자 기능
- **메뉴 조회**: 카테고리별 메뉴 목록, 품절 상태 표시
- **장바구니 관리**: 메뉴 추가/수정/삭제, 수량 조정, 특별 요청사항
- **주문하기**: 고객 정보 입력, 배달 정보, 주문 완료

### 관리자 기능
- **인증**: 관리자 로그인/로그아웃
- **매출 관리**: 일/주/월 매출 통계, 주문 목록 조회
- **메뉴 관리**: 메뉴 추가/수정/삭제, 이미지 업로드, 품절 상태 관리
- **카테고리 관리**: 카테고리 추가/삭제
- **데이터 관리**: Excel 파일 가져오기/내보내기
- **영수증 출력**: 주문 영수증 생성

## 기술 스택

- **백엔드**: Flask (Python)
- **데이터베이스**: Supabase (PostgreSQL)
- **프론트엔드**: Bootstrap 5, HTML5, CSS3, JavaScript
- **아이콘**: Font Awesome
- **세션 관리**: Flask-Session
- **파일 처리**: Werkzeug
- **클라우드 서비스**: Supabase

## 설치 및 실행

### 1. Supabase 설정

먼저 Supabase 프로젝트를 설정해야 합니다. 자세한 설정 방법은 [SUPABASE_SETUP.md](SUPABASE_SETUP.md)를 참조하세요.

### 2. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 Supabase 설정을 추가하세요:

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

### 3. 환경 설정

```bash
# 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필요한 패키지 설치
pip install -r requirements.txt
```

### 4. 애플리케이션 실행

```bash
# Flask 애플리케이션 실행
python app.py
```

### 5. 데이터베이스 초기화

브라우저에서 다음 URL에 접속하여 데이터베이스를 초기화하세요:
- `http://localhost:4011/init_db` - 샘플 데이터와 함께 데이터베이스 초기화

### 6. 접속

- **메인 페이지**: `http://localhost:4011`
- **사용자 메뉴**: `http://localhost:4011/user/menu`
- **관리자 로그인**: `http://localhost:4011/admin/login`

## 관리자 계정

기본 관리자 계정:
- **아이디**: admin
- **비밀번호**: admin123

## 프로젝트 구조

```
cafe_management/
├── app.py                 # 메인 Flask 애플리케이션
├── models.py              # 데이터베이스 모델 (참조용)
├── config.py              # 설정 파일
├── requirements.txt       # Python 패키지 목록
├── supabase_client.py     # Supabase 클라이언트
├── supabase_schema.sql    # Supabase 데이터베이스 스키마
├── SUPABASE_SETUP.md      # Supabase 설정 가이드
├── env_example.txt        # 환경 변수 예시
├── static/
│   ├── css/               # CSS 파일들
│   ├── js/                # JavaScript 파일들
│   ├── images/            # 기본 이미지들
│   └── uploads/           # 업로드된 메뉴 이미지들
├── templates/
│   ├── base.html          # 기본 템플릿
│   ├── index.html         # 메인 페이지
│   ├── user/              # 사용자 페이지들
│   │   ├── menu.html      # 메뉴 주문 페이지
│   │   └── cart.html      # 장바구니 페이지
│   └── admin/             # 관리자 페이지들
│       ├── login.html     # 관리자 로그인
│       ├── dashboard.html # 관리자 대시보드
│       ├── sales.html     # 매출 관리
│       ├── menu.html      # 메뉴 관리
│       ├── add_menu.html  # 메뉴 추가
│       ├── edit_menu.html # 메뉴 수정
│       ├── categories.html # 카테고리 관리
│       └── receipt.html   # 영수증 출력
└── flask_session/         # 세션 파일 저장소
```

## 데이터베이스 모델

### Menu (메뉴)
- id: 메뉴 ID
- name: 메뉴명
- category: 카테고리
- price: 가격
- description: 설명
- image: 이미지 파일명
- temperature_option: 온도 옵션 (hot/ice/both)
- display_order: 표시 순서
- is_soldout: 품절 여부

### Order (주문)
- id: 주문 ID
- order_date: 주문일시
- status: 주문상태 (pending/confirmed/completed/cancelled)
- total_amount: 총 주문금액
- customer_name: 고객명
- delivery_location: 배달위치
- delivery_time: 배달시간
- order_request: 주문요청사항

### OrderItem (주문항목)
- id: 주문항목 ID
- order_id: 주문 ID (외래키)
- menu_id: 메뉴 ID (외래키)
- quantity: 수량
- subtotal: 소계
- special_request: 특별요청사항
- temperature: 온도 (hot/ice)

## 주요 라우트

### 메인 라우트
- `GET /` - 메인 페이지
- `GET /init_db` - 데이터베이스 초기화
- `GET /update_db_schema` - 데이터베이스 스키마 업데이트

### 사용자 라우트
- `GET /user/menu` - 메뉴 조회
- `POST /user/add_to_cart` - 장바구니에 추가
- `GET /user/view_cart` - 장바구니 조회
- `POST /user/update_cart` - 장바구니 수정
- `POST /user/place_order` - 주문하기
- `GET /user/clear_cart` - 장바구니 비우기

### 관리자 라우트
- `GET /admin/login` - 관리자 로그인 페이지
- `POST /admin/login` - 관리자 로그인 처리
- `GET /admin/logout` - 관리자 로그아웃
- `GET /admin` - 관리자 대시보드
- `GET /admin/sales` - 매출 관리
- `GET /admin/menu` - 메뉴 관리
- `GET /admin/menu/add` - 메뉴 추가 페이지
- `POST /admin/menu/add` - 메뉴 추가 처리
- `GET /admin/menu/edit/<id>` - 메뉴 수정 페이지
- `POST /admin/menu/edit/<id>` - 메뉴 수정 처리
- `GET /admin/menu/delete/<id>` - 메뉴 삭제
- `POST /admin/menu/toggle_soldout/<id>` - 품절 상태 토글
- `GET /admin/categories` - 카테고리 관리
- `POST /admin/categories` - 카테고리 추가
- `POST /admin/categories/delete/<category>` - 카테고리 삭제
- `GET /admin/export_all_orders` - 전체 주문 내역 내보내기
- `GET /admin/print_receipt/<id>` - 영수증 출력

## 개발 시 주의사항

### 1. 보안
- 관리자 인증 필수
- 파일 업로드 보안 처리
- SQL 인젝션 방지
- XSS 방지

### 2. 성능
- 데이터베이스 쿼리 최적화
- 이미지 파일 크기 제한
- 세션 데이터 관리

### 3. 사용자 경험
- 직관적인 UI/UX
- 실시간 피드백
- 오류 메시지 명확화
- 로딩 상태 표시

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여

버그 리포트나 기능 제안은 이슈를 통해 제출해주세요. 