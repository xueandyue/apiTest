import json
from django.shortcuts import render
from django.http import HttpResponse
from Index.page import get_pager_info
from Index.models import EnvInfo
from Common.util import get_ajax_msg, DataError
from django.core.exceptions import ObjectDoesNotExist
import logging


def set_env(request):
    """
    环境设置
    :param request:
    :return:
    """

    account = request.session["now_account"]
    if request.is_ajax():
        env_lists = json.loads(request.body.decode('utf-8'))
        msg = env_data_logic(**env_lists)
        return HttpResponse(get_ajax_msg(msg, 'ok'))

    elif request.method == 'GET':
        return render(request, 'Index/env_list.html', {'account': account})


def list_env(request, id):
    """
    环境列表
    :param request:
    :param id: str or int：当前页
    :return:
    """

    account = request.session["now_account"]
    if request.method == 'GET':
        env_lists = get_pager_info(
            EnvInfo, None, '/Index/env_list/', id)
        dataInfo = {
            'account': account,
            'env': env_lists[1],
            'page_list': env_lists[0],
        }
        return render(request,'Index/env_list.html', dataInfo)


def env_data_logic(**kwargs):
    """
    环境信息逻辑判断及落地
    :param kwargs: dict
    :return: ok or tips
    """
    id = kwargs.get('id', None)
    if id:
        try:
            EnvInfo.objects.delete_env(id)
        except ObjectDoesNotExist:
            return '删除异常，请重试'
        return 'ok'
    index = kwargs.pop('index')
    env_name = kwargs.get('env_name')
    if env_name is '':
        return '环境名称不可为空'
    elif kwargs.get('base_url') is '':
        return '请求地址不可为空'
    elif kwargs.get('simple_desc') is '':
        return '请添加环境描述'

    if index == 'add':
        try:
            if EnvInfo.objects.filter(env_name=env_name).count() < 1:
                EnvInfo.objects.insert_env(**kwargs)
                logging.info('环境添加成功：{kwargs}'.format(kwargs=kwargs))
                return 'ok'
            else:
                return '环境名称重复'
        except DataError:
            return '环境信息过长'
        except Exception:
            logging.error('添加环境异常：{kwargs}'.format(kwargs=kwargs))
            return '环境信息添加异常，请重试'
    else:
        try:
            if EnvInfo.objects.get_env_name(index) != env_name and EnvInfo.objects.filter(
                    env_name=env_name).count() > 0:
                return '环境名称已存在'
            else:
                EnvInfo.objects.update_env(index, **kwargs)
                logging.info('环境信息更新成功：{kwargs}'.format(kwargs=kwargs))
                return 'ok'
        except DataError:
            return '环境信息过长'
        except ObjectDoesNotExist:
            logging.error('环境信息查询失败：{kwargs}'.format(kwargs=kwargs))
            return '更新失败，请重试'