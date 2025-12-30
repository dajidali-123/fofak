# fofak简介
-安全运营中做资产监控只能通过扫描ip、域名的方式来监控。通过其他方式例如title监控资产，只能依赖fofa资产测绘平台来测绘。但是平台没有监控功能所以fofak弥补了这个监控功能。

# 监控原理
-使用fofa接口获取搜索结果
-config目录下提前写好已经排除过的host记录
-运行脚本后自动生成已确认过的资产信息

# 实际效果
<img width="1503" height="1017" alt="图片" src="https://github.com/user-attachments/assets/90da6744-e8a4-4967-847b-27dc4b3e21bf" />

# 运行截图
<img width="1572" height="843" alt="图片" src="https://github.com/user-attachments/assets/515402af-2a12-454c-800b-38578f03d042" />

# 使用方法

usage: fofak.py [-h] --query QUERY [--output OUTPUT] [--exclude]

███████╗ ██████╗ ███████╗ █████╗ ██╗  ██╗
██╔════╝██╔═══██╗██╔════╝██╔══██╗██║ ██╔╝
█████╗  ██║   ██║█████╗  ███████║█████╔╝
██╔══╝  ██║   ██║██╔══╝  ██╔══██║██╔═██╗
██║     ╚██████╔╝██║     ██║  ██║██║  ██╗
╚═╝      ╚═════╝ ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝
═══════════════════════════════════════════
                v1.0


options:
  -h, --help       show this help message and exit
  --query QUERY    FOFA查询语法
  --output OUTPUT  输出文件 (默认: results.xlsx)
  --exclude        启用排除模式

使用示例:
  python main.py --query 'app="Apache-Tomcat"'
  python main.py --query 'title="登录"' --exclude
  python main.py --query 'port="80"' --exclude --output "http_results.xlsx"

排除文件格式:
  在 config/exclude_domain.xlsx 中:
  A列: 排除的域名 (如: example.com, 192.168.1.1:8080)
  B列: 备注说明 (如: 内部系统, 测试环境, 误报设备)

# 后续
-后续完善自动监控和针对特殊开放状态的资产二次探测
