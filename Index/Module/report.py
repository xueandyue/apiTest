from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse
from Index.models import TestReports
from Index.page import get_pager_info
from Index.utils.common import set_filter_session
from Common.util import get_ajax_msg
import json, os, shutil
from Index.utils.operations import del_report_data
from django.utils.safestring import mark_safe
from Index  import separator
from Index.Pmysql import Pmysql


def list_report(request, id):
    """
    报告列表
    :param request:
    :param id: str or int：当前页
    :return:
    """

    if request.is_ajax():
        msg=""
        report_info = json.loads(request.body.decode('utf-8'))
        if report_info.get('mode') == 'del':
            id=report_info['id']
            if isinstance(id,list):
                for i in id:
                    msg=del_report_data(i)
            else :
                msg = del_report_data(report_info.pop('id'))
        return HttpResponse(get_ajax_msg(msg, 'ok'))
    else:
        filter_query = set_filter_session(request)
        # 获取userid
        username=request.session["now_account"]
        sql = 'SELECT id from UserInfo where  username= %s'
        params = [username]
        helper = Pmysql()
        data = helper.fetchone(sql,params)
        helper.close()
        userid=data['id']
        # 获取userid结束
        report_list = get_pager_info(
            TestReports, filter_query, '/Index/report_list/', id,userid=userid)
        dataInfo = {
            'account': request.session["now_account"],
            'report': report_list[1],
            'page_list': report_list[0],
            'info': filter_query
        }
        return render(request, 'Index/report_list.html', dataInfo)


def report_view(request, id):
    """
    查看报告
    :param request:
    :param id: str or int：报告名称索引
    :return:
    """
    reports = TestReports.objects.get(id=id).reports
    return render(request, 'Index/view_report.html', {"reports": mark_safe(reports)})


def report_download(request, id):
    if request.method == 'GET':

        summary = TestReports.objects.get(id=id)
        reports = summary.reports
        start_at = summary.start_at

        if os.path.exists(os.path.join(os.getcwd(), "reports")):
            shutil.rmtree(os.path.join(os.getcwd(), "reports"))
        os.makedirs(os.path.join(os.getcwd(), "reports"))

        report_path = os.path.join(os.getcwd(), "reports{}{}.html".format(separator, start_at.replace(":", "-")))
        with open(report_path, 'w+', encoding='utf-8') as stream:
            stream.write(reports)

        def file_iterator(file_name, chunk_size=512):
            with open(file_name, encoding='utf-8') as f:
                while True:
                    c = f.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break

        response = StreamingHttpResponse(file_iterator(report_path))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(start_at.replace(":", "-") + '.html')
        return response