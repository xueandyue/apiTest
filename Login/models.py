from django.db import models
from Login.managers import UserInfoManager,UserTypeManager


# Create your models here.
class BaseInfo(models.Model):
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        abstract = True
        verbose_name = '公共字段表'
        db_table = 'BaseInfo'



