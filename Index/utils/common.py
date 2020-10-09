from Index.models import ModuleInfo, TestCaseInfo, TestSuite, TestReports
from django.core.exceptions import ObjectDoesNotExist
import datetime
from Common.util import *
from django.db.models import Sum
from Index.Pmysql import Pmysql
logger = logging.getLogger('Index')

def get_total_values(userid=None):
    total = {
        'pass': [],
        'fail': [],
        'percent': []
    }
    today = datetime.date.today()
    for i in range(-11, 1):
        begin = today + datetime.timedelta(days=i)
        end = begin + datetime.timedelta(days=1)

    
        total_run = TestReports.objects.filter(create_time__range=(begin, end)).filter(userid=userid).aggregate(testRun=Sum('testsRun'))['testRun']
        total_success = TestReports.objects.filter(create_time__range=(begin, end)).filter(userid=userid).aggregate(success=Sum('successes'))['success']
        if not total_run:
            total_run = 0
        if not total_success:
            total_success = 0

        total_percent = round(total_success / total_run * 100, 2) if total_run != 0 else 0.00
        total['pass'].append(total_success)
        total['fail'].append(total_run - total_success)
        total['percent'].append(total_percent)

    return total


def set_filter_session(request):
    """
    update session
    :param request:
    :return:
    """
    if 'user' in request.POST.keys():
        request.session['user'] = request.POST.get('user')
    if 'name' in request.POST.keys():
        request.session['name'] = request.POST.get('name')
    if 'project' in request.POST.keys():
        request.session['project'] = request.POST.get('project')
    if 'module' in request.POST.keys():
        try:
            request.session['module'] = ModuleInfo.objects.get(id=request.POST.get('module')).module_name
        except Exception:
            request.session['module'] = request.POST.get('module')
    if 'report_name' in request.POST.keys():
        request.session['report_name'] = request.POST.get('report_name')

    if 'import_type' in request.POST.keys():
        if request.POST.get('import_type') != '':
            request.session['import_type'] = int(request.POST.get('import_type'))
        else:
            request.session['import_type'] = request.POST.get('import_type')

    filter_query = {
        'user': request.session['user'],
        'name': request.session['name'],
        'belong_project': request.session['project'],
        'belong_module': request.session['module'],
        'report_name': request.session['report_name'],
        'import_type': request.session['import_type']
    }

    return filter_query


def update_include(include):
    for i in range(0, len(include)):
        if isinstance(include[i], dict):
            id = include[i]['config'][0]
            source_name = include[i]['config'][1]
            try:
                name = TestCaseInfo.objects.get(id=id).name
            except ObjectDoesNotExist:
                name = source_name+'_已删除!'
                logger.warning('依赖的 {name} 用例/配置已经被删除啦！！'.format(name=source_name))

            include[i] = {
                'config': [id, name]
            }
        else:
            id = include[i][0]
            source_name = include[i][1]
            try:
                name = TestCaseInfo.objects.get(id=id).name
            except ObjectDoesNotExist:
                name = source_name + ' 已删除'
                logger.warning('依赖的 {name} 用例/配置已经被删除啦！！'.format(name=source_name))

            include[i] = [id, name]

    return include

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


def load_cases(type=1, **kwargs):
    """
    加载指定项目模块下的用例
    :param kwargs: dict: 项目与模块信息
    :return: str: 用例信息
    """
    belong_project = kwargs.get('name').get('project')
    module = kwargs.get('name').get('module')
    if module == '请选择':
        return ''
    case_info = TestCaseInfo.objects.filter(belong_project=belong_project, belong_module=module, type=type). \
        values_list('id', 'name').order_by('-create_time')
    case_info = list(case_info)
    string = ''
    for value in case_info:
        string = string + str(value[0]) + '^=' + value[1] + 'replaceFlag'
    return string[:len(string) - 11]


def load_testsuites(**kwargs):
    """
    加载对应项目的模块信息，用户前端ajax请求返回
    :param kwargs:  dict：项目相关信息
    :return: str: module_info
    """
    belong_project = kwargs.get('name').get('project')
    module_info = TestSuite.objects.filter(belong_project__project_name=belong_project) \
        .values_list('id', 'suite_name').order_by('-create_time')
    module_info = list(module_info)
    string = ''
    for value in module_info:
        string = string + str(value[0]) + '^=' + value[1] + 'replaceFlag'
    return string[:len(string) - 11]




