# api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_root, name='api-root'),
    path('goods/', views.goods_list, name='goods-list'),
    path('goods/<int:id>/', views.good_detail, name='good-detail'),
    path('auth/register/', views.user_register, name='user_register'),
    path('test/', views.test_view, name='test-api'),
    path('auth/login/', views.user_login, name='user_login'),
    path('auth/csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('auth/logout/', views.user_logout, name='user_logout'),
    path('auth/status/', views.check_auth_status, name='check_auth_status'),

    # 用户商品相关路由
    path('user-goods/<str:action>/', views.user_goods_list, name='user-goods'),
    # 购买商品路由
    path('goods/<int:id>/purchase/', views.purchase_good, name='purchase-good'),

    # 🔥 新增：评论相关路由
    path('goods/<int:goods_id>/comments/', views.goods_comments, name='goods-comments'),
    path('comments/<int:comment_id>/', views.delete_comment, name='delete-comment'),

    # 🔥 新增：点赞相关路由
    path('goods/<int:goods_id>/like/', views.goods_like, name='goods-like'),

    # 🔥 新增：收藏相关路由
    path('goods/<int:goods_id>/favorite/', views.goods_favorite, name='goods-favorite'),
    path('user/favorites/', views.user_favorites, name='user-favorites'),

    # 🔥 新增：留言相关路由
    path('goods/<int:goods_id>/messages/', views.goods_messages, name='goods-messages'),
    path('user/messages/', views.user_messages, name='user-messages'),
    path('messages/<int:message_id>/read/', views.mark_message_read, name='mark-message-read'),
]