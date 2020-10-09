
INDEX_DIR = 'Index'
PROJECT_DIR = INDEX_DIR
MODULE_DIR = INDEX_DIR
TEST_DIR = INDEX_DIR
SUITE_DIR = INDEX_DIR
CONFIG_DIR = INDEX_DIR
DEBUG_TALK_DIR = INDEX_DIR
REPORT_DIR = INDEX_DIR
ENV_DIR = INDEX_DIR
TASK_DIR = INDEX_DIR
PERIODICT_TASK_DIR = INDEX_DIR

WEB_NAME = '接口测试自动化平台'

INDEX_HTML = '{}/index.html'.format(INDEX_DIR)
INDEX_URL = '/{}/index'.format(INDEX_DIR)

PROJECT_LIST_URL = '/{}/project_list'.format(PROJECT_DIR)
ADD_PROJECT_URL = '/{}/add_project'.format(PROJECT_DIR)

MODULE_LIST_URL = '/{}/module_list'.format(MODULE_DIR)
ADD_MODULE_URL = '/{}/add_module'.format(MODULE_DIR)

TEST_LIST_URL = '/{}/test_list'.format(TEST_DIR)
ADD_CASE_URL = '/{}/add_case'.format(TEST_DIR)

CONFIG_LIST_URL = '/{}/config_list'.format(CONFIG_DIR)
ADD_CONFIG_URL = '/{}/add_config'.format(CONFIG_DIR)

SUITE_LIST_URL = '/{}/suite_list'.format(SUITE_DIR)
ADD_SUITE_URL = '/{}/add_suite/'.format(SUITE_DIR)

DEBUG_TALK_LIST_URL = '/{}/debugtalk_list'.format(DEBUG_TALK_DIR)

REPORT_LIST_URL = '/{}/report_list'.format(REPORT_DIR)

ENV_LIST_URL = '/{}/env_list'.format(ENV_DIR)

ADD_TASK_URL = '/{}/add_task/'.format(TASK_DIR)

PERIODICT_TASK_URL = '/{}/periodictask'.format(PERIODICT_TASK_DIR)

TASK_MONITOR_ADDRESS = "http://10.73.10.116:5555/dashboard"

ENVFILE_LIST_URL = '/{}/env_file_list'.format(DEBUG_TALK_DIR)






#服务器繁忙
WARRING = 'Sorry，服务器可能开小差啦, 请重试!'
#用例类型
TEST_CASE_TYPE = 1
CONFIG_TYPE = 2
API_TYPE = 3
ALL_CASE_TYPE  = 0
PROJECT_NAME = "项目"