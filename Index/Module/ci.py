import json, os, shutil
from django.shortcuts import render
from django.http import HttpResponse
from Index.page import get_pager_info
from Index.models import EnvInfo, ProjectInfo
from Common.util import get_ajax_msg
from Index.utils.common import set_filter_session, load_modules, load_testsuites
from djcelery.models import PeriodicTask
from djcelery import models as celery_models
from Index.utils.task_opt import create_task, update_task
from Index.utils.runner import generate_file_by_type, generate_file_by_batch
from Index.tasks import main_hrun, run
from Common.util import get_time_stamp
from builtins import type
from Index.Pmysql import Pmysql


def email_task(request, id):
    """
    定时任务列表
    :param request:
    :param id: str or int：当前页
    :return:
    """

    account = request.session["now_account"]
    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        mode = kwargs.pop('mode')
        id = kwargs.pop('id')
        msg = delete_task(id) if mode == 'del' else change_task_status(id, mode)
        return HttpResponse(get_ajax_msg(msg, 'ok'))
    else:
        filter_query = set_filter_session(request)
        task_list = get_pager_info(
            PeriodicTask, filter_query, '/Index/periodictask/', id)
        dataInfo = {
            'account': account,
            'task': task_list[1],
            'page_list': task_list[0],
            'info': filter_query
        }
    return render(request, 'Index/email_task_list.html', dataInfo)


def email_task_add(request):
    """
    添加任务
    :param request:
    :return:
    """

    account = request.session["now_account"]
    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        kwargs['username']=account
        msg = task_logic(**kwargs)
        return HttpResponse(get_ajax_msg(msg, '/Index/email_task/1/'))
    elif request.method == 'GET':
        info = {
            'account': account,
            'env': EnvInfo.objects.all().order_by('-create_time'),
            'project': ProjectInfo.objects.all().order_by('-create_time')
        }
        return render(request, 'Index/email_add_task.html', info)


def email_task_edit(request, task_id=None):
    account = request.session["now_account"]
    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        kwargs['username']=account
        msg = task_logic(**kwargs)
        return HttpResponse(get_ajax_msg(msg, '/Index/email_task/1/'))
    if request.method == 'GET':
        if not task_id:
            return HttpResponse("任务ID为空")
        obj = PeriodicTask.objects.filter(id=task_id)
        if obj.count() < 1:
            return HttpResponse("该任务不存在")
        name = obj[0].name
        task_info = eval(obj[0].kwargs)
        crontab_time = obj[0].description
        data = {
            "id": task_id,
            "name": name,
            "task_info": task_info,
            "crontab_time": crontab_time,
            'env': EnvInfo.objects.all().order_by('-create_time'),
            'project': ProjectInfo.objects.all().order_by('-create_time')
        }
        return render(request, 'Index/email_edit_task.html', data)



def delete_task(name):
    '''
    根据任务名称删除任务
    :param name: task name
    :return: ok or error
    '''
    try:
        task = celery_models.PeriodicTask.objects.get(name=name)
        task.enabled = False  # 设置关闭
        task.delete()
        return 'ok'
    except celery_models.PeriodicTask.DoesNotExist:
        return 'error'




def periodic_task(request, id):
    """
    定时任务列表
    :param request:
    :param id: str or int：当前页
    :return:
    """

    account = request.session["now_account"]
    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        mode = kwargs.pop('mode')
        id = kwargs.pop('id')
        msg = delete_task(id) if mode == 'del' else change_task_status(id, mode)
        return HttpResponse(get_ajax_msg(msg, 'ok'))
    else:
        filter_query = set_filter_session(request)
        task_list = get_pager_info(
            PeriodicTask, filter_query, '/Index/periodictask/', id)
        dataInfo = {
            'account': account,
            'task': task_list[1],
            'page_list': task_list[0],
            'info': filter_query
        }
    return render(request, 'Index/periodictask_list.html', dataInfo)


def task_add(request):
    """
    添加任务
    :param request:
    :return:
    """

    account = request.session["now_account"]
    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        kwargs['username']=account
        msg = task_logic(**kwargs)
        return HttpResponse(get_ajax_msg(msg, '/Index/periodictask/1/'))
    elif request.method == 'GET':
        info = {
            'account': account,
            'env': EnvInfo.objects.all().order_by('-create_time'),
            'project': ProjectInfo.objects.all().order_by('-create_time')
        }
        return render(request, 'Index/add_task.html', info)


def task_edit(request, task_id=None):
    account = request.session["now_account"]
    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        kwargs['username']=account
        msg = task_logic(**kwargs)
        return HttpResponse(get_ajax_msg(msg, '/Index/periodictask/1/'))
    if request.method == 'GET':
        if not task_id:
            return HttpResponse("任务ID为空")
        obj = PeriodicTask.objects.filter(id=task_id)
        if obj.count() < 1:
            return HttpResponse("该任务不存在")
        name = obj[0].name
        task_info = eval(obj[0].kwargs)
        crontab_time = obj[0].description
        data = {
            "id": task_id,
            "name": name,
            "task_info": task_info,
            "crontab_time": crontab_time,
            'env': EnvInfo.objects.all().order_by('-create_time'),
            'project': ProjectInfo.objects.all().order_by('-create_time')
        }
        return render(request, 'Index/edit_task.html', data)



def task_logic(**kwargs):
    """
    定时任务逻辑处理
    :param kwargs: dict: 定时任务数据
    :return:
    """
    if 'task' in kwargs.keys():
        if kwargs.get('task').get('type') == 'module':
            return load_modules(**kwargs.pop('task'))
        else:
            return load_testsuites(**kwargs.pop('task'))
    if kwargs.get('name') is '':
        return '任务名称不可为空'
    elif kwargs.get('project') is '':
        return '请选择一个项目'
    elif kwargs.get('crontab_time') is '':
        return '定时配置不可为空'
    # elif not kwargs.get('module'):
    #     kwargs.pop('module')

    try:
        crontab_time = kwargs.pop('crontab_time').strip().split(' ')
        if(len(crontab_time)>5):
            return '定时配置参数格式不正确'
        crontab = {
            'day_of_week': crontab_time[-1],
            'month_of_year': crontab_time[3],  # 月份
            'day_of_month': crontab_time[2],  # 日期
            'hour': crontab_time[1],  # 小时
            'minute': crontab_time[0],  # 分钟
        }
    except Exception:
        return '定时配置参数格式不正确'
    desc = " ".join(str(i) for i in crontab_time)
    name = kwargs.get('name')
    mode = kwargs.pop('mode')
    # project = kwargs.pop('project')
    print("mode："+mode)
    if mode == 'update':
        task_id = kwargs.pop('periodictask_id')
        return update_task(task_id, name, kwargs, crontab, desc)
    # else:
    #     if PeriodicTask.objects.filter(name__exact=name).count() > 0:
    #         return '任务名称重复，请重新命名'
    # mode = kwargs.pop('mode')

    # if 'module' in kwargs.keys():
    #     kwargs.pop('project')
    #
    #     if mode == '1':
    #         return create_task(name, 'Index.tasks.module_hrun', kwargs, crontab, desc)
    #     else:
    #         kwargs['suite'] = kwargs.pop('module')
    #         return create_task(name, 'Index.tasks.suite_hrun', kwargs, crontab, desc)
    # else:
    #     return create_task(name, 'Index.tasks.project_hrun', kwargs, crontab, desc)


    print("name:   "+name)
    if(name=='send_email_task'):
        return create_task(name, 'Index.tasks.send_email_task', kwargs, crontab, desc)
    else:
        return create_task(name, 'Index.tasks.suite_hrun', kwargs, crontab, desc)





    

def change_task_status(name, mode):
    '''
    任务状态切换：open or close
    :param name: 任务名称
    :param mode: 模式
    :return: ok or error
    '''
    try:
        task = celery_models.PeriodicTask.objects.get(name=name)
        task.enabled = mode
        task.save()
        return 'ok'
    except celery_models.PeriodicTask.DoesNotExist:
        return 'error'


def run_case(request):
    """
    运行用例
    :param request:
    :return:
    """
    testcase_dir_path = os.path.join(os.getcwd(), "suite")
    testcase_dir_path = os.path.join(testcase_dir_path, get_time_stamp())

    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        id = kwargs.pop('id')
        base_url = kwargs.pop('env_name')
        type = kwargs.pop('type')
        project = kwargs.pop('project')
        if type == 'suite':
            ids = id
        else:
            ids = id.split(',')
        generate_file_by_type(ids, project, base_url,  testcase_dir_path, type)
        report_name = kwargs.get('report_name', None)
        main_hrun.delay(testcase_dir_path, report_name)
        return HttpResponse('用例执行中，请稍后查看报告即可,默认时间戳命名报告')
    else:
        id = request.POST.get('id')
        base_url = request.POST.get('env_name')
        type = request.POST.get('type', 'test')
        project = request.POST.get('project')
        if type == 'suite':
            ids = id
        else:
            ids = id.split(',')
        generate_file_by_type(ids, project, base_url, testcase_dir_path, type)
        runner = run(testcase_dir_path)
        # print(json.dumps(runner._summary))
        return render(request, 'Index/report_template_for_single.html', runner._summary)


def run_batch_case(request):
    """
    批量运行用例
    :param request:
    :return:
    """
    testcase_dir_path = os.path.join(os.getcwd(), "suite")
    testcase_dir_path = os.path.join(testcase_dir_path, get_time_stamp())

    from django.core.cache import cache
    cache.set('username', request.session['now_account'], 300)
    username=cache.get('username')
    if request.is_ajax():
        kwargs = json.loads(request.body.decode('utf-8'))
        test_list = kwargs.pop('id')
        base_url = kwargs.pop('env_name')
        type = kwargs.pop('type')
        project = kwargs.pop('project')
        report_name = kwargs.get('report_name', None)
        generate_file_by_batch(test_list, project, base_url, testcase_dir_path, type)
        main_hrun.delay(testcase_dir_path, report_name,username=username)
        return HttpResponse('用例执行中，请稍后查看报告即可,默认时间戳命名报告')
    else:
        type = request.POST.get('type', None)
        base_url = request.POST.get('env_name')
        project = request.POST.get('project')
        test_list = request.body.decode('utf-8').split('&')
        if type:
            generate_file_by_batch(test_list, project, base_url, testcase_dir_path, type=type, mode=True)
        else:
            generate_file_by_batch(test_list, project, base_url, testcase_dir_path)
        runner = run(testcase_dir_path)
        return render(request, 'Index/report_template_for_single.html', runner._summary)