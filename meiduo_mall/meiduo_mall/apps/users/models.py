from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer

# Create your models here.
from users import constants


class User(AbstractUser):
    """用户模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    # 给模型类增加一个方法而已，不会影响数据库的迁移
    def generate_verify_email_url(self):
        """
        生成验证邮箱的url
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        data = {'user_id': self.id, 'email': self.email} #嵌入token的数据，可以自己更改，只要生成的url能够唯一标识用户是谁即可
        token = serializer.dumps(data).decode()  # 因为发给每个人的链接都不一样，所以写在模型类中了，又因为怕别人篡改url中的user_id所以使用itsdangerous生成token，而把用户id嵌入token
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token
        return verify_url