import json
from django.shortcuts import render
from django.http import HttpResponse
from Index.utils.common import set_filter_session
from Index.page import get_pager_info
from Index.models import TestSuite, ProjectInfo, EnvInfo, ModuleInfo
from Common.util import get_ajax_msg
from django.core.exceptions import ObjectDoesNotExist
from Index.Pmysql import Pmysql
import logging

logger = logging.getLogger('apiTest')


def list_suite(request, id):
    account = request.session["now_account"]
    # 获取userid
    username=request.session["now_account"]
    sql = 'SELECT id from userinfo where  username= %s'
    params = [username]
    helper = Pmysql()
    data = helper.fetchone(sql,params)
    helper.close()
    userid=data['id']
    if request.is_ajax():
        suite_info = json.loads(request.body.decode('utf-8'))

        if suite_info.get('mode') == 'del':
            msg = del_suite_data(suite_info.pop('id'))
        elif suite_info.get('mode') == 'copy':
            msg = copy_suite_data(suite_info.get('data').pop('index'), suite_info.get('data').pop('name'))
        return HttpResponse(get_ajax_msg(msg, 'ok'))
    else:
        filter_query = set_filter_session(request)
        pro_list = get_pager_info(
            TestSuite, filter_query, '/Index/suite_list/', id,userid=userid)
        dataInfo = {
            'account': account,
            'suite': pro_list[1],
            'page_list': pro_list[0],
            'info': filter_query,
            'sum': pro_list[2],
            'env': EnvInfo.objects.all().order_by('-create_time'),
            'project': ProjectInfo.objects.filter(userid=userid).order_by('-update_time')
        }
        return render(request, 'Index/suite_list.html', dataInfo)


def suite_add(request):
    account = request.session["now_account"]
    # 获取userid
    username=request.session["now_account"]
    sql = 'SELECT id from userinfo where  username= %s'
    params = [username]
    helper = Pmysql()
    data = helper.fetchone(sql,params)
    helper.close()
    userid=data['id']

    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        msg = add_suite_data(**kwargs)
        return HttpResponse(get_ajax_msg(msg, '/Index/suite_list/1/'))

    elif request.method == 'GET':
        dataInfo = {
            'account': account,
            'project': ProjectInfo.objects.filter(userid=userid).values('project_name').order_by('-create_time')
        }
        return render(request, 'Index/add_suite.html', dataInfo)


def suite_edit(request, id=None):
    account = request.session["now_account"]
    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        msg = edit_suite_data(**kwargs)
        return HttpResponse(get_ajax_msg(msg, '/Index/suite_list/1/'))

    suite_info = TestSuite.objects.get(id=id)
    belong_project_id = suite_info.belong_project_id
    modules = ModuleInfo.objects.all().filter(belong_project__exact=belong_project_id).values('id', 'module_name')
    dataInfo = {
        'account': account,
        'info': suite_info,
        'project': ProjectInfo.objects.all().values(
            'project_name').order_by('-create_time'),
        'module': modules
    }
    return render(request, 'Index/edit_suite.html', dataInfo)


def del_suite_data(id):
    """
    根据Suite索引删除数据
    :param id: str or int: test or config index
    :return: ok or tips
    """
    try:
        TestSuite.objects.get(id=id).delete()
    except ObjectDoesNotExist:
        return '删除异常，请重试'
    logging.info('Suite已删除')
    return 'ok'

def copy_suite_data(id, name):
    """
    复制suite信息，默认插入到当前项目、莫夸
    :param id: str or int: 复制源
    :param name: str：新用例名称
    :return: ok or tips
    """
    try:
        suite = TestSuite.objects.get(id=id)
        belong_project = suite.belong_project
    except ObjectDoesNotExist:
        return '复制异常，请重试'
    if TestSuite.objects.filter(suite_name=name, belong_project=belong_project).count() > 0:
        return 'Suite名称重复了哦'
    suite.id = None
    suite.suite_name = name
    suite.save()
    logging.info('{name}suite添加成功'.format(name=name))
    return 'ok'


def add_suite_data(**kwargs):
    belong_project = kwargs.pop('project')
    # config = kwargs.pop('config')
    suite_name = kwargs.get('suite_name')
    kwargs['belong_project'] = ProjectInfo.objects.get(project_name=belong_project)
    # kwargs['include']

    try:
        if TestSuite.objects.filter(belong_project__project_name=belong_project, suite_name=suite_name).count() > 0:
            return 'Suite已存在, 请重新命名'
        TestSuite.objects.create(**kwargs)
        logging.info('suite添加成功: {kwargs}'.format(kwargs=kwargs))
    except Exception:
        return 'suite添加异常，请重试'
    return 'ok'


def edit_suite_data(**kwargs):
    id = kwargs.pop('id')
    project_name = kwargs.pop('project')
    suite_name = kwargs.get('suite_name')
    include = kwargs.pop('include')
    belong_project = ProjectInfo.objects.get(project_name=project_name)

    suite_obj = TestSuite.objects.get(id=id)
    try:
        if suite_name != suite_obj.suite_name and \
                TestSuite.objects.filter(belong_project=belong_project, suite_name=suite_name).count() > 0:
            return 'Suite已存在, 请重新命名'
        suite_obj.suite_name = suite_name
        suite_obj.belong_project = belong_project
        suite_obj.include = include
        suite_obj.save()
        logging.info('suite更新成功: {kwargs}'.format(kwargs=kwargs))
    except Exception:
        return 'suite添加异常，请重试'
    return 'ok'
