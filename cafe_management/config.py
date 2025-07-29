"""
Flask 카페 주문 관리 시스템 설정 파일
"""
import os
from datetime import timedelta

# Flask 기본 설정
SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
DEBUG = True

# Supabase 설정
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')
SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

# 데이터베이스 설정 (PostgreSQL)
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///cafe.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 파일 업로드 설정
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# 세션 설정
PERMANENT_SESSION_LIFETIME = timedelta(days=1)
SESSION_TYPE = 'filesystem'

# 관리자 계정 설정
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin123'

# 애플리케이션 설정
APP_NAME = '카페 주문 관리 시스템'
APP_VERSION = '1.0.0' 