import json
from django.shortcuts import render
from django.http import HttpResponse
from Index.page import get_pager_info
from Index.models import EnvInfo, ProjectInfo, ModuleInfo, TestCaseInfo, TestSuite, DebugTalk,ENV
from Common.util import get_ajax_msg, DataError
from django.core.exceptions import ObjectDoesNotExist
from Index.utils.common import set_filter_session, load_modules
import logging
logger = logging.getLogger('apiTest')
from Index.Pmysql import Pmysql

def list_project(request, id):
    """
    项目列表
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
        project_info = json.loads(request.body.decode('utf-8'))
        if 'mode' in project_info.keys():
            # 删除项目
            msg = del_project_data(project_info.pop('id'))
        else:
            msg = project_info_logic(type=False, **project_info)
        return HttpResponse(get_ajax_msg(msg, 'ok'))
    else:
        filter_query = set_filter_session(request)
        pro_list = get_pager_info(
            ProjectInfo, filter_query, '/Index/project_list/', id,userid=userid)
        dataInfo = {
            'account': account,
            'project': pro_list[1],
            'page_list': pro_list[0],
            'info': filter_query,
            'sum': pro_list[2],
            'env': EnvInfo.objects.all().order_by('-create_time'),
            'project_all': ProjectInfo.objects.filter(userid=userid).order_by('-update_time')
        }
        return render(request,'Index/project_list.html', dataInfo)


def project_add(request):
    """
    新增项目
    """
    account = request.session['now_account']
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
        project_info = json.loads(request.body.decode("utf-8"))
        project_info['userid']=userid
        project_info['project_name']=(project_info['project_name']).strip()

        msg = project_info_logic(**project_info)
        return HttpResponse(get_ajax_msg(msg, '/Index/project_list/1'))
    elif request.method == 'GET':
        data = {
            'account':account
        }
        return render(request,'Index/add_project.html', data)


def project_info(request):
    """
     获取项目相关信息
     :param request:
     :return:
     """

    if request.is_ajax():
        project_info = json.loads(request.body.decode('utf-8'))

        msg = load_modules(**project_info.pop('task'))
        return HttpResponse(msg)


def del_project_data(id):
    """
    根据项目索引删除项目数据，强制删除其下所有用例、配置、模块、Suite
    :param id: str or int: 项目索引
    :return: ok or tips
    """
    try:
        project_name = ProjectInfo.objects.get_pro_name('', type=False, id=id)

        belong_modules = ModuleInfo.objects.filter(belong_project__project_name=project_name).values_list('module_name')
        for obj in belong_modules:
            TestCaseInfo.objects.filter(belong_module__module_name=obj).delete()

        TestSuite.objects.filter(belong_project__project_name=project_name).delete()

        ModuleInfo.objects.filter(belong_project__project_name=project_name).delete()

        DebugTalk.objects.filter(belong_project__project_name=project_name).delete()

        ProjectInfo.objects.get(id=id).delete()

    except ObjectDoesNotExist:
        return '删除异常，请重试'
    logging.info('{project_name} 项目已删除'.format(project_name=project_name))
    return 'ok'

def project_info_logic(type=True, **kwargs):
    """
    项目信息逻辑处理
    :param type: boolean:True 默认新增项目
    :param kwargs: dict: 项目信息
    :return:
    """
    if kwargs.get('project_name') is '':
        return '项目名称不能为空'
    if kwargs.get('responsible_name') is '':
        return '负责人不能为空'
    if kwargs.get('test_user') is '':
        return '测试人员不能为空'
    if kwargs.get('dev_user') is '':
        return '开发人员不能为空'
    if kwargs.get('publish_app') is '':
        return '发布应用不能为空'

    return add_project_data(type, **kwargs)


def add_project_data(type, **kwargs):
    """
    项目信息落地 新建时必须默认添加debugtalk.py
    :param type: true: 新增， false: 更新
    :param kwargs: dict
    :return: ok or tips
    """
    project_opt = ProjectInfo.objects
    project_name = kwargs.get('project_name')
    if type:
        if project_opt.get_pro_name(project_name) < 1:
            try:
                project_opt.insert_project(**kwargs)
                belong_project = project_opt.get(project_name=project_name)
                DebugTalk.objects.create(belong_project=belong_project, debugtalk='# debugtalk.py')
                ENV.objects.create(belong_project=belong_project, env='')
            except DataError:
                return '项目信息过长'
            except Exception as e:
                logging.error('项目添加异常：{kwargs}'.format(kwargs=kwargs))
                return '添加失败，请重试'
            logger.info('项目添加成功：{kwargs}'.format(kwargs=kwargs))
        else:
            return '该项目已存在，请重新编辑'
    else:
        if project_name != project_opt.get_pro_name('', type=False, id=kwargs.get(
                'index')) and project_opt.get_pro_name(project_name) > 0:
            return '该项目已存在， 请重新命名'
        try:
            project_opt.update_project(kwargs.pop('index'), **kwargs)  # testcaseinfo的belong_project也得更新，这个字段设计的有点坑了
        except DataError:
            return '项目信息过长'
        except Exception:
            logging.error('更新失败：{kwargs}'.format(kwargs=kwargs))
            return '更新失败，请重试'
        logger.info('项目更新成功：{kwargs}'.format(kwargs=kwargs))

    return 'ok'