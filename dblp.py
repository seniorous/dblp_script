import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from bs4 import BeautifulSoup as bs
import requests
def get_content():
    # 输入查询关键字
    Nam = input("请输入查询关键字: ")
    year = input("请输入查询年份(如不输入则默认查询所有年份): ")
    params = {"q": Nam+" "+year}
    return params
def fetch_dblp_urls(query):
    # 设置 Edge 浏览器选项
    edge_options = Options()
    edge_options.add_argument("--headless")  # 隐藏浏览器窗口

    # 启动 Edge 浏览器
    service = Service(r"D:\tool\edgedriver_win32\msedgedriver.exe")  # 替换为实际的 msedgedriver 路径
    driver = webdriver.Edge(service=service, options=edge_options)

    try:
        url = f"https://dblp.org/search?q={query}"
        driver.get(url)

        try:
            # 等待页面加载
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'publ')))
        except Exception as e:
            print(f"页面加载时出错: {e}")

        # 模拟滚动以加载更多内容
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            try:
                # 滚动到底部
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # 等待加载更多内容

                # 检查新内容是否已加载
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:  # 如果没有新内容
                    break
                last_height = new_height
            except Exception as e:
                print(f"滚动过程中出错: {e}")
                break

        try:
            # 获取所有 'publ' 类的元素
            soup = bs(driver.page_source, 'html.parser')
            all_urls = soup.find_all("nav", attrs={"class": "publ"})
        except Exception as e:
            print(f"解析页面时出错: {e}")
            return []

        urls = []
        for publ in all_urls:
            try:
                first_a = publ.find('a')
                if first_a and 'href' in first_a.attrs:
                    urls.append(first_a['href'])
            except Exception as e:
                print(f"提取 URL 时出错: {e}")

        return urls
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
    finally:
        driver.quit()  # 关闭浏览器
# 调用函数
# params = get_content()
# urls = fetch_dblp_urls(params)
# abstracts = get_abstract(urls)
# print("\n".join(abstracts))  # 输出所有摘要

query=get_content()
urls=fetch_dblp_urls(query)
print("\n".join(urls))  # 输出所有摘要
