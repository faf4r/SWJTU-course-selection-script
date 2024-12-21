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
然后在`main.ipymb`里
设置需要删除的课程编号(chooseId)，
修改需要选的课的teachId或者课程编号(chooseId)

### 推荐使用`main.ipynb`来进行选课，配置好选课策略，选课时按照自己想法来启动线程。
### 也可以使用main.py，但不太建议，请自行参照ipynb进行修改

# !!!注意使用脚本前第一次选课先自己分析好第二次选课要选的课程，
## 建议第一次选课用这个脚本来选以测试脚本是否正常


## chore
不知为何，目前教务网选课系统的返回好像都不能加`res.encoding = res.apparent_encoding`


## Update
更新了代码，适合长时间挂着，登录过期会自动重新登。
且只为了抢课，只有返回选课成功才退出线程，否则继续选，因此需要退出请手动操作

### 2024/12/21更新

本次选课出现了教务系统入口一未开启选课系统，但**入口二**正常开启选课，过了很久入口一才开启选课，导致不能及时选课。所以本次更新添加了`main2.ipynb`、`User2.py`、`utils2.py`，专门用于**入口二**的选课，使用和原来一样，仅替换了教务API。