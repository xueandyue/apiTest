from Login.views import login_check
from django.shortcuts import render, HttpResponse
from Common.util import init_filter_session
from Index.utils.common import get_total_values
from Index.Module.project import list_project, project_add, project_info
from Index.Module.module import list_module, module_add
from Index.Module.case import case_add, case_list, case_edit, load_case_file
from Index.Module.config import config_add, list_config, config_edit
from Index.Module.suite import suite_add, suite_edit, list_suite
from Index.Module.env import set_env, list_env
from Index.Module.debugtalk import debug_talk, list_debugtalk,list_env_file,file_env
from Index.Module.upload import file_upload
from Index.Module.ci import run_case, run_batch_case, periodic_task, task_add, task_edit,email_task,email_task_add,email_task_edit
from Index.Module.report import list_report, report_view, report_download
from Index.Module.api import get_apilist
from Index.models import ProjectInfo, ModuleInfo, TestCaseInfo, TestSuite
import requests
from Index.Pmysql import Pmysql
from Index.utils.operations import add_config_data, add_case_data
from Index.Module.case import case_info_logic
from Index.Pmysql import Pmysql
from django.http import StreamingHttpResponse
from django.http import HttpResponse

# from Common.config import *
# from django.conf import settings


@login_check
def index(request):
    init_filter_session(request)
    """
    首页
    """
    # 获取userid
    username=request.session["now_account"]
    sql = 'SELECT id from userinfo where  username= %s'
    params = [username]
    helper = Pmysql()
    data = helper.fetchone(sql,params)
    helper.close()
    userid=data['id']
    # 获取userid结束
    project_length = ProjectInfo.objects.filter(userid=userid).count()
    print(project_length)
    print(type(project_length))
    if(project_length>0):
        #根据userid查belong_project_id
        sql = 'SELECT id from ProjectInfo where userid= %s'
        params = [userid]
        helper = Pmysql()
        data = helper.fetchall(sql,params)
        helper.close()
        project_id_list=[]


        for i in data:
            project_id_list.append(str(i['id']))
        project_id_list=','.join(project_id_list) 

        module_length = ModuleInfo.objects.extra(where=["belong_project_id in ("+project_id_list+")"]).count()
        suite_length = TestSuite.objects.extra(where=["belong_project_id in ("+project_id_list+")"]).count()

        #根据userid查project_name
        sql = 'SELECT project_name FROM userinfo,ProjectInfo WHERE ProjectInfo.userid=userinfo.id and userinfo.id= %s'
        params = [userid]
        helper = Pmysql()
        data = helper.fetchall(sql,params)
        helper.close()
        project_name_list=[]
        if(data is not None):
            for i in data:
                temp="'"+i['project_name']+"'"
                project_name_list.append(temp)
            project_name_list=','.join(project_name_list)
            test_length=TestCaseInfo.objects.filter(type__exact=1).extra(where=["belong_project in ("+project_name_list+")"]).count()



        else:
            test_length =0
    else:
        module_length = 0
        test_length =0
        suite_length = 0

    total = get_total_values(userid=userid)
    dataInfo = {
        'project_length': project_length,
        'module_length': module_length,
        'test_length': test_length,
        'suite_length': suite_length,
        'account': request.session["now_account"],
        'total': total
    }

    return render(request, 'Index/index.html', dataInfo)


@login_check
def project_list(request, id):
    return list_project(request, id)


@login_check
def add_project(request):
    return project_add(request)


@login_check
def get_project_info(request):
    return project_info(request)


@login_check
def module_list(request, id):
    return list_module(request, id)


@login_check
def add_module(request):
    return module_add(request)


@login_check
def add_case(request):
    return case_add(request)


@login_check
def test_list(request,id):
    return case_list(request, id)


@login_check
def edit_case(request, id=None):
    return case_edit(request, id)


@login_check
def add_config(request):
    return config_add(request)


@login_check
def config_list(request, id):
    return list_config(request, id)


@login_check
def edit_config(request, id=None):
    return config_edit(request, id)


@login_check
def suite_list(request, id):
    return list_suite(request, id)


@login_check
def add_suite(request):
    return suite_add(request)


@login_check
def edit_suite(request, id=None):
    return suite_edit(request, id)


@login_check
def env_set(request):
    return set_env(request)


@login_check
def env_list(request, id):
    return list_env(request, id)


@login_check
def debugtalk(request, id=None):
    return debug_talk(request,id)


@login_check
def debugtalk_list(request, id):
    return list_debugtalk(request, id)

@login_check
def env_file(request, id=None):
    return file_env(request,id)


@login_check
def env_file_list(request, id):
    return list_env_file(request, id)


@login_check
def upload_file(request):
    return file_upload(request)


@login_check
def run_test(request):
    return run_case(request)


@login_check
def run_batch_test(request):
    return run_batch_case(request)


@login_check
def periodictask(request, id):
    return periodic_task(request, id)


@login_check
def add_task(request):
    return task_add(request)


@login_check
def edit_task(request, id=None):
    return task_edit(request, id)


@login_check
def email_add_task(request):
    return email_task_add(request)


@login_check
def email_edit_task(request, id=None):
    return email_task_edit(request, id)


@login_check
def email_task_list(request, id):
    return email_task(request, id)


@login_check
def report_list(request, id):
    return list_report(request, id)


@login_check
def view_report(request, id):
    return report_view(request, id)


@login_check
def download_report(request, id):
    return report_download(request, id)


def api(request):
    data={}
    return render(request, 'Index/api.html', data)


def api_file(request):
    import json
    filename = request.FILES.get('file_id')
    filename = request.FILES.get('input_apifile')
    project=request.POST.get("project")
    data={}
    data["code"]="200"
    return HttpResponse(json.dumps(data),content_type="application/json")


@login_check
def getapilist(request):
    return get_apilist(request)


@login_check
def type_upload_file(request):
    return load_case_file(request)







@login_check
def export_testcase(request):
    import os
    from io import StringIO
    import xlsxwriter
    import json
    from decimal import Decimal


    exist_file = os.path.exists("./static/export/接口测试用例.xlsx")
    if exist_file:
        os.remove("./static/export/接口测试用例.xlsx")
    excel = xlsxwriter.Workbook('./static/export/接口测试用例.xlsx')


    sheet = excel.add_worksheet(u"接口测试用例执行统计")

    centerstyle = excel.add_format({
    'border': 1, # 边框
    'align': 'center', # 水平居中
    'valign': 'vcenter', # 垂直居中
    'font': u'宋体', # 字体
    'text_wrap':1
    })

    style_head=excel.add_format({
    'border': 1, # 边框
    'align': 'center', # 水平居中
    'valign': 'vcenter', # 垂直居中
    'font': u'宋体', # 字体
    'text_wrap':1,
    'bold': True, # 加粗（默认False）
    'color': 'blue' #字体颜色
    })
    #改变行高或者列宽  xlwt中是行和列都是从0开始计算的

    sheet.set_column('A:A', 36)
    sheet.set_column("D:D", 32) 
    sheet.set_column("E:E", 32)
    sheet.set_column("F:I", 60)


    sheet.merge_range('E2:I3', u'接口测试用例执行统计', style_head)
    sheet.write(3,4,"用例总数",centerstyle)
    sheet.write(3,5,"成功",centerstyle)
    sheet.write(3,6,"失败",centerstyle)
    sheet.write(3,7,"错误",centerstyle)
    sheet.write(3,8,"跳过",centerstyle)



    # print(request.body)
    receive_data =json.loads(request.body.decode('utf-8'))
    count=receive_data[0]['count']
    success=count['TESTSTEPS']['success']
    fail=count['TESTSTEPS']['fail']
    error=count['TESTSTEPS']['error']
    skip=count['TESTSTEPS']['skip']
    count=int(success)+int(fail)+int(error)+int(skip)


    sheet.write(4,4,count,centerstyle)
    sheet.write(4,5,success,centerstyle)
    sheet.write(4,6,fail,centerstyle)
    sheet.write(4,7,error,centerstyle)
    sheet.write(4,8,skip,centerstyle)


    sheet.merge_range('A7:B8', u'接口最大响应时间统计', style_head)

    sheet.write(8,0,"接口url",centerstyle)
    sheet.write(8,1,"最大响应时间（单位是秒）",centerstyle)

    sheet.merge_range('E7:J8', u'接口用例详情', style_head)


    elapsed_total_seconds=receive_data[0]['count']['elapsed_total_seconds']

    for i in range(len(elapsed_total_seconds)):
        sheet.write(i+9,0,elapsed_total_seconds[i]['elapsed_url'],centerstyle)
        max_response_time=float(elapsed_total_seconds[i]['max_response_time'])
        max_response_time = round(max_response_time,2) 
        sheet.write(i+9,1,max_response_time,centerstyle)


    sheet.write(8,4,"接口url",centerstyle)
    sheet.write(8,5,"用例标题",centerstyle)
    sheet.write(8,6,"请求数据",centerstyle)
    sheet.write(8,7,"响应内容",centerstyle)
    sheet.write(8,8,"结果期望",centerstyle)
    sheet.write(8,9,"结果",centerstyle)


    for i in range(len(receive_data)):
        if(i!=0):
            test=receive_data[i]['test']
            sheet.write(i+9,4,test['url'],centerstyle)
            sheet.write(i+9,5,test['name'],centerstyle)
            sheet.write(i+9,6,json.dumps(test['request']),centerstyle)
            sheet.write(i+9,7,json.dumps(test['response']),centerstyle)
            sheet.write(i+9,8,json.dumps(test['validators']),centerstyle)
            sheet.write(i+9,9,test['status'],centerstyle)

    
    excel.close()
    data={}
    data["code"]="200"
    return HttpResponse(json.dumps(data),content_type="application/json")
  

@login_check
def createtest(request,id):


    helper = Pmysql()
    # 连接
    # helper.connect()
    # sql
    sql = 'select * from ModuleInfo where id = %s'
    # params
    params = [id]
    # 执行
    data = helper.fetchone(sql, params)
    helper.close()
    module_name=data['module_name']
    module_id=data['id']
    belong_project_id=data['belong_project_id']

    IsCreatetest=data['IsCreatetest']

    if(IsCreatetest!='1'):
        return index(request)

    sql = 'select project_name from ProjectInfo where id = %s'
    
    params = [belong_project_id]
    helper = Pmysql()
    data = helper.fetchone(sql,params)
    helper.close()


    project_name=data['project_name']


    account = request.session["now_account"]


    # module_name=ModuleInfo.objects.filter(id=id)


    # 判断是否已经批量生成过用例


    # 获取项目等信息

    renderdata={}
    renderdata['module_name']=module_name
    renderdata['project_name']=project_name
    renderdata['account']=account

    renderdata['module_id']=module_id

    

 
    return render(request, 'Index/createtest.html', renderdata)

@login_check
def createtest_ajax(request):
    import json
    tempjson=json.loads(request.body.decode('utf-8'))
    project=tempjson['test']['name']['project']
    module=tempjson['test']['name']['module']
    author=tempjson['test']['name']['author']
    config=tempjson['test']['name']['config']
    import_type=tempjson['test']['name']['import_type']
    # 判断是否已经生成过用例
    helper = Pmysql()
    # 连接
    # sql
    sql = 'select * from ModuleInfo where id = %s'
    # params
    params = [module]
    # 执行
    data = helper.fetchone(sql, params)
    helper.close()
    IsCreatetest=data['IsCreatetest']
    if(IsCreatetest!='1'):
        data={}
        data["code"]="201"
        data['error']='该项目不能重复批量生成用例'
        return HttpResponse(json.dumps(data),content_type="application/json")
        return index(request)

    tempjson['test']['name']='test001'
    url="http://localhost:8888/test/Createtestcase"
    
    tempjson['test']['name']='test001'


    tempjson['test']['request']['json']=tempjson['test']['request']['request_data']
    tempjson['test']['request'].pop('request_data')

    ## headers中添加上content-type这个参数，指定为json格式
    headers = {'Content-Type': 'application/json'}

    ## post的时候，将data字典形式的参数用json包转换成json格式。
    response = requests.post(url=url, headers=headers, data=json.dumps(tempjson))

    # print(response.content)

    content=json.loads(response.content.decode('utf-8'))
    # if isinstance (content,list):
    #     pass
    # else:
    #     pass
    #     # import_type='3'
    #     # typecontent=content
    #     # typecontent_dict={}
    #     # typecontent_dict['test']=typecontent
    #     # content=[]
    #     # content.append(typecontent_dict)
    # print(content)
    for test_case in content:
        casename=test_case['test']['name'].strip()
        test_case['test']['name']={}
        test_case['test']['name']['project']=project
        test_case['test']['name']['module']=module
        test_case['test']['name']['author']=author
        test_case['test']['name']['config']=config
        test_case['test']['name']['import_type']=import_type
        test_case['test']['name']['case_name']=casename
        test_case['test']['name']['include']=[]
        test_case['test']['request']['request_data']=test_case['test']['request']['json']
        test_case['test']['request'].pop('json')

        # test_case
        msg = case_info_logic(**test_case)
        

            


    helper = Pmysql()
    # 连接
    # sql
    sql = 'update  ModuleInfo set  IsCreatetest="0" where id = %s'
    # params
    params = [module]
    # 执行
    data = helper.update(sql,params)
    helper.close()
    
    data={}
    data["code"]="200"
    return HttpResponse(json.dumps(data),content_type="application/json")


    









