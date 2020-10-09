from django.http import HttpResponse
from django.shortcuts  import render
import json
from Common.util import get_ajax_msg, key_value_dict, key_value_list, DataError
from Index.models import ProjectInfo, ModuleInfo, TestCaseInfo
from Index.Module.case import del_test_data, copy_test_data
from Index.utils.common import set_filter_session
from Index.page import get_pager_info
from Index.Pmysql import Pmysql
import logging
logger = logging.getLogger('apiTest')


def config_add(request):
    """
    新增配置
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
        testconfig_info = json.loads(request.body.decode('utf-8'))
        msg = config_info_logic(**testconfig_info)
        return HttpResponse(get_ajax_msg(msg, '/Index/config_list/1/'))
    elif request.method == 'GET':
        dataInfo = {
            'account': account,
            'project': ProjectInfo.objects.filter(userid=userid).values('project_name').order_by('-create_time')
        }
        return render(request, 'Index/add_config.html', dataInfo)


def list_config(request, id):
    """
    配置列表
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
        test_info = json.loads(request.body.decode('utf-8'))

        if test_info.get('mode') == 'del':
            msg = del_test_data(test_info.pop('id'))
        elif test_info.get('mode') == 'copy':
            msg = copy_test_data(test_info.get('data').pop('index'), test_info.get('data').pop('name'))
        return HttpResponse(get_ajax_msg(msg, 'ok'))
    else:
        filter_query = set_filter_session(request)
        test_list = get_pager_info(
            TestCaseInfo, filter_query, '/Index/config_list/', id,userid=userid)
        dataInfo = {
            'account': account,
            'test': test_list[1],
            'page_list': test_list[0],
            'info': filter_query,
            'project': ProjectInfo.objects.filter(userid=userid).order_by('-update_time')
        }
        return render(request, 'Index/config_list.html', dataInfo)


def config_edit(request, id=None):
    """
    编辑配置
    :param request:
    :param id:
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
        testconfig_lists = json.loads(request.body.decode('utf-8'))
        msg = config_info_logic(type=False, **testconfig_lists)
        return HttpResponse(get_ajax_msg(msg, '/Index/config_list/1/'))

    config_info = TestCaseInfo.objects.get_case_by_id(id)
    req = eval(config_info[0].request)
    dataInfo = {
        'account': account,
        'info': config_info[0],
        'request': req['config'],
        'project': ProjectInfo.objects.filter(userid=userid).values(
            'project_name').order_by('-create_time')
    }
    return render(request, 'Index/edit_config.html', dataInfo)


def config_info_logic(type=True, **kwargs):
    """
    模块信息逻辑处理及数据处理
    :param type: boolean: True 默认新增 False：更新数据
    :param kwargs: dict: 模块信息
    :return: ok or tips
    """
    config = kwargs.pop('config')
    '''
        动态展示模块
    '''
    if 'request' not in config.keys():
        return load_modules(**config)
    else:
        logging.debug('配置原始信息: {kwargs}'.format(kwargs=kwargs))
        if config.get('name').get('config_name') is '':
            return '配置名称不可为空'
        if config.get('name').get('author') is '':
            return '创建者不能为空'
        if config.get('name').get('project') == '请选择':
            return '请选择项目'
        if config.get('name').get('module') == '请选择':
            return '请选择或者添加模块'
        if config.get('name').get('project') == '':
            return '请先添加项目'
        if config.get('name').get('module') == '':
            return '请添加模块'

        name = config.pop('name')
        config.setdefault('name', name.pop('config_name'))

        config.setdefault('config_info', name)

        request_data = config.get('request').pop('request_data')
        data_type = config.get('request').pop('type')
        if request_data and data_type:
            if data_type == 'json':
                config.get('request').setdefault(data_type, request_data)
            else:
                data_dict = key_value_dict('data', **request_data)
                if not isinstance(data_dict, dict):
                    return data_dict
                config.get('request').setdefault(data_type, data_dict)

        headers = config.get('request').pop('headers')
        if headers:
            config.get('request').setdefault('headers', key_value_dict('headers', **headers))

        variables = config.pop('variables')
        if variables:
            variables_list = key_value_list('variables', **variables)
            if not isinstance(variables_list, list):
                return variables_list
            config.setdefault('variables', variables_list)

        parameters = config.pop('parameters')
        if parameters:
            params_list = key_value_list('parameters', **parameters)
            if not isinstance(params_list, list):
                return params_list
            config.setdefault('parameters', params_list)

        hooks = config.pop('hooks')
        if hooks:

            setup_hooks_list = key_value_list('setup_hooks', **hooks)
            if not isinstance(setup_hooks_list, list):
                return setup_hooks_list
            config.setdefault('setup_hooks', setup_hooks_list)

            teardown_hooks_list = key_value_list('teardown_hooks', **hooks)
            if not isinstance(teardown_hooks_list, list):
                return teardown_hooks_list
            config.setdefault('teardown_hooks', teardown_hooks_list)

        kwargs.setdefault('config', config)
        return add_config_data(type, **kwargs)

def load_modules(**kwargs):
    """
    加载对应项目的模块信息，用户前端ajax请求返回
    :param kwargs:  dict：项目相关信息
    :return: str: module_info
    """
    belong_project = kwargs.get('name').get('project')
    module_info = ModuleInfo.objects.filter(belong_project__project_name=belong_project) \
        .values_list('id', 'module_name').order_by('-create_time')
    module_info = list(module_info)
    string = ''
    for value in module_info:
        string = string + str(value[0]) + '^=' + value[1] + 'replaceFlag'
    return string[:len(string) - 11]


def add_config_data(type, **kwargs):
    """
    配置信息落地
    :param type: boolean: true: 添加新配置， fasle: 更新配置
    :param kwargs: dict
    :return: ok or tips
    """
    case_opt = TestCaseInfo.objects
    config_info = kwargs.get('config').get('config_info')
    name = kwargs.get('config').get('name')
    module = config_info.get('module')
    project = config_info.get('project')
    belong_module = ModuleInfo.objects.get_module_name(module, type=False)


    try:
        if type:

            if case_opt.get_case_by_name(name,module,project).count() < 1:
                case_opt.insert_config(belong_module, **kwargs)
                logger.info('{name}配置添加成功: {kwargs}'.format(name=name, kwargs=kwargs))
            else:
                return '用例或配置已存在，请重新编辑'
        else:
            index = config_info.get('test_index')
            if name != case_opt.get_case_by_id(index, type=False) \
                    and case_opt.get_case_by_name(name,module,project).count() > 0:
                return '用例或配置已在该模块中存在，请重新命名'
            case_opt.update_config(belong_module, **kwargs)
            logger.info('{name}配置更新成功: {kwargs}'.format(name=name, kwargs=kwargs))
    except DataError:
        logger.error('{name}配置信息过长：{kwargs}'.format(name=name, kwargs=kwargs))
        return '字段长度超长，请重新编辑'
    return 'ok'