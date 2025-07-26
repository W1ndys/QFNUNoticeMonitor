#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
网站监控模块模板
用于快速创建新的网站监控器

使用方法：
1. 复制此模板文件
2. 修改类名、URL、选择器等配置
3. 根据网站结构调整解析逻辑
4. 添加到主程序中
"""

import requests
import json
import os
from bs4 import BeautifulSoup
from qfnu_monitor.utils.feishu import feishu
from qfnu_monitor.utils.onebot import onebot_send_all
from qfnu_monitor.utils import logger


class WebsiteMonitorTemplate:
    """
    网站监控模板类

    需要修改的配置项：
    - __init__ 中的 URL 和文件名
    - get_notices 中的选择器和解析逻辑
    - push_to_* 方法中的消息标题
    """

    def __init__(self, data_dir="data"):
        """
        初始化监控器

        Args:
            data_dir (str): 数据存储目录
        """
        # ====== 需要修改的配置 ======
        self.url = "https://example.com/notices"  # 目标网站URL
        self.base_url = "https://example.com/"  # 网站基础URL
        self.site_name = "示例网站"  # 网站名称（用于日志和通知）
        self.data_file_prefix = "example"  # 数据文件前缀
        # ===========================

        self.data_dir = data_dir
        # 确保数据目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        # 确保归档目录存在
        self.archive_dir = os.path.join(self.data_dir, "archive")
        os.makedirs(self.archive_dir, exist_ok=True)

        # 数据文件路径
        self.data_file = os.path.join(
            self.data_dir, f"{self.data_file_prefix}_notices.json"
        )
        self.archive_file = os.path.join(
            self.archive_dir, f"{self.data_file_prefix}_notices_archive.json"
        )
        self.max_notices = 30  # 最多保留的通知数量，应大于网站公告数量

    def get_html(self):
        """
        获取网页HTML内容

        Returns:
            str: HTML内容
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(self.url, headers=headers, timeout=10)
        response.encoding = "utf-8"
        return response.text

    def parse_html(self, html):
        """
        解析HTML内容

        Args:
            html (str): HTML内容

        Returns:
            BeautifulSoup: 解析后的soup对象
        """
        soup = BeautifulSoup(html, "html.parser")
        return soup

    def get_notices(self, soup):
        """
        从解析后的HTML中提取公告信息

        ⚠️ 此方法需要根据目标网站的HTML结构进行修改

        Args:
            soup (BeautifulSoup): 解析后的soup对象

        Returns:
            list: 公告列表，每个公告包含 title、link、date 字段
        """
        notices = []

        # ====== 需要根据网站结构修改的选择器 ======
        # 示例：通用的公告列表选择器
        notice_list = soup.select("ul li")  # 修改为实际的选择器

        for item in notice_list:
            try:
                # 提取标题和链接
                title_tag = item.select_one("a")  # 修改为实际的选择器
                if not title_tag:
                    continue

                title = title_tag.get_text().strip()
                link = title_tag.get("href")

                # 处理相对链接
                if link and not link.startswith("http"):
                    link = self.base_url + link.lstrip("/")

                # 提取日期
                date_tag = item.select_one(".date")  # 修改为实际的选择器
                date = date_tag.get_text().strip() if date_tag else ""

                # 过滤无效数据
                if title and link:
                    notices.append({"title": title, "link": link, "date": date})

            except Exception as e:
                logger.warning(f"解析公告项时出错: {e}")
                continue
        # ========================================

        return notices

    def load_saved_notices(self):
        """
        加载已保存的公告

        Returns:
            list: 已保存的公告列表
        """
        if not os.path.exists(self.data_file) or os.path.getsize(self.data_file) == 0:
            logger.info(f"初始化{self.site_name}公告记录文件")
            return []

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取{self.site_name}公告记录失败: {e}")
            return []

    def load_archived_notices(self):
        """
        加载已存档的公告

        Returns:
            list: 已存档的公告列表
        """
        if (
            not os.path.exists(self.archive_file)
            or os.path.getsize(self.archive_file) == 0
        ):
            return []

        try:
            with open(self.archive_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取{self.site_name}公告存档记录失败: {e}")
            return []

    def save_notices(self, notices):
        """
        保存公告，只保存最新的max_notices条

        Args:
            notices (list): 公告列表
        """
        latest_notices = (
            notices[-self.max_notices :] if len(notices) > self.max_notices else notices
        )
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(latest_notices, f, ensure_ascii=False, indent=2)

        # 如果有超过max_notices的公告，归档多余的公告
        if len(notices) > self.max_notices:
            self.archive_notices(notices[: -self.max_notices])

    def archive_notices(self, notices_to_archive):
        """
        将公告存档

        Args:
            notices_to_archive (list): 需要存档的公告列表
        """
        if not notices_to_archive:
            return

        archived_notices = self.load_archived_notices()
        all_archived = archived_notices + notices_to_archive

        with open(self.archive_file, "w", encoding="utf-8") as f:
            json.dump(all_archived, f, ensure_ascii=False, indent=2)

        logger.info(f"已归档{len(notices_to_archive)}条公告到{self.archive_file}")

    def append_new_notices(self, new_notices):
        """
        将新公告添加到已保存的公告列表中

        Args:
            new_notices (list): 新公告列表
        """
        saved_notices = self.load_saved_notices()
        all_notices = saved_notices + new_notices
        self.save_notices(all_notices)

    def find_new_notices(self, current_notices, saved_notices):
        """
        查找新公告

        Args:
            current_notices (list): 当前抓取的公告
            saved_notices (list): 已保存的公告

        Returns:
            list: 新公告列表
        """
        if not saved_notices:
            return current_notices

        saved_titles = {notice["title"] for notice in saved_notices}
        return [
            notice for notice in current_notices if notice["title"] not in saved_titles
        ]

    def push_to_feishu(self, new_notices):
        """
        推送新公告到飞书

        Args:
            new_notices (list): 新公告列表
        """
        if not new_notices:
            return

        # ====== 可以修改消息格式 ======
        title = f"📢 {self.site_name}有{len(new_notices)}条新公告"
        content = ""

        for i, notice in enumerate(new_notices, 1):
            content += f"【{i}】{notice['title']}\n"
            content += f"📅 {notice['date']}\n"
            content += f"🔗 {notice['link']}\n\n"
        # ============================

        feishu(title, content)

    def push_to_onebot(self, new_notices):
        """
        通过OneBot发送新公告通知

        Args:
            new_notices (list): 新公告列表
        """
        if not new_notices:
            return

        # ====== 可以修改消息格式 ======
        message = f"📢 {self.site_name}有{len(new_notices)}条新公告\n\n"

        for i, notice in enumerate(new_notices, 1):
            message += f"【{i}】{notice['title']}\n"
            message += f"📅 {notice['date']}\n"
            message += f"🔗 {notice['link']}\n\n"
        # ============================

        # 发送到所有配置的群组
        result = onebot_send_all(message)

        if "error" in result:
            logger.error(f"OneBot发送失败: {result['error']}")
        else:
            logger.info(f"OneBot发送成功: {result.get('success_count', 0)} 个群组")

    def push_notifications(self, new_notices):
        """
        推送通知到所有配置的平台

        Args:
            new_notices (list): 新公告列表
        """
        if not new_notices:
            return

        # 推送到飞书
        try:
            self.push_to_feishu(new_notices)
        except Exception as e:
            logger.error(f"飞书推送失败: {e}")

        # 推送到OneBot群组
        try:
            self.push_to_onebot(new_notices)
        except Exception as e:
            logger.error(f"OneBot推送失败: {e}")

    def monitor(self):
        """
        执行监控逻辑
        """
        try:
            # 获取当前公告
            html = self.get_html()
            soup = self.parse_html(html)
            current_notices = self.get_notices(soup)

            if not current_notices:
                logger.warning(f"未从{self.site_name}获取到任何公告")
                return

            # 加载已保存的公告
            saved_notices = self.load_saved_notices()

            # 检查是否为初始化（第一次运行）
            is_first_run = not saved_notices

            # 查找新公告
            new_notices = self.find_new_notices(current_notices, saved_notices)

            if new_notices:
                if is_first_run:
                    # 第一次运行，只初始化数据，不推送消息
                    logger.info(
                        f"首次运行{self.site_name}监控器，初始化{len(new_notices)}条公告数据，不推送消息"
                    )
                    # 直接保存所有当前公告作为初始数据
                    self.save_notices(current_notices)
                else:
                    # 非首次运行，正常推送新公告
                    logger.info(f"从{self.site_name}发现{len(new_notices)}条新公告")
                    self.push_notifications(new_notices)
                    # 更新保存的公告，添加新公告而不覆盖已有公告
                    self.append_new_notices(new_notices)
            else:
                logger.info(f"{self.site_name}没有新公告")

        except Exception as e:
            logger.error(f"{self.site_name}监控过程发生错误: {e}")

    def run(self):
        """
        运行监控器
        """
        logger.info(f"开始监控{self.site_name}")
        self.monitor()


# =============================================
# 使用示例：创建具体的监控器
# =============================================


class ExampleUniversityMonitor(WebsiteMonitorTemplate):
    """
    示例大学官网监控器
    继承模板类并修改特定配置
    """

    def __init__(self, data_dir="data"):
        super().__init__(data_dir)

        # 重写配置
        self.url = "https://example-university.edu.cn/news"
        self.base_url = "https://example-university.edu.cn/"
        self.site_name = "示例大学官网"
        self.data_file_prefix = "example_university"

    def get_notices(self, soup):
        """
        重写公告解析方法以适应具体网站结构
        """
        notices = []

        # 根据实际网站结构修改选择器
        notice_list = soup.select("div.news-list .news-item")

        for item in notice_list:
            try:
                title_tag = item.select_one("h3 a")
                if not title_tag:
                    continue

                title = title_tag.get_text().strip()
                link = title_tag.get("href")

                if link and not link.startswith("http"):
                    link = self.base_url + link.lstrip("/")

                date_tag = item.select_one(".news-date")
                date = date_tag.get_text().strip() if date_tag else ""

                if title and link:
                    notices.append({"title": title, "link": link, "date": date})

            except Exception as e:
                logger.warning(f"解析{self.site_name}公告项时出错: {e}")
                continue

        return notices


# =============================================
# 测试代码
# =============================================


def main():
    """
    测试函数
    """
    print("网站监控模板测试")
    print("=" * 50)

    # 测试模板类（会失败，因为URL是示例）
    try:
        monitor = WebsiteMonitorTemplate()
        print(f"创建监控器: {monitor.site_name}")
        print(f"目标URL: {monitor.url}")
        print(f"数据文件: {monitor.data_file}")

        # 不实际运行，只演示配置
        print("\n配置检查完成！")
        print("使用步骤：")
        print("1. 复制此模板文件")
        print("2. 修改 __init__ 方法中的配置")
        print("3. 根据目标网站调整 get_notices 方法")
        print("4. 测试并添加到主程序")

    except Exception as e:
        print(f"测试过程出错（这是正常的）: {e}")


if __name__ == "__main__":
    main()
