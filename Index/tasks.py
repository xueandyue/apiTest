# Create your tasks here
# encoding:utf-8
from __future__ import absolute_import, unicode_literals

import os
import shutil

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist

from Index.models import ProjectInfo
from Index.utils.util import timestamp_to_datetime
from Index.utils.emails import send_email_reports,send_email
from Index.utils.operations import add_test_reports
from Index.utils.runner import generate_file_by_project, generate_file_by_module,generate_file_by_suite
from Index.utils.testcase import get_time_stamp
from httprunner.api import HttpRunner, logger


@shared_task
def main_hrun(testset_path, report_name,username=None):
    """
    用例运行
    :param testset_path: dict or list
    :param report_name: str
    :return:
    """
    logger.setup_logger('INFO')
    runner = run(testset_path)
    report_path = add_test_reports(runner, report_name=report_name,username=username)
    os.remove(report_path)


@shared_task
def project_hrun(name, base_url, project, receiver):
    """
    异步运行整个项目
    :param env_name: str: 环境地址
    :param project: str
    :return:
    """
    logger.setup_logger('INFO')
    id = ProjectInfo.objects.get(project_name=project).id

    testcase_dir_path = os.path.join(os.getcwd(), "suite")
    testcase_dir_path = os.path.join(testcase_dir_path, get_time_stamp())

    generate_file_by_project(id, base_url, testcase_dir_path)

    runner = run(testcase_dir_path)
    report_path = add_test_reports(runner, report_name=name)

    if receiver != '':
        send_email_reports(receiver, report_path)
    os.remove(report_path)


@shared_task
def module_hrun(name, base_url, module, receiver):
    """
    异步运行模块
    :param env_name: str: 环境地址
    :param project: str：项目所属模块
    :param module: str：模块名称
    :return:
    """
    module = list(module)

    testcase_dir_path = os.path.join(os.getcwd(), "suite")
    testcase_dir_path = os.path.join(testcase_dir_path, get_time_stamp())

    try:
        for value in module:
            generate_file_by_module(value[0], base_url, testcase_dir_path)
    except ObjectDoesNotExist:
        return '找不到模块信息'
    runner = run(testcase_dir_path)
    report_path = add_test_reports(runner, report_name=name)

    if receiver != '':
        send_email_reports(receiver, report_path)
    os.remove(report_path)


@shared_task
def suite_hrun(name, base_url, receiver, suite,project,username):
    """
    异步运行模块
    :param env_name: str: 环境地址
    :param project: str：项目所属模块
    :param module: str：模块名称
    :return:
    """
    logger.setup_logger('INFO')

    suite = list(suite)

    testcase_dir_path = os.path.join(os.getcwd(), "suite")
    testcase_dir_path = os.path.join(testcase_dir_path, get_time_stamp())
    suites = []
    for data in suite:
        suites.append(data['id'])
    base_url = base_url['base_url']
    try:
        for value in suites:
            generate_file_by_suite(value,project, base_url, testcase_dir_path)
    except ObjectDoesNotExist:
        return '找不到Suite信息'

    runner = run(testcase_dir_path)
    report_path = add_test_reports(runner, report_name=name,username=username)

    if receiver != '':
        send_email_reports(receiver, report_path)
    os.remove(report_path)


def run(testcase_dir_path):
    kwargs = {
        "failfast": False,
    }
    runner = HttpRunner(**kwargs)
    run_path = os.path.join(testcase_dir_path, 'testcases')
    runner.run(run_path)
    # shutil.rmtree(run_path)
    runner._summary = timestamp_to_datetime(runner._summary, type=False)
    return runner


@shared_task
def send_email_task(name, email_task_name,send_content, receiver,username):
    """
    异步运行模块
    :param env_name: str: 环境地址
    :param project: str：项目所属模块
    :param module: str：模块名称
    :return:
    """
    logger.setup_logger('INFO')
    send_email(receiver,email_task_name,send_content)

