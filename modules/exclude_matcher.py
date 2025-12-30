#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
排除匹配模块
"""

import pandas as pd
import os
from config import config

class ExcludeMatcher:
    """排除域名匹配器"""
    
    def __init__(self):
        """初始化"""
        self.exclude_file = config.EXCLUDE_FILE_PATH
        self.exclude_dict = {}  # 字典，存储域名->备注
        self._load_exclude_domains()
    
    def _load_exclude_domains(self):
        """加载排除域名和备注"""
        # 检查文件是否存在
        if not os.path.exists(self.exclude_file):
            print(f"⚠ 未找到排除文件: {self.exclude_file}")
            print("  请创建文件并填写排除域名 (A列:域名, B列:备注)")
            return {}
        
        try:
            # 读取Excel文件
            df = pd.read_excel(self.exclude_file, engine='openpyxl', header=None)
            
            if df.empty:
                print("⚠ 排除文件为空")
                return {}
            
            loaded_count = 0
            for index, row in df.iterrows():
                # 第一列 (A列): 域名
                if len(df.columns) >= 1 and pd.notna(row.iloc[0]):
                    domain = str(row.iloc[0]).strip()
                    domain = self._remove_protocol(domain)
                    
                    if domain:
                        # 第二列 (B列): 备注 (如果存在)
                        remark = ""
                        if len(df.columns) >= 2 and pd.notna(row.iloc[1]):
                            remark = str(row.iloc[1]).strip()
                        
                        # 添加到字典
                        if domain not in self.exclude_dict:
                            self.exclude_dict[domain] = remark
                            loaded_count += 1
                        else:
                            print(f"  ⚠ 重复域名已跳过: {domain}")
            
            # 显示加载信息
            if loaded_count > 0:
                print(f"✓ 已加载 {loaded_count} 条排除记录")
                # 显示前几条作为示例
                items = list(self.exclude_dict.items())
                for i, (domain, remark) in enumerate(items[:3]):
                    remark_display = f" - {remark}" if remark else ""
                    print(f"  {i+1}. {domain}{remark_display}")
                if loaded_count > 3:
                    print(f"  ... 共 {loaded_count} 条")
                            
        except Exception as e:
            print(f"❌ 读取排除文件失败: {e}")
        
        return self.exclude_dict
    
    @staticmethod
    def _remove_protocol(url):
        """去除协议头"""
        if not url:
            return ""
        url = str(url)
        if url.startswith("http://"):
            return url[7:].rstrip('/')
        elif url.startswith("https://"):
            return url[8:].rstrip('/')
        return url.rstrip('/')
    
    def get_exclude_info(self, host):
        """
        检查主机是否在排除列表中
        返回: (是否排除, 备注)
        """
        if not host or not self.exclude_dict:
            return False, ""
        
        clean_host = self._remove_protocol(host)
        
        # 1. 检查完整域名
        if clean_host in self.exclude_dict:
            return True, self.exclude_dict[clean_host]
        
        # 2. 检查不带端口的域名
        if ":" in clean_host:
            host_without_port = clean_host.split(":")[0]
            if host_without_port in self.exclude_dict:
                return True, self.exclude_dict[host_without_port]
        
        return False, ""
    
    def is_excluded(self, host):
        """检查是否排除"""
        excluded, _ = self.get_exclude_info(host)
        return excluded
    
    @property
    def exclude_domains(self):
        """获取排除域名列表"""
        return list(self.exclude_dict.keys())
    
    def get_exclude_list(self):
        """获取带备注的排除列表"""
        return list(self.exclude_dict.items())