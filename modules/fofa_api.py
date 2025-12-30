#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FOFA API模块
"""

import base64
import requests
from config import config

class FofaAPI:
    """FOFA API"""
    
    def __init__(self):
        """初始化FOFA API"""
        self.email = config.FOFA_EMAIL
        self.key = config.FOFA_KEY
    
    def search(self, query, fields=None, size=None):
        """
        执行FOFA查询
        """
        # Base64编码
        qbase64 = base64.b64encode(query.encode('utf-8')).decode('utf-8')
        
        # 参数
        fields = fields or config.DEFAULT_FIELDS
        size = size or config.DEFAULT_PAGE_SIZE
        
        # 构造URL
        url = f'{config.FOFA_API_URL}?email={self.email}&key={self.key}&qbase64={qbase64}&size={size}&fields={fields}'
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {e}")
        except Exception as e:
            raise Exception(f"查询失败: {e}")