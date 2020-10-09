from django.conf import settings
import Common.config as con


def global_config(request):
    content = {
        "WEB_NAME": con.WEB_NAME,
        "INDEX_URL": con.INDEX_URL, "INDEX_HTML": con.INDEX_HTML,
        "WARRING": con.WARRING,
        "PROJECT_LIST_URL": con.PROJECT_LIST_URL, "ADD_PROJECT_URL": con.ADD_PROJECT_URL,
        "MODULE_LIST_URL": con.MODULE_LIST_URL, "ADD_MODULE_URL": con.ADD_MODULE_URL,
        "TEST_LIST_URL": con.TEST_LIST_URL, "ADD_CASE_URL": con.ADD_CASE_URL,
        "CONFIG_LIST_URL": con.CONFIG_LIST_URL, "ADD_CONFIG_URL": con.ADD_CONFIG_URL,
        "SUITE_LIST_URL": con.SUITE_LIST_URL, "ADD_SUITE_URL": con.ADD_SUITE_URL,
        "DEBUG_TALK_LIST_URL": con.DEBUG_TALK_LIST_URL,
        "REPORT_LIST_URL": con.REPORT_LIST_URL,
        "ENV_LIST_URL": con.ENV_LIST_URL,
        "ADD_TASK_URL": con.ADD_TASK_URL, "PERIODICT_TASK_URL": con.PERIODICT_TASK_URL,
        "ENVFILE_LIST_URL":con.ENVFILE_LIST_URL,
    }
    return content