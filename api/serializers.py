# api/serializers.py
from rest_framework import serializers
from goods.models import Goods, Comment, Like, Favorite, Message
from django.contrib.auth.models import User


class UserSimpleSerializer(serializers.ModelSerializer):
    """简化用户序列化器"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    user = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'goods', 'user', 'content', 'rating', 'created_at', 'updated_at']
        read_only_fields = ['id', 'goods', 'user', 'created_at', 'updated_at']  # 🔥 修复：添加 goods 和 user


class LikeSerializer(serializers.ModelSerializer):
    """点赞序列化器"""
    user = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'goods', 'user', 'created_at']
        read_only_fields = ['id', 'goods', 'user', 'created_at']  # 🔥 修复：添加 goods 和 user


class FavoriteSerializer(serializers.ModelSerializer):
    """收藏序列化器"""
    user = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'goods', 'user', 'created_at']
        read_only_fields = ['id', 'goods', 'user', 'created_at']  # 🔥 修复：添加 goods 和 user


class MessageSerializer(serializers.ModelSerializer):
    """留言序列化器"""
    sender = UserSimpleSerializer(read_only=True)
    receiver = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'goods', 'sender', 'receiver', 'content', 'is_read', 'created_at']
        read_only_fields = ['id', 'goods', 'sender', 'receiver', 'created_at']  # 🔥 修复：添加所有关联字段


# 更新商品序列化器
class GoodsSerializer(serializers.ModelSerializer):
    seller = UserSimpleSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    favorites_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Goods
        fields = [
            "id", "name", "price", "description", "category", "condition",
            "location", "contact", "image", "seller", "is_sold", "created_at",
            "updated_at", "get_image_url", "comments_count", "likes_count",
            "favorites_count", "is_liked", "is_favorited"
        ]
        read_only_fields = ["seller", "is_sold", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["seller"] = self.context["request"].user
        return super().create(validated_data)

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_favorites_count(self, obj):
        return obj.favorites.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorites.filter(user=request.user).exists()
        return False