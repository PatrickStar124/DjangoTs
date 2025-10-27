from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def get_data(request):
    goods={"name":"测试商品","price":12.3}
    return Response(goods)