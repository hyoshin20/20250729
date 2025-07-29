-- Supabase 카페 주문 관리 시스템 데이터베이스 스키마

-- 메뉴 테이블
CREATE TABLE IF NOT EXISTS cafe_menu (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    description TEXT,
    image VARCHAR(255),
    temperature_option VARCHAR(20) DEFAULT 'both',
    display_order INTEGER DEFAULT 9999,
    is_soldout BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 주문 테이블
CREATE TABLE IF NOT EXISTS cafe_order (
    id SERIAL PRIMARY KEY,
    order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    total_amount INTEGER NOT NULL,
    customer_name VARCHAR(50) NOT NULL,
    delivery_location VARCHAR(100) NOT NULL,
    delivery_time VARCHAR(50),
    order_request TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 주문 항목 테이블
CREATE TABLE IF NOT EXISTS cafe_order_item (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES cafe_order(id) ON DELETE CASCADE,
    menu_id INTEGER NOT NULL REFERENCES cafe_menu(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    special_request TEXT,
    temperature VARCHAR(10) DEFAULT 'ice',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_menu_category ON cafe_menu(category);
CREATE INDEX IF NOT EXISTS idx_menu_display_order ON cafe_menu(display_order);
CREATE INDEX IF NOT EXISTS idx_order_date ON cafe_order(order_date);
CREATE INDEX IF NOT EXISTS idx_order_status ON cafe_order(status);
CREATE INDEX IF NOT EXISTS idx_order_item_order_id ON cafe_order_item(order_id);
CREATE INDEX IF NOT EXISTS idx_order_item_menu_id ON cafe_order_item(menu_id);

-- 업데이트 트리거 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 업데이트 트리거 생성
CREATE TRIGGER update_cafe_menu_updated_at 
    BEFORE UPDATE ON cafe_menu 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cafe_order_updated_at 
    BEFORE UPDATE ON cafe_order 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RLS (Row Level Security) 활성화
ALTER TABLE cafe_menu ENABLE ROW LEVEL SECURITY;
ALTER TABLE cafe_order ENABLE ROW LEVEL SECURITY;
ALTER TABLE cafe_order_item ENABLE ROW LEVEL SECURITY;

-- 기본 정책 (모든 사용자가 읽기 가능)
CREATE POLICY "Allow public read access" ON cafe_menu FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON cafe_order FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON cafe_order_item FOR SELECT USING (true);

-- 관리자 정책 (서비스 롤 키로 모든 작업 가능)
CREATE POLICY "Allow admin full access" ON cafe_menu FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Allow admin full access" ON cafe_order FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Allow admin full access" ON cafe_order_item FOR ALL USING (auth.role() = 'service_role');

-- 샘플 데이터 삽입
INSERT INTO cafe_menu (name, category, price, description, temperature_option, display_order) VALUES
('아메리카노', '커피', 4500, '깔끔하고 진한 에스프레소', 'both', 1),
('카페라떼', '커피', 5000, '부드러운 우유와 에스프레소의 조화', 'both', 2),
('카푸치노', '커피', 5000, '에스프레소와 스팀밀크, 우유거품의 완벽한 조화', 'both', 3),
('카라멜 마끼아또', '커피', 5500, '달콤한 카라멜과 에스프레소', 'both', 4),
('바닐라 라떼', '커피', 5500, '바닐라 시럽이 들어간 부드러운 라떼', 'both', 5),
('녹차 라떼', '녹차', 5000, '진한 말차와 부드러운 우유', 'both', 6),
('레몬에이드', '음료', 4500, '상큼한 레몬과 탄산의 조화', 'ice', 7),
('오렌지 주스', '음료', 4000, '신선한 오렌지 주스', 'ice', 8),
('티라떼', '티', 4500, '홍차와 우유의 조화', 'both', 9),
('허브티', '티', 3500, '다양한 허브의 향기로운 티', 'hot', 10)
ON CONFLICT (id) DO NOTHING; 