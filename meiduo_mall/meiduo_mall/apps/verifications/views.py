from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from meiduo_mall.libs.captcha.captcha import captcha
from django_redis import get_redis_connection  #通过get_redis_connection可以拿到一个连接对象，通过这个对象可以执行redis指令

from . import constants

# Create your views here.


class ImageCodeView(APIView): #因为不需要使用序列化器，所以使用APIView，因为只有这个和序列化器无关
    """图片验证码"""
    def get(self,request,image_code_id):
        #接受参数   接收参数和校验参数因为是在url中就进行了正则匹配了，
        #校验参数   所以不用考虑使用序列化器帮我们校验了，所以只需要在get方法里接收校验好的参数即可

        #生成图片验证码图片
        text,image = captcha.generate_captcha()
        print(text)
        print(image)

        #保存真实值
        redis_conn = get_redis_connection('verify_codes')
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        #返回图片
        return HttpResponse(image,content_type='image/jpg')
