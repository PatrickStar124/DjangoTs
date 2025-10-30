from django.db import models
from django.contrib.auth.models import User  # 新增导入


class Goods(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="商品名称",
        default="默认商品名称"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="价格",
        default=0.00
    )
    description = models.TextField(blank=True, verbose_name="描述")
    category = models.CharField(
        max_length=100,
        verbose_name="分类",
        default="通用分类"
    )

    # 新增缺失的字段
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="卖家",
        null=True,  # 允许为空，避免迁移问题
        blank=True
    )
    is_sold = models.BooleanField(
        default=False,
        verbose_name="是否已售出"
    )
    image_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="图片链接",
        default="https://via.placeholder.com/300x200?text=商品图片"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "商品"
        verbose_name_plural = "商品"

    def __str__(self):
        return self.title