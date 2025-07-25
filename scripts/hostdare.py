# import undetected_chromedriver as uc
from seleniumbase import SB
from selenium.webdriver.common.by import By
import time
import pickle
import os
from bs4 import BeautifulSoup
import json
from datetime import datetime

# ====================== 配置部分 ======================
# 日志文件名
log_file = "hostdare_login_log.txt"
def log_output(message, to_console=False, to_file=True):
    """
    打印信息并可选写入日志文件
    :param message: 要记录的信息
    :param to_console: 是否输出到控制台
    :param to_file: 是否写入文件
    """
    if to_console:
        print(message)
    
    if to_file:
        with open(log_file, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            f.write(f"{timestamp} {message}\n")
login_url = "https://vps.hostdare.com "            # 替换为你的登录页面地址
sessid = ""
purl = "https://vps.hostdare.com/{sessid}/index.php?api=json&act=bandwidth&svs=54436&show=undefined "
protected_url = purl.format(sessid=sessid)    # 登录后才能访问的页面
cookie_file_name = "hostdare_cookies.pkl"
cookie_file_path = "saved_cookies/" + cookie_file_name + ".txt"                   # 用于保存 cookies 的文件名

username = ""                         # 替换为你的账号
password = ""                         # 替换为你的密码
csrf_token = ""

# ====================== 检查是否存在 cookies ======================
if os.path.exists(cookie_file_path):
    use_cookies = True
    log_output(f"✅ 发现已保存的 cookies，将尝试复用...")
    with open("session_id.txt", "r") as f:
        sessid = f.read().strip()
        protected_url = purl.format(sessid=sessid)

else:
    use_cookies = False
    log_output(f"⚠️ 未发现 cookies，将进行登录操作...")

# ====================== 初始化浏览器 ======================
# options = uc.ChromeOptions()
# options.add_argument("--start-minimized")  # 可选：最大化窗口
# options.add_argument('--headless')   # 可选：无头模式运行（隐藏浏览器）
binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # macOS 用户可取消注释

# --- 如果存在 cookies，则加载 ---
with SB(uc=True, binary_location=binary_location, headless=True) as sb:
    log_output(f"初始化浏览器…")
    # driver = uc.Chrome(executable_path=uc_driver,options=options)
    # driver = Driver(uc=True, driver_version="130.0.6723.91", binary_location=binary_location)
    # sb = SB(uc=True, binary_location=binary_location)
    # driver = Driver(browser="safari")
    if not use_cookies:
        sb.activate_cdp_mode(login_url)
        # sb.open(login_url)
        time.sleep(3)  # 等待页面加载（可替换为 WebDriverWait）
    else:
        try:
            if use_cookies:
                sb.open(login_url)
                sb.load_cookies(name=cookie_file_name)
                # with open(cookie_file, "rb") as f:
                #     cookies = pickle.load(f)
                # for cookie in cookies:
                #     log_output(f"加载 cookie: {cookie}")
                #     # cookie["domain"] = "app.vmiss.com"
                #     driver.add_cookie(cookie)
                log_output(f"开始访问页面：{protected_url}")
                sb.open(protected_url)
                log_output(f"页面内容前2000字符：")
                log_output(sb.get_page_source()[:2000])
                # 解析为 Python 字典
                try:
                    soup = BeautifulSoup(sb.get_page_source(), 'html.parser')
                    json_str = soup.body.get_text()  # 获取 body 中的文本（即 JSON 字符串）
                    if "Safari浏览器无法打开页面" in json_str:
                        log_output(f"❌ Safari浏览器无法打开页面,稍后再试")
                        time.sleep(10)
                    if "login" in json_str:
                        log_output(f"❌ cookie无效，删除 cookies 文件")
                        os.remove(cookie_file_path)
                    # 打印原始 JSON 字符串
                    if "bandwidth" and "used" in json_str:
                        log_output(f"原始 JSON 字符串：")
                        log_output(json_str,to_console=True)
                except json.JSONDecodeError as e:
                    log_output(f"JSON 解析失败：{e}")
                # input("按回车关闭浏览器...")
                # sb.quit()
                exit()  # 结束程序，避免继续执行下面的登录逻辑
        except Exception as e:
            log_output(f"❌ 异常：{e}")
            err_msg = str(e).lower()
            # sb.quit()
            if "invalid cookie domain" in err_msg:
                log_output(f"❌ 检测到 cookie 无效，请删除 cookies 文件并重新运行程序。")
                # os.remove(cookie_file)
            exit()

    # ====================== 自动处理 Turnstile 验证证码 ======================
    time.sleep(5)
    try:
        sb.uc_gui_click_captcha()

        log_output(f"点击验证按钮成功")
        time.sleep(3)
    except Exception as e:
        log_output(f"未找到验证按钮 {e}")
        try:
            log_output(f"❌ 未找到验证按钮,尝试查找 Cloudflare 验证按钮...")
            verify_button = sb.find_element(
                By.XPATH,
                '//button[@id="turnstile" or contains(text(), "I\'m not a robot")]'
            )
            log_output(f"找到验证按钮，正在点击...")
            verify_button.click()
            time.sleep(5)
        except Exception as e:
            log_output(f"未找到验证按钮或已自动通过验证")

    # ====================== 提取 CSRF Token ======================
    try:
        # 使用 execute_script 提取变量值
        csrf_token = sb.execute_script("return csrfToken;")
        log_output(f"✅ 成功提取 CSRF Token: {csrf_token}")
    except Exception as e:
        log_output(f"❌ 未找到 CSRF Token，请检查页面结构")
        # input("按回车关闭浏览器...")
        # sb.quit()
        # exit()

    # ====================== 模拟登录操作 ======================
    try:
        log_output(f"正在尝试登录...")

        # 替换为你网站的实际输入框 name 或 id
        # username_input = driver.find_element(By.ID, "inputEmail")
        # password_input = driver.find_element(By.ID, "inputPassword")
        # login_button = driver.find_element(By.ID, 'login')
        # token = driver.find_element(By.NAME, 'token')
        sb.type("#username", username)
        sb.type("#_password", password)
        # sb.wait_for_element('//button[@id="login" and text()="Login"]')
        bs = sb.find_visible_elements('#login')
        for b in bs:
            # print("b.text:", b.text)
            if b.text == "Login":
                b.click()
                break
        
        # sb.click('//button[@id="login" and text()="Login"]')

        log_output(f"登录中，请等待10s跳转...")
        time.sleep(5)  # 等待跳转到受保护页面
        # input("按回车继续...")

    except Exception as e:
        if "Connection refused" or "was not found" in str(e):
            log_output(f"❌ 登录失败: {e}")
            # sb.quit()
            exit()
        log_output(f"无需登录 {e}")

    # ====================== 访问受保护页面 ======================
    newurl = sb.get_current_url()
    sessid = newurl.split("/")[3]
    protected_url = purl.format(sessid=sessid)
    with open("session_id.txt", "w") as f:
        f.write(sessid)
    log_output(f"正在访问受保护页面... {protected_url}")
    sb.open(protected_url)
    sb.save_cookies(name=cookie_file_name)
    log_output(f"✅ 当前 cookies 已保存到文件: {cookie_file_name}")
    log_output(f"页面内容前2000字符：")
    log_output(sb.get_page_source()[:2000])
    soup = BeautifulSoup(sb.get_page_source(), 'html.parser')
    json_str = soup.body.get_text()  # 获取 body 中的文本（即 JSON 字符串）

    # 打印原始 JSON 字符串
    if "bindwidth" and "used" in json_str:
        log_output(f"原始 JSON 字符串：")
        log_output(json_str,to_console=True)

    if "无法打开页面" in json_str:
        log_output(f"❌ 浏览器无法打开页面,稍后再试")
        time.sleep(10)

    if "login" in json_str:
        log_output(f"❌ cookie无效，删除 cookies 文件")
        os.remove(cookie_file_path)

    # sb.quit()
