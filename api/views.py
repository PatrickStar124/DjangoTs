from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db import IntegrityError
import json

from goods.models import Goods
from api.serializers  import GoodsSerializer

@api_view(['GET', 'POST'])
def goods_list(request):
    if request.method == 'GET':
        goods = Goods.objects.all()
        serializer = GoodsSerializer(goods, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        serializer = GoodsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def good_detail(request, id):
    try:
        goods = Goods.objects.get(id=id)
    except Goods.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = GoodsSerializer(goods)
        return Response(serializer.data)
    if request.method == 'PUT':
        serializer = GoodsSerializer(goods, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        goods.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def test_view(request):
    return Response({"message": "API is working!"})

@api_view(['POST'])
@csrf_exempt
def user_login(request):
    """
    用户登录API
    """
    try:
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return Response({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email if user.email else '',
                    'is_staff': user.is_staff
                },
                'message': '登录成功'
            })
        else:
            return Response({
                'success': False,
                'message': '用户名或密码错误'
            }, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        return Response({
            'success': False,
            'message': '登录过程中发生错误'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_csrf_token(request):
    """
    获取CSRF token
    """
    return Response({'csrfToken': get_token(request)})

@api_view(['POST'])
def user_logout(request):
    """
    用户登出API
    """
    logout(request)
    return Response({
        'success': True,
        'message': '登出成功'
    })

@api_view(['GET'])
def check_auth_status(request):
    """
    检查用户认证状态
    """
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email if request.user.email else '',
                'is_staff': request.user.is_staff
            }
        })
    else:
        return Response({
            'authenticated': False
        })

@api_view(['POST'])
@csrf_exempt
def user_register(request):
    """
    用户注册API
    """
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')

        # 验证必填字段
        if not username or not password:
            return Response({
                'success': False,
                'message': '用户名和密码是必填项'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证用户名长度
        if len(username) < 3:
            return Response({
                'success': False,
                'message': '用户名至少需要3个字符'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证密码长度
        if len(password) < 6:
            return Response({
                'success': False,
                'message': '密码至少需要6个字符'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 创建新用户
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )

            # 自动登录新用户
            login(request, user)

            return Response({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_staff': user.is_staff
                },
                'message': '注册成功'
            }, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response({
                'success': False,
                'message': '用户名已存在'
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'注册过程中发生错误: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)