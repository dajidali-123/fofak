#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
"""

import os

# FOFA API配置 - 请修改这里
FOFA_EMAIL = ''
FOFA_KEY = ''  # 替换为你的 API 密钥

# 排除配置文件路径
EXCLUDE_FILE_PATH = os.path.join(os.path.dirname(__file__), 'exclude_domain.xlsx')

# 输出配置
DEFAULT_OUTPUT_FILE = 'results.xlsx'

# 查询配置
DEFAULT_PAGE_SIZE = 10000
DEFAULT_FIELDS = 'host,ip,port,title,domain,country,protocol'

# FOFA API URL
FOFA_API_URL = 'https://fofa.info/api/v1/search/all'