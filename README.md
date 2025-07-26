# 曲阜师范大学监控

一个用于监控曲阜师范大学各网站公告的爬虫脚本，并通过飞书机器人推送新公告。同时具备存档功能，定期存档曲阜师范大学各网站公告通知

## 已监控网站

- [曲阜师范大学教务处公告](https://jwc.qfnu.edu.cn/gg_j_.htm)
- [曲阜师范大学教务处通知](https://jwc.qfnu.edu.cn/tz_j_.htm)
- [曲阜师范大学图书馆公告](https://lib.qfnu.edu.cn/ggxw/gg.htm)
- [曲阜师范大学学工处通知公告](https://xg.qfnu.edu.cn/tzgg.htm)
- [曲阜师范大学本科招生网招生快讯](https://zsb.qfnu.edu.cn)

## 功能

- 定时爬取曲阜师范大学公告
- 自动检测新公告并通过飞书机器人推送消息
- 支持自定义监控间隔时间
- 支持单次运行模式

## 目录结构

```
QFNUNoticeMonitor/
├── qfnu_monitor/             # 主包目录
│   ├── __init__.py
│   ├── core/                 # 核心功能模块
│   │   ├── __init__.py
│   │   └── qfnu_jwc.py       # 公告监控实现
│   ├── utils/                # 工具模块
│   │   ├── __init__.py
│   │   ├── logger.py         # 日志工具
│   │   └── feishu.py         # 飞书机器人消息推送
│   ├── data/                 # 数据存储目录
│   └── main.py               # 主程序逻辑
├── run.py                    # 入口文件
├── .gitignore
├── LICENSE
└── README.md
```

## 环境变量配置

在项目根目录创建 `.env` 文件，并配置以下环境变量：

```
FEISHU_BOT_URL=你的飞书机器人webhook地址
FEISHU_BOT_SECRET=你的飞书机器人安全设置密钥
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
python run.py
```

### 参数说明

- `--interval`: 监控间隔时间(秒)，默认 3600 秒
- `--data-dir`: 数据存储目录，默认为 'data'
- `--once`: 仅运行一次，不循环监控

### 示例

```bash
# 每小时检查一次（默认）
python run.py

# 每10分钟检查一次
python run.py --interval 600

# 仅运行一次
python run.py --once

# 指定数据目录
python run.py --data-dir /path/to/data
```
