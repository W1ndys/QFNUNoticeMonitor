import os
from qfnu_monitor.core.qfnu_jwc_tz import QFNUJWCTZMonitor
from qfnu_monitor.core.qfnu_jwc_gg import QFNUJWCGGMonitor
import requests
from bs4 import BeautifulSoup
import json


class QFNUJWCAllDataCollector:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

        # 初始化爬虫
        self.tz_monitor = QFNUJWCTZMonitor(data_dir)
        self.gg_monitor = QFNUJWCGGMonitor(data_dir)

        # 设置数据文件路径
        self.all_tz_file = os.path.join(data_dir, "jwc_tz_notices.json")
        self.all_gg_file = os.path.join(data_dir, "jwc_gg_notices.json")

    def get_page_html(self, url):
        try:
            response = requests.get(url)
            response.encoding = "utf-8"
            return response.text
        except Exception as e:
            print(f"获取页面失败: {e}")
            return None

    def collect_all_notices(self, notice_type, total_pages):
        """
        收集所有通知/公告
        notice_type: 'tz' 或 'gg'
        total_pages: 页面总数
        """
        all_notices = []
        base_url = (
            self.tz_monitor.base_url
            if notice_type == "tz"
            else self.gg_monitor.base_url
        )
        monitor = self.tz_monitor if notice_type == "tz" else self.gg_monitor

        for page in range(1, total_pages + 1):
            url = f"{base_url}{notice_type}_j_/{page}.htm#/"
            print(f"正在获取{notice_type}第{page}/{total_pages}页")

            html = self.get_page_html(url)
            if not html:
                continue

            soup = BeautifulSoup(html, "html.parser")
            notices = monitor.get_notices(soup)
            all_notices.extend(notices)

            # 防止请求过于频繁
            # time.sleep(1)

        return all_notices

    def save_all_notices(self, notices, file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(notices, f, ensure_ascii=False, indent=2)

    def run(self):
        # 获取所有通知 (132页)
        print("开始获取所有通知...")
        all_tz_notices = self.collect_all_notices("tz", 132)
        self.save_all_notices(all_tz_notices, self.all_tz_file)
        print(f"已保存{len(all_tz_notices)}条通知到 {self.all_tz_file}")

        # 获取所有公告 (13页)
        print("开始获取所有公告...")
        all_gg_notices = self.collect_all_notices("gg", 13)
        self.save_all_notices(all_gg_notices, self.all_gg_file)
        print(f"已保存{len(all_gg_notices)}条公告到 {self.all_gg_file}")


if __name__ == "__main__":
    collector = QFNUJWCAllDataCollector()
    collector.run()
