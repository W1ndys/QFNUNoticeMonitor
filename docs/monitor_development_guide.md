# 监控模块开发指南

本指南帮助开发者快速创建新的网站监控模块，实现自动化公告监控和消息推送。

## 📁 项目结构

```
qfnu_monitor/
├── core/                    # 监控模块核心
│   ├── qfnu_jwc_gg.py      # 教务处公告监控
│   ├── qfnu_jwc_tz.py      # 教务处通知监控
│   ├── qfnu_library_gg.py  # 图书馆公告监控
│   └── qfnu_xg_tzgg.py     # 学工处通知监控
├── utils/                   # 工具模块
│   ├── feishu.py           # 飞书推送
│   ├── onebot.py           # OneBot推送
│   └── logger.py           # 日志管理
└── main.py                 # 主程序入口

examples/
├── monitor_template.py     # 监控模块模板
└── onebot_example.py       # OneBot使用示例

docs/
├── onebot_usage.md         # OneBot使用说明
└── monitor_development_guide.md  # 本开发指南
```

## 🚀 快速开始

### 1. 使用模板创建新监控器

复制 `examples/monitor_template.py` 并按以下步骤修改：

```python
# 1. 修改类名
class YourWebsiteMonitor(WebsiteMonitorTemplate):
    
    def __init__(self, data_dir="data"):
        super().__init__(data_dir)
        
        # 2. 修改配置
        self.url = "https://your-website.com/notices"
        self.base_url = "https://your-website.com/"
        self.site_name = "您的网站名称"
        self.data_file_prefix = "your_website"

    # 3. 重写解析方法
    def get_notices(self, soup):
        # 根据网站结构实现解析逻辑
        pass
```

### 2. 添加到主程序

在 `qfnu_monitor/main.py` 中注册新监控器：

```python
from qfnu_monitor.core.your_website import YourWebsiteMonitor

def main():
    # ... 现有代码 ...
    
    # 添加新监控器
    your_monitor = YourWebsiteMonitor(data_dir=data_dir)
    your_monitor.run()
```

## 🔧 详细开发步骤

### 第一步：分析目标网站

1. **查看网站结构**
   ```bash
   curl -s "https://target-website.com/notices" | head -100
   ```

2. **使用浏览器开发者工具**
   - 打开目标网站
   - 按F12打开开发者工具
   - 查看公告列表的HTML结构
   - 记录选择器路径

3. **识别关键信息**
   - 公告标题选择器
   - 链接地址选择器
   - 发布日期选择器
   - 分页机制（如果有）

### 第二步：实现解析逻辑

```python
def get_notices(self, soup):
    notices = []
    
    # 根据网站结构修改选择器
    notice_list = soup.select("ul.notice-list li")  # 示例选择器
    
    for item in notice_list:
        try:
            # 提取标题
            title_tag = item.select_one("h3 a")
            if not title_tag:
                continue
            title = title_tag.get_text().strip()
            
            # 提取链接
            link = title_tag.get("href")
            if link and not link.startswith("http"):
                link = self.base_url + link.lstrip("/")
            
            # 提取日期
            date_tag = item.select_one(".publish-date")
            date = date_tag.get_text().strip() if date_tag else ""
            
            # 过滤和验证
            if title and link:
                notices.append({
                    "title": title,
                    "link": link,
                    "date": date
                })
                
        except Exception as e:
            logger.warning(f"解析公告项时出错: {e}")
            continue
    
    return notices
```

### 第三步：自定义消息格式（可选）

```python
def push_to_feishu(self, new_notices):
    if not new_notices:
        return

    # 自定义消息标题和格式
    title = f"🎓 {self.site_name} - {len(new_notices)}条新公告"
    content = f"📅 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    for i, notice in enumerate(new_notices, 1):
        content += f"📌 【{i}】{notice['title']}\n"
        content += f"🕒 {notice['date']}\n"
        content += f"🔗 {notice['link']}\n"
        content += "─" * 40 + "\n"

    feishu(title, content)
```

### 第四步：测试和调试

1. **单元测试**
   ```python
   def test_monitor():
       monitor = YourWebsiteMonitor()
       
       # 测试HTML获取
       html = monitor.get_html()
       assert html, "无法获取HTML内容"
       
       # 测试解析
       soup = monitor.parse_html(html)
       notices = monitor.get_notices(soup)
       assert notices, "无法解析公告"
       
       print(f"成功解析到{len(notices)}条公告")
       for notice in notices[:3]:  # 显示前3条
           print(f"- {notice['title']}")
   ```

2. **日志调试**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   
   monitor = YourWebsiteMonitor()
   monitor.run()
   ```

## 📋 常见问题和解决方案

### 1. 网站反爬虫措施

**问题**: 请求被拒绝或返回空内容
**解决方案**:
```python
def get_html(self):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    # 添加延迟
    import time
    time.sleep(1)
    
    response = requests.get(self.url, headers=headers, timeout=15)
    response.encoding = "utf-8"
    return response.text
```

### 2. 动态内容加载

**问题**: 公告通过JavaScript动态加载
**解决方案**:
```python
# 方案1: 寻找API接口
def get_notices_from_api(self):
    api_url = "https://website.com/api/notices"
    response = requests.get(api_url)
    data = response.json()
    return data['notices']

# 方案2: 使用selenium（需要额外依赖）
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_html_with_selenium(self):
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    driver.get(self.url)
    time.sleep(3)  # 等待内容加载
    html = driver.page_source
    driver.quit()
    
    return html
```

### 3. 字符编码问题

**问题**: 中文乱码
**解决方案**:
```python
def get_html(self):
    response = requests.get(self.url)
    
    # 方法1: 自动检测编码
    response.encoding = response.apparent_encoding
    
    # 方法2: 手动指定编码
    # response.encoding = "gbk"  # 或 "utf-8"
    
    return response.text
```

### 4. 日期格式标准化

**问题**: 不同网站日期格式不统一
**解决方案**:
```python
import re
from datetime import datetime

def normalize_date(self, date_str):
    """标准化日期格式"""
    if not date_str:
        return ""
    
    # 常见格式匹配
    patterns = [
        (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d'),
        (r'(\d{4})年(\d{1,2})月(\d{1,2})日', '%Y年%m月%d日'),
        (r'(\d{1,2})/(\d{1,2})/(\d{4})', '%m/%d/%Y'),
    ]
    
    for pattern, date_format in patterns:
        if re.match(pattern, date_str):
            try:
                # 转换为标准格式
                dt = datetime.strptime(date_str, date_format)
                return dt.strftime('%Y-%m-%d')
            except:
                pass
    
    return date_str  # 无法解析时返回原始字符串
```

## 🛠️ 高级功能

### 1. 支持分页

```python
def get_all_notices(self, max_pages=3):
    """获取多页公告"""
    all_notices = []
    
    for page in range(1, max_pages + 1):
        url = f"{self.url}?page={page}"
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            notices = self.get_notices(soup)
            
            if not notices:  # 没有更多公告
                break
                
            all_notices.extend(notices)
            time.sleep(1)  # 避免请求过快
            
        except Exception as e:
            logger.error(f"获取第{page}页时出错: {e}")
            break
    
    return all_notices
```

### 2. 自定义过滤规则

```python
def filter_notices(self, notices):
    """过滤公告"""
    filtered = []
    
    # 关键词过滤
    keywords = ["重要", "紧急", "通知", "公告"]
    exclude_keywords = ["测试", "草稿"]
    
    for notice in notices:
        title = notice['title'].lower()
        
        # 排除特定关键词
        if any(word in title for word in exclude_keywords):
            continue
            
        # 包含重要关键词或所有公告
        if any(word in title for word in keywords) or not keywords:
            filtered.append(notice)
    
    return filtered
```

### 3. 监控频率控制

```python
import time
from datetime import datetime, timedelta

class ScheduledMonitor(WebsiteMonitorTemplate):
    def __init__(self, data_dir="data", interval_minutes=30):
        super().__init__(data_dir)
        self.interval = timedelta(minutes=interval_minutes)
        self.last_check = None
    
    def should_run(self):
        """判断是否应该执行监控"""
        if not self.last_check:
            return True
        
        return datetime.now() - self.last_check >= self.interval
    
    def run(self):
        if self.should_run():
            super().run()
            self.last_check = datetime.now()
        else:
            logger.info(f"{self.site_name}: 距离上次检查不足{self.interval}，跳过")
```

## 📝 最佳实践

### 1. 错误处理
- 总是使用 try-except 包装网络请求
- 记录详细的错误日志
- 实现优雅降级（部分失败不影响整体）

### 2. 性能优化
- 设置合理的请求超时时间
- 添加请求间隔避免被封IP
- 缓存不变的数据（如网站结构）

### 3. 数据一致性
- 使用标题作为唯一标识符
- 定期清理过期数据
- 备份重要通知到归档文件

### 4. 可维护性
- 使用清晰的变量命名
- 添加详细的注释和文档
- 模块化代码便于测试

## 🔄 完整示例

以下是一个完整的监控器实现示例：

```python
# qfnu_monitor/core/example_university.py

import requests
import json
import os
import re
from bs4 import BeautifulSoup
from datetime import datetime
from qfnu_monitor.utils.feishu import feishu
from qfnu_monitor.utils.onebot import onebot_send_all
from qfnu_monitor.utils import logger


class ExampleUniversityMonitor:
    """示例大学监控器 - 完整实现"""
    
    def __init__(self, data_dir="data"):
        self.url = "https://example-university.edu.cn/notices"
        self.base_url = "https://example-university.edu.cn/"
        self.site_name = "示例大学"
        self.data_dir = data_dir
        
        # 确保目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "archive"), exist_ok=True)
        
        self.data_file = os.path.join(self.data_dir, "example_university_notices.json")
        self.archive_file = os.path.join(self.data_dir, "archive", "example_university_notices_archive.json")
        self.max_notices = 30

    def get_html(self):
        """获取网页内容"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(self.url, headers=headers, timeout=15)
            response.encoding = "utf-8"
            return response.text
        except Exception as e:
            logger.error(f"获取{self.site_name}页面失败: {e}")
            raise

    def parse_html(self, html):
        """解析HTML"""
        return BeautifulSoup(html, "html.parser")

    def get_notices(self, soup):
        """解析公告列表"""
        notices = []
        
        # 根据实际网站结构修改选择器
        notice_list = soup.select("div.notice-list .notice-item")
        
        for item in notice_list:
            try:
                # 提取标题和链接
                title_tag = item.select_one("h3 a")
                if not title_tag:
                    continue
                
                title = title_tag.get_text().strip()
                link = title_tag.get("href")
                
                # 处理相对链接
                if link and not link.startswith("http"):
                    link = self.base_url + link.lstrip("/")
                
                # 提取日期
                date_tag = item.select_one(".notice-date")
                date = self.normalize_date(date_tag.get_text().strip() if date_tag else "")
                
                # 验证数据
                if title and link:
                    notices.append({
                        "title": title,
                        "link": link,
                        "date": date,
                        "created_at": datetime.now().isoformat()
                    })
                    
            except Exception as e:
                logger.warning(f"解析{self.site_name}公告项时出错: {e}")
                continue
        
        return notices

    def normalize_date(self, date_str):
        """标准化日期格式"""
        if not date_str:
            return ""
        
        # 移除多余空白字符
        date_str = re.sub(r'\s+', ' ', date_str.strip())
        
        # 常见日期格式处理
        patterns = [
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', lambda m: f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"),
            (r'(\d{4})年(\d{1,2})月(\d{1,2})日', lambda m: f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"),
        ]
        
        for pattern, formatter in patterns:
            match = re.search(pattern, date_str)
            if match:
                return formatter(match)
        
        return date_str

    def load_saved_notices(self):
        """加载已保存的公告"""
        if not os.path.exists(self.data_file) or os.path.getsize(self.data_file) == 0:
            logger.info(f"初始化{self.site_name}公告记录文件")
            return []

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取{self.site_name}公告记录失败: {e}")
            return []

    def save_notices(self, notices):
        """保存公告"""
        # 保留最新的公告
        latest_notices = notices[-self.max_notices:] if len(notices) > self.max_notices else notices
        
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(latest_notices, f, ensure_ascii=False, indent=2)

        # 归档超出的公告
        if len(notices) > self.max_notices:
            self.archive_notices(notices[:-self.max_notices])

    def archive_notices(self, notices_to_archive):
        """归档公告"""
        if not notices_to_archive:
            return

        archived_notices = []
        if os.path.exists(self.archive_file):
            try:
                with open(self.archive_file, "r", encoding="utf-8") as f:
                    archived_notices = json.load(f)
            except:
                pass

        all_archived = archived_notices + notices_to_archive

        with open(self.archive_file, "w", encoding="utf-8") as f:
            json.dump(all_archived, f, ensure_ascii=False, indent=2)

        logger.info(f"已归档{len(notices_to_archive)}条{self.site_name}公告")

    def find_new_notices(self, current_notices, saved_notices):
        """查找新公告"""
        if not saved_notices:
            return current_notices

        saved_titles = {notice["title"] for notice in saved_notices}
        new_notices = [notice for notice in current_notices if notice["title"] not in saved_titles]
        
        return new_notices

    def push_notifications(self, new_notices):
        """推送通知"""
        if not new_notices:
            return

        # 推送到飞书
        try:
            title = f"📢 {self.site_name}有{len(new_notices)}条新公告"
            content = f"🕒 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            for i, notice in enumerate(new_notices, 1):
                content += f"📌 【{i}】{notice['title']}\n"
                content += f"📅 {notice['date']}\n"
                content += f"🔗 {notice['link']}\n\n"

            feishu(title, content)
            logger.info(f"{self.site_name}飞书推送成功")
            
        except Exception as e:
            logger.error(f"{self.site_name}飞书推送失败: {e}")

        # 推送到OneBot
        try:
            message = f"📢 {self.site_name}有{len(new_notices)}条新公告\n\n"

            for i, notice in enumerate(new_notices, 1):
                message += f"【{i}】{notice['title']}\n"
                message += f"📅 {notice['date']}\n"
                message += f"🔗 {notice['link']}\n\n"

            result = onebot_send_all(message)
            if "error" not in result:
                logger.info(f"{self.site_name}OneBot推送成功: {result.get('success_count', 0)} 个群组")
            else:
                logger.error(f"{self.site_name}OneBot推送失败: {result['error']}")
                
        except Exception as e:
            logger.error(f"{self.site_name}OneBot推送失败: {e}")

    def monitor(self):
        """执行监控"""
        try:
            # 获取当前公告
            html = self.get_html()
            soup = self.parse_html(html)
            current_notices = self.get_notices(soup)

            if not current_notices:
                logger.warning(f"未从{self.site_name}获取到任何公告")
                return

            logger.info(f"从{self.site_name}获取到{len(current_notices)}条公告")

            # 加载已保存的公告
            saved_notices = self.load_saved_notices()

            # 查找新公告
            new_notices = self.find_new_notices(current_notices, saved_notices)

            if new_notices:
                logger.info(f"从{self.site_name}发现{len(new_notices)}条新公告")
                self.push_notifications(new_notices)
                
                # 保存更新后的公告
                all_notices = saved_notices + new_notices
                self.save_notices(all_notices)
            else:
                logger.info(f"{self.site_name}没有新公告")

        except Exception as e:
            logger.error(f"{self.site_name}监控过程发生错误: {e}")

    def run(self):
        """运行监控器"""
        logger.info(f"开始监控{self.site_name}")
        self.monitor()
```

## 📞 技术支持

如果在开发过程中遇到问题：

1. **查看日志**: 检查详细的错误信息
2. **调试模式**: 使用 `logging.DEBUG` 级别
3. **测试网站**: 确认目标网站可访问
4. **参考现有**: 查看已实现的监控器代码

开发愉快！🎉