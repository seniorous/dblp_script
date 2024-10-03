import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from bs4 import BeautifulSoup as bs
import requests
import random
min_wait = 0.2
max_wait = 0.4
def get_content():
    keyword = input("请输入查询关键字: ")
    year = input("请输入查询年份: ")
    return {"q": f"{keyword} {year}"}
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
def get_abstract(source_url):
    if not source_url:
        return None,None
    url=source_url   
# Send a request to the website
    source=requests.get(url).text
#print(source)
# Parse the HTML content using BeautifulSoup
    soup=bs(source,'html.parser')
    title=None
    abstract=None
#print(soup.prettify())
    if url.startswith("https://doi.org/10.1109/"):
                title=soup.find("h1", attrs={"property": "name"})
                if title:
                    title=title.text
                else:
                    title=None
                abstract = soup.find("div", attrs={"role": "paragraph"})
                if abstract:
                    abstract = abstract.text
                else:
                    abstract = None
    elif url.startswith("https://doi.org/10.1109/"):
                title=soup.find("h1", attrs={"property": "name"})
                if title:
                    title=title.text    
                else:
                    title=None
                abstract = soup.find("div", attrs={"role": "paragraph"})
                if abstract:
                    abstract = abstract.text
                else:
                    abstract = None
    elif "openreview" in url:
                #divcontent 
                title=soup.find("h2", attrs={"class": "citation_title"})
                if title:
                    title=title.text
                else:
                    title=None
                abstract = soup.find("span", attrs={"class": "note-content-value"})
                if abstract:
                    abstract = abstract.text
                else:
                    abstract = None
    #elif "arxiv" in url:
    elif url.startswith("https://proceddings.mlr.neurips.cc/") or url.startswith("https://papers.nips.cc"):
        h4_tags = soup.find_all('h4')
        title=soup.find("h4")
        for h4 in h4_tags:
            if h4.get_text(strip=True) == 'Abstract':
        # 找到下一个兄弟标签（应该是<p>）
                p_tag = h4.find_next_sibling('p')
                if p_tag:
            # 由于存在嵌套的<p>标签，获取内部的<p>标签
                        inner_p = p_tag.find('p')
                        if inner_p:
                            abstract_text = inner_p.get_text(strip=True)
                        else:
                            abstract_text = p_tag.get_text(strip=True)
    elif url.startswith("https://proceedings.mlr.press/"):
        title = soup.find("h1", attrs={"class": "post-content"})
        h4_tags = soup.find_all('h4')

        abstract_text = None

            # 遍历<h4>标签，找到文本为"Abstract"的标签
        for h4 in h4_tags:
            if h4.get_text(strip=True) == 'Abstract':
        # 找到下一个兄弟标签（应该是<p>）
                p_tag = h4.find_next_sibling('p')
                if p_tag:
            # 由于存在嵌套的<p>标签，获取内部的<p>标签
                        inner_p = p_tag.find('p')
                        if inner_p:
                            abstract_text = inner_p.get_text(strip=True)
                        else:
                            abstract_text = p_tag.get_text(strip=True)
        

    return title,abstract
query=get_content()
urls=fetch_dblp_urls(query["q"])
with open(query["q"]+"plus"+".docx", "w", encoding="utf-8") as file:
        for url in urls:
        #生成随机等待时间
            wait_time = random.uniform(min_wait, max_wait)
            time.sleep(wait_time)
            title,abstract = get_abstract(url)
            if abstract:
                file.write(f"{url}\n{title}\n{abstract}\n\n")  # 每个URL和对应的abstract用换行分隔
            else:
                print(f"No abstract found for {url}")
        print(f"Abstracts saved to {query['q']}.docx")
