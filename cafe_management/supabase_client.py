"""
Supabase 클라이언트 설정 및 유틸리티 함수
"""
import os
from supabase import create_client, Client
from typing import Optional

# Supabase 클라이언트 인스턴스
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Supabase 클라이언트를 반환합니다.
    환경 변수에서 설정을 읽어와 클라이언트를 초기화합니다.
    """
    global _supabase_client
    
    if _supabase_client is None:
        url = os.environ.get('SUPABASE_URL')
        key = os.environ.get('SUPABASE_ANON_KEY')
        
        if not url or not key:
            raise ValueError(
                "Supabase 설정이 누락되었습니다. "
                "SUPABASE_URL과 SUPABASE_ANON_KEY 환경 변수를 설정해주세요."
            )
        
        _supabase_client = create_client(url, key)
    
    return _supabase_client

def get_supabase_admin_client() -> Client:
    """
    관리자 권한을 가진 Supabase 클라이언트를 반환합니다.
    """
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    
    if not url or not key:
        raise ValueError(
            "Supabase 관리자 설정이 누락되었습니다. "
            "SUPABASE_URL과 SUPABASE_SERVICE_ROLE_KEY 환경 변수를 설정해주세요."
        )
    
    return create_client(url, key)

def test_supabase_connection() -> bool:
    """
    Supabase 연결을 테스트합니다.
    """
    try:
        client = get_supabase_client()
        # 간단한 쿼리로 연결 테스트
        response = client.table('cafe_menu').select('id').limit(1).execute()
        return True
    except Exception as e:
        print(f"Supabase 연결 테스트 실패: {e}")
        return False 