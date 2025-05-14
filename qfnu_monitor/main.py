#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
曲阜师范大学教务处公告监控主程序
"""

import time
import argparse
import os
from qfnu_monitor.core.qfnu_jwc_gg import QFNUJWCGGMonitor
from qfnu_monitor.core.qfnu_jwc_tz import QFNUJWCTZMonitor
from qfnu_monitor.utils import logger


def parse_arguments():
    parser = argparse.ArgumentParser(description="曲阜师范大学教务处公告监控程序")
    parser.add_argument(
        "--interval", type=int, default=3600, help="监控间隔时间(秒), 默认3600秒"
    )
    parser.add_argument("--data-dir", type=str, default="data", help="数据存储目录")
    parser.add_argument("--once", action="store_true", help="仅运行一次, 不循环监控")
    return parser.parse_args()


def main():
    args = parse_arguments()

    # 确保数据目录存在
    os.makedirs(args.data_dir, exist_ok=True)

    qfnu_jwc_gg_monitor = QFNUJWCGGMonitor(data_dir=args.data_dir)
    qfnu_jwc_tz_monitor = QFNUJWCTZMonitor(data_dir=args.data_dir)
    if args.once:
        logger.info(f"单次运行模式")
        qfnu_jwc_gg_monitor.run()
        qfnu_jwc_tz_monitor.run()
    else:
        logger.info(f"循环监控模式, 间隔: {args.interval}秒")
        while True:
            qfnu_jwc_gg_monitor.run()
            qfnu_jwc_tz_monitor.run()
            logger.info(f"等待{args.interval}秒后重新检查...")
            time.sleep(args.interval)


if __name__ == "__main__":
    main()
