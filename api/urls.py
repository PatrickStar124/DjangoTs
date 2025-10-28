# api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 认证相关接口
    path('auth/login/', views.user_login, name='user-login'),
    path('auth/register/', views.user_register, name='user-register'),
    path('auth/logout/', views.user_logout, name='user-logout'),
    path('auth/status/', views.check_auth_status, name='auth-status'),
    path('auth/csrf-token/', views.get_csrf_token, name='csrf-token'),

    # 商品相关接口
    path('goods/', views.goods_list, name='goods-list'),
    path('goods/<int:id>/', views.good_detail, name='goods-detail'),

    # 测试接口
    path('test/', views.test_view, name='api-test'),

    # API根目录
    path('', views.api_root, name='api-root'),
]