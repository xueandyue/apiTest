import shutil, os, sys, json, logging, io, yaml
from json import JSONDecodeError
from django.http import JsonResponse
from Index import separator
from Index.utils.operations import add_config_data, add_case_data
from Index.models import TestCaseInfo

logger = logging.getLogger('apiTest')


def file_upload(request):
    account = request.session["now_account"]
    if request.method == 'POST':
        try:
            project_name = request.POST.get('project')
            module_name = request.POST.get('module')
        except KeyError as e:
            return JsonResponse({"status": e})
        if project_name == '请选择' or module_name == '请选择':
            return JsonResponse({"status": '项目或模块不能为空'})

        upload_path = sys.path[0] + separator + 'upload' + separator
        if os.path.exists(upload_path):
            shutil.rmtree(upload_path)

        os.mkdir(upload_path)

        upload_obj = request.FILES.getlist('upload')
        file_list = []
        for i in range(len(upload_obj)):
            temp_path = upload_path + upload_obj[i].name
            file_list.append(temp_path)
            try:
                with open(temp_path, 'wb') as data:
                    for line in upload_obj[i].chunks():
                        data.write(line)
            except IOError as e:
                return JsonResponse({"status": e})
        upload_file_logic(file_list, project_name, module_name, account)

        return JsonResponse({'status': '/Index/test_list/1/'})


def upload_file_logic(files, project, module, account):
    """
    解析yaml或者json用例
    :param files:
    :param project:
    :param module:
    :param account:
    :return:
    """
    import_type='1'
    for file in files:
        file_suffix = os.path.splitext(file)[1].lower()
        if file_suffix == '.json':
            with io.open(file, encoding='utf-8') as data_file:
                try:
                    content = json.load(data_file)
                except JSONDecodeError:
                    err_msg = u"JSONDecodeError: JSON file format error: {}".format(file)
                    logging.error(err_msg)

        elif file_suffix in ['.yaml', '.yml']:
            with io.open(file, 'r', encoding='utf-8') as stream:
                content = yaml.load(stream)
        if isinstance (content,list):
            pass
        else:
            import_type='3'
            typecontent=content
            typecontent_dict={}
            typecontent_dict['test']=typecontent
            content=[]
            content.append(typecontent_dict)
        for test_case in content:
            test_dict = {
                'project': project,
                'module': module,
                'author': account,
                'import_type':import_type,
                'include': []
            }

            
            if 'config' in test_case.keys():
                test_case.get('config')['config_info'] = test_dict
                if 'variables' in test_case['config'].keys():
                    datalist=[]
                    if isinstance (test_case['config']['variables'],list):
                        pass
                    else:
                        for k,v in test_case['config']['variables'].items():
                            tempdict={k:v}
                            datalist.append(tempdict)
                        test_case['config']['variables']=datalist


                a=add_config_data(type=True, **test_case)
                test_case.get('config')['config_info'] = test_dict
            if 'test' in test_case.keys():  # 忽略config

                test_case.get('test')['case_info'] = test_dict

                if 'variables' in test_case['test'].keys():
                    datalist=[]
                    if isinstance (test_case['test']['variables'],list):
                        pass
                    else:
                        for k,v in test_case['test']['variables'].items():
                            tempdict={k:v}
                            datalist.append(tempdict)
                        test_case['test']['variables']=datalist
                
                if "api" in test_case['test'].keys():
                    api = test_case['test']['api']
                    if api == '':
                        msg = "用例[name：%s]引用的API为空：".format(test_case['test']['name'])
                        print(msg)
                        break
                    TestCaseInfo.objects.get_case_name
                    api_objs = TestCaseInfo.objects.get_case_by_name(api,module,project)
                    if api_objs.count() < 1:
                        msg = "用例[name：%s]引用的API不存在：".format(test_case['test']['name'])
                        print(msg)
                        break
                    api_id = api_objs[0].id
                    test_case['test']['api'] = api_id
                if 'validate' in test_case.get('test').keys():  # 适配validate两种格式
                    validate = test_case.get('test').pop('validate')
                    new_validate = []
                    for check in validate:
                        if 'comparator' not in check.keys():
                            for key, value in check.items():
                                tmp_check = {"check": value[0], "comparator": key, "expect": value[1]}
                                new_validate.append(tmp_check)
                        else:
                            new_validate.append(check)
                    test_case.get('test')['validate'] = new_validate
                add_case_data(type=True, **test_case)