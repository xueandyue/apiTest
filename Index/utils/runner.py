# encoding:utf-8
import os, shutil
from django.core.exceptions import ObjectDoesNotExist
from Index.models import TestCaseInfo, ModuleInfo, ProjectInfo, DebugTalk, TestSuite,ENV
from Index.utils.testcase import dump_python_file, dump_yaml_file
from Common.util import get_time_stamp
from Common.config import TEST_CASE_TYPE, CONFIG_TYPE


# def generate_file_by_single(index, base_url, path):
#     """
#     加载单个case用例信息
#     :param index: int or str：用例索引
#     :param base_url: str：环境地址
#     :return: dict
#     """
#     config = {
#         'config': {
#             'name': '',
#             'base_url': base_url
#         }
#     }
#     testcase_list = []
#
#     testcase_list.append(config)
#
#     try:
#         obj = TestCaseInfo.objects.get(id=index)
#     except ObjectDoesNotExist:
#         return testcase_list
#
#     include = eval(obj.include)
#     request = eval(obj.request)
#     name = obj.name
#     project = obj.belong_project
#     module = obj.belong_module.module_name
#
#     config['config']['name'] = name
#     testcase_dir_path = path
#     generate_debugtalk_file(testcase_dir_path, project)
#     testcase_dir_path = os.path.join(testcase_dir_path, 'testcases')
#     if not os.path.exists(testcase_dir_path):
#         os.makedirs(testcase_dir_path)
#
#     for test_info in include:
#         try:
#             if isinstance(test_info, dict):
#                 config_id = test_info.pop('config')[0]
#                 config_request = eval(TestCaseInfo.objects.get(id=config_id).request)
#                 config_request.get('config').setdefault('base_url', base_url)
#                 config_request['config']['name'] = name
#                 testcase_list[0] = config_request
#             else:
#                 id = test_info[0]
#                 pre_request = eval(TestCaseInfo.objects.get(id=id).request)
#                 # 处理测试用例是api请求形式的
#                 if "api" in pre_request:
#                     pre_request = generate_api_file(pre_request, path)
#                 testcase_list.append(pre_request)
#
#         except ObjectDoesNotExist:
#             return testcase_list
#
#     if "request" in request['test'] and request['test']['request']['url'] != '':
#         testcase_list.append(request)
#     elif "api" in request['test'] and request['test']['api'] != '':
#         data = generate_api_file(request['test'], path)
#         request['test'] = data
#         testcase_list.append(request)
#
#     dump_yaml_file(os.path.join(testcase_dir_path, name + '.yml'), testcase_list)

def generate_case(case_id_list, project, base_url, path):
    generate_debugtalk_file(path, project)
    generate_env_file(path,project)
    generate_case_file(case_id_list, base_url, path)


def generate_case_file(case_id_list, base_url, path):
    case_data_list = []
    config = {
        'config': {
            'name': "test",
            'base_url': base_url
        }
    }
    case_data_list.append(config)
    for case_index in case_id_list:
        case_data = get_case_data(case_index)
        if not case_data:
            continue
        if "config" in case_data.keys():
            case_data.get('config').setdefault('base_url', base_url)
            case_data_list[0] = case_data
            continue
        elif 'test' in case_data.keys():
            if "api" in case_data['test'] and case_data['test']['api'] != '':
                data = generate_api_file(case_data['test'], path)
                case_data['test'] = data
            case_data_list.append(case_data)

    case_dir = os.path.join(path, 'testcases')
    if not os.path.exists(case_dir):
        os.makedirs(case_dir)
    case_file_path = os.path.join(case_dir, get_time_stamp() + '.yml')
    dump_yaml_file(case_file_path, case_data_list)


def get_case_data(index):
    try:
        obj = TestCaseInfo.objects.get(id=index)
    except ObjectDoesNotExist:
        return
    request = eval(obj.request)
    return request


def generate_debugtalk_file(path, project):
    if not os.path.exists(path):
        os.makedirs(path)
    try:
        debugtalk = DebugTalk.objects.get(belong_project__project_name=project).debugtalk
    except ObjectDoesNotExist:
        debugtalk = ''
    dump_python_file(os.path.join(path, 'debugtalk.py'), debugtalk)

def generate_env_file(path, project):
    if not os.path.exists(path):
        os.makedirs(path)
    try:
        env = ENV.objects.get(belong_project__project_name=project).env
    except ObjectDoesNotExist:
        env = ''
    dump_python_file(os.path.join(path, '.env'), env)


def generate_api_file(data, path):
    api_id = data["api"]
    api_request = eval(TestCaseInfo.objects.get(id=api_id).request)
    api_name = TestCaseInfo.objects.get(id=api_id).name
    api_path = os.path.join(path, "api")
    if not os.path.exists(api_path):
        os.makedirs(api_path)
    dump_yaml_file(os.path.join(api_path, api_name + '.yml'), api_request['test'])
    data["api"] = 'api/' + api_name + '.yml'
    return data


def generate_file_by_suite(index, project, base_url, path):
    obj = TestSuite.objects.get(id=index)

    include = eval(obj.include)
    # name = obj.suite_name
    ids = []
    for val in include:
        ids.append(val[0])
    generate_case(ids, project, base_url, path)

    # for val in include:
    #     generate_case(val[0], base_url, path)


def generate_file_by_batch(test_list, project, base_url, path, type=None, mode=False):
    """
    批量组装用例数据
    :param test_list:
    :param base_url: str: 环境地址
    :param type: str：用例级别
    :param mode: boolean：True 同步 False: 异步
    :return: list
    """

    if mode:
        for index in range(len(test_list) - 3):
            form_test = test_list[index].split('=')
            value = form_test[1]
            if type == 'project':
                generate_file_by_project(value, project, base_url, path)
            elif type == 'module':
                generate_file_by_module(value, project, base_url, path)
            elif type == 'suite':
                generate_file_by_suite(value, project, base_url, path)
            else:
                generate_case([value], project, base_url, path)

    else:
        if type == 'project':
            for value in test_list.values():
                generate_file_by_project(value, project, base_url, path)

        elif type == 'module':
            for value in test_list.values():
                generate_file_by_module(value, project, base_url, path)
        elif type == 'suite':
            for value in test_list.values():
                generate_file_by_suite(value, project, base_url, path)

        else:
            for index in range(len(test_list) - 2):
                form_test = test_list[index].split('=')
                index = form_test[1]
                generate_case([index], project, base_url, path)


def generate_file_by_module(id, base_url, path):
    """
    组装模块用例
    :param id: int or str：模块索引
    :param base_url: str：环境地址
    :return: list
    """
    obj = ModuleInfo.objects.get(id=id)
    test_index_list = TestCaseInfo.objects.filter(belong_module=obj, type=1).values_list('id')
    for index in test_index_list:
        generate_case(index[0], base_url, path)


def generate_file_by_project(id, base_url, path):
    """
    组装项目用例
    :param id: int or str：项目索引
    :param base_url: 环境地址
    :return: list
    """
    obj = ProjectInfo.objects.get(id=id)
    module_index_list = ModuleInfo.objects.filter(belong_project=obj).values_list('id')
    for index in module_index_list:
        module_id = index[0]
        generate_file_by_module(module_id, base_url, path)


def generate_file_by_type(ids, project, base_url, path, type):
    if type == 'project':
        generate_file_by_project(ids, base_url, path)
    elif type == 'module':
        generate_file_by_module(ids, base_url, path)
    elif type == 'suite':
        generate_file_by_suite(ids, project, base_url, path)
    else:
        generate_case(ids, project, base_url,  path)



