# api/views.py
import os
import uuid
import json
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.contrib.auth.models import User
from django.db import IntegrityError

# 导入你的模型和序列化器
from goods.models import Goods
from api.serializers import   GoodsSerializer


# ----------------------------------------------------------------------
# 文件上传接口（如果需要）
@csrf_exempt
def upload_image(request):
    if request.method == "POST" and request.FILES.get("image"):
        image_file = request.FILES["image"]
        filename = f"goods_{uuid.uuid4().hex}{os.path.splitext(image_file.name)[1]}"
        filepath = os.path.join(settings.MEDIA_ROOT, "goods_images", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "wb+") as f:
            for chunk in image_file.chunks():
                f.write(chunk)

        image_url = f"{settings.MEDIA_URL}goods_images/{filename}"
        return JsonResponse({"success": True, "image_url": image_url})
    return JsonResponse({"success": False, "error": "上传失败"})


# ----------------------------------------------------------------------
# 商品列表与创建接口
@api_view(['GET', 'POST'])
def goods_list(request):
    # GET请求：查询所有未售出的商品
    if request.method == 'GET':
        try:
            goods = Goods.objects.filter(is_sold=False).order_by('-created_at')
            serializer = GoodsSerializer(goods, many=True)
            return Response({
                'success': True,
                'goods': serializer.data,
                'count': len(serializer.data)
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': '获取商品列表失败',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # POST请求：新建商品
    elif request.method == 'POST':
        try:
            # 检查用户是否登录
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'message': '请先登录'
                }, status=status.HTTP_401_UNAUTHORIZED)

            # 准备数据，确保image_url不为空
            data = request.data.copy()
            if not data.get('image_url'):
                data['image_url'] = 'https://via.placeholder.com/300x200?text=商品图片'

            serializer = GoodsSerializer(data=data, context={'request': request})

            if serializer.is_valid():
                # 自动设置卖家为当前用户
                serializer.save(seller=request.user)
                return Response({
                    'success': True,
                    'message': '商品发布成功',
                    'goods': serializer.data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': '数据验证失败',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'success': False,
                'message': '创建商品失败',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------------------------------------------------
# 商品详情接口
@api_view(['GET', 'PUT', 'DELETE'])
def good_detail(request, id):
    try:
        goods = Goods.objects.get(id=id)
    except Goods.DoesNotExist:
        return Response({
            'success': False,
            'message': '商品不存在'
        }, status=status.HTTP_404_NOT_FOUND)

    # GET请求：查询单个商品详情
    if request.method == 'GET':
        try:
            serializer = GoodsSerializer(goods)
            return Response({
                'success': True,
                'goods': serializer.data
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': '获取商品详情失败',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # PUT请求：修改商品信息
    elif request.method == 'PUT':
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'message': '请先登录'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if goods.seller != request.user:
            return Response({
                'success': False,
                'message': '您只能修改自己发布的商品'
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            serializer = GoodsSerializer(goods, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': '商品修改成功',
                    'goods': serializer.data
                })
            else:
                return Response({
                    'success': False,
                    'message': '数据验证失败',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': '修改商品失败',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # DELETE请求：删除商品
    elif request.method == 'DELETE':
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'message': '请先登录'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if goods.seller != request.user:
            return Response({
                'success': False,
                'message': '您只能删除自己发布的商品'
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            goods.delete()
            return Response({
                'success': True,
                'message': '商品删除成功'
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': '删除商品失败',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        'success': False,
        'message': '不支持的请求方法'
    }, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# ----------------------------------------------------------------------
# 测试接口
@api_view(['GET'])
def test_view(request):
    return Response({"message": "API is working!", "status": "success"})


# ----------------------------------------------------------------------
# 用户登录接口
@api_view(['POST'])
@csrf_exempt
def user_login(request):
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


# ----------------------------------------------------------------------
# CSRF Token获取接口
@api_view(['GET'])
def get_csrf_token(request):
    return Response({'csrfToken': get_token(request)})


# ----------------------------------------------------------------------
# 用户登出接口
@api_view(['POST'])
def user_logout(request):
    logout(request)
    return Response({
        'success': True,
        'message': '登出成功'
    })


# ----------------------------------------------------------------------
# 登录状态检查接口
@api_view(['GET'])
def check_auth_status(request):
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


# ----------------------------------------------------------------------
# 用户注册接口
@api_view(['POST'])
@csrf_exempt
def user_register(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')

        if not username or not password:
            return Response({
                'success': False,
                'message': '用户名和密码是必填项'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(username) < 3:
            return Response({
                'success': False,
                'message': '用户名至少需要3个字符'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(password) < 6:
            return Response({
                'success': False,
                'message': '密码至少需要6个字符'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )

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
        }, status=status.HTTP_400_BAD_REQUEST)


# ----------------------------------------------------------------------
# API根目录接口
@api_view(['GET'])
def api_root(request):
    base_url = request.build_absolute_uri('/')[:-1]
    return Response({
        "message": "🛒 商品市场API服务",
        "version": "1.0.0",
        "endpoints": {
            "商品接口": {
                "商品列表": f"{base_url}/api/goods/",
                "商品详情": f"{base_url}/api/goods/{{id}}/",
            },
            "认证接口": {
                "用户登录": f"{base_url}/api/auth/login/",
                "用户注册": f"{base_url}/api/auth/register/",
                "获取CSRF": f"{base_url}/api/auth/csrf-token/",
                "用户登出": f"{base_url}/api/auth/logout/",
                "认证状态": f"{base_url}/api/auth/status/"
            },
            "测试接口": f"{base_url}/api/test/"
        }
    })