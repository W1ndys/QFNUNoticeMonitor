#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
曲阜师范大学教务处公告监控 - 主程序入口
"""

import os
import datetime
from qfnu_monitor.main import main
from qfnu_monitor.utils.logger import logger


def clean_old_logs():
    """
    清理1天前的日志文件
    """
    try:
        # 获取项目根目录
        project_root = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(project_root, "logs")

        # 如果日志目录不存在，则无需清理
        if not os.path.exists(logs_dir):
            return

        # 计算1天前的日期
        current_time = datetime.datetime.now()
        one_day_ago = current_time - datetime.timedelta(days=1)

        # 遍历日志目录中的所有文件
        deleted_count = 0
        for filename in os.listdir(logs_dir):
            if not filename.startswith("monitor_") or not filename.endswith(".log"):
                continue

            file_path = os.path.join(logs_dir, filename)
            file_creation_time = datetime.datetime.fromtimestamp(
                os.path.getctime(file_path)
            )

            # 如果文件创建时间早于1天前，则删除
            if file_creation_time < one_day_ago:
                os.remove(file_path)
                deleted_count += 1

        if deleted_count > 0:
            logger.info(f"已清理 {deleted_count} 个1天前的日志文件")
        else:
            logger.info("没有清理到1天前的日志文件")

    except Exception as e:
        logger.error(f"清理日志文件时出错: {str(e)}")


if __name__ == "__main__":
    clean_old_logs()
    main()
