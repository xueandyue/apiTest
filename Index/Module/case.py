import json, os, yaml
from django.http import HttpResponse
from django.shortcuts import render
from Index.models import ProjectInfo, ModuleInfo, TestCaseInfo, EnvInfo
from Common.util import get_ajax_msg, key_value_list, key_value_dict, DataError
from django.core.exceptions import ObjectDoesNotExist
from Index.utils.common import set_filter_session, load_modules, load_cases
from Index.page import get_pager_info
import logging
from Common.config import API_TYPE, TEST_CASE_TYPE
from Index.Pmysql import Pmysql
logger = logging.getLogger('apiTest.case')

def case_add(request):
    """
    新增用例
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
        testcase_info = json.loads(request.body.decode('utf-8'))
        print(testcase_info)
        msg = case_info_logic(**testcase_info)
        return HttpResponse(get_ajax_msg(msg, '/Index/test_list/1/'))
    elif request.method == 'GET':
        dataInfo = {
            'account': account,
            'project': ProjectInfo.objects.filter(userid=userid).values('project_name').order_by('-update_time')
        }
        return render(request, 'Index/add_case.html', dataInfo)


def case_list(request, id):
    """
    用例列表
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
            ids = test_info.pop('id')
            for test_id in ids:
                msg = del_test_data(test_id)
        elif test_info.get('mode') == 'copy':
            msg = copy_test_data(test_info.get('data').pop('index'), test_info.get('data').pop('name'))
        return HttpResponse(get_ajax_msg(msg, 'ok'))

    else:
        filter_query = set_filter_session(request)
        test_list = get_pager_info(
            TestCaseInfo, filter_query, '/Index/test_list/', id,userid=userid)
        dataInfo = {
            'account': account,
            'test': test_list[1],
            'page_list': test_list[0],
            'info': filter_query,
            'env': EnvInfo.objects.all().order_by('-create_time'),
            'project': ProjectInfo.objects.filter(userid=userid).order_by('-update_time')
        }
        return render(request,'Index/test_list.html', dataInfo)


def case_edit(request, id=None):
    """
    编辑用例
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
        testcase_lists = json.loads(request.body.decode('utf-8'))
        msg = case_info_logic(type=False, **testcase_lists)
        return HttpResponse(get_ajax_msg(msg, '/Index/test_list/1/'))
    api = {}
    test_info = TestCaseInfo.objects.get_case_by_id(id)

    req = eval(test_info[0].request)
    # include = test_info[0].include

    info = test_info[0]
    case_type = test_info[0].type
    belong_project = test_info[0].belong_project
    belong_module_id = test_info[0].belong_module_id
    #获取当前case的project_id
    project_id = ProjectInfo.objects.all().filter(project_name__exact=belong_project).values('id')[0]['id']
    modules = ModuleInfo.objects.all().filter(belong_project__exact=project_id).values('id', 'module_name')
    # configs = TestCaseInfo.objects.all().filter(belong_module_id__exact=belong_module_id, type__exact=2).values('id', 'name')
    if "test" in req.keys() and "api" in req['test'].keys():
        api_id = req['test']['api']
        api_info = TestCaseInfo.objects.get_case_by_id(api_id)
        api_name = api_info[0].name
        api = {'id': api_id, 'name': api_name}


    dataInfo = {
        'account': account,
        'info': info,
        'request': req['test'],
        # 'include': include,
        'project': ProjectInfo.objects.filter(userid=userid).values('project_name').order_by('-create_time'),
        'module': modules,
        # 'config': configs,
        'import_type': case_type,
        'api': api
    }

    return render(request, 'Index/edit_case.html', dataInfo)


def load_case_file(request):
    data = {}
    if request.method == 'POST':
        file = request.FILES.get('type_uploadfile')
        file_path = os.path.join('./upload', file.name)
        destination = open(file_path, 'wb+')
        for chunk in file.chunks():  # 分块写入文件
            destination.write(chunk)
        destination.close()
        read_file = open(file_path,encoding="utf8")
        extension = os.path.splitext(file.name)[1]
        file_data = ''
        if extension == '.json':
            file_data = json.load(read_file)
        if extension == '.yml':
            file_data = yaml.load(read_file)
        project = request.POST.get("project")
        module = request.POST.get("module")
        import_type = int(request.POST.get("import_type"))
        include = request.POST.get('include')
        config = request.POST.get('config')
        author = request.POST.get('author')
        case_name = request.POST.get('case_name')
        if import_type == 3:
            include = []
            config = ''
        if isinstance(file_data, dict):
            file_data['name'] = case_name
            test_case_list = [{'test': file_data}]
        else:
            test_case_list = file_data
        msg = ''
        for test_case in test_case_list:
            keys = test_case.keys()
            if "config" in keys or 'test' not in keys:
                continue
            test_case['test']['case_info'] = {'author': author,'config': config, 'include': include,'project': project ,'module':module,'import_type': import_type}
            if 'validate' in test_case['test'].keys():
                validates = test_case['test']['validate']
                validate_list = []
                for validate in validates:
                    comparator = list(validate.keys())[0]
                    validate_list.append({'comparator': comparator, 'check': validate[comparator][0], 'expect': validate[comparator][1]})
                test_case['test']['validate'] = validate_list
            if import_type == TEST_CASE_TYPE:
                test_case['test']['name'] = case_name + "_" + test_case['test']['name']
            test = test_case.get('test')
            logging.info('用例原始信息: {kwargs}'.format(kwargs=test_case))

            if test.get('name') is '':
                msg = '用例名称不可为空'
                break
            if test.get('case_info').get('module') == '请选择':
                msg = '请选择或者添加模块'
                break
            if test.get('case_info').get('project') == '请选择':
                msg = '请选择项目'
                break
            if test.get('case_info').get('project') == '':
                msg = '请先添加项目'
                break
            if test.get('case_info').get('module') == '':
                msg = '请添加模块'
                break
            if "api" in test.keys():
                api = test['api']
                if api == '':
                    msg = "用例[name：%s]引用的API为空：".format(test['name'])
                    break
                api_name = os.path.split(api)[1]
                file_name = os.path.splitext(api_name)[0]
                api_objs = TestCaseInfo.objects.get_case_by_name(file_name)
                if api_objs.count() < 1:
                    msg = "用例[name：%s]引用的API不存在：".format(test['name'])
                    break
                api_id = api_objs[0].id
                test_case['test']['api'] = api_id
                msg = add_case_data(type, **test_case)
            else:
                msg = add_case_data(type, **test_case)
        data['msg'] = get_ajax_msg(msg, 'ok')
    else:
        data['msg'] = "请求方式不为POST"
    return HttpResponse(json.dumps(data), content_type="application/json")


def del_test_data(id):
    """
    根据用例或配置索引删除数据
    :param id: str or int: test or config index
    :return: ok or tips
    """
    try:
        TestCaseInfo.objects.get(id=id).delete()
    except ObjectDoesNotExist:
        return '删除异常，请重试'
    logging.info('用例/配置已删除')
    return 'ok'


def case_info_logic(type=True, **kwargs):
    """
    用例信息逻辑处理以数据处理
    :param type: boolean: True 默认新增用例信息， False: 更新用例
    :param kwargs: dict: 用例信息
    :return: str: ok or tips
    """
    test = kwargs.pop('test')
    '''
        动态展示模块
    '''
    if 'request' not in test.keys() and 'api' not in test.keys():
        type = test.pop('type')
        if type == 'module':
            return load_modules(**test)
        elif type == 'case':
            return load_cases(**test)
        else:
            return load_cases(type=2, **test)

    else:
        logging.info('用例原始信息: {kwargs}'.format(kwargs=kwargs))
        if test.get('name').get('case_name') is '':
            return '用例名称不可为空'
        if test.get('name').get('module') == '请选择':
            return '请选择或者添加模块'
        if test.get('name').get('project') == '请选择':
            return '请选择项目'
        if test.get('name').get('project') == '':
            return '请先添加项目'
        if test.get('name').get('module') == '':
            return '请添加模块'

        name = test.pop('name')
        # case_type = name['import_type']
        test.setdefault('name', name.pop('case_name'))
        if 'describe' in test.keys():
            test.setdefault('describe', name.pop('describe'))
        else:
            test.setdefault('describe',"")
        test.setdefault('case_info', name)
        # if case_type == '3':
        #     kwargs.setdefault('test', test)
            # return add_case_data(type, **kwargs)

        validate = test.pop('validate')
        if validate:
            validate_list = key_value_list('validate', **validate)
            if not isinstance(validate_list, list):
                return validate_list
            test.setdefault('validate', validate_list)

        extract = test.pop('extract')
        if extract:
            test.setdefault('extract', key_value_list('extract', **extract))

        if 'request' in test.keys():
            request_data = test.get('request').pop('request_data')
            data_type = test.get('request').pop('type')
            if request_data and data_type:
                if data_type == 'json':
                    test.get('request').setdefault(data_type, request_data)
                else:
                    data_dict = key_value_dict('data', **request_data)
                    if not isinstance(data_dict, dict):
                        return data_dict
                    test.get('request').setdefault(data_type, data_dict)

            headers = test.get('request').pop('headers')
            if headers:
                test.get('request').setdefault('headers', key_value_dict('headers', **headers))

        variables = test.pop('variables')
        if variables:
            variables_list = key_value_list('variables', **variables)
            if not isinstance(variables_list, list):
                return variables_list
            test.setdefault('variables', variables_list)

        hooks = test.pop('hooks')
        if hooks:
            setup_hooks_list = key_value_list('setup_hooks', **hooks)
            if not isinstance(setup_hooks_list, list):
                return setup_hooks_list
            test.setdefault('setup_hooks', setup_hooks_list)

            teardown_hooks_list = key_value_list('teardown_hooks', **hooks)
            if not isinstance(teardown_hooks_list, list):
                return teardown_hooks_list
            test.setdefault('teardown_hooks', teardown_hooks_list)

        kwargs.setdefault('test', test)
        return add_case_data(type, **kwargs)


def add_case_data(type, **kwargs):
    """
    用例信息落地
    :param type: boolean: true: 添加新用例， false: 更新用例
    :param kwargs: dict
    :return: ok or tips
    """
    case_info = kwargs.get('test').get('case_info')
    case_opt = TestCaseInfo.objects
    name = kwargs.get('test').get('name')
    module = case_info.get('module')
    project = case_info.get('project')
    belong_module = ModuleInfo.objects.get_module_name(module, type=False)

    config = case_info.get('config', '')
    if config != '':
        case_info.get('include')[0] = eval(config)
    try:
        if type:

            if case_opt.get_case_by_name(name,module,project).count() < 1:
                case_opt.insert_case(belong_module, **kwargs)
                logger.info('{name}用例添加成功: {kwargs}'.format(name=name, kwargs=kwargs))
            else:
                return '用例或配置已存在，请重新编辑'
        else:
            index = case_info.get('test_index')
            if name != case_opt.get_case_by_id(index, type=False) \
                    and case_opt.get_case_by_name(name,module,project).count() > 0:
                return '用例或配置已在该模块中存在，请重新命名'
            case_opt.update_case(belong_module, **kwargs)
            logger.info('{name}用例更新成功: {kwargs}'.format(name=name, kwargs=kwargs))

    except DataError:
        logger.error('用例信息：{kwargs}过长！！'.format(kwargs=kwargs))
        return '字段长度超长，请重新编辑'
    return 'ok'


def copy_test_data(id, name):
    """
    复制用例信息，默认插入到当前项目、莫夸
    :param id: str or int: 复制源
    :param name: str：新用例名称
    :return: ok or tips
    """
    try:
        test = TestCaseInfo.objects.get(id=id)
        belong_module = test.belong_module
    except ObjectDoesNotExist:
        return '复制异常，请重试'
    if TestCaseInfo.objects.filter(name=name, belong_module=belong_module).count() > 0:
        return '用例/配置名称重复了哦'
    test.id = None
    test.name = name
    request = eval(test.request)
    if 'test' in request.keys():
        request.get('test')['name'] = name
    else:
        request.get('config')['name'] = name
    test.request = request
    test.save()
    logging.info('{name}用例/配置添加成功'.format(name=name))
    return 'ok'



def test_create_add(request):
  
    try:
        test = TestCaseInfo.objects.get(id=id)
        belong_module = test.belong_module
    except ObjectDoesNotExist:
        return '复制异常，请重试'
    if TestCaseInfo.objects.filter(name=name, belong_module=belong_module).count() > 0:
        return '用例/配置名称重复了哦'
    test.id = None
    test.name = name
    request = eval(test.request)
    if 'test' in request.keys():
        request.get('test')['name'] = name
    else:
        request.get('config')['name'] = name
    test.request = request
    test.save()
    logging.info('{name}用例/配置添加成功'.format(name=name))
    return 'ok'



