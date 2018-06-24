import urllib
from urllib.request import urlopen
import logging
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer
from rest_framework.utils import json
from . import constants
from .exceptions import OAuthQQAPIError
from django.conf import settings  #无论配置文件在哪都可以找到

logger = logging.getLogger('django')

class OAuthQQ(object):
    """
    QQ认证辅助工具类
    """
    #定义对象属性
    def __init__(self,client_id=None,client_secret=None,redirect_uri=None,state=None):
        self.client_id = client_id if client_id else settings.QQ_CLIENT_ID
        self.redirect_uri = redirect_uri if redirect_uri else settings.QQ_REDIRECT_URI
        # self.state = state if state else settings.QQ_STATE
        self.state = state or settings.QQ_STATE
        self.client_secret = client_secret if client_secret else settings.QQ_CLIENT_SECRET


    def get_login_url(self):
        """获取QQ登录的网址"""
        url = 'https://graph.qq.com/oauth2.0/authorize?' #根据QQ文档要求，需要去这个网址去获取
        #但是有以下几个必须要传的参数
        params = {
            'response_type':'code', #要求必须传code
            'client_id':self.client_id, #这是注册成为QQ开发者所获得的
            'redirect_uri':self.redirect_uri, #同上
            'state':self.state #可以用来存储next参数

        }

        url += urllib.parse.urlencode(params) #在url的基础上，将必传参数以查询字符串的方式（因为是GET方式）拼接好
        return url #将url返回

    def get_access_token(self,code):
        url = 'https://graph.qq.com/oauth2.0/token?'

        params = {
            'grant_type':'authorization_code',
            'client_id':self.client_id,
            'client_secret':self.client_secret,
            'code':code,
            'redirect_uri':self.redirect_uri
        }
        url += urllib.parse.urlencode(params)
        try:
            #发送请求
            resp = urlopen(url)
            #读取响应体数据
            resp_data = resp.read() #bytes
            resp_data = resp_data.decode() #str
            #解析 access_token
            resp_dict = urllib.parse.parse_qs(resp_data)
        except Exception as e:
            logger.error('获取access_token失败%s'%e)
            raise OAuthQQAPIError
        else:
            access_token = resp_dict.get('access_token')
            return access_token[0]

    def get_open_id(self,access_token):
        url = 'https://graph.qq.com/oauth2.0/me?access_token='+access_token

        try:
            #发送请求
            resp = urlopen(url)
            #读取响应体数据
            resp_data = resp.read() #bytes
            resp_data = resp_data.decode() #str
            #解析 callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} );
            resp_data = resp_data[10:-4]
            resp_dict = json.loads(resp_data)
        except Exception as e:
            logger.error('获取openid失败%s'%e)
            raise OAuthQQAPIError
        else:
            openid = resp_dict.get('openid')
            return openid

    def generate_bind_user_access_token(self,openid):
        serializer = TJWSSerializer(settings.SECRET_KEY,constants.BIND_USER_ACCESS_TOKEN_EXPIRES)
        token = serializer.dumps({'openid':openid})
        return token.decode()

