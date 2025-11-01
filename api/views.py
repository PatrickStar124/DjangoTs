# views.py - 完整版本
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db import IntegrityError, models
from django.contrib.auth import authenticate
from django.middleware.csrf import get_token
from django.utils import timezone
from goods.models import Goods, Comment, Like, Favorite, Message
from api.serializers import GoodsSerializer, CommentSerializer, LikeSerializer, FavoriteSerializer, MessageSerializer


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
            if not request.user.is_authenticated:
                return Response({
                    'success': False,
                    'message': '请先登录'
                }, status=status.HTTP_401_UNAUTHORIZED)

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
    try:
        goods = Goods.objects.get(id=id)
    except Goods.DoesNotExist:
        return Response({
            'success': False,
            'message': '商品不存在'
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = GoodsSerializer(goods, context={'request': request})
        return Response({
            'success': True,
            'goods': serializer.data
        })

    elif request.method in ['PUT', 'DELETE']:
        if goods.seller != request.user:
            return Response({
                'success': False,
                'message': '无权操作此商品'
            }, status=status.HTTP_403_FORBIDDEN)

        if request.method == 'PUT':
            serializer = GoodsSerializer(
                goods,
                data=request.data,
                partial=True,
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
            if not goods.is_sold:
                return Response({
                    'success': False,
                    'message': '请先下架商品再删除'
                }, status=status.HTTP_400_BAD_REQUEST)

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
    """API测试接口"""
    return Response({"message": "API is working!"})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_csrf_token(request):
    """获取CSRF Token"""
    return Response({'csrfToken': get_token(request)})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_root(request):
    """API根目录"""
    base_url = request.build_absolute_uri('/')[:-1]
    return Response({
        "message": "🛒 商品市场API服务",
        "version": "1.0.0",
        "endpoints": {
            "商品列表": f"{base_url}/api/goods/",
            "商品详情": f"{base_url}/api/goods/{{id}}/",
            "用户登录": f"{base_url}/api/auth/login/",
            "用户注册": f"{base_url}/api/auth/register/",
        }
    })


# -------------------------- 4. 用户商品相关接口 --------------------------
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_goods_list(request, action):
    """
    获取用户相关的商品信息
    action: 'my-goods' - 我的出售商品, 'my-purchases' - 我的购买记录
    """
    try:
        if action == 'my-goods':
            try:
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

        elif action == 'my-purchases':
            try:
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


# -------------------------- 5. 购买商品接口 --------------------------
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
        if goods.is_sold:
            return Response({
                'success': False,
                'message': '该商品已售出'
            }, status=status.HTTP_400_BAD_REQUEST)

        if goods.seller == request.user:
            return Response({
                'success': False,
                'message': '不能购买自己的商品'
            }, status=status.HTTP_400_BAD_REQUEST)

        goods.buyer = request.user
        goods.is_sold = True
        goods.sold_at = timezone.now()
        goods.save()

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


# -------------------------- 6. 评论相关接口 --------------------------
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def goods_comments(request, goods_id):
    """获取商品评论列表和发布评论"""
    try:
        goods = Goods.objects.get(id=goods_id)
    except Goods.DoesNotExist:
        return Response({
            'success': False,
            'message': '商品不存在'
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        comments = goods.comments.all().order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response({
            'success': True,
            'comments': serializer.data,
            'count': len(serializer.data)
        })

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'message': '请先登录'
            }, status=status.HTTP_401_UNAUTHORIZED)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(goods=goods, user=request.user)
            return Response({
                'success': True,
                'message': '评论发布成功',
                'comment': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_comment(request, comment_id):
    """删除评论（只能删除自己的评论）"""
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response({
            'success': False,
            'message': '评论不存在'
        }, status=status.HTTP_404_NOT_FOUND)

    if comment.user != request.user:
        return Response({
            'success': False,
            'message': '无权删除此评论'
        }, status=status.HTTP_403_FORBIDDEN)

    comment.delete()
    return Response({
        'success': True,
        'message': '评论删除成功'
    })


# -------------------------- 7. 点赞相关接口 --------------------------
@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def goods_like(request, goods_id):
    """点赞/取消点赞商品"""
    try:
        goods = Goods.objects.get(id=goods_id)
    except Goods.DoesNotExist:
        return Response({
            'success': False,
            'message': '商品不存在'
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        like, created = Like.objects.get_or_create(goods=goods, user=request.user)
        if created:
            return Response({
                'success': True,
                'message': '点赞成功',
                'action': 'liked'
            })
        else:
            return Response({
                'success': False,
                'message': '已经点过赞了'
            }, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            like = Like.objects.get(goods=goods, user=request.user)
            like.delete()
            return Response({
                'success': True,
                'message': '取消点赞成功',
                'action': 'unliked'
            })
        except Like.DoesNotExist:
            return Response({
                'success': False,
                'message': '尚未点赞'
            }, status=status.HTTP_400_BAD_REQUEST)


# -------------------------- 8. 收藏相关接口 --------------------------
@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def goods_favorite(request, goods_id):
    """收藏/取消收藏商品"""
    try:
        goods = Goods.objects.get(id=goods_id)
    except Goods.DoesNotExist:
        return Response({
            'success': False,
            'message': '商品不存在'
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        favorite, created = Favorite.objects.get_or_create(goods=goods, user=request.user)
        if created:
            return Response({
                'success': True,
                'message': '收藏成功',
                'action': 'favorited'
            })
        else:
            return Response({
                'success': False,
                'message': '已经收藏过了'
            }, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            favorite = Favorite.objects.get(goods=goods, user=request.user)
            favorite.delete()
            return Response({
                'success': True,
                'message': '取消收藏成功',
                'action': 'unfavorited'
            })
        except Favorite.DoesNotExist:
            return Response({
                'success': False,
                'message': '尚未收藏'
            }, status=status.HTTP_400_BAD_REQUEST)


# -------------------------- 9. 留言相关接口 --------------------------
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def goods_messages(request, goods_id):
    """获取商品留言和发送留言"""
    try:
        goods = Goods.objects.get(id=goods_id)
    except Goods.DoesNotExist:
        return Response({
            'success': False,
            'message': '商品不存在'
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        messages = Message.objects.filter(
            goods=goods
        ).filter(
            models.Q(sender=request.user) | models.Q(receiver=request.user)
        ).order_by('created_at')

        serializer = MessageSerializer(messages, many=True)
        return Response({
            'success': True,
            'messages': serializer.data,
            'count': len(serializer.data)
        })

    elif request.method == 'POST':
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            receiver = goods.seller
            if receiver == request.user:
                return Response({
                    'success': False,
                    'message': '不能给自己发送留言'
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save(goods=goods, sender=request.user, receiver=receiver)
            return Response({
                'success': True,
                'message': '留言发送成功',
                'message_data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_messages(request):
    """获取用户相关的所有留言"""
    sent_messages = Message.objects.filter(sender=request.user).order_by('-created_at')
    received_messages = Message.objects.filter(receiver=request.user).order_by('-created_at')

    sent_serializer = MessageSerializer(sent_messages, many=True)
    received_serializer = MessageSerializer(received_messages, many=True)

    return Response({
        'success': True,
        'sent_messages': sent_serializer.data,
        'received_messages': received_serializer.data,
        'sent_count': len(sent_serializer.data),
        'received_count': len(received_serializer.data)
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_message_read(request, message_id):
    """标记留言为已读"""
    try:
        message = Message.objects.get(id=message_id, receiver=request.user)
    except Message.DoesNotExist:
        return Response({
            'success': False,
            'message': '留言不存在或无权操作'
        }, status=status.HTTP_404_NOT_FOUND)

    message.is_read = True
    message.save()

    return Response({
        'success': True,
        'message': '标记为已读成功'
    })


# -------------------------- 10. 获取用户收藏的商品 --------------------------
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_favorites(request):
    """获取用户收藏的商品列表"""
    favorites = Favorite.objects.filter(user=request.user).order_by('-created_at')
    favorite_goods = [fav.goods for fav in favorites]

    serializer = GoodsSerializer(favorite_goods, many=True, context={'request': request})

    return Response({
        'success': True,
        'favorites': serializer.data,
        'count': len(serializer.data)
    })