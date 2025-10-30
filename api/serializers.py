from rest_framework import serializers
from goods.models import Goods
from django.contrib.auth.models import User  # 导入User模型，用于优化seller显示


# 先定义一个简化的用户序列化器（只返回必要信息，避免暴露敏感数据）
class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']  # 只返回用户ID和用户名，隐藏密码、邮箱等


# 再修改商品序列化器
class GoodsSerializer(serializers.ModelSerializer):
    # 1. 用简化的用户序列化器处理seller，返回清晰的用户信息（而非纯ID）
    seller = SimpleUserSerializer(read_only=True)  # read_only=True：禁止前端修改

    class Meta:
        model = Goods
        # 2. 明确指定需要的字段，替代 fields='__all__'，排除不需要的或敏感的
        fields = [
            'id', 'title', 'price', 'description', 'category',
            'seller', 'is_sold', 'image_url', 'created_at', 'updated_at'
        ]
        # 3. 额外指定哪些字段是只读的（即使前端传了也会被忽略）
        read_only_fields = ['id', 'seller', 'created_at', 'updated_at']

    # 可选：添加字段验证（比如防止价格为负数，避免无效数据）
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("商品价格不能为负数")
        return value