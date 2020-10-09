# encoding:utf-8
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


from apiTest.settings import EMAIL_SEND_USERNAME, EMAIL_SEND_PASSWORD


def send_email_reports(receiver, html_report_path):
    if '@sina.com' in EMAIL_SEND_USERNAME:
        smtp_server = 'smtp.sina.com'
    elif '@163.com' in EMAIL_SEND_USERNAME:
        smtp_server = 'smtp.163.com'
    elif '@139.com' in EMAIL_SEND_USERNAME:
        smtp_server = 'smtp.139.com'
    else:
        smtp_server = 'smtp.exmail.qq.com'

    subject = "接口自动化测试报告"

    with io.open(html_report_path, 'r', encoding='utf-8') as stream:
        send_file = stream.read()

    att = MIMEText(send_file, "base64", "utf-8")
    att["Content-Type"] = "application/octet-stream"
    att["Content-Disposition"] = "attachment;filename = TestReports.html"

    body = MIMEText("附件为定时任务生成的接口测试报告，请查收，谢谢！", _subtype='html', _charset='gb2312')

    msg = MIMEMultipart('related')
    msg['Subject'] = subject
    msg['from'] = EMAIL_SEND_USERNAME
    msg['to'] = receiver
    msg.attach(att)
    msg.attach(body)

    smtp = smtplib.SMTP()
    print(smtp_server)
    smtp.connect(smtp_server,25)
    smtp.starttls()
    smtp.login(EMAIL_SEND_USERNAME, EMAIL_SEND_PASSWORD)
    print(receiver.split(','))
    smtp.sendmail(EMAIL_SEND_USERNAME, receiver.split(','), msg.as_string())
    smtp.quit()
def send_email(receiver,email_task_name,send_content):
    if '@sina.com' in EMAIL_SEND_USERNAME:
        smtp_server = 'smtp.sina.com'
    elif '@163.com' in EMAIL_SEND_USERNAME:
        smtp_server = 'smtp.163.com'
    elif '@139.com' in EMAIL_SEND_USERNAME:
        smtp_server = 'smtp.139.com'
    else:
        smtp_server = 'smtp.exmail.qq.com'

    subject = email_task_name

    body = MIMEText(send_content)

    msg = MIMEMultipart('related')
    msg['Subject'] = subject
    msg['from'] = EMAIL_SEND_USERNAME
    msg['to'] = receiver
    msg.attach(body)

    smtp = smtplib.SMTP()
    print(smtp_server)
    smtp.connect(smtp_server,25)
    smtp.starttls()
    smtp.login(EMAIL_SEND_USERNAME, EMAIL_SEND_PASSWORD)
    print(receiver.split(','))
    smtp.sendmail(EMAIL_SEND_USERNAME, receiver.split(','), msg.as_string())
    smtp.quit()




if __name__ == '__main__':
    send_email_reports('##@qq.com, example@163.com', 'D:\\接口测试自动化平台\\reports\\2018-06-05 15-58-00.html')
