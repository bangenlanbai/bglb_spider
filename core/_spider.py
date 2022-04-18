# -*- coding:utf-8  -*-
# @Time     : 2022/4/15 18:06
# @Author   : BGLB
# @Software : PyCharm
import abc
import json
import os
import re
import traceback
import typing
from abc import ABC

import requests
from loguru import logger
from requests import Response

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# import json
# import os
# import time
# from abc import abstractmethod, ABC
# from json import JSONDecodeError
#
#
# class SpiderBase(object, ABC):
#     """
#     爬取数据基类
#     """
#     host = ""
#
#     def __init__(self, crawler_config: dict):
#         super().__init__()
#         self.init_timestamp = str(int(time.time()))
#
#         self.cookie_txt_path = r"{}\{}_{}_cookies.txt".format(self.cookie_dir, self.login_id, crawler_config[
#             'CrawlerType'])
#
#     def __init_data_dir(self):
#         """
#             初始化一些数据目录, 方便之后文件上传
#         :return:
#         """
#         # 数据保存根目录
#         self.data_dir = os.path.join(self.base_dir, self.login_id, self.init_timestamp)
#         self.cookie_dir = os.path.join(self.base_dir, 'cookie')
#         self.temp_dir = os.path.join(self.data_dir, 'temp')
#         self.json_dir = os.path.join(self.data_dir, 'json')
#         self.img_dir = os.path.join(self.data_dir, 'img')
#         self.db_dir = os.path.join(self.data_dir, 'db')
#         self.zip_dir = os.path.join(self.data_dir, 'zip')
#         self.log.info('数据存储路径: 【{}】'.format(self.data_dir))
#         self.zip_file_path = os.path.join(self.data_dir, "{}_{}.zip".format(self.crawler_config.get('TaskId'),
#                                                                             self.init_timestamp))
#         self.log_file_path = self.log.log_path('info')
#         os.makedirs(self.temp_dir, exist_ok=True)
#         os.makedirs(self.json_dir, exist_ok=True)
#         os.makedirs(self.img_dir, exist_ok=True)
#         os.makedirs(self.db_dir, exist_ok=True)
#         os.makedirs(self.cookie_dir, exist_ok=True)
#
#     def make_dir_to_spider_data_dir(self, dir_name: str or list):
#         """
#             在self.data_dir创建自定义目录 并返回绝对路径
#         :param dir_name: str or list
#         :return:
#         """
#
#         if isinstance(dir_name, list) and dir_name:
#             target_dirs = []
#             for _dir in dir_name:
#                 target_dir = os.path.join(self.data_dir, _dir)
#                 os.makedirs(target_dir)
#                 target_dirs.append(target_dir)
#             return target_dirs
#
#         else:
#             target_dir = os.path.join(self.data_dir, dir_name)
#             os.makedirs(target_dir)
#             self.log.info('创建目录： {}'.format(target_dir))
#             return target_dir
#
#     @staticmethod
#     def save_to_file(filename, filedir, file_ext, content: any, addition: bool=False):
#         """
#             保存数据为文件
#         :param filename:
#         :param filedir:
#         :param file_ext:
#         :param content:
#         :return:
#         """
#         filepath = os.path.join(filedir, "{}.{}".format(filename, file_ext))
#
#         if isinstance(content, list) or isinstance(content, dict):
#             content = json.dumps(content, ensure_ascii=False)
#
#         if file_ext == 'img' or file_ext == 'db':
#             with open(filepath, mode='wb+', encoding='utf-8') as f:
#                 for chunk in content.iter_content():
#                     f.write(chunk)
#             return filepath
#
#         with open(filepath, mode='w+', encoding='utf-8') as f:
#             f.write(content)
#
#         return filepath
#
#     @staticmethod
#     def exec_javascript(scripts: str, func_name: str, runtime_dir: str = None, *args):
#         """
#
#         :param scripts: js脚本字符串
#         :param func_name: 需要调用的js 函数名
#         :param runtime_dir: 运行js的目录
#         :param args: 执行js函数需要的参数
#         :return:
#         """
#         ct = execjs.compile(scripts, cwd=runtime_dir)
#         return ct.call(func_name, *args)
#
#     @abstractmethod
#     def load_cookie(self) -> list or dict:
#         """
#             加载保存下来的历史cookie
#         :return: cookies
#         """
#         try:
#             with open(self.cookie_txt_path, 'r') as f:
#                 return json.load(f, encoding='utf8')
#         except IOError:
#             self.log.warn('不存在历史cookie')
#             return []
#         except JSONDecodeError:
#             self.log.warn('cookies 格式不规范 无法加载 可能进行了手动更改')
#             return []
#
#     @abstractmethod
#     def save_cookie(self, cookies: dict or list):
#         """
#             保存当前cookies
#         :return:
#         """
#         with open(self.cookie_txt_path, 'w+', encoding='utf8') as f:
#             json.dump(cookies, f)
#         self.log.info('保存cookies成功')
#
#     @abstractmethod
#     def close_some_server(self):
#         """
#             关闭一些服务
#         :return:
#         """
#         self.cmd.__del__()
#         self.log.info('所有服务已结束完毕, 爬虫任务结束')
#
#     def check_login(self) -> bool:
#         """
#             检查历史cookie是否生效
#         :return:
#         """
#         raise NotImplementedError
#
#     def login(self) -> bool:
#         """
#             登录方法 调用前 必须重写
#         :return:
#         """
#         raise NotImplementedError
#
#     def run(self):
#         """
#             调用前 必须重写
#         :return:
#         """
#         raise NotImplementedError


class SpiderBase(metaclass=abc.ABCMeta):
    """
        SpiderBase
    """

    def __init__(self):
        super().__init__()
        self._host = None

    @property
    def host(self):
        return self._host

    @abc.abstractmethod
    def check_login(self) -> bool:
        """
            检查历史cookie是否生效
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def login(self, login_id, password, **kwargs) -> bool:
        """
            登录方法 调用前 必须重写
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def spider(self, *args, **kwargs):
        """

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def run(self):
        """
            调用前 必须重写
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def parse_data(self, content):
        """
            解析数据
        :return:
        """

        raise NotImplementedError

    @abc.abstractmethod
    def save_data(self, content) -> bool:
        """
            保存数据
        :return:
        """
        raise NotImplementedError


class FileUtil(object):
    """
        FilesUtils
    """
    __ContentT = typing.TypeVar('__ContentT', str, list, Response, dict)

    def save_to_file(self, filename: str, filedir: str, file_ext: str, content: __ContentT, addition: bool = False):
        """
            保存数据为文件
        :param filename: 文件名称 不带 .
        :param filedir: 文件 dir
        :param file_ext: 文件 后缀
        :param content: 文件 内容
        :param addition: 写入模式
        :return:
        """

        mode = 'a' if addition else 'w'

        filepath = os.path.join(filedir, "{}.{}".format(filename, file_ext))
        if not os.path.exists(filedir):
            os.makedirs(filedir, exist_ok=True)

        if isinstance(content, list) or isinstance(content, dict):
            content = json.dumps(content, ensure_ascii=False)

        if isinstance(content, Response):

            with open(filepath, mode=f'{mode}b+') as f:
                for chunk in content.iter_content():
                    f.write(chunk)
                    f.flush()
        else:
            with open(filepath, mode=f'{mode}+', encoding='utf-8') as f:
                # 以 w 或 w+ 模式打开文件时，程序会立即清空文件的内容。
                f.write(content)
                f.flush()

        return filepath

    def read_file(self, filepath):
        """
            
        :param filepath:
        :return:
        """
        pass


class TimeUtil(object):
    """
        TimeUtil
    """

    def timestamp13(self) -> str:
        return ''


class SpiderUtil(FileUtil, TimeUtil):
    """
        SpiderUtil
    """

    @staticmethod
    def exec_javascripts():
        """
            执行 js
        :return:
        """

        pass

    @staticmethod
    def headers_format(header_str: str) -> dict:
        """

        :param header_str:
        :return:
        """
        header_dict = {}
        for line in header_str.split("\n"):
            if line and line.split('\n') and line.split('\n')[0] != "":
                line = line.strip(' ')
                if line:
                    line_split = line.split(": ", 1)
                    header_dict[line_split[0]] = line_split[1]
        return header_dict


class Spider(SpiderBase, SpiderUtil, ABC):
    """
        SpiderBase
    """
    __log_base_config = {
        'backtrace': True,
        'diagnose': True,
        'enqueue': True,
        'catch': True
    }

    def __init__(self, spider_name: str, debug=True):
        """ init """
        main_logger_level = "DEBUG" if debug else "INFO"

        logger.add(os.path.join(BASE_DIR, 'log', f'{spider_name}.log'), **self.__log_base_config,
                   level=main_logger_level)
        logger.add(os.path.join(BASE_DIR, 'log', f'error.log'), **self.__log_base_config,
                   level='ERROR')
        self.spider_name = spider_name
        self.log = logger
        self.session = requests.Session()
        self.__init_data_dir()
        super().__init__()

    def __init_data_dir(self):
        """
            创建数据目录
        :return:
        """
        self.data_dir = os.path.join(BASE_DIR, 'spider_data', self.spider_name)
        self.cookies_dir = os.path.join(BASE_DIR, 'cookies', self.spider_name)
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.cookies_dir, exist_ok=True)


if __name__ == '__main__':
    # class TestSpider(Spider):
    #     host = 'www.sss.com'
    #
    #     def check_login(self) -> bool:
    #         """
    #             检查历史cookie是否生效
    #         :return:
    #         """
    #         self.log.info('未实现')
    #         return True
    #
    #     def login(self) -> bool:
    #         """
    #             登录方法 调用前 必须重写
    #         :return:
    #         """
    #         self.log.warning('未实现')
    #         return True
    #
    #     def run(self):
    #         """
    #             调用前 必须重写
    #         :return:
    #         """
    #         self.check_login()
    #         self.login()
    #         self.parse_data()
    #
    #         self.log.error('未实现')
    #         self.log.debug('debug')
    #         return True
    #
    #     def parse_data(self):
    #         """
    #             解析数据
    #         :return:
    #         """
    #
    #         try:
    #             raise Exception('错误我')
    #         except Exception:
    #             self.log.error(traceback.format_exc())
    #
    #     def save_data(self):
    #         """
    #             保存数据
    #         :return:
    #         """
    #         return True
    # spider = TestSpider('test_spider')
    # spider.run()

    spider_util = SpiderUtil()
    headers = """Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
                    Accept-Encoding: gzip, deflate, br
                    Accept-Language: zh-CN,zh;q=0.9
                    Cache-Control: no-cache
                    Connection: keep-alive
                    Cookie: UM_distinctid=1802c8d77aac6c-0f9abeb34f69e2-6b3e555b-1fa400-1802c8d77ab1121
                    Host: ssr1.scrape.center
                    Pragma: no-cache
                    Referer: https://ssr1.scrape.center/page/10
                    sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"
                    sec-ch-ua-mobile: ?0
                    sec-ch-ua-platform: "Windows"
                    Sec-Fetch-Dest: document
                    Sec-Fetch-Mode: navigate
                    Sec-Fetch-Site: same-origin
                    Sec-Fetch-User: ?1
                    Upgrade-Insecure-Requests: 1
                    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36
            """
    spider_util.headers_format(headers)
