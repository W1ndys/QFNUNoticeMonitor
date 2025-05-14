import requests
import json
import os
from bs4 import BeautifulSoup
import time
from ..utils.feishu import feishu
from ..utils import logger


class QFNUJWCGGMonitor:
    def __init__(self, data_dir="../data"):
        self.url = "https://jwc.qfnu.edu.cn/gg_j_.htm"
        self.base_url = "https://jwc.qfnu.edu.cn/"
        self.data_dir = data_dir
        # 确保数据目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        self.data_file = os.path.join(self.data_dir, "jwc_gg_notices.json")

    def get_html(self):
        response = requests.get(self.url)
        response.encoding = "utf-8"
        return response.text

    def parse_html(self, html):
        soup = BeautifulSoup(html, "html.parser")
        return soup

    def get_notices(self, soup):
        notices = []
        notice_list = soup.select("ul.n_listxx1 li")

        for item in notice_list:
            title_tag = item.select_one("h2 a")
            if title_tag:
                title = title_tag.get_text().strip()
                link = title_tag.get("href")
                if link and not link.startswith("http"):
                    link = self.base_url + link
                date_tag = item.select_one("h2 span.time")
                date = date_tag.get_text().strip() if date_tag else ""
                notices.append({"title": title, "link": link, "date": date})
        return notices

    def load_saved_notices(self):
        if not os.path.exists(self.data_file) or os.path.getsize(self.data_file) == 0:
            logger.info("初始化曲阜师范大学教务处公告记录文件")
            return []

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取曲阜师范大学教务处公告记录失败: {e}")
            return []

    def save_notices(self, notices):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(notices, f, ensure_ascii=False, indent=2)

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

        title = f"📢 曲阜师范大学教务处有{len(new_notices)}条新公告"
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
                # 更新保存的公告
                self.save_notices(current_notices)
            else:
                logger.info("没有新公告")

        except Exception as e:
            logger.error(f"监控过程发生错误: {e}")

    def run(self):
        logger.info("开始监控曲阜师范大学教务处公告")
        self.monitor()
