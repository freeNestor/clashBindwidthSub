项目名称

自用vps流量订阅脚本,支持vmiss和hostdare,适用MAC系统。

环境准备

在使用本项目前，请确保你的环境满足以下要求，并按照步骤完成准备工作。

### 系统要求&#xA;

*   操作系统：macOS或Linux

### 依赖软件&#xA;

*   Python：3.8 及以上版本

*   Git：用于克隆仓库代码

*   pip：Python 包管理工具

### 安装步骤&#xA;

1.  克隆仓库到本地

```
git clone https://github.com/freeNestor/clashBindwidthSub.git
```

1.  创建并激活虚拟环境（推荐）

*   macOS/Linux 系统

```
python3 -m venv clashBindwidthSub
source clashBindwidthSub/bin/activate
```

2.  安装项目依赖

```
pip install seleniumbase BeautifulSoup4 webdriver-manager undetected-chromedriver
```

3.  安装chrome浏览器（如已安装忽略）

4.  修改shell脚本中的路径为对应的路径，修改Python脚本中用户名和密码为你的账号信息，并保存

5.  编译go文件，生成可执行文件

```
cd clashBindwidthSub
go build -o clashsub cmd/main.go cmd/subbindwidth.go
```

使用方法

### 基本使用流程&#xA;

1.  在本地运行go程序

```
cd clashBindwidthSub
./clashsub
```

2.  在clash上配置订阅

```
python main.py
```

### 日志&#xA;

```
在scripts目录下有日志文件，可以查看日志
vmiss_login_log.txt
hostdare_login_log.txt
```