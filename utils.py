# 换策略，直接等教务网（反正都要验证码）
import requests
import json
import time
import ddddocr

import smtplib
from email.mime.text import MIMEText

ocr = ddddocr.DdddOcr()

url = 'http://jwc.swjtu.edu.cn/vatuu/UserLoginAction'
html_url = 'http://jwc.swjtu.edu.cn/service/login.html'

headers = {
    'Referer': 'http://jwc.swjtu.edu.cn/service/login.html',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}


def login(username: str, password: str) -> requests.Session:
    ss = requests.Session()
    ss.headers = headers

    ss.get(html_url)
    img_url = 'http://jwc.swjtu.edu.cn/vatuu/GetRandomNumberToJPEG'
    time.sleep(1)
    img = ss.get(img_url)
    time.sleep(3)

    # with open('验证码.jpg', 'wb') as f:
    #     f.write(img.content)
    ranstring = ocr.classification(img.content)

    data = {
        'username': username,
        'password': password,
        'url': '',
        'returnType': '',
        'returnUrl': '',
        'area': '',
        'ranstring': ranstring  # 验证码
    }

    # print(data)
    res = ss.post(url=url, data=data)
    res = json.loads(res.text)
    if res['loginStatus'] == '-2':
        raise ValueError(res['loginMsg'])
    elif res['loginStatus'] == '1':
        print(res['loginMsg'])
    # print(res)

    ss.headers.update({'Referer': 'http://jwc.swjtu.edu.cn/vatuu/UserLoginAction'})
    data = {
        'url': url,
        'returnType': '',
        'returnUrl': '',
        'loginMsg': res['loginMsg']
    }
    res = ss.post(url='http://jwc.swjtu.edu.cn/vatuu/UserLoadingAction', data=data)
    # print(res.text)

    return ss


# 发送邮件
def send(config, subject, text):
    # 构建邮件
    msg = MIMEText(text, 'html', 'utf-8')
    msg['From'] = config['from']
    msg['To'] = ','.join(config['to'])
    msg['Subject'] = subject

    # 发送邮件
    with smtplib.SMTP_SSL('smtp.qq.com', 465) as smtp:
        smtp.login(config['from'], config['pwd'])
        smtp.send_message(msg)
        # smtp.sendmail(mail, to, msg.as_string())  # 一样的，但明显上面更简单


if __name__ == '__main__':
    username = '2022112275'
    password = '**************'
    ss = login(username, password)

    resp = ss.get('http://jwc.swjtu.edu.cn/vatuu/StudentScoreInfoAction?setAction=studentMarkUseProgram')  # 不能主页面，要找个模块进去才行
    resp.encoding = resp.apparent_encoding
    print('----\n', resp.text)
