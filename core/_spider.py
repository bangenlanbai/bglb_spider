# -*- coding:utf-8  -*-
# @Time     : 2022/4/15 18:06
# @Author   : BGLB
# @Software : PyCharm
import abc
import json
import os
import typing
from abc import ABC

import requests
from loguru import logger
from requests import Response

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
