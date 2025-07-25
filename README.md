自用vps流量订阅脚本,支持vmiss和hostdare,适用MAC系统（可改造适合其他linux或Windows系统）。

### 环境准备&#xA;

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

3.  安装chrome浏览器（如已安装忽略）和jq命令

4.  （关键）修改shell脚本中的路径为对应的路径，修改Python脚本中url需要替换的id号为你的id号(可通过浏览器devTools查看你的id)，以及用户名和密码为你的账号信息，并保存

5.  编译go文件，生成可执行文件

```
cd clashBindwidthSub
go build -o clashsub cmd/main.go cmd/subbindwidth.go
```

### 使用方法&#xA;

### 基本使用流程&#xA;

1.  在本地运行go程序

```
cd clashBindwidthSub
./clashsub
```

2.  在clash上配置订阅

<img width="400" height="600" alt="iShot_2025-07-25_14 47 01" src="https://github.com/user-attachments/assets/dc4d0a6f-8f1f-408d-9611-2e18a2fd6e9f" /><img width="400" height="600" alt="iShot_2025-07-25_14 47 21" src="https://github.com/user-attachments/assets/f2104f45-9ec3-4e6f-a824-684f53c21ba4" />

<img width="994" height="227" alt="iShot_2025-07-25_14 47 37" src="https://github.com/user-attachments/assets/d687f991-39af-4629-835f-708bb7971e1b" />
<img width="978" height="334" alt="iShot_2025-07-25_14 47 54" src="https://github.com/user-attachments/assets/70bd2f29-8695-4ce0-8926-afb41ed7916d" />


### 日志&#xA;

```
在scripts目录下有日志文件，可以查看日志
vmiss_login_log.txt
hostdare_login_log.txt
```
