## Asynchronous_Web_Crawler_EnhancePublicVersion.py

import aiohttp
import asyncio
import math
import re
import os
import concurrent.futures


semaphore = asyncio.Semaphore(value=50)
word = input("Pleas input the name of image you want to downloand:")
fpath = 'C://PythonCodes//Image//' + word + '-ImageURLInfo.txt'
error_path = 'C://PythonCodes//Image//' + word + '-ImageErrorInfo.txt'
root = 'C://PythonCodes//Image//' + word + '-Image//'

if not os.path.exists(root):
    os.mkdir(root)
else:
    print("Root Existed")

async def read_website(url, proxy=None):
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"}
    async with semaphore:
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, timeout=10, proxy=proxy) as response:
                    assert response.status == 200, "response.status Error"
                    contents = await response.read()
                    return contents
        except:
            pass

async def parse_website(html, url_list):
    ulist = re.findall(r'\"objURL\"\:\".*?\"', html)
    for url in ulist:
        objURL = eval(url.split(':', 1)[1])
        url_list.append(objURL)
    return url_list

def save_data(url,data):
    img_name = ''
    url_name = url.split('/')[2:]
    pattern = re.compile(r'.*\.(jpg|png|jpeg|gif)+?')
    if pattern.match(url) is not None:
        for index in url_name:
            img_name = img_name + index
    else:
        url_name.append('.png')
        for index in url_name:
            img_name = img_name + index
    path = root + "-image-" + img_name

    try:
        if not os.path.exists(path):
            with open(path, 'wb') as f:
                f.write(data)
                f.close()
        else:
            print("Data Existed from save_data")
    except:
        pass

def run_show(count, url_length):
    print("\r当前进度: {:.2f}%".format((count+1) * 100 / url_length), end="")

async def main(executor):
    proxys = ["http://123.207.30.131:80",
              "http://121.8.98.198:80",
              "None",]
    count = 0
    urls_list = []
    depth = 1
    start_url = 'https://image.baidu.com/search/flip?tn=baiduimage&word=' + word

    loop = asyncio.get_event_loop()

    for i in range(depth):
        try:
            url = start_url + '&pn=' + str(20 * i)
            html = str(await read_website(url))
            urls_list = await parse_website(html, urls_list)

            url_length = len(urls_list)
            proxys_length = len(proxys)
            iter_range = url_length / proxys_length ## 取url长度与Proxy长度相除的商
            inter_urls = math.floor(iter_range)      ## 取url长度与Proxy长度相除的商的最小整数
            mod_urls = int(math.fmod(url_length, proxys_length)) ## 取url长度与Proxy长度相除得到余数的整数
            
            print(url_length)
            if mod_urls == 0:  ## url长度与Proxy长度相除得到余数为零时，运行此处
                for url_index in range(inter_urls):
                    for proxy in proxys:
                        try:
                            data = await read_website(urls_list[count])
                            await loop.run_in_executor(executor, save_data, urls_list[count], data)
                            loop.call_soon(run_show, count, url_length)
                            count += 1
                        except:
                            continue

            elif mod_urls > 0 :  ## url长度与Proxy长度相除得到余数为不为零时，运行此处
                  for url_index in range(inter_urls):
                    for proxy in proxys:
                        try:
                            print(count)
                            data = await read_website(urls_list[count])
                            await loop.run_in_executor(executor, save_data, urls_list[count], data)
                            loop.call_soon(run_show, count, url_length)
                            count += 1
                        except:
                            continue

                    for url_index in range(len(mod_urls)):
                        try:
                            data = await read_website(urls_list[count])
                            await loop.run_in_executor(executor, save_data, urls_list[count], data)
                            loop.call_soon(run_show, count, url_length)
                            count += 1
                        except:
                            continue

            # assert count == url_length, "count != url_length" ## 检验tasks的长度是否等于urls的长度
         
        except:
            continue

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
    try:       
        loop.run_until_complete(main(executor))
    except:
        print("Loop Run Error")
        pass
    finally:
        # Zero-sleep to allow underlying connections to close
        loop.run_until_complete(asyncio.sleep(0))
        loop.close()
