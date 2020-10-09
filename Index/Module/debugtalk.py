from django.shortcuts import render
from django.http import HttpResponseRedirect
from Index.page import get_pager_info
from Index.models import DebugTalk,ENV
from Index.Pmysql import Pmysql

def debug_talk(request, id=None):
    if request.method == 'GET':
        debugtalk = DebugTalk.objects.values('id', 'debugtalk').get(id=id)
        return render(request, 'Index/debugtalk.html', debugtalk)
    else:
        id = request.POST.get('id')
        debugtalk = request.POST.get('debugtalk')
        code = debugtalk.replace('new_line', '\r\n')
        obj = DebugTalk.objects.get(id=id)
        obj.debugtalk = code
        obj.save()
        return HttpResponseRedirect('/Index/debugtalk_list/1/')


def list_debugtalk(request, id):
    """
       debugtalk.py列表
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
    debugtalk = get_pager_info(
        DebugTalk, None, '/Index/debugtalk_list/', id,userid=userid)
    
    dataInfo = {
        'account': account,
        'debugtalk': debugtalk[1],
        'page_list': debugtalk[0],
    }
    return render(request, 'Index/debugtalk_list.html', dataInfo)




#env 处理


def file_env(request, id=None):
    if request.method == 'GET':
        debugtalk = ENV.objects.values('id', 'env').get(id=id)
        return render(request, 'Index/env_file.html', debugtalk)
    else:
        id = request.POST.get('id')
        debugtalk = request.POST.get('env')
        
        code=debugtalk
        code = debugtalk.replace('new_line', '\n')
        obj = ENV.objects.get(id=id)
        obj.env = code
        obj.save()
        return HttpResponseRedirect('/Index/env_file_list/1/')



def list_env_file(request, id):
    """
       .env列表
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
    debugtalk = get_pager_info(
        ENV, None, '/Index/env_file_list/', id,userid=userid)
    dataInfo = {
        'account': account,
        'debugtalk': debugtalk[1],
        'page_list': debugtalk[0],
    }
    return render(request, 'Index/env_file_list.html', dataInfo)
