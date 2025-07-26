#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
曲阜师范大学招生办招生快讯监控模块
通过API接口获取招生快讯信息
"""

import requests
import json
import os
import time
from datetime import datetime
from qfnu_monitor.utils.feishu import feishu
from qfnu_monitor.utils.onebot import onebot_send_all
from qfnu_monitor.utils import logger


class QFNUZSBZSKXMonitor:
    """
    曲阜师范大学招生办招生快讯监控器
    通过POST API接口获取招生快讯数据
    """

    def __init__(self, data_dir="data"):
        """
        初始化监控器

        Args:
            data_dir (str): 数据存储目录
        """
        self.api_url = "https://zsb.qfnu.edu.cn/f/newsCenter/ajax_category_article_list"
        self.base_url = "https://zsb.qfnu.edu.cn"
        self.site_name = "曲师大招生办招生快讯"
        self.data_file_prefix = "zsb_zskx"

        # API请求参数
        self.category_id = "e8659322e16240d296178402510b34f2"  # 招生快讯分类ID
        self.page_size = 20  # 每次获取的文章数量

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
        self.max_notices = 50  # 最多保留的通知数量

    def get_api_data(self):
        """
        通过API获取招生快讯数据

        Returns:
            dict: API返回的JSON数据
        """
        # 生成时间戳
        timestamp = str(int(time.time() * 1000))

        # 请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua-platform": '"Windows"',
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "Csrf-Token": "T3IWIIT",
            "sec-ch-ua-mobile": "?0",
            "X-Requested-With": "XMLHttpRequest",
            "X-Requested-Time": timestamp,
            "Origin": "https://zsb.qfnu.edu.cn",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://zsb.qfnu.edu.cn/",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        # 请求数据
        data = {"categoryId": self.category_id, "pageSize": str(self.page_size)}

        # 添加时间戳参数到URL
        url_with_ts = f"{self.api_url}?ts={timestamp}"

        response = requests.post(url_with_ts, headers=headers, data=data, timeout=10)
        response.encoding = "utf-8"

        return response.json()

    def parse_api_data(self, api_data):
        """
        解析API返回的数据

        Args:
            api_data (dict): API返回的JSON数据

        Returns:
            list: 公告列表，每个公告包含 title、link、date、id、description 字段
        """
        notices = []

        try:
            if api_data.get("state") != 1:
                logger.error(f"API返回错误: {api_data.get('msg', '未知错误')}")
                return notices

            data = api_data.get("data", [])
            if not data:
                logger.warning("API返回的data为空")
                return notices

            # 获取第一个分类的内容列表
            content_list = data[0].get("contentList", [])

            for item in content_list:
                try:
                    # 提取基本信息
                    notice_id = item.get("id", "")
                    title = item.get("title", "").strip()

                    # 构建链接
                    url = item.get("url", "")
                    link = ""
                    if url:
                        if url.startswith("http"):
                            link = url
                        else:
                            link = self.base_url + url

                    # 处理外部链接
                    if item.get("isExternalLink", False):
                        external_url = item.get("externalLinkUrl", "")
                        if external_url:
                            link = self.base_url + external_url

                    # 转换发布时间
                    release_date = item.get("releaseDate", 0)
                    if release_date:
                        # 时间戳转换为日期字符串
                        date = datetime.fromtimestamp(release_date / 1000).strftime(
                            "%Y-%m-%d"
                        )
                    else:
                        date = ""

                    # 其他信息
                    description = item.get("description", "").strip()
                    publisher = item.get("publisher", "")
                    hits = item.get("hits", 0)
                    is_new = item.get("isNew", False)

                    # 过滤无效数据
                    if title and notice_id:
                        notices.append(
                            {
                                "id": notice_id,
                                "title": title,
                                "link": link,
                                "date": date,
                                "description": description,
                                "publisher": publisher,
                                "hits": hits,
                                "is_new": is_new,
                                "release_timestamp": release_date,
                            }
                        )

                except Exception as e:
                    logger.warning(f"解析单个招生快讯项时出错: {e}")
                    continue

        except Exception as e:
            logger.error(f"解析API数据时出错: {e}")

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
        查找新公告（基于ID）

        Args:
            current_notices (list): 当前抓取的公告
            saved_notices (list): 已保存的公告

        Returns:
            list: 新公告列表
        """
        if not saved_notices:
            return current_notices

        saved_ids = {notice["id"] for notice in saved_notices}
        return [notice for notice in current_notices if notice["id"] not in saved_ids]

    def push_to_feishu(self, new_notices):
        """
        推送新公告到飞书

        Args:
            new_notices (list): 新公告列表
        """
        if not new_notices:
            return

        title = f"📢 {self.site_name}有{len(new_notices)}条新公告"
        content = ""

        for i, notice in enumerate(new_notices, 1):
            content += f"【{i}】{notice['title']}\n"
            content += f"📅 发布时间：{notice['date']}\n"
            if notice.get("publisher"):
                content += f"👤 发布者：{notice['publisher']}\n"
            if notice.get("hits"):
                content += f"👁️ 浏览量：{notice['hits']}\n"
            if notice.get("is_new"):
                content += f"🆕 最新公告\n"
            if notice.get("description"):
                # 截取描述前100个字符
                desc = (
                    notice["description"][:100] + "..."
                    if len(notice["description"]) > 100
                    else notice["description"]
                )
                content += f"📝 简介：{desc}\n"
            content += f"🔗 链接：{notice['link']}\n\n"

        feishu(title, content)

    def push_to_onebot(self, new_notices):
        """
        通过OneBot发送新公告通知

        Args:
            new_notices (list): 新公告列表
        """
        if not new_notices:
            return

        message = f"📢 {self.site_name}有{len(new_notices)}条新公告\n\n"

        for i, notice in enumerate(new_notices, 1):
            message += f"【{i}】{notice['title']}\n"
            message += f"📅 发布时间：{notice['date']}\n"
            if notice.get("publisher"):
                message += f"👤 发布者：{notice['publisher']}\n"
            if notice.get("hits"):
                message += f"👁️ 浏览量：{notice['hits']}\n"
            if notice.get("is_new"):
                message += f"🆕 最新公告\n"
            if notice.get("description"):
                # 截取描述前80个字符
                desc = (
                    notice["description"][:80] + "..."
                    if len(notice["description"]) > 80
                    else notice["description"]
                )
                message += f"📝 简介：{desc}\n"
            message += f"🔗 {notice['link']}\n\n"

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
            api_data = self.get_api_data()
            current_notices = self.parse_api_data(api_data)

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


def main():
    """
    测试函数
    """
    print("曲阜师范大学招生办招生快讯监控器测试")
    print("=" * 50)

    try:
        monitor = QFNUZSBZSKXMonitor()
        print(f"创建监控器: {monitor.site_name}")
        print(f"API地址: {monitor.api_url}")
        print(f"数据文件: {monitor.data_file}")
        print(f"分类ID: {monitor.category_id}")

        # 测试API调用
        print("\n测试API调用...")
        api_data = monitor.get_api_data()
        print(f"API调用状态: {api_data.get('state', 'unknown')}")
        print(f"API返回消息: {api_data.get('msg', 'unknown')}")

        notices = monitor.parse_api_data(api_data)
        print(f"解析到{len(notices)}条招生快讯")

        if notices:
            print("\n最新几条公告:")
            for i, notice in enumerate(notices[:3], 1):
                print(f"{i}. {notice['title']}")
                print(f"   日期: {notice['date']}")
                print(f"   链接: {notice['link']}")
                print()

    except Exception as e:
        print(f"测试过程出错: {e}")


if __name__ == "__main__":
    main()
