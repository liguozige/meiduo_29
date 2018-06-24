from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from oauth.models import OAuthQQUser
from .utils import OAuthQQ
from .exceptions import OAuthQQAPIError

# Create your views here.
#  url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),

                    #因为不需要DRF来帮助我们实现什么
class QQAuthURLView(APIView):
    """
    获取QQ登录的url   ?next=xxx
    """
    def get(self,request):
        #获取next参数(不是必传参数，所以不用校验)  因为next参数是查询字符串
        next = request.query_params.get("next")

        #拼接QQ登录的网址  自己封装，以后不管谁来调用QQ登录的接口，都可以。需要按照qq文档的要求，以类的方式封装，后面还要向qq发送请求或企业access_token 和open_id
        oauth_qq = OAuthQQ(state=next)
        login_url = oauth_qq.get_login_url()

        #返回给前端
        return Response({'login_url':login_url})


class QQAuthUserView(APIView):
    """
    QQ登录的用户
    """
    def get(self,request):
        #获取code
        code = request.query_params.get('code')
        if not code:
            return Response({'message':'缺少code'},status=status.HTTP_400_BAD_REQUEST)

        oauth_qq = OAuthQQ()
        try:
            # 凭借code获取access_token
            access_token = oauth_qq.get_access_token(code)
            # 凭借access_token 获取openid
            openid = oauth_qq.get_open_id(access_token)
        except OAuthQQAPIError:
            return Response({'message':'访问QQ接口异常'},status=status.HTTP_503_SERVICE_UNAVAILABLE)

        #根据openid查询数据库OAuthQQUser 判断数据是否存在
        try:
            oauth_qq_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果数据不存在，处理openid 并返回
            access_token = oauth_qq.generate_bind_user_access_token(openid)
        else:
            #如果数据存在，表示用户已经绑定过身份，签发JWT token
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            user = oauth_qq_user.user
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            return ({
                'username':user.username,
                'user_id':user.id,
                'token':user.token
            })



