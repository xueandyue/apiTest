import json
from django.shortcuts import render
from django.http import HttpResponse
from Index.page import get_pager_info
from Index.models import EnvInfo, ProjectInfo, ModuleInfo, TestCaseInfo
from Common.util import get_ajax_msg, DataError
from django.core.exceptions import ObjectDoesNotExist
from Index.utils.common import set_filter_session
import logging
logger = logging.getLogger('apiTest')
from Index.Pmysql import Pmysql


def list_module(request, id):
    """
    模块列表
    :param request:
    :param id: str or int：当前页
    :return:
    """
    account = request.session["now_account"]
    # 获取userid
    username=request.session["now_account"]
    sql = 'SELECT id from UserInfo where  username= %s'
    params = [username]
    helper = Pmysql()
    data = helper.fetchone(sql,params)
    helper.close()
    userid=data['id']
    # 获取userid结束
    if request.is_ajax():
        module_info = json.loads(request.body.decode('utf-8'))
        if 'module_name' in module_info.keys():
            module_info['module_name']=module_info['module_name'].strip()
        if 'mode' in module_info.keys():  # del module
            msg = del_module_data(module_info.pop('id'))
        else:
            msg = module_info_logic(type=False, **module_info)
        return HttpResponse(get_ajax_msg(msg, 'ok'))
    else:
        filter_query = set_filter_session(request)
        module_list = get_pager_info(
            ModuleInfo, filter_query, '/Index/module_list/', id,userid=userid)
        dataInfo = {
            'account': account,
            'module': module_list[1],
            'page_list': module_list[0],
            'info': filter_query,
            'sum': module_list[2],
            'env': EnvInfo.objects.all().order_by('-create_time'),
            'project': ProjectInfo.objects.filter(userid=userid).order_by('-update_time')
        }
        return render(request,'Index/module_list.html', dataInfo)


def module_add(request):
    """
    新增模块
    :param request:
    :return:
    """
    account = request.session["now_account"]
    # 获取userid
    username=request.session["now_account"]
    sql = 'SELECT id from UserInfo where  username= %s'
    params = [username]
    helper = Pmysql()
    data = helper.fetchone(sql,params)
    helper.close()
    userid=data['id']
    # 获取userid结束
    if request.is_ajax():
        module_info = json.loads(request.body.decode('utf-8'))
        module_info['module_name']=module_info['module_name'].strip()
        msg = module_info_logic(**module_info)
        return HttpResponse(get_ajax_msg(msg, '/Index/module_list/1/'))
    elif request.method == 'GET':
        dataInfo = {
            'account': account,
            'data': ProjectInfo.objects.filter(userid=userid).values('project_name')
        }
        return render(request,'Index/add_module.html', dataInfo)


def del_module_data(id):
    """
    根据模块索引删除模块数据，强制删除其下所有用例及配置
    :param id: str or int:模块索引
    :return: ok or tips
    """
    try:
        module_name = ModuleInfo.objects.get_module_name('', type=False, id=id)
        TestCaseInfo.objects.filter(belong_module__module_name=module_name).delete()
        ModuleInfo.objects.get(id=id).delete()
    except ObjectDoesNotExist:
        return '删除异常，请重试'
    logging.info('{module_name} 模块已删除'.format(module_name=module_name))
    return 'ok'


def module_info_logic(type=True, **kwargs):
    """
    模块信息逻辑处理
    :param type: boolean: True:默认新增模块
    :param kwargs: dict: 模块信息
    :return:
    """
    if kwargs.get('module_name') is '':
        return '模块名称不能为空'
    if kwargs.get('belong_project') == '请选择':
        return '请选择项目，没有请先添加哦'
    if kwargs.get('test_user') is '':
        return '测试人员不能为空'
    return add_module_data(type, **kwargs)


def add_module_data(type, **kwargs):
    """
    模块信息落地
    :param type: boolean: true: 新增， false: 更新
    :param kwargs: dict
    :return: ok or tips
    """
    module_opt = ModuleInfo.objects
    belong_project = kwargs.pop('belong_project')
    module_name = kwargs.get('module_name')
    if type:
        if module_opt.filter(belong_project__project_name__exact=belong_project) \
                .filter(module_name__exact=module_name).count() < 1:
            try:
                belong_project = ProjectInfo.objects.get_pro_name(belong_project, type=False)
            except ObjectDoesNotExist:
                logging.error('项目信息读取失败：{belong_project}'.format(belong_project=belong_project))
                return '项目信息读取失败，请重试'
            kwargs['belong_project'] = belong_project
            try:
                module_opt.insert_module(**kwargs)
            except DataError:
                return '模块信息过长'
            except Exception:
                logging.error('模块添加异常：{kwargs}'.format(kwargs=kwargs))
                return '添加失败，请重试'
            logger.info('模块添加成功：{kwargs}'.format(kwargs=kwargs))
        else:
            return '该模块已在项目中存在，请重新编辑'
    else:
        if module_name != module_opt.get_module_name('', type=False, id=kwargs.get('index')) \
                and module_opt.filter(belong_project__project_name__exact=belong_project) \
                .filter(module_name__exact=module_name).count() > 0:
            return '该模块已存在，请重新命名'
        try:
            module_opt.update_module(kwargs.pop('index'), **kwargs)
        except DataError:
            return '模块信息过长'
        except Exception:
            logging.error('更新失败：{kwargs}'.format(kwargs=kwargs))
            return '更新失败，请重试'
        logger.info('模块更新成功：{kwargs}'.format(kwargs=kwargs))
    return 'ok'