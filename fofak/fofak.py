#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序
"""

import argparse
import pandas as pd
import os
import sys

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from config import config
from modules.fofa_api import FofaAPI
from modules.exclude_matcher import ExcludeMatcher

def main():
    parser = argparse.ArgumentParser(
        description="""
███████╗ ██████╗ ███████╗ █████╗ ██╗  ██╗
██╔════╝██╔═══██╗██╔════╝██╔══██╗██║ ██╔╝
█████╗  ██║   ██║█████╗  ███████║█████╔╝ 
██╔══╝  ██║   ██║██╔══╝  ██╔══██║██╔═██╗ 
██║     ╚██████╔╝██║     ██║  ██║██║  ██╗
╚═╝      ╚═════╝ ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝
═══════════════════════════════════════════
                v1.0
    """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py --query 'app="Apache-Tomcat"'
  python main.py --query 'title="登录"' --exclude
  python main.py --query 'port="80"' --exclude --output "http_results.xlsx"
  
排除文件格式:
  在 config/exclude_domain.xlsx 中:
  A列: 排除的域名 (如: example.com, 192.168.1.1:8080)
  B列: 备注说明 (如: 内部系统, 测试环境, 误报设备)
        """
    )
    
    parser.add_argument('--query', required=True, help='FOFA查询语法')
    parser.add_argument('--output', default=config.DEFAULT_OUTPUT_FILE, 
                       help=f'输出文件 (默认: {config.DEFAULT_OUTPUT_FILE})')
    parser.add_argument('--exclude', action='store_true', help='启用排除模式')
    
    args = parser.parse_args()
    
    # 检查配置
    if not config.FOFA_EMAIL or not config.FOFA_KEY:
        print("错误: 请先配置FOFA邮箱和API密钥")
        print("编辑 config/config.py 文件")
        sys.exit(1)
    
    print("""
███████╗ ██████╗ ███████╗ █████╗ ██╗  ██╗
██╔════╝██╔═══██╗██╔════╝██╔══██╗██║ ██╔╝
█████╗  ██║   ██║█████╗  ███████║█████╔╝ 
██╔══╝  ██║   ██║██╔══╝  ██╔══██║██╔═██╗ 
██║     ╚██████╔╝██║     ██║  ██║██║  ██╗
╚═╝      ╚═════╝ ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝
═══════════════════════════════════════════
                v1.0
    """)

    
    # 初始化API
    try:
        fofa_api = FofaAPI()
    except Exception as e:
        print(f"API初始化失败: {e}")
        sys.exit(1)
    
    # 初始化排除匹配器
    exclude_matcher = None
    if args.exclude:
        try:
            exclude_matcher = ExcludeMatcher()
            # 不再需要单独调用 show_summary，因为初始化时已经显示了
                    
        except Exception as e:
            print(f"排除模式初始化失败: {e}")
            args.exclude = False
    
    # 执行查询
    print(f"\n查询语句: {args.query}")
    print("-" * 50)
    
    try:
        results = fofa_api.search(args.query)
        
        # 检查错误
        if results.get('error'):
            error_msg = results.get('errmsg', '未知错误')
            print(f"查询失败: {error_msg}")
            sys.exit(1)
        
        if not results.get('results'):
            print("未查询到结果")
            sys.exit(0)
        
        total_results = len(results['results'])
        print(f"查询成功，获取到 {total_results} 条记录")
        
        # 处理数据
        data = []
        excluded_count = 0
        
        for item in results['results']:
            host = str(item[0]) if item[0] else ""
            ip = str(item[1]) if item[1] else ""
            port = str(item[2]) if item[2] else ""
            title = str(item[3]) if item[3] else ""
            domain = str(item[4]) if item[4] else ""
            country = str(item[5]) if item[5] else ""
            protocol = str(item[6]) if item[6] else ""
            
            # 添加协议前缀
            if protocol == "http" and not host.startswith("http://"):
                host = f"http://{host}"
            elif protocol == "https" and not host.startswith("https://"):
                host = f"https://{host}"
            
            # 检查排除和获取备注
            excluded = "否"
            remark = ""
            if args.exclude and exclude_matcher:
                excluded, remark = exclude_matcher.get_exclude_info(host)
                if excluded:
                    excluded = "是"
                    excluded_count += 1
                else:
                    excluded = "否"
            
            data.append([host, ip, port, title, domain, country, protocol, excluded, remark])
        
        # 创建DataFrame
        df = pd.DataFrame(data, columns=[
            'host', 'ip', 'port', 'title', 'domain', 
            'country', 'protocol', '是否排除', '备注'
        ])
        
        # 按排除状态排序
        df = df.sort_values(by=['是否排除', 'host'], ascending=[False, True])
        
        # 保存到Excel
        output_file = args.output
        if not output_file.endswith('.xlsx'):
            output_file += '.xlsx'
        
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        # 保存Excel文件
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 主表 - 包含备注列
            df.to_excel(writer, sheet_name='查询结果', index=False)
            
            # 如果启用了排除，创建更多工作表
            if args.exclude and exclude_matcher:
                # 有效记录（未排除的）
                valid_df = df[df['是否排除'] == '否']
                if not valid_df.empty:
                    valid_df.to_excel(writer, sheet_name='有效记录', index=False)
                
                # 排除记录（已排除的）
                excluded_df = df[df['是否排除'] == '是']
                if not excluded_df.empty:
                    excluded_df.to_excel(writer, sheet_name='已排除记录', index=False)
                
                # 排除列表（带备注）
                exclude_data = []
                for domain, remark in exclude_matcher.get_exclude_list():
                    exclude_data.append([domain, remark])
                
                exclude_list_df = pd.DataFrame(exclude_data, columns=['排除域名', '备注'])
                exclude_list_df.to_excel(writer, sheet_name='排除列表', index=False)
        
        print(f"\n结果已保存到: {output_file}")
        
        # 统计信息
        total_count = len(df)
        print(f"\n统计信息:")
        print(f"  总记录数: {total_count}")
        
        if args.exclude:
            print(f"  已排除: {excluded_count}")
            print(f"  有效记录: {total_count - excluded_count}")
            
            # 显示备注统计
            if excluded_count > 0:
                remarks_df = df[df['是否排除'] == '是']
                remarks_count = len(remarks_df[remarks_df['备注'] != ''])
                print(f"  有备注的排除记录: {remarks_count}")
        
        if 'size' in results:
            print(f"  总计数量(FOFA): {results['size']}")
        
        print("\n" + "=" * 50)
        print("完成")
        print("=" * 50)
        
    except Exception as e:
        print(f"执行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()