from django.http import HttpResponse
import json
from Index.models import TestCaseInfo


def get_apilist(request):
    data = []
    request_data = json.loads(request.body)
    project_name = request_data.get('project')
    module_id = request_data.get('module')
    obj = TestCaseInfo.objects.all().filter(belong_project=project_name,belong_module_id=module_id, type=3).values('id', 'name')
    for case in obj:
        if case:
            data.append({"api_id": case.get('id'), "api_value": case.get('name')})
    return HttpResponse(json.dumps(data), content_type="application/json")