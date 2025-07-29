"""
데이터베이스 모델 정의
SQLAlchemy ORM을 사용한 카페 주문 관리 시스템의 데이터 모델
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Menu(db.Model):
    """메뉴 테이블 모델"""
    __tablename__ = 'cafe_menu'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))
    temperature_option = db.Column(db.String(20), default='both')  # hot, ice, both
    display_order = db.Column(db.Integer, default=9999)
    is_soldout = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 관계 설정
    order_items = db.relationship('OrderItem', backref='menu', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Menu {self.name}>'
    
    def to_dict(self):
        """메뉴 객체를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'description': self.description,
            'image': self.image,
            'temperature_option': self.temperature_option,
            'display_order': self.display_order,
            'is_soldout': self.is_soldout
        }

class Order(db.Model):
    """주문 테이블 모델"""
    __tablename__ = 'cafe_order'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, confirmed, completed, cancelled
    total_amount = db.Column(db.Integer, nullable=False)
    customer_name = db.Column(db.String(50), nullable=False)
    delivery_location = db.Column(db.String(100), nullable=False)
    delivery_time = db.Column(db.String(50), nullable=True)
    order_request = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 관계 설정
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.id} - {self.customer_name}>'
    
    def to_dict(self):
        """주문 객체를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'order_date': self.order_date.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status,
            'total_amount': self.total_amount,
            'customer_name': self.customer_name,
            'delivery_location': self.delivery_location,
            'delivery_time': self.delivery_time,
            'order_request': self.order_request,
            'order_items': [item.to_dict() for item in self.order_items]
        }

class OrderItem(db.Model):
    """주문 항목 테이블 모델"""
    __tablename__ = 'cafe_order_item'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('cafe_order.id'), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('cafe_menu.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    special_request = db.Column(db.Text)
    temperature = db.Column(db.String(10), default='ice')  # hot, ice
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<OrderItem {self.menu.name} x {self.quantity}>'
    
    def to_dict(self):
        """주문 항목 객체를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'menu_id': self.menu_id,
            'menu_name': self.menu.name if self.menu else '',
            'quantity': self.quantity,
            'subtotal': self.subtotal,
            'special_request': self.special_request,
            'temperature': self.temperature
        } 