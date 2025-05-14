import requests
import json
import os
from bs4 import BeautifulSoup
from qfnu_monitor.utils.feishu import feishu
from qfnu_monitor.utils import logger


class QFNUXGTZGGMonitor:
    def __init__(self, data_dir="data"):
        self.url = "https://xg.qfnu.edu.cn/tzgg1.htm#/"
        self.base_url = "https://xg.qfnu.edu.cn/"
        self.data_dir = data_dir
        # 确保数据目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        # 确保归档目录存在
        self.archive_dir = os.path.join(self.data_dir, "archive")
        os.makedirs(self.archive_dir, exist_ok=True)
        self.data_file = os.path.join(self.data_dir, "xg_tzgg_notices.json")
        self.archive_file = os.path.join(
            self.archive_dir, "xg_tzgg_notices_archive.json"
        )
        self.max_notices = 30  # 最多保留的通知数量，应大于网站公告数量

    def get_html(self):
        response = requests.get(self.url)
        response.encoding = "utf-8"
        return response.text

    def parse_html(self, html):
        soup = BeautifulSoup(html, "html.parser")
        return soup

    def get_notices(self, soup):
        notices = []
        notice_list = soup.select("div.list ul li")

        for item in notice_list:
            title_tag = item.select_one("a")
            if title_tag:
                title = title_tag.get_text().strip()
                link = title_tag.get("href")
                if link and not link.startswith("http"):
                    link = self.base_url + link
                # 日期文本直接在 li 标签内，a 标签后面
                date = item.contents[-1].strip() if len(item.contents) > 1 else ""
                notices.append({"title": title, "link": link, "date": date})
        return notices

    def load_saved_notices(self):
        if not os.path.exists(self.data_file) or os.path.getsize(self.data_file) == 0:
            logger.info("初始化曲阜师范大学学工处通知公告记录文件")
            return []

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取曲阜师范大学学工处通知公告记录失败: {e}")
            return []

    def load_archived_notices(self):
        """加载已存档的公告"""
        if (
            not os.path.exists(self.archive_file)
            or os.path.getsize(self.archive_file) == 0
        ):
            return []

        try:
            with open(self.archive_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取曲阜师范大学学工处通知公告存档记录失败: {e}")
            return []

    def save_notices(self, notices):
        """只保存最新的max_notices条公告"""
        latest_notices = (
            notices[-self.max_notices :] if len(notices) > self.max_notices else notices
        )
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(latest_notices, f, ensure_ascii=False, indent=2)

        # 如果有超过max_notices的公告，归档多余的公告
        if len(notices) > self.max_notices:
            self.archive_notices(notices[: -self.max_notices])

    def archive_notices(self, notices_to_archive):
        """将公告存档"""
        if not notices_to_archive:
            return

        archived_notices = self.load_archived_notices()
        all_archived = archived_notices + notices_to_archive

        with open(self.archive_file, "w", encoding="utf-8") as f:
            json.dump(all_archived, f, ensure_ascii=False, indent=2)

        logger.info(f"已归档{len(notices_to_archive)}条公告到{self.archive_file}")

    def append_new_notices(self, new_notices):
        """将新公告添加到已保存的公告列表中"""
        saved_notices = self.load_saved_notices()
        all_notices = saved_notices + new_notices
        self.save_notices(all_notices)

    def find_new_notices(self, current_notices, saved_notices):
        if not saved_notices:
            return current_notices

        saved_titles = {notice["title"] for notice in saved_notices}
        return [
            notice for notice in current_notices if notice["title"] not in saved_titles
        ]

    def push_to_feishu(self, new_notices):
        if not new_notices:
            return

        title = f"📢 曲阜师范大学学工处有{len(new_notices)}条新通知"
        content = ""

        for i, notice in enumerate(new_notices, 1):
            content += f"【{i}】{notice['title']}\n"
            content += f"📅 {notice['date']}\n"
            content += f"🔗 {notice['link']}\n\n"

        feishu(title, content)

    def monitor(self):
        try:
            # 获取当前公告
            html = self.get_html()
            soup = self.parse_html(html)
            current_notices = self.get_notices(soup)

            if not current_notices:
                logger.warning("未获取到任何公告")
                return

            # 加载已保存的公告
            saved_notices = self.load_saved_notices()

            # 查找新公告
            new_notices = self.find_new_notices(current_notices, saved_notices)

            if new_notices:
                logger.info(f"发现{len(new_notices)}条新公告")
                self.push_to_feishu(new_notices)
                # 更新保存的公告，添加新公告而不覆盖已有公告
                self.append_new_notices(new_notices)
            else:
                logger.info("没有新公告")

        except Exception as e:
            logger.error(f"监控过程发生错误: {e}")

    def run(self):
        logger.info("开始监控曲阜师范大学学工处通知公告")
        self.monitor()
