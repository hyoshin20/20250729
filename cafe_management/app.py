"""
Flask 카페 주문 관리 시스템 메인 애플리케이션 (Supabase 연동)
사용자 주문과 관리자 메뉴 관리 기능을 제공하는 웹 애플리케이션
"""
import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_session import Session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import pandas as pd
from io import BytesIO
import uuid
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

from supabase_client import get_supabase_client, get_supabase_admin_client, test_supabase_connection
from config import *

app = Flask(__name__)
app.config.from_object('config')

# Supabase 클라이언트 초기화
try:
    supabase = get_supabase_client()
    print("✅ Supabase 연결 성공")
except Exception as e:
    print(f"❌ Supabase 연결 실패: {e}")
    print("환경 변수를 확인해주세요: SUPABASE_URL, SUPABASE_ANON_KEY")

# 세션 초기화
Session(app)

# 업로드 폴더 생성
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('flask_session', exist_ok=True)

def allowed_file(filename):
    """업로드된 파일의 확장자 검증"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_cart_total():
    """장바구니 총 금액 계산"""
    cart = session.get('cart', {})
    total = 0
    for item in cart.values():
        total += item['price'] * item['quantity']
    return total

@app.route('/')
def index():
    """메인 페이지 - 사용자/관리자 선택"""
    return render_template('index.html')

@app.route('/init_db')
def init_db():
    """Supabase 데이터베이스 초기화 및 샘플 데이터 생성"""
    try:
        # Supabase 연결 테스트
        if not test_supabase_connection():
            flash('Supabase 연결에 실패했습니다. 환경 변수를 확인해주세요.', 'error')
            return redirect(url_for('index'))
        
        # 샘플 메뉴 데이터 생성
        sample_menus = [
            {'name': '아메리카노', 'category': '커피', 'price': 4500, 'description': '깔끔한 아메리카노', 'temperature_option': 'both', 'display_order': 1},
            {'name': '카페라떼', 'category': '커피', 'price': 5000, 'description': '부드러운 카페라떼', 'temperature_option': 'both', 'display_order': 2},
            {'name': '카푸치노', 'category': '커피', 'price': 5000, 'description': '거품이 풍부한 카푸치노', 'temperature_option': 'both', 'display_order': 3},
            {'name': '에스프레소', 'category': '커피', 'price': 3500, 'description': '진한 에스프레소', 'temperature_option': 'hot', 'display_order': 4},
            {'name': '녹차라떼', 'category': '녹차', 'price': 5500, 'description': '진한 녹차라떼', 'temperature_option': 'both', 'display_order': 5},
            {'name': '레몬에이드', 'category': '에이드', 'price': 6000, 'description': '상큼한 레몬에이드', 'temperature_option': 'ice', 'display_order': 6},
            {'name': '오렌지에이드', 'category': '에이드', 'price': 6000, 'description': '달콤한 오렌지에이드', 'temperature_option': 'ice', 'display_order': 7},
            {'name': '티라떼', 'category': '티', 'price': 5500, 'description': '부드러운 티라떼', 'temperature_option': 'both', 'display_order': 8},
            {'name': '허브티', 'category': '티', 'price': 4500, 'description': '건강한 허브티', 'temperature_option': 'hot', 'display_order': 9},
            {'name': '스무디', 'category': '스무디', 'price': 6500, 'description': '시원한 스무디', 'temperature_option': 'ice', 'display_order': 10},
        ]
        
        supabase = get_supabase_client()
        
        # 기존 메뉴 확인 및 새 메뉴 추가
        for menu_data in sample_menus:
            existing = supabase.table('cafe_menu').select('id').eq('name', menu_data['name']).execute()
            if not existing.data:
                supabase.table('cafe_menu').insert(menu_data).execute()
        
        flash('Supabase 데이터베이스가 초기화되었습니다.', 'success')
        
    except Exception as e:
        flash(f'데이터베이스 초기화 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/update_db_schema')
def update_db_schema():
    """데이터베이스 스키마 업데이트"""
    with app.app_context():
        db.create_all()
        flash('데이터베이스 스키마가 업데이트되었습니다.', 'success')
    
    return redirect(url_for('index'))

# 사용자 라우트
@app.route('/user/menu')
def user_menu():
    """사용자 메뉴 페이지"""
    try:
        supabase = get_supabase_client()
        
        # 모든 메뉴 가져오기 (품절되지 않은 것만)
        response = supabase.table('cafe_menu').select('*').eq('is_soldout', False).order('display_order').execute()
        all_menus = response.data
        
        # 카테고리별로 메뉴 분류
        categories = list(set(menu['category'] for menu in all_menus))
        categories.sort()
        
        menus = {}
        for category in categories:
            menus[category] = [menu for menu in all_menus if menu['category'] == category]
        
        return render_template('user/menu.html', menus=menus, categories=categories)
        
    except Exception as e:
        flash(f'메뉴를 불러오는 중 오류가 발생했습니다: {str(e)}', 'error')
        return render_template('user/menu.html', menus={}, categories=[])

@app.route('/user/add_to_cart', methods=['POST'])
def add_to_cart():
    """장바구니에 메뉴 추가"""
    try:
        menu_id = request.form.get('menu_id')
        quantity = int(request.form.get('quantity', 1))
        temperature = request.form.get('temperature', 'ice')
        special_request = request.form.get('special_request', '')
        
        # Supabase에서 메뉴 정보 가져오기
        supabase = get_supabase_client()
        response = supabase.table('cafe_menu').select('*').eq('id', menu_id).execute()
        
        if not response.data:
            flash('메뉴를 찾을 수 없습니다.', 'error')
            return redirect(url_for('user_menu'))
        
        menu = response.data[0]
        
        if menu['is_soldout']:
            flash('품절된 메뉴입니다.', 'error')
            return redirect(url_for('user_menu'))
        
        # 세션에서 장바구니 가져오기
        cart = session.get('cart', {})
        
        # 메뉴 ID와 온도 옵션을 키로 사용
        cart_key = f"{menu_id}_{temperature}"
        
        if cart_key in cart:
            cart[cart_key]['quantity'] += quantity
        else:
            cart[cart_key] = {
                'menu_id': menu_id,
                'name': menu['name'],
                'price': menu['price'],
                'quantity': quantity,
                'temperature': temperature,
                'special_request': special_request
            }
        
        session['cart'] = cart
        flash(f'{menu["name"]}이(가) 장바구니에 추가되었습니다.', 'success')
        
    except Exception as e:
        flash(f'장바구니 추가 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('user_menu'))

@app.route('/user/view_cart')
def view_cart():
    """장바구니 조회"""
    cart = session.get('cart', {})
    total = get_cart_total()
    
    return render_template('user/cart.html', cart=cart, total=total)

@app.route('/user/update_cart', methods=['POST'])
def update_cart():
    """장바구니 수정"""
    cart_key = request.form.get('cart_key')
    quantity = int(request.form.get('quantity', 0))
    
    cart = session.get('cart', {})
    
    if quantity <= 0:
        cart.pop(cart_key, None)
        flash('메뉴가 장바구니에서 제거되었습니다.', 'success')
    else:
        if cart_key in cart:
            cart[cart_key]['quantity'] = quantity
            flash('수량이 업데이트되었습니다.', 'success')
    
    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/user/place_order', methods=['POST'])
def place_order():
    """주문하기"""
    try:
        cart = session.get('cart', {})
        
        if not cart:
            flash('장바구니가 비어있습니다.', 'error')
            return redirect(url_for('view_cart'))
        
        customer_name = request.form.get('customer_name')
        delivery_location = request.form.get('delivery_location')
        delivery_time = request.form.get('delivery_time')
        order_request = request.form.get('order_request')
        
        if not customer_name or not delivery_location:
            flash('고객명과 배달 위치를 입력해주세요.', 'error')
            return redirect(url_for('view_cart'))
        
        total_amount = get_cart_total()
        
        supabase = get_supabase_client()
        
        # 주문 생성
        order_data = {
            'total_amount': total_amount,
            'customer_name': customer_name,
            'delivery_location': delivery_location,
            'delivery_time': delivery_time,
            'order_request': order_request
        }
        
        order_response = supabase.table('cafe_order').insert(order_data).execute()
        order_id = order_response.data[0]['id']
        
        # 주문 항목 생성
        order_items = []
        for cart_key, item in cart.items():
            order_item_data = {
                'order_id': order_id,
                'menu_id': item['menu_id'],
                'quantity': item['quantity'],
                'subtotal': item['price'] * item['quantity'],
                'special_request': item['special_request'],
                'temperature': item['temperature']
            }
            order_items.append(order_item_data)
        
        if order_items:
            supabase.table('cafe_order_item').insert(order_items).execute()
        
        # 장바구니 비우기
        session.pop('cart', None)
        
        flash(f'주문이 완료되었습니다. 주문번호: {order_id}', 'success')
        
    except Exception as e:
        flash(f'주문 처리 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('user_menu'))

@app.route('/user/clear_cart')
def clear_cart():
    """장바구니 비우기"""
    session.pop('cart', None)
    flash('장바구니가 비워졌습니다.', 'success')
    return redirect(url_for('user_menu'))

# 관리자 라우트
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """관리자 로그인"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('관리자로 로그인되었습니다.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('잘못된 로그인 정보입니다.', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    """관리자 로그아웃"""
    session.pop('admin_logged_in', None)
    flash('로그아웃되었습니다.', 'success')
    return redirect(url_for('admin_login'))

def admin_required(f):
    """관리자 인증 데코레이터"""
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('관리자 로그인이 필요합니다.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/admin')
@admin_required
def admin_dashboard():
    """관리자 대시보드"""
    try:
        supabase = get_supabase_client()
        
        # 오늘 날짜
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 오늘 주문 수
        today_orders_response = supabase.table('cafe_order').select('id').gte('order_date', f'{today} 00:00:00').lt('order_date', f'{today} 23:59:59').execute()
        today_orders = len(today_orders_response.data)
        
        # 오늘 매출
        today_sales_response = supabase.table('cafe_order').select('total_amount').gte('order_date', f'{today} 00:00:00').lt('order_date', f'{today} 23:59:59').execute()
        today_sales = sum(order['total_amount'] for order in today_sales_response.data)
        
        # 대기 중인 주문 수
        pending_orders_response = supabase.table('cafe_order').select('id').eq('status', 'pending').execute()
        pending_orders = len(pending_orders_response.data)
        
        return render_template('admin/dashboard.html', 
                             today_orders=today_orders,
                             today_sales=today_sales,
                             pending_orders=pending_orders)
                             
    except Exception as e:
        flash(f'대시보드 로딩 중 오류가 발생했습니다: {str(e)}', 'error')
        return render_template('admin/dashboard.html', 
                             today_orders=0,
                             today_sales=0,
                             pending_orders=0)

@app.route('/admin/sales')
@admin_required
def admin_sales():
    """매출 관리"""
    try:
        supabase = get_supabase_client()
        
        # 기본 필터 (오늘)
        start_date = request.args.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        
        # 주문 조회
        orders_response = supabase.table('cafe_order').select('*').gte('order_date', f'{start_date} 00:00:00').lte('order_date', f'{end_date} 23:59:59').order('order_date', desc=True).execute()
        orders = orders_response.data
        
        # 통계 계산
        total_orders = len(orders)
        total_sales = sum(order['total_amount'] for order in orders)
        
        return render_template('admin/sales.html', 
                             orders=orders,
                             total_orders=total_orders,
                             total_sales=total_sales,
                             start_date=start_date,
                             end_date=end_date)
                             
    except Exception as e:
        flash(f'매출 데이터 로딩 중 오류가 발생했습니다: {str(e)}', 'error')
        return render_template('admin/sales.html', 
                             orders=[],
                             total_orders=0,
                             total_sales=0,
                             start_date=start_date,
                             end_date=end_date)

@app.route('/admin/menu')
@admin_required
def admin_menu():
    """메뉴 관리"""
    try:
        supabase = get_supabase_client()
        
        # 모든 메뉴 가져오기
        response = supabase.table('cafe_menu').select('*').order('display_order').execute()
        all_menus = response.data
        
        # 카테고리별로 메뉴 분류
        categories = list(set(menu['category'] for menu in all_menus))
        categories.sort()
        
        menus = {}
        for category in categories:
            menus[category] = [menu for menu in all_menus if menu['category'] == category]
        
        return render_template('admin/menu.html', menus=menus, categories=categories)
        
    except Exception as e:
        flash(f'메뉴 데이터 로딩 중 오류가 발생했습니다: {str(e)}', 'error')
        return render_template('admin/menu.html', menus={}, categories=[])

@app.route('/admin/menu/add', methods=['GET', 'POST'])
@admin_required
def admin_add_menu():
    """메뉴 추가"""
    try:
        if request.method == 'POST':
            name = request.form.get('name')
            category = request.form.get('category')
            price = float(request.form.get('price'))
            description = request.form.get('description')
            temperature_option = request.form.get('temperature_option')
            
            # 이미지 업로드 처리
            image_filename = None
            if 'image' in request.files:
                file = request.files['image']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # 고유한 파일명 생성
                    image_filename = f"{uuid.uuid4().hex}_{filename}"
                    file.save(os.path.join(UPLOAD_FOLDER, image_filename))
            
            # Supabase에 메뉴 추가
            supabase = get_supabase_client()
            menu_data = {
                'name': name,
                'category': category,
                'price': price,
                'description': description,
                'temperature_option': temperature_option,
                'image': image_filename
            }
            
            supabase.table('cafe_menu').insert(menu_data).execute()
            
            flash('메뉴가 추가되었습니다.', 'success')
            return redirect(url_for('admin_menu'))
        
        # GET 요청: 카테고리 목록 가져오기
        supabase = get_supabase_client()
        response = supabase.table('cafe_menu').select('category').execute()
        categories = list(set(menu['category'] for menu in response.data))
        categories.sort()
        
        return render_template('admin/add_menu.html', categories=categories)
        
    except Exception as e:
        flash(f'메뉴 추가 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('admin_menu'))

@app.route('/admin/menu/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_menu(id):
    """메뉴 수정"""
    menu = Menu.query.get_or_404(id)
    
    if request.method == 'POST':
        menu.name = request.form.get('name')
        menu.category = request.form.get('category')
        menu.price = float(request.form.get('price'))
        menu.description = request.form.get('description')
        menu.temperature_option = request.form.get('temperature_option')
        
        # 이미지 업로드 처리
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                # 기존 이미지 삭제
                if menu.image:
                    try:
                        os.remove(os.path.join(UPLOAD_FOLDER, menu.image))
                    except:
                        pass
                
                filename = secure_filename(file.filename)
                image_filename = f"{uuid.uuid4().hex}_{filename}"
                file.save(os.path.join(UPLOAD_FOLDER, image_filename))
                menu.image = image_filename
        
        db.session.commit()
        flash('메뉴가 수정되었습니다.', 'success')
        return redirect(url_for('admin_menu'))
    
    categories = db.session.query(Menu.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('admin/edit_menu.html', menu=menu, categories=categories)

@app.route('/admin/menu/delete/<int:id>')
@admin_required
def admin_delete_menu(id):
    """메뉴 삭제"""
    menu = Menu.query.get_or_404(id)
    
    # 이미지 파일 삭제
    if menu.image:
        try:
            os.remove(os.path.join(UPLOAD_FOLDER, menu.image))
        except:
            pass
    
    db.session.delete(menu)
    db.session.commit()
    
    flash('메뉴가 삭제되었습니다.', 'success')
    return redirect(url_for('admin_menu'))

@app.route('/admin/menu/toggle_soldout/<int:id>', methods=['POST'])
@admin_required
def admin_toggle_soldout(id):
    """품절 상태 토글"""
    try:
        supabase = get_supabase_client()
        
        # 현재 메뉴 상태 가져오기
        response = supabase.table('cafe_menu').select('is_soldout').eq('id', id).execute()
        
        if not response.data:
            return jsonify({'success': False, 'error': '메뉴를 찾을 수 없습니다.'})
        
        current_status = response.data[0]['is_soldout']
        new_status = not current_status
        
        # 상태 업데이트
        supabase.table('cafe_menu').update({'is_soldout': new_status}).eq('id', id).execute()
        
        return jsonify({'success': True, 'is_soldout': new_status})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/categories')
@admin_required
def admin_categories():
    """카테고리 관리"""
    categories = db.session.query(Menu.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories', methods=['POST'])
@admin_required
def admin_add_category():
    """카테고리 추가"""
    category = request.form.get('category')
    
    if category and category not in [cat[0] for cat in db.session.query(Menu.category).distinct().all()]:
        flash('카테고리가 추가되었습니다.', 'success')
    else:
        flash('이미 존재하는 카테고리입니다.', 'error')
    
    return redirect(url_for('admin_categories'))

@app.route('/admin/categories/delete/<category>', methods=['POST'])
@admin_required
def admin_delete_category(category):
    """카테고리 삭제"""
    # 해당 카테고리의 메뉴들을 삭제
    Menu.query.filter_by(category=category).delete()
    db.session.commit()
    
    flash(f'카테고리 "{category}"가 삭제되었습니다.', 'success')
    return redirect(url_for('admin_categories'))

@app.route('/admin/export_all_orders')
@admin_required
def admin_export_all_orders():
    """전체 주문 내역 내보내기"""
    orders = Order.query.order_by(Order.order_date.desc()).all()
    
    # Excel 파일 생성
    data = []
    for order in orders:
        for item in order.order_items:
            data.append({
                '주문번호': order.id,
                '주문일시': order.order_date.strftime('%Y-%m-%d %H:%M:%S'),
                '고객명': order.customer_name,
                '배달위치': order.delivery_location,
                '메뉴명': item.menu.name,
                '수량': item.quantity,
                '단가': item.menu.price,
                '소계': item.subtotal,
                '온도': item.temperature,
                '특별요청': item.special_request or '',
                '주문상태': order.status,
                '총금액': order.total_amount
            })
    
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='주문내역')
    
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'주문내역_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )

@app.route('/admin/print_receipt/<int:id>')
@admin_required
def admin_print_receipt(id):
    """영수증 출력"""
    order = Order.query.get_or_404(id)
    return render_template('admin/receipt.html', order=order)

@app.route('/admin/get_recent_orders')
@admin_required
def admin_get_recent_orders():
    """최근 주문 조회 (AJAX)"""
    try:
        supabase = get_supabase_client()
        
        # 최근 10개 주문 가져오기
        response = supabase.table('cafe_order').select('*').order('order_date', desc=True).limit(10).execute()
        orders = response.data
        
        # 주문 항목도 함께 가져오기
        for order in orders:
            items_response = supabase.table('cafe_order_item').select('*, cafe_menu(name)').eq('order_id', order['id']).execute()
            order['order_items'] = items_response.data
        
        return jsonify(orders)
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/admin/update_order_status/<int:id>', methods=['POST'])
@admin_required
def admin_update_order_status(id):
    """주문 상태 업데이트 (AJAX)"""
    try:
        supabase = get_supabase_client()
        status = request.json.get('status')
        
        if status in ['pending', 'confirmed', 'completed', 'cancelled']:
            supabase.table('cafe_order').update({'status': status}).eq('id', id).execute()
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': '잘못된 상태값입니다.'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/delete_order/<int:id>', methods=['POST'])
@admin_required
def admin_delete_order(id):
    """주문 삭제 (AJAX)"""
    try:
        supabase = get_supabase_client()
        
        # 주문 항목 먼저 삭제 (CASCADE로 자동 삭제되지만 명시적으로 처리)
        supabase.table('cafe_order_item').delete().eq('order_id', id).execute()
        
        # 주문 삭제
        supabase.table('cafe_order').delete().eq('id', id).execute()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Supabase 연결 테스트
    try:
        if test_supabase_connection():
            print("✅ Supabase 연결 성공")
        else:
            print("❌ Supabase 연결 실패")
            print("환경 변수를 확인해주세요:")
            print("- SUPABASE_URL")
            print("- SUPABASE_ANON_KEY")
    except Exception as e:
        print(f"❌ Supabase 연결 오류: {e}")
    
    app.run(debug=True, host='0.0.0.0', port=4011) 