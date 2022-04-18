# -*- coding:utf-8  -*-
# @Time     : 2022/4/18 19:11
# @Author   : BGLB
# @Software : PyCharm
import os
import traceback

import aiohttp
from aiohttp import ClientSession
import asyncio
from lxml import etree
from loguru import logger

logger.add('error.log', level='ERROR', enqueue=True, catch=True)
logger.add('info.log', level='INFO', enqueue=True, catch=True)


class TuDaoJi(object):
    """
        TuDaoJi
    """
    root_url = 'https://www.tujidao.com'
    headers = {
        'authority': 'www.tujidao.com',
        'method': 'POST',
        'path': '/?action=save',
        'scheme': 'https',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'origin': 'https://www.tujidao.com',
        'referer': 'https://www.tujidao.com/?action=login',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    BASE_DIR = os.path.join('E:/', 'extal', '图岛集')
    is_login = False
    cookies_jar = ''

    async def login(self, username, password):
        """
            登录
        :return:
        """
        async with aiohttp.ClientSession() as session:
            url = "{}/?action=save".format(self.root_url)
            payload = f'way=login&username={username}&password={password}'
            response = await session.post(url, headers=self.headers, data=payload)
            logger.info(await response.json(encoding='utf-8', content_type='text/html'))
            self.cookies_jar = session.cookie_jar

    async def logout(self, session):
        """
        :return:
        """
        path = '/u/?action=out'
        await session.get(f'{self.root_url}{path}', headers=self.headers, allow_redirects=False)

    async def fetch_html(self, url: str, session: ClientSession, **kwargs) -> str:
        """
        """
        resp = await session.request(method="GET", url=url, headers=self.headers, **kwargs)
        resp.raise_for_status()
        logger.info(f"Got response [{resp.status}] for URL: {url}")
        html = await resp.text()
        return html

    async def parse(self, url: str, session: ClientSession, **kwargs):
        """Find HREFs in the HTML of `url`."""

        found = set()
        try:
            if not url:
                raise Exception('url 为空')
            html = await self.fetch_html(url=url, session=session, **kwargs)
        except (
                aiohttp.ClientError,
                aiohttp.http_exceptions.HttpProcessingError,
        ):
            logger.error(f"aiohttp exception for {url} {traceback.format_exc()}")
            return found
        except Exception:
            logger.error(
                f"Non-aiohttp exception occured: \n{traceback.format_exc()}"
            )
            return found
        else:
            found = etree.HTML(html)
            return found

    async def get_all_tags(self):
        """
            tags
        :return:
        """
        url = f'{self.root_url}/s/?id=193'
        self.headers.update({'referer': 'https://www.tujidao.com/s/?id=151'})
        async with aiohttp.ClientSession(cookie_jar=self.cookies_jar) as session:
            eroot = await self.parse(url, session)
            if isinstance(eroot, set):
                return
            a_list = eroot.xpath('//*[@class="tags"]//a[not (@target="_blank")]')
            tags_dict = {
                item.xpath('./@href')[0]: item.xpath('./text()')[0] for item in a_list
            }
            return tags_dict

    async def download_tag(self, tag_path, tag_name, page):
        """
            每个tag 下载 10 页
        :return:
        """
        task_list = []
        li_list = []
        parse_tasks = []
        for _page in range(1, page+1):
            url = f'{self.root_url}{tag_path}&page={_page}'
            session = aiohttp.ClientSession(cookie_jar=self.cookies_jar)
            parse_task = asyncio.create_task(self.parse(url, session))
            parse_tasks.append(parse_task)
        for task in parse_tasks:
            result = await task
            if isinstance(result, set):
                continue
            temp_li_list = result.xpath('//div[@class="hezi"]//li')
            li_list.extend(temp_li_list)

        for li_item in li_list:
            li_id = li_item.xpath('./@id')[0]
            li_count = int(str(li_item.xpath('.//span[@class="shuliang"]//text()')[0]).replace('P', ''))
            li_title = li_item.xpath('.//p[@class="biaoti"]//text()')[0]
            task = asyncio.create_task(self.download_img(li_id, li_title, li_count, tag_name))
            task_list.append(task)

        return task_list

    async def download_img(self, pic_id, pic_title: str, img_count: int, tag):
        """
                下载一个 图集
        :return:
        """
        img_host = 'https://tjg.gzhuibei.com'
        logger.info(f'图集标签: 【{tag}】; 图集名称: 【{pic_title}】; 共有【{img_count}张;】 开始下载')
        _path = os.path.join(tag, pic_title).rstrip(' ')
        for item in '/<>|:*?':
            _path = _path.replace(item, '')
        img_save_dir = os.path.join(self.BASE_DIR, _path)

        try:
            os.makedirs(img_save_dir, exist_ok=True)
        except Exception:
            logger.error(f'文件夹创建失败-【{img_save_dir}】')
            return

        tasks = []
        for index in range(img_count):
            img_url = f'{img_host}/a/1/{pic_id}/{index+1}.jpg'
            task = asyncio.create_task(self.download_one_img(img_url, img_save_dir))
            tasks.append(task)

        await asyncio.wait(tasks)

        logger.info(f'图集标签: 【{tag}】; 图集名称: 【{pic_title}】; 共有【{img_count}张;】 下载完成')

    async def download_with_tags_url(self, pic_url):
        """
            给一个图集 url
        #     https://www.tujidao.com/s/?id=47
        :param pic_url:
        :return:
        """
        async with aiohttp.ClientSession(cookie_jar=self.cookies_jar) as session:
            async with session.get(pic_url, headers=self.headers) as resp:
                eroot = etree.HTML(resp.text)
                pic_title = eroot.xpath('//div[@class="titletxt"]//text()')[0]
                li_list = eroot.xpath('//div[@class="hezi"]//li')
                # li biaoti & shuliang & id
                for li_item in li_list:
                    li_id = li_item.xpath('./@id')[0]
                    li_count = int(str(li_item.xpath('.//span[@class="shuliang"]//text()')[0]).replace('P', ''))
                    li_title = li_item.xpath('.//p[@class="biaoti"]//text()')[0]
                    await self.download_img(li_id, li_title, li_count, pic_title)

    async def download_one_img(self, url: str, save_dir):
        """
        :param save_dir:
        :param url:
        :return:
        """
        img_path = os.path.join(save_dir, url.split('/')[-1])
        if os.path.exists(img_path):
            logger.warning(f'{url}图片路径已存在 {img_path}')
            return
        else:
            os.makedirs(save_dir, exist_ok=True)
        async with aiohttp.ClientSession() as session:
            try:
                resp = await session.get(url=url, headers=self.headers)
                if resp.status == 200:
                    try:
                        with open(img_path, mode=f'wb+') as f:
                            data = True
                            while data:
                                data = await resp.content.read(1024*1024)
                                f.write(data)
                                f.flush()
                    except Exception:
                        os.remove(img_path)
                else:
                    logger.error('图片请求失败')
            except Exception:
                logger.info(f'图片 {url} 等待下载失败{traceback.format_exc()}')

    async def main(self, user, pass_wod):
        """
        :return:
        """
        await self.login(user, pass_wod)
        tags = await self.get_all_tags()
        for url, tag_name in tags.items():
            if url.startswith('https://'):
                logger.info(f'{url} 忽略')
                continue
            sub_task_list = await self.download_tag(url, tag_name, page=10)
            logger.info(f'【{tag_name}】任务开始')
            await asyncio.wait(sub_task_list)


def clear_path(file_path):
    for root, dirs, files in os.walk(file_path):
        for file in files:
            filename = os.path.join(root, file)
            size = os.path.getsize(filename)
            if size < 300*1024:
                print("remove", filename)
                os.remove(filename)
        if not os.listdir(root):
            os.rmdir(root)


if __name__ == '__main__':
    tudaoji = TuDaoJi()
    clear_path(os.path.join(tudaoji.BASE_DIR, '图岛集'))
    asyncio.run(tudaoji.main(user='yuanzhong', pass_wod='123456789'))
    clear_path(os.path.join(tudaoji.BASE_DIR, '图岛集'))
