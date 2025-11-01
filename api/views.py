# views.py
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import authenticate
from django.middleware.csrf import get_token
from django.utils import timezone
from goods.models import Goods
from api.serializers import GoodsSerializer


# -------------------------- 1. 商品相关视图 --------------------------
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def goods_list(request):
    """商品列表（GET）+ 创建商品（POST）"""
    if request.method == 'GET':
        try:
            goods = Goods.objects.filter(is_sold=False).order_by('-created_at')
            serializer = GoodsSerializer(goods, many=True, context={'request': request})
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

    elif request.method == 'POST':
        try:
            # 未登录拦截
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'message': '请先登录'
                }, status=status.HTTP_401_UNAUTHORIZED)

            # 数据验证与保存
            serializer = GoodsSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': '商品发布成功',
                    'goods': serializer.data
                }, status=status.HTTP_201_CREATED)
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


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def good_detail(request, id):
    """商品详情（GET）+ 更新商品（PUT）+ 删除商品（DELETE）"""
    # 先查询商品是否存在
    try:
        goods = Goods.objects.get(id=id)
    except Goods.DoesNotExist:
        return Response({
            'success': False,
            'message': '商品不存在'
        }, status=status.HTTP_404_NOT_FOUND)

    # 处理不同请求方法
    if request.method == 'GET':
        # 🔥 修改：所有登录用户都可以查看商品详情
        serializer = GoodsSerializer(goods, context={'request': request})
        return Response({
            'success': True,
            'goods': serializer.data
        })

    elif request.method in ['PUT', 'DELETE']:
        # 🔥 只有商品卖家可以修改或删除
        if goods.seller != request.user:
            return Response({
                'success': False,
                'message': '无权操作此商品'
            }, status=status.HTTP_403_FORBIDDEN)

        if request.method == 'PUT':
            serializer = GoodsSerializer(
                goods,
                data=request.data,
                partial=True,  # 允许部分更新
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': '商品更新成功',
                    'goods': serializer.data
                })
            return Response({
                'success': False,
                'message': '数据验证失败',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            # 删除商品时同步删除图片文件
            if goods.image:
                goods.image.delete(save=False)
            goods.delete()
            return Response({
                'success': True,
                'message': '商品删除成功'
            }, status=status.HTTP_200_OK)


# -------------------------- 2. 认证相关视图 --------------------------
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def user_login(request):
    """用户登录（返回Token）"""
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            # 获取或创建用户Token
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email if user.email else '',
                    'is_staff': user.is_staff
                },
                'token': token.key,
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
            'message': f'登录过程中发生错误: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def user_register(request):
    """用户注册（自动创建Token）"""
    try:
        # 获取注册参数
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')

        # 基础参数校验
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

        # 创建用户与Token
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        token = Token.objects.create(user=user)

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
            'token': token.key,
            'message': '注册成功'
        }, status=status.HTTP_201_CREATED)

    # 用户名重复
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


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def user_logout(request):
    """用户登出（删除Token）"""
    try:
        request.user.auth_token.delete()
        return Response({
            'success': True,
            'message': '登出成功'
        })
    except:
        return Response({
            'success': True,
            'message': '登出成功（无有效Token）'
        })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_auth_status(request):
    """检查用户认证状态"""
    return Response({
        'authenticated': True,
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email if request.user.email else '',
            'is_staff': request.user.is_staff
        }
    })


# -------------------------- 3. 辅助视图 --------------------------
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def test_view(request):
    """API测试接口（验证服务是否正常）"""
    return Response({"message": "API is working!"})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_csrf_token(request):
    """获取CSRF Token（保留兼容性）"""
    return Response({'csrfToken': get_token(request)})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_root(request):
    """API根目录（展示所有可用接口）"""
    base_url = request.build_absolute_uri('/')[:-1]
    return Response({
        "message": "🛒 商品市场API服务 - Token认证版本",
        "version": "1.0.0",
        "authentication": "Token Authentication",
        "endpoints": {
            "商品接口": {
                "商品列表": f"{base_url}/api/goods/",
                "商品详情": f"{base_url}/api/goods/{{id}}/",
            },
            "认证接口": {
                "用户登录": f"{base_url}/api/auth/login/",
                "用户注册": f"{base_url}/api/auth/register/",
                "用户登出": f"{base_url}/api/auth/logout/",
                "认证状态": f"{base_url}/api/auth/status/"
            },
            "用户商品接口": {
                "我的出售商品": f"{base_url}/api/user-goods/my-goods/",
            },
            "测试接口": f"{base_url}/api/test/"
        }
    })


# ----------------------------------------------------------------------
# 10. 用户商品相关接口
# ----------------------------------------------------------------------
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_goods_list(request, action):
    """
    获取用户相关的商品信息
    action: 'my-goods' - 我的出售商品, 'my-purchases' - 我的购买记录
    """
    try:
        # 获取我的出售商品
        if action == 'my-goods':
            try:
                # 获取当前用户发布的商品
                my_goods = Goods.objects.filter(seller=request.user).order_by('-created_at')
                serializer = GoodsSerializer(my_goods, many=True, context={'request': request})

                return Response({
                    'success': True,
                    'goods': serializer.data,
                    'count': len(serializer.data)
                })
            except Exception as e:
                return Response({
                    'success': False,
                    'message': '获取我的商品失败',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 获取我的购买记录
        elif action == 'my-purchases':
            try:
                # 获取当前用户购买的商品
                purchased_goods = Goods.objects.filter(buyer=request.user).order_by('-sold_at')
                serializer = GoodsSerializer(purchased_goods, many=True, context={'request': request})

                return Response({
                    'success': True,
                    'purchases': serializer.data,
                    'count': len(serializer.data)
                })
            except Exception as e:
                return Response({
                    'success': False,
                    'message': '获取购买记录失败',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response({
                'success': False,
                'message': '无效的操作类型'
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'success': False,
            'message': f'操作失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------------------------------------------------
# 11. 购买商品接口
# ----------------------------------------------------------------------
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def purchase_good(request, id):
    """购买商品接口"""
    try:
        goods = Goods.objects.get(id=id)
    except Goods.DoesNotExist:
        return Response({
            'success': False,
            'message': '商品不存在'
        }, status=status.HTTP_404_NOT_FOUND)

    try:
        # 检查商品是否已售出
        if goods.is_sold:
            return Response({
                'success': False,
                'message': '该商品已售出'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 检查是否是自己的商品
        if goods.seller == request.user:
            return Response({
                'success': False,
                'message': '不能购买自己的商品'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 更新商品状态
        goods.buyer = request.user
        goods.is_sold = True
        goods.sold_at = timezone.now()
        goods.save()

        # 序列化返回数据
        serializer = GoodsSerializer(goods, context={'request': request})

        return Response({
            'success': True,
            'message': '购买成功！',
            'goods': serializer.data
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'购买失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------------------------------------------------
# 12. 收藏商品接口
# ----------------------------------------------------------------------
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def favorite_good(request, id):
    """收藏商品接口"""
    try:
        goods = Goods.objects.get(id=id)

        # 这里可以添加收藏逻辑，比如创建收藏关系
        # 暂时先返回成功消息
        return Response({
            'success': True,
            'message': '收藏成功！'
        })

    except Goods.DoesNotExist:
        return Response({
            'success': False,
            'message': '商品不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'收藏失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)