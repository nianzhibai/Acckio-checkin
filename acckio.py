import time
import requests
import re
import sys
import json
import os
import configparser
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

# 日志输出处理类
class Tee:
    def __init__(self, *files):
        self.files = files
    
    def write(self, data):
        for f in self.files:
            f.write(data)
            f.flush()  # 确保立即写入
    
    def flush(self):
        for f in self.files:
            f.flush()

# 从配置文件读取邮箱、密码、MY_PUSH_KEY和sleep_time
config = configparser.ConfigParser()
# 尝试读取 config.ini
if os.path.exists("config.ini"):
    config.read("config.ini", encoding="utf-8")
    email = config.get("Account", "email")
    password = config.get("Account", "password")
    MY_PUSH_KEY = config.get("Account", "push_key")
    sleep_time = int(config.get("Others", "sleep_time"))
else:
    print("未找到 config.ini 配置文件，请检查！")
    sys.exit(1)
msg = ""

# 绕过检测
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
# 无头模式配置
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-software-rasterizer")
# 检查是否有 Docker 环境的路径，如果没有则用默认的
driver_path = os.getenv("CHROMEDRIVER_PATH", "chromedriver") 
service = Service(driver_path)

browser = webdriver.Chrome(service=service, options=options)
browser.get("https://acck.io/")
browser.maximize_window()


# 日期
def print_time():
    global msg
    # 获取当前本地时间
    now = datetime.now()
    # 格式化输出 (更符合阅读习惯)
    print(f"{now.strftime('%Y-%m-%d %H:%M:%S')}")
    msg += f"{now.strftime('%Y-%m-%d %H:%M:%S')}\n"

# 保存凭证
def save_auth_data():
    global msg
    try:
        data = {
            "cookies": browser.get_cookies(),
            "localStorage": browser.execute_script("return window.localStorage;"),
        }
        with open("auth_data.json", "w") as f:
            json.dump(data, f)
        print("此次登录凭证Cookies已保存")
        msg += "此次登录凭证Cookies已保存\n"
    except Exception as e:
        print(f"保存凭证Cookies失败: {e}")
        msg += f"保存凭证Cookies失败: {e}\n"


def login():
    global msg
    # --- 1. 注入本地凭证 ---
    if os.path.exists("auth_data.json"):
        try:
            with open("auth_data.json", "r") as f:
                auth_data = json.load(f)

            # 注入 Cookies
            for cookie in auth_data.get("cookies", []):
                if "expiry" in cookie:
                    del cookie["expiry"]
                browser.add_cookie(cookie)

            # 注入 LocalStorage
            for key, value in auth_data.get("localStorage", {}).items():
                # 这种写法可以防止引号冲突
                browser.execute_script(
                    "window.localStorage.setItem(arguments[0], arguments[1]);",
                    key,
                    value,
                )

            print("本地已保存登录凭证, 尝试注入凭证")
            msg += "本地已保存登录凭证, 尝试注入凭证\n"
            time.sleep(sleep_time)  # 注入登录凭证后等待3s(等待注入操作执行完)
            browser.refresh()
            time.sleep(sleep_time)  # 给页面一点反应时间
        except Exception as e:
            print(
                f"本地已保存登录凭证, 但是注入凭证失败: {e}\n尝试使用用户名和密码登录"
            )
            msg = (
                msg + "本地已保存登录凭证, 但是注入凭证失败, 尝试使用用户名和密码登录\n"
            )

    # --- 2. 核心判断：页面上是否还有“登录”按钮 ---
    # 我们用 find_elements (复数)，找不到不会报错，而是返回空列表
    login_buttons = browser.find_elements(
        By.XPATH, "//button[contains(., '登录') or contains(., 'Login')]"
    )

    if len(login_buttons) == 0:
        # print("页面上没找到登录按钮，看来凭证有效，已处于登录状态")
        print("通过登录凭证登录成功")
        msg += "通过登录凭证登录成功\n"
        return  # 直接跳出，不执行后面的账号密码逻辑
    else:
        # print("依然存在登录按钮，开始执行账号密码登录流程")
        print("登录凭证登录失败, 尝试使用用户名和密码登录")
        msg += "登录凭证登录失败, 尝试使用用户名和密码登录\n"

    # --- 3. 账号密码登录逻辑 ---
    try:
        # 点击那个“登录”按钮（此时 login_buttons[0] 就是我们要点的那一个）
        login_buttons[0].click()
        time.sleep(sleep_time)

        # 输入账号密码
        browser.find_element(By.XPATH, "//input[@placeholder='请输入邮箱']").send_keys(
            email
        )
        browser.find_element(By.XPATH, "//input[@placeholder='请输入密码']").send_keys(
            password
        )

        # 点击确认登录
        submit_btn = browser.find_element(
            By.XPATH,
            "//button[@class='arco-btn arco-btn-primary arco-btn-shape-square arco-btn-size-large arco-btn-status-normal arco-btn-long']",
        )
        submit_btn.click()

        # 等待一会儿确保登录完成（存入 Cookie）
        time.sleep(sleep_time)
        print("通过用户名和密码登录成功")
        msg += "通过用户名和密码登录成功\n"
        save_auth_data()

    except Exception as e:
        print(f"使用账号和用户名登录失败: {e}\n签到失败")
        msg += f"使用账号和用户名登录失败: {e}\n签到失败"
        serverJ(MY_PUSH_KEY, "Acck.io签到", msg)


# 跳过2FA弹窗
def skip_2fa():
    # 如果已经登录进去了，这里加一个容错判断
    time.sleep(sleep_time)
    browser.refresh()


# 进入控制台
def enter_the_console():
    global msg
    time.sleep(sleep_time)
    try:
        # 这里使用了和登录入口一样的 class，可能需要确认是否有多个同类按钮
        button = browser.find_element(
            By.XPATH,
            "//button[@class='arco-btn arco-btn-secondary arco-btn-shape-square arco-btn-size-medium arco-btn-status-normal']",
        )
        button.click()
    except Exception as e:
        # 如果已经是控制台页面，可能找不到这个按钮，直接 pass
        if "console" in browser.current_url:
            pass
        else:
            msg += f"进入控制台过程出错: {e}" + "\n" + "签到失败"
            print(f"进入控制台过程出错: {e}" + "\n" + "签到失败")
            browser.quit()
            serverJ(MY_PUSH_KEY, "Acck.io签到", msg)


def enter_store():
    global msg
    try:
        button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "/html/body/div[1]/div/div[1]/div/div/div[1]/div[2]/a[6]/div",
                )
            )
        )
        button.click()
    except TimeoutError as e:
        msg += f"进入AC币商店过程出错: {e}" + "\n" + "签到失败"
        print(f"进入AC币商店过程出错: {e}" + "\n" + "签到失败")
        browser.quit()
        serverJ(MY_PUSH_KEY, "Acck.io签到", msg)


def check_in():
    global msg
    try:
        iframe = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="app"]/div/div[3]/div/div/iframe')
            )
        )
        browser.switch_to.frame(iframe)
    except TimeoutException as e:
        msg += f"进入签到子界面失败: {e}\n签到失败"
        browser.quit()
        serverJ(MY_PUSH_KEY, "Acck.io签到", msg)

    pre_points = "未获取到"
    try:
        pre_points = (
            WebDriverWait(browser, 10)
            .until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//div[@class="balance"]/span[@class="amount"]')
                )
            )
            .text.strip()
        )
    except TimeoutException as e:
        print(
            f"获取先前的积分失败: {e}"
        )  # 对于没签到的情况，这个积分属于先前积分；对于已经签到的情况，这个积分就是当前积分
    try:
        check_in_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//button[@class='arco-btn arco-btn-primary arco-btn-shape-square arco-btn-size-medium arco-btn-status-normal sign-button']",
                )
            )
        )
        check_in_button.click()
        msg += "签到成功, "
        print("签到成功")
        browser.refresh()
        browser.switch_to.frame(
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="app"]/div/div[3]/div/div/iframe')
                )
            )
        )
        cur_points = (
            WebDriverWait(browser, 10)
            .until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//div[@class="balance"]/span[@class="amount"]')
                )
            )
            .text.strip()
        )
        if cur_points.isdigit() and pre_points.isdigit():
            increase = int(cur_points) - int(pre_points)
            msg += f"获得了{increase}个积分，当前总积分：{cur_points}\n"
            print(f"获得了{increase}个积分，当前积分：{cur_points}")
        else:
            msg += f"但积分显示异常，当前：{cur_points}\n"
            print(f"但积分显示异常，当前：{cur_points}")
    except TimeoutException as e:
        try:
            checked_in_button = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//button[@class='arco-btn arco-btn-secondary arco-btn-shape-square arco-btn-size-medium arco-btn-status-normal sign-button']",
                    )
                )
            )
            msg += "今天已经签到过了, 不用重复执行脚本\n"
            msg += f"当前积分为: {pre_points}\n"
            print("今天已经签到过了, 不用重复执行脚本")
            print(f"当前积分为: {pre_points}")
        except TimeoutException:
            msg += "机器网络太差, 签到失败\n"
            print("机器网络太差, 签到失败")
    finally:
        browser.quit()
        serverJ(MY_PUSH_KEY, "Acck.io签到", msg)


def serverJ(push_key, title, content):
    if not push_key:
        return
    desp = content.replace("\n", "\n\n")
    data = {"text": title, "desp": desp}
    match = re.match(r"sctp(\d+)t", push_key)
    if match:
        url = f"https://{match.group(1)}.push.ft07.com/send/{push_key}.send"
    else:
        url = f"https://sctapi.ftqq.com/{push_key}.send"
    try:
        requests.post(url, data=data, timeout=15)
    except:
        pass
    print("Server酱通知工作结束")
    sys.exit()


if __name__ == "__main__":
    # 同时输出到控制台和日志文件
    log_file = open("acckio.log", "w", encoding="utf-8")
    sys.stdout = Tee(sys.stdout, log_file)

    print_time()
    login()
    skip_2fa()
    enter_the_console()
    enter_store()
    check_in()
    print("签到工作结束")
    serverJ(MY_PUSH_KEY, "acck.io签到", msg)
