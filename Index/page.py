from Common.util import customer_pager
from Common.config import ALL_CASE_TYPE, CONFIG_TYPE, TEST_CASE_TYPE, API_TYPE
from Index.models import TestCaseInfo, ModuleInfo, TestSuite
from django.db.models import Q
from Index.Pmysql import Pmysql

class PageInfo(object):
    """
    分页类
    """

    def __init__(self, current, total_item, per_items=5):
        self.__current = current
        self.__per_items = per_items
        self.__total_item = total_item

    @property
    def start(self):
        return (self.__current - 1) * self.__per_items

    @property
    def end(self):
        return self.__current * self.__per_items

    @property
    def total_page(self):
        result = divmod(self.__total_item, self.__per_items)
        if result[1] == 0:
            return result[0]
        else:
            return result[0] + 1


def get_pager_info(Model, filter_query, url, id, per_items=18,userid=0):
    """
    筛选列表信息
    :param Model: Models实体类
    :param filter_query: dict: 筛选条件
    :param url:
    :param id:
    :param per_items: int: m默认展示12行
    :return:
    """
    id = int(id)
    if filter_query:
        belong_project = filter_query.get('belong_project')
        belong_module = filter_query.get('belong_module')
        name = filter_query.get('name')
        user = filter_query.get('user')
        import_type = filter_query.get('import_type')
    
    obj = Model.objects

 
    



    if url == '/Index/project_list/':
        obj = obj.filter(project_name__contains=belong_project).filter(userid=userid) if belong_project != 'All' \
            else obj.filter(responsible_name__contains=user).filter(userid=userid)
    elif url == '/Index/test_list/':
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
   
            name=str(name)
            if ((belong_project != 'All') and (belong_module != '请选择')):
            
                sql = "SELECT id FROM ModuleInfo WHERE module_name=%s"
                params = [belong_module]
                helper = Pmysql()
                data = helper.fetchone(sql,params)
                helper.close()
                if(data is not None):
                    case_belong_module_id=data['id']
                    

                    if(import_type==0 or import_type=='' ):
                        obj=obj.filter(belong_project=belong_project,belong_module_id=case_belong_module_id).filter(name__contains=name).filter(author__contains=user).extra(where=["belong_project in ("+project_name_list+")"]).order_by('-update_time')
                    else:
                        obj=obj.filter(belong_project=belong_project,belong_module_id=case_belong_module_id,type=import_type).filter(name__contains=name).filter(author__contains=user).extra(where=["belong_project in ("+project_name_list+")"]).order_by('-update_time')
                else:
                    obj=obj.filter(id='-999')

            if ((belong_project == 'All') and (belong_module == '请选择')):
                if(import_type==0 or import_type=='' ):
                    obj=obj.filter(name__contains=name).filter(author__contains=user).extra(where=["belong_project in ("+project_name_list+")"]).order_by('-update_time')

                else:
                    
                    obj=obj.filter(type=import_type).filter(name__contains=name).filter(author__contains=user).extra(where=["belong_project in ("+project_name_list+")"]).order_by('-update_time')

            if ((belong_project != 'All') and (belong_module == '请选择')):
                if(import_type==0 or import_type=='' ):
                    obj=obj.filter(belong_project=belong_project).filter(name__contains=name).filter(author__contains=user).extra(where=["belong_project in ("+project_name_list+")"]).order_by('-update_time')
                else:
                    obj=obj.filter(type=import_type,belong_project=belong_project).filter(name__contains=name).filter(author__contains=user).extra(where=["belong_project in ("+project_name_list+")"]).order_by('-update_time')
        else:
            obj=obj.filter(id='-999')
        obj=obj.extra(where=["type != 2"])
    elif url == '/Index/config_list/':
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
    
            name=str(name)
            import_type='2'
            
            if ((belong_project != 'All') and (belong_module != '请选择')):
            
                sql = "SELECT id FROM ModuleInfo WHERE module_name=%s"
                params = [belong_module]
                helper = Pmysql()
                data = helper.fetchone(sql,params)
                helper.close()
                case_belong_module_id=data['id']
                

                if(import_type==0 or import_type=='' ):
                    obj=obj.filter(belong_project=belong_project,belong_module_id=case_belong_module_id).filter(name__contains=name).filter(author__contains=user).extra(where=["belong_project in ("+project_name_list+")"]).order_by('-update_time')
                else:
                    obj=obj.filter(belong_project=belong_project,belong_module_id=case_belong_module_id,type=import_type).filter(name__contains=name).filter(author__contains=user).extra(where=["belong_project in ("+project_name_list+")"]).order_by('-update_time')

            if ((belong_project == 'All') and (belong_module == '请选择')):
                if(import_type==0 or import_type=='' ):
                    obj=obj.filter(name__contains=name).filter(author__contains=user).extra(where=["belong_project in ("+project_name_list+")"]).order_by('-update_time')

                else:
                    
                    obj=obj.filter(type=import_type).filter(name__contains=name).filter(author__contains=user).extra(where=["belong_project in ("+project_name_list+")"]).order_by('-update_time')

            if ((belong_project != 'All') and (belong_module == '请选择')):
                if(import_type==0 or import_type=='' ):
                    obj=obj.filter(belong_project=belong_project).filter(name__contains=name).filter(author__contains=user).extra(where=["belong_project in ("+project_name_list+")"]).order_by('-update_time')
                else:
                    obj=obj.filter(type=import_type,belong_project=belong_project).filter(name__contains=name).filter(author__contains=user).extra(where=["belong_project in ("+project_name_list+")"]).order_by('-update_time')
        else:
            obj=obj.filter(id='-999')



    elif url == '/Index/module_list/':
        #根据userid查belong_project_id
        sql = 'SELECT id from ProjectInfo where userid= %s'
        params = [userid]
        helper = Pmysql()
        data = helper.fetchall(sql,params)
        helper.close()
        project_id_list=[]
        
        if(data is not None):

            for i in data:
                project_id_list.append(str(i['id']))
            project_id_list=','.join(project_id_list) 

            if belong_project != 'All':
                obj = obj.filter(belong_project__project_name__contains=belong_project).extra(where=["belong_project_id in ("+project_id_list+")"]).order_by('-update_time')

            elif belong_module != '请选择':
                obj = obj.filter(module_name__contains=belong_module).extra(where=["belong_project_id in ("+project_id_list+")"]).order_by('-update_time')
                
            else:
                obj=obj.filter(test_user__contains=user).extra(where=["belong_project_id in ("+project_id_list+")"]).order_by('-update_time')
        else:
            obj=obj.filter(id='-999')
    elif url == '/Index/report_list/':
        obj = obj.filter(report_name__contains=filter_query.get('report_name')).filter(userid=userid)

    elif url == '/Index/periodictask/':
        obj = obj.filter(name__contains=name).values('id', 'name', 'kwargs', 'enabled', 'date_changed') \
            if name is not '' else obj.all().values('id', 'name', 'kwargs', 'enabled', 'date_changed', 'description')

    elif url == '/Index/suite_list/':
        #根据userid查belong_project_id
        sql = 'SELECT id from ProjectInfo where userid= %s'
        params = [userid]
        helper = Pmysql()
        data = helper.fetchall(sql,params)
        helper.close()
        project_id_list=[]
        if(data is not None):
            for i in data:
                project_id_list.append(str(i['id']))
            project_id_list=','.join(project_id_list) 
            if belong_project != 'All':
                obj = obj.filter(belong_project__project_name__contains=belong_project).filter(suite_name__contains=name).extra(where=["belong_project_id in ("+project_id_list+")"]).order_by('-update_time')
            else:
                obj = obj.filter(suite_name__contains=name).extra(where=["belong_project_id in ("+project_id_list+")"]).order_by('-update_time')
        else:
            obj=obj.filter(id='-999')


    elif url != '/Index/env_list/' and url != '/Index/debugtalk_list/' and url != '/Index/env_file_list/' :

        if import_type == ALL_CASE_TYPE or import_type == '':
            obj = obj.filter(Q(type__exact=TEST_CASE_TYPE) | Q(type__exact=API_TYPE)) if url == '/Index/test_list/' else obj.filter(type__exact=CONFIG_TYPE)
        else:
            obj = obj.filter(type__exact=import_type)

        if belong_project != 'All' and belong_module != '请选择':
            obj = obj.filter(belong_project__contains=belong_project).filter(
                belong_module__module_name__contains=belong_module)
            if name is not '':
                obj = obj.filter(name__contains=name)

        else:
            if belong_project != 'All':
                obj = obj.filter(belong_project__contains=belong_project)
            elif belong_module != '请选择':
                obj = obj.filter(belong_module__module_name__contains=belong_module)
            else:
                obj = obj.filter(name__contains=name) if name is not '' else obj.filter(author__contains=user)

    elif url != '/Index/periodictask/':
        if url=='/Index/debugtalk_list/':
            #根据userid查belong_project_id
            sql = 'SELECT id from ProjectInfo where userid= %s'
            params = [userid]
            helper = Pmysql()
            data = helper.fetchall(sql,params)
            helper.close()
            project_id_list=[]
            if(data is not None):

                for i in data:
                    project_id_list.append(str(i['id']))
                project_id_list=','.join(project_id_list) 
                obj=obj.extra(where=["belong_project_id in ("+project_id_list+")"]).order_by('-update_time')
            else:
                obj=obj.filter(id='-999')

        elif url=='/Index/env_file_list/':
            #根据userid查belong_project_id
            sql = 'SELECT id from ProjectInfo where userid= %s'
            params = [userid]
            helper = Pmysql()
            data = helper.fetchall(sql,params)
            helper.close()
            project_id_list=[]
            if(data is not None):
                for i in data:
                    project_id_list.append(str(i['id']))
                project_id_list=','.join(project_id_list) 
                obj=obj.extra(where=["belong_project_id in ("+project_id_list+")"]).order_by('-update_time')
            else:
                obj=obj.filter(id='-999')
        else:
            obj = obj.order_by('-update_time')
    else:
        obj = obj.order_by('-date_changed')

    total = obj.count()


    page_info = PageInfo(id, total, per_items=per_items)
    info = obj[page_info.start:page_info.end]

    sum = {}
    page_list = ''
    if total != 0:
        if url == '/Index/project_list/':
            for model in info:
                pro_name = model.project_name
                module_count = str(ModuleInfo.objects.filter(belong_project__project_name__exact=pro_name).count())
                suite_count = str(TestSuite.objects.filter(belong_project__project_name__exact=pro_name).count())
                test_count = str(TestCaseInfo.objects.filter(belong_project__exact=pro_name, type__exact=1).count())
                config_count = str(TestCaseInfo.objects.filter(belong_project__exact=pro_name, type__exact=2).count())
                sum.setdefault(model.id, module_count + '/ ' + suite_count + '/' + test_count + '/ ' + config_count)

        elif url == '/Index/module_list/':
            for model in info:
                module_name = model.module_name
                project_name = model.belong_project.project_name
                test_count = str(TestCaseInfo.objects.filter(belong_module__module_name=module_name,
                                                             type__exact=1, belong_project=project_name).count())
                config_count = str(TestCaseInfo.objects.filter(belong_module__module_name=module_name,
                                                               type__exact=2, belong_project=project_name).count())
                sum.setdefault(model.id, test_count + '/ ' + config_count)

        elif url == '/Index/suite_list/':
            for model in info:
                suite_name = model.suite_name
                project_name = model.belong_project.project_name
                test_count = str(len(eval(TestSuite.objects.get(suite_name=suite_name,
                                                                belong_project__project_name=project_name).include)))
                sum.setdefault(model.id, test_count)

        page_list = customer_pager(url, id, page_info.total_page)

    return page_list, info, sum