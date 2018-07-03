from _decimal import Decimal

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from requests import Response
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from goods.models import SKU
from orders.serializers import OrderSettlementSerializer,SaveOrderSerializer


class OrderSettlementView(APIView):
    """
    订单结算
    """
    permission_classes = [IsAuthenticated]  # 必须是登录后的用户

    def get(self, request):  # get请求向后端获取订单信息
        """
        获取
        """
        user = request.user

        # 从购物车中获取用户勾选要结算的商品信息
        redis_conn = get_redis_connection('cart')
        #hash 商品数量 sku_id count
        redis_cart_dict = redis_conn.hgetall('cart_%s' % user.id)
        #set 勾选商品
        redis_cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)

        cart = {}
        for sku_id in redis_cart_selected:
            cart[int(sku_id)] = int(redis_cart_dict[sku_id])

        # 查询商品信息
        sku_id_list = cart.keys()
        sku_obj_list = SKU.objects.filter(id__in=sku_id_list)
        for sku in sku_obj_list:
            sku.count = cart[sku.id]

        # 运费
        freight = Decimal('10.00')

        serializer = OrderSettlementSerializer({'freight': freight, 'skus': sku_obj_list})
        return Response(serializer.data)

class SaveOrderView(CreateAPIView):
    """
    保存订单
    """
    #接受参数
    #校验
    #获取购物车勾选结算的数据
    #创建订单保存
    #序列化返回
    permission_classes = [IsAuthenticated]
    serializer_class = SaveOrderSerializer