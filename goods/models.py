from django.db import models

class Goods(models.Model):
    # 给 title 字段添加 default，解决非空默认值问题
    title = models.CharField(
        max_length=200,
        verbose_name="商品名称",
        default="默认商品名称"  # 新增默认值
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="价格",
        default=0.00  # 建议也给 price 加默认值，避免后续可能的同类问题
    )
    description = models.TextField(blank=True, verbose_name="描述")
    category = models.CharField(
        max_length=100,
        verbose_name="分类",
        default="通用分类"  # 之前加的默认值
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "商品"
        verbose_name_plural = "商品"

    def __str__(self):
        return self.title