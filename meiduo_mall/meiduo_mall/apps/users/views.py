from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework import mixins
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from users import constants
from users.serializers import AddUserBrowsingHistorySerializer, SKUSerializer
from . import serializers
from users.models import User



# Create your views here.

# url(r'^users/$', views.UserView.as_view()),
class UserView(CreateAPIView):
    """
    用户注册
    传入参数：
        username, password, password2, sms_code, mobile, allow
    """
    serializer_class = serializers.CreateUserSerializer
    #接受参数

    #校验参数

    #保存用户数据  密码加密

    #序列化 返回数据

# url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
class MobileCountView(APIView):
    """
    手机号数量
    """
    def get(self, request, mobile):
        """
        获取指定手机号数量
        """
        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)


# url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
class UsernameCountView(APIView):
    """
    用户名数量
    """
    def get(self, request, username):
        """
        获取指定用户名数量
        """
        count = User.objects.filter(username=username).count()

        data = {
            'username': username,
            'count': count
        }

        return Response(data)


class UserDetailView(RetrieveAPIView):
    """
    用户详情
    """
    # RetrieveAPIView这个视图中的序列化器会帮我们完成
    # def get(self):
    #     #查询用户数据
    #
    #     #序列化返回
    serializer_class = serializers.UserDetailSerializer
    permission_classes = [IsAuthenticated]  # 指明必须登录认证后才能访问
    # queryset = User.objects.all()  # 指明数据的来源，可以通过重写get_object()方法
    def get_object(self):
        # 返回当前请求的用户
        # 在类视图对象中，可以通过类视图对象的属性获取request
        # 在django的请求request对象中，user属性表明当前请求的用户
        return self.request.user


class EmailView(UpdateAPIView):
    """
    保存用户邮箱
    """
    serializer_class = serializers.EmailSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user

    # def put(self):
    #     # 获取email
    #     # 校验email
    #     # 查询user
    #     # 更新数据
    #     # 序列化返回


# url(r'^emails/verification/$', views.VerifyEmailView.as_view()),
class VerifyEmailView(APIView):
    """
    邮箱验证
    """
    def get(self,request):
        # 获取token
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证token
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({'message': '链接信息无效'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.email_active = True
            user.save()
            return Response({'message': 'OK'})

class UserBrowsingHistoryView(mixins.CreateModelMixin, GenericAPIView):
    """
    用户浏览历史记录
    """
    serializer_class = AddUserBrowsingHistorySerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        保存
        """
        return self.create(request)

    def get(self, request):
        """
        获取
        """
        #获取user_id
        user_id = request.user.id
        #查询redis  list
        redis_conn = get_redis_connection("history")
        sku_id_list = redis_conn.lrange("history_%s" % user_id, 0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT - 1)

        skus = []
        # 为了保持查询出的顺序与用户的浏览历史保存顺序一致,使用for循环
        for sku_id in sku_id_list:
            sku = SKU.objects.get(id=sku_id)
            skus.append(sku)

        #序列化返回
        serializer = SKUSerializer(skus, many=True)
        return Response(serializer.data)

