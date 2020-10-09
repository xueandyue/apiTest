from django.db import models


class ProjectInfoManager(models.Manager):

    def insert_project(self, **kwargs):
        self.create(**kwargs)

    def update_project(self, id, **kwargs):  # 如此update_time才会自动更新！！
        obj = self.get(id=id)
        obj.project_name = (kwargs.get('project_name')).strip()
        obj.responsible_name = kwargs.get('responsible_name')
        obj.test_user = kwargs.get('test_user')
        obj.dev_user = kwargs.get('dev_user')
        obj.publish_app = kwargs.get('publish_app')
        obj.simple_desc = kwargs.get('simple_desc')
        obj.other_desc = kwargs.get('other_desc')
        obj.save()

    def get_pro_name(self, pro_name, type=True, id=None):
        if type:
            return self.filter(project_name__exact=pro_name).count()
        else:
            if id is not None:
                return self.get(id=id).project_name
            return self.get(project_name__exact=pro_name)

    def get_pro_info(self, type=True):
        if type:
            return self.all().values('project_name')
        else:
            return self.all()


class ModuleInfoManager(models.Manager):
    def insert_module(self, **kwargs):
        self.create(**kwargs)

    def update_module(self, id, **kwargs):
        obj = self.get(id=id)
        obj.module_name = kwargs.get('module_name')
        obj.test_user = kwargs.get('test_user')
        obj.simple_desc = kwargs.get('simple_desc')
        obj.other_desc = kwargs.get('other_desc')

        obj.save()

    def get_module_name(self, module_name, type=True, id=None):
        if type:
            return self.filter(module_name__exact=module_name).count()
        else:
            if id is not None:
                return self.get(id=id).module_name
            else:
                return self.get(id=module_name)


class TestCaseInfoManager(models.Manager):
    def insert_case(self, belong_module, **kwargs):
        
        case_info = kwargs.get('test').pop('case_info')
        if 'import_type' in case_info.keys():
            case_type = case_info.pop('import_type')
        else:
            case_type='1'
        self.create(name=kwargs.get('test').get('name'),describe=kwargs.get('test').get('describe'), belong_project=case_info.pop('project'),
                    belong_module=belong_module,
                    author=case_info.pop('author'), type=case_type, include=case_info.pop('include'), request=kwargs)

    def update_case(self, belong_module, **kwargs):
        case_info = kwargs.get('test').pop('case_info')
        case_type = case_info.pop('import_type')
        obj = self.get(id=case_info.pop('test_index'))
        obj.belong_project = case_info.pop('project')
        obj.belong_module = belong_module
        obj.name = kwargs.get('test').get('name')
        obj.describe=kwargs.get('test').get('describe')
        obj.author = case_info.pop('author')
        obj.type = case_type
        obj.include = case_info.pop('include')
        obj.request = kwargs
        obj.save()

    def insert_config(self, belong_module, **kwargs):
        config_info = kwargs.get('config').get('config_info')

        self.create(name=kwargs.get('config').get('name'), belong_project=config_info.get('project'),
                    belong_module=belong_module,
                    author=config_info.get('author'), type=2, request=kwargs,include="[]")

    def update_config(self, belong_module, **kwargs):
        config_info = kwargs.get('config').pop('config_info')
        obj = self.get(id=config_info.pop('test_index'))
        obj.belong_module = belong_module
        obj.belong_project = config_info.pop('project')
        obj.name = kwargs.get('config').get('name')
        obj.author = config_info.pop('author')
        obj.request = kwargs
        obj.save()

    def get_case_by_name(self, name, module_name, belong_project):
        return self.filter(belong_module__id=module_name).filter(name__exact=name).filter(
            belong_project__exact=belong_project)

    def get_case_name(self, name, module_name, belong_project):
        return self.filter(belong_module__id=module_name).filter(name__exact=name).filter(
        belong_project__exact=belong_project).count()

    def get_case_by_id(self, index, type=True):
        if type:
            return self.filter(id=index).all()
        else:
            return self.get(id=index).name


class EnvInfoManager(models.Manager):
    def insert_env(self, **kwargs):
        self.create(**kwargs)

    def update_env(self, index, **kwargs):
        obj = self.get(id=index)
        obj.env_name = kwargs.pop('env_name')
        obj.base_url = kwargs.pop('base_url')
        obj.simple_desc = kwargs.pop('simple_desc')
        obj.save()

    def get_env_name(self, index):
        return self.get(id=index).env_name

    def delete_env(self, index):
        self.get(id=index).delete()