## description

选课脚本

## Usage

项目需要将个人信息以`config.py`导入

在当前目录下修改`config.py`，形如：

```python
# 教务处登录的账号密码
username = '2022*****'  # 学号
password = '**************'  # 密码

# email config
config = {
    'from': 'send_from@example.com',  # 邮件发送方，需要开通SMTP服务
    'pwd': 'abcdefghyukj',  # 开通SMTP后给的登录秘钥
    'to': ['send_to@example.com']  # 邮件接收方，可以是自己，也可以多人
}
# 因为实际未使用邮件发送通知，所以里面的值可以随便设置
```
然后在`main.py`里
设置需要删除的课程编号(chooseId)，
修改需要选的课的teachId或者课程编号(chooseId)

#### 或者也可以使用`main.ipynb`来进行选课，配置好选课策略，选课时按照自己想法来启动线程。

# !!!注意使用脚本前第一次选课先自己分析好第二次选课要选的课程，
## 建议第一次选课用这个脚本来选以测试脚本是否正常


## chore
不知为何，目前教务网选课系统的返回好像都不能加`res.encoding = res.apparent_encoding`

