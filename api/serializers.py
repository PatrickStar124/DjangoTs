from rest_framework import serializers
from goods.models import Goods

class GoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        # 明确序列化字段，包含模型所有必要字段
        fields = [
            "id", "name", "price", "description", "category", "condition",
            "location", "contact", "image", "seller", "is_sold", "created_at",
            "updated_at", "get_image_url"
        ]
        # 只读字段（后端自动填充，前端无需传参）
        read_only_fields = ["seller", "is_sold", "created_at", "updated_at"]

    # 重写create方法：自动关联当前登录用户为卖家
    def create(self, validated_data):
        validated_data["seller"] = self.context["request"].user
        return super().create(validated_data)