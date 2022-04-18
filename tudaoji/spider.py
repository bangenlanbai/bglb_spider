# -*- coding:utf-8  -*-
# @Time     : 2022/4/18 18:51
# @Author   : BGLB
# @Software : PyCharm
import os
import traceback

from lxml import etree

import requests
from loguru import logger


class TuDaoJi():
    """
        TuDaoJi
    """
    session = requests.session()
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
    BASR_DIR = os.path.dirname(os.path.abspath(__file__))

    def login(self, username, password):
        """
            登录
        :return:
        """
        url = "{}/?action=save".format(self.root_url)

        payload = f'way=login&username={username}&password={password}'

        response = self.session.post(url, headers=self.headers, data=payload)
        logger.info(response.json())

    def logout(self):
        """

        :return:
        """
        path = '/u/?action=out'
        resp = self.session.get(f'{self.root_url}{path}', headers=self.headers, allow_redirects=False)
        logger.info(resp.text)

    def get_all_tags(self, ):
        """
            tags
        :return:
        """
        url = f'{self.root_url}/s/?id=193'
        self.headers.update({'referer': 'https://www.tujidao.com/s/?id=151'})
        # logger.info(dict(self.session.cookies))
        # self.headers.update({'cookie': self.session.cookies})
        response = self.session.get(url, headers=self.headers, allow_redirects=False)
        html = response.text
        eroot = etree.HTML(html)
        a_list = eroot.xpath('//*[@id="caidian"]//a[not (@target="_blank")]')
        tags_list = {
            item.xpath('./@href')[0]: item.xpath('./text()')[0] for item in a_list
        }
        return tags_list

    def download(self):
        """
        :return:
        """
        try:
            tags_list = self.get_all_tags()

            for tag_path, tage_name in tags_list.items():
                if tag_path.startswith('https://'):
                    logger.info(f'{tag_path} 忽略')
                    continue
                url = f'{self.root_url}{tag_path}'
                resp = self.session.get(url, headers=self.headers, allow_redirects=False)
                eroot = etree.HTML(resp.text)
                li_list = eroot.xpath('//div[@class="hezi"]//li')
                # li biaoti & shuliang & id
                for li_item in li_list:
                    li_id = li_item.xpath('./@id')[0]
                    li_count = int(str(li_item.xpath('.//span[@class="shuliang"]//text()')[0]).replace('P', ''))
                    li_title = li_item.xpath('.//p[@class="biaoti"]//text()')[0]
                    self.download_img(li_id, li_title, li_count,  tage_name)
        except Exception:
            logger.info(traceback.format_exc())

    def download_img(self, pic_id, pic_title, img_count: int, tag):
        """
                下载一个 图集
        :return:
        """

        img_host = 'https://tjg.gzhuibei.com'

        logger.info(f'图集标签: 【{tag}】; 图集名称: 【{pic_title}】; 共有【{img_count}张;】 ')
        img_save_dir = os.path.join(self.BASR_DIR, tag, pic_title)
        os.makedirs(img_save_dir, exist_ok=True)
        for index in range(img_count):
            img_url = f'{img_host}/a/1/{pic_id}/{index+1}.jpg'
            logger.info(f'{img_url}下载中...')

            resp = requests.get(img_url, headers=self.headers)
            if resp.status_code == 200:
                with open(os.path.join(img_save_dir, f'{index}.jpg'), mode=f'wb+') as f:
                    for chunk in resp.iter_content():
                        f.write(chunk)
                        f.flush()
            else:
                logger.error('图片请求失败')
        self.logout()

    def download_one_img(self, url: str, save_dir):
        """

        :param url:
        :return:
        """
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            with open(os.path.join(save_dir, url.split('/')[-1]), mode=f'wb+') as f:
                for chunk in resp.iter_content():
                    f.write(chunk)
                    f.flush()
        else:
            logger.error('图片请求失败')


if __name__ == '__main__':
    tudaoji = TuDaoJi()

    tudaoji.login(username='yuanzhong', password='123456789')

    tudaoji.download()
