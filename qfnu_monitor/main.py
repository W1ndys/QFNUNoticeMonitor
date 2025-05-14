#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
曲阜师范大学教务处公告监控主程序
"""

import os
from qfnu_monitor.utils import logger
from qfnu_monitor.core.qfnu_jwc_gg import QFNUJWCGGMonitor
from qfnu_monitor.core.qfnu_jwc_tz import QFNUJWCTZMonitor


def main():
    # 确保数据目录存在
    data_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
    )
    logger.info(f"数据存储目录：{data_dir}")
    os.makedirs(data_dir, exist_ok=True)

    qfnu_jwc_gg_monitor = QFNUJWCGGMonitor(data_dir=data_dir)
    qfnu_jwc_gg_monitor.run()

    qfnu_jwc_tz_monitor = QFNUJWCTZMonitor(data_dir=data_dir)
    qfnu_jwc_tz_monitor.run()


if __name__ == "__main__":
    main()
