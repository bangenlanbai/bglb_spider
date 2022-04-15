# -*- coding:utf-8  -*-
# @Time     : 2022/4/15 19:48
# @Author   : BGLB
# @Software : PyCharm
import importlib
import traceback
from loguru import logger

SpiderConfig = {
    'spider_name': 'ssr1',
    'host_prefix': 'ssr1',
    'debug': False,

}


def main():
    """
        运行爬虫
    """
    host_prefix = SpiderConfig['host_prefix']
    module_name = '{}.spider'.format(SpiderConfig['host_prefix'])
    try:
        SPIDER_MODULE = importlib.import_module(module_name)
    except ModuleNotFoundError:
        logger.error('未找到模块【{}】{}'.format(module_name, traceback.format_exc()))
        return

    try:
        Spider = getattr(SPIDER_MODULE, f'{host_prefix.upper()}Spider')
        spider_init_config = SpiderConfig.copy()
        spider_init_config.pop('host_prefix')
        spider = Spider(**spider_init_config)
    except Exception:
        logger.error('爬虫模块初始化错误【{}】{}'.format(module_name, traceback.format_exc()))
        return

    try:
        spider.run()
    except Exception:
        logger.error(traceback.format_exc())


main()
