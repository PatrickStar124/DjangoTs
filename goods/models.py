# goods/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.utils import timezone


class Goods(models.Model):
    # 基础信息
    name = models.CharField(max_length=100, verbose_name="商品名称")
    price = models.FloatField(verbose_name="价格")
    description = models.TextField(verbose_name="商品描述")

    # 分类信息
    CATEGORY_CHOICES = [
        ('electronics', '电子产品'),
        ('clothing', '服装鞋帽'),
        ('books', '图书文具'),
        ('sports', '运动户外'),
        ('beauty', '美妆个护'),
        ('home', '家居日用'),
        ('other', '其他'),
    ]
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name="商品分类"
    )

    # 商品状态
    CONDITION_CHOICES = [
        ('new', '全新'),
        ('like_new', '几乎全新'),
        ('good', '良好'),
        ('fair', '一般'),
        ('needs_repair', '需维修'),
    ]
    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        default='good',
        verbose_name="商品状态"
    )

    # 位置和联系方式
    location = models.CharField(max_length=100, blank=True, default='', verbose_name="所在位置")
    contact = models.CharField(max_length=50, default='未提供', verbose_name="联系方式")

    # 图片字段
    image = models.ImageField(
        upload_to='goods/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="商品图片",
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp'],
                message='只支持 JPG, JPEG, PNG, GIF, WebP 格式的图片'
            )
        ]
    )

    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='goods',
        null=True,
        blank=True,
        verbose_name="卖家"
    )

    # 购买相关字段
    buyer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchased_goods',
        verbose_name="购买者"
    )
    is_sold = models.BooleanField(default=False, verbose_name="是否已售出")
    sold_at = models.DateTimeField(null=True, blank=True, verbose_name="售出时间")

    # 时间信息
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return f"{self.name} - ¥{self.price}"

    # 获取图片URL的方法
    def get_image_url(self):
        """返回图片的完整URL"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None

    class Meta:
        verbose_name = "商品"
        verbose_name_plural = "商品"
        ordering = ['-created_at']


# 🔥 新增：评论模型
class Comment(models.Model):
    """商品评论模型"""
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=500, verbose_name='评论内容')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name='评分')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '商品评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username} - {self.goods.name}"


# 🔥 新增：点赞模型
class Like(models.Model):
    """商品点赞模型"""
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('goods', 'user')  # 防止重复点赞
        verbose_name = '商品点赞'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username} 喜欢 {self.goods.name}"


# 🔥 新增：收藏模型
class Favorite(models.Model):
    """商品收藏模型"""
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, related_name='favorites')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('goods', 'user')  # 防止重复收藏
        verbose_name = '商品收藏'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username} 收藏 {self.goods.name}"


# 🔥 新增：留言模型
class Message(models.Model):
    """用户与商家留言模型"""
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(max_length=500, verbose_name='留言内容')
    is_read = models.BooleanField(default=False, verbose_name='已读')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '用户留言'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}"