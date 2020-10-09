from django.db import models
from Login.managers import userinfoManager,UserTypeManager


# Create your models here.
class BaseInfo(models.Model):
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        abstract = True
        verbose_name = '公共字段表'
        db_table = 'BaseInfo'

class userinfo(BaseInfo):
    class Meta:
        verbose_name = '用户信息'
        db_table = 'userinfo'
    username = models.CharField('用户名', max_length=20, unique=True, null=False)
    password = models.CharField('密码', max_length=20, null=False)
    email = models.EmailField('邮箱', null=False, unique=True)
    status = models.IntegerField('有效/无效', default=1)
    objects = userinfoManager()


class UserType(BaseInfo):
    class Meta:
        verbose_name = '用户类型'
        db_table = 'UserType'
    type_name = models.CharField('类型名称', max_length=20)
    type_desc = models.CharField('描述', max_length=20)
    objects = UserTypeManager()

