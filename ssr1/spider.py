# -*- coding:utf-8  -*-
# @Time     : 2022/4/15 17:32
# @Author   : BGLB
# @Software : PyCharm
import os
import traceback

from core import Spider
from lxml import etree

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


class SSR1Spider(Spider):
    """
        ssr1.scrape.center
    """
    host = 'https://ssr1.scrape.center/'

    def check_login(self) -> bool:
        """

        :return:
        """
        return True

    def login(self, **kwargs) -> bool:
        """

        :return:
        """

        return True

    def spider(self, *args, **kwargs):
        """

        :return:
        """
        try:
            page_index = kwargs.pop('page_index')

            headers = """
                    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
                    Accept-Encoding: gzip, deflate, br
                    Accept-Language: zh-CN,zh;q=0.9
                    Cache-Control: no-cache
                    Connection: keep-alive
                    Cookie: UM_distinctid=1802c8d77aac6c-0f9abeb34f69e2-6b3e555b-1fa400-1802c8d77ab1121
                    Host: ssr1.scrape.center
                    Pragma: no-cache
                    Referer: https://ssr1.scrape.center/page/{}
                    sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"
                    sec-ch-ua-mobile: ?0
                    sec-ch-ua-platform: "Windows"
                    Sec-Fetch-Dest: document
                    Sec-Fetch-Mode: navigate
                    Sec-Fetch-Site: same-origin
                    Sec-Fetch-User: ?1
                    Upgrade-Insecure-Requests: 1
                    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36
            """.format(100//page_index)
            page_url = f'{self.host}detail/{page_index}'
            self.log.info(f'请求第{page_index}页')
            html = self.session.get(page_url, headers=self.headers_format(headers)).text
            return html
        except Exception:
            self.log.error('请求 url : {} 出错: \n {}', traceback.format_exc())
            return None

    def save_data(self, **kwargs):
        """

        :return:
        """
        content = kwargs.pop('content')
        save_result = self.save_to_file('ssr1', self.data_dir, 'json', content=content)
        return save_result

    def parse_data(self, content) -> list or dict:
        """

        :param content:
        :return:
        """
        try:
            result = self.parse_html(content)
        except Exception:
            result = None
            self.log.error('解析内容出错: \n {}', traceback.format_exc())
        return result

    def run(self):
        """
            主函数
        :return:
        """
        result = []
        raw_html = []
        for page_index in range(1, 101):
            html = self.spider(page_index=page_index)
            if html:
                raw_html.append(html)
        self.session.close()

        for index, item in enumerate(raw_html):
            self.log.info(f'解析第{index+1}页')
            data = self.parse_data(item)
            result.append(data)
        self.log.info(f'总数量： {len(result)}')

        if self.save_data(content=result):
            self.log.info(f'保存数量{len(result)}')

    def parse_html(self, html):
        """
            解析 html
        :return:
        """
        eroot = etree.HTML(html)
        movie_info = eroot.xpath('//div[contains(@class, "item")]')[0]

        img_url = movie_info.xpath('.//img[@class="cover"]/@src')
        title = movie_info.xpath('.//h2//text()')
        categories = movie_info.xpath('.//div[@class="categories"]//span/text()')
        score = movie_info.xpath('.//p[contains(@class, "score")]/text()')
        extra_info = movie_info.xpath('.//div[contains(@class, "info")]//span/text()')

        introductions = eroot.xpath('.//div[@class="drama"]/p//text()')
        # 取 img 兄弟节点的 第节点 <div><img /><p></p></div>
        actor_div = eroot.xpath('//img[@class="image"]')
        try:
            director_info = actor_div.pop(0)
            director = ["".join(director_info.xpath('..//text()')).replace('\n', '').strip(' '),
                        director_info.xpath('./@src')[0]]
        except Exception:
            director = []
        actor_info = [("".join(item.xpath('..//text()')).replace('\n', '').strip(' '),
                       item.xpath('./@src')[0]) for _, item in enumerate(actor_div)]
        # actor_info = [(姓名, url)]
        stills_div = eroot.xpath('//div[@class="el-image"]//img/@src')

        country = extra_info[0] if extra_info else '',
        duration = ''
        release_time = ''
        if len(extra_info) >= 3:
            duration = extra_info[2].split()[0] if extra_info else '',

        if len(extra_info) >= 4:
            release_time = extra_info[3].split()[0] if extra_info else '',

        movie_data = {
            'img_url': img_url[0] if img_url else '',
            'movie_name': title[0] if title else '',
            'categories': categories if categories else [],
            'score': int(score[0].strip(' ')[-1]) if score else '',
            'country': country,
            'duration': duration,
            'release_time': release_time,
            'introductions': introductions[0].replace('\n', '').strip(' ') if introductions else '',
            'director': director,
            'actor_info': actor_info if actor_info else [],
            'stills_div': stills_div if stills_div else []
        }
        return movie_data


if __name__ == '__main__':
    ssr1_spider = SSR1Spider('ssr1', debug=True)
    ssr1_spider.run()
