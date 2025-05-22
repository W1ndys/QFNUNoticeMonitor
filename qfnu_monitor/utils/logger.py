import logging
import os
import datetime
import glob
import time


def cleanup_old_logs(days=7):
    """
    清理指定天数之前的日志文件

    Args:
        days: 保留的天数，默认7天
    """
    try:
        # 确定项目根目录
        project_root = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir
            )
        )

        # 日志目录
        logs_dir = os.path.join(project_root, "logs")
        if not os.path.exists(logs_dir):
            return

        # 当前时间戳
        current_time = time.time()
        # 计算days天前的时间戳
        cutoff_time = current_time - (days * 24 * 60 * 60)

        # 获取所有日志文件
        log_files = glob.glob(os.path.join(logs_dir, "monitor_*.log"))

        # 遍历日志文件
        deleted_count = 0
        for log_file in log_files:
            file_mod_time = os.path.getmtime(log_file)
            # 如果文件修改时间早于截止时间，则删除
            if file_mod_time < cutoff_time:
                os.remove(log_file)
                deleted_count += 1

        # 使用基本的logging模块记录，因为此时可能还没有创建logger对象
        if deleted_count > 0:
            logging.info(f"已清理 {deleted_count} 个超过 {days} 天的日志文件")
    except Exception as e:
        logging.error(f"清理日志文件时出错: {str(e)}")


def setup_logger(name=None, log_file=None):
    """
    设置日志记录器

    Args:
        name: 日志记录器名称，如果为None则获取root logger
        log_file: 日志文件路径

    Returns:
        配置好的logger对象
    """
    # 清理旧日志文件
    cleanup_old_logs()

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 确定项目根目录
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir)
    )

    # 默认日志文件路径
    if log_file is None:
        logs_dir = os.path.join(project_root, "logs")

        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(logs_dir, f"monitor_{current_time}.log")

    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 创建文件处理器，使用UTF-8编码
    file_handler = logging.FileHandler(log_file, encoding="utf-8")

    # 创建控制台处理器
    console_handler = logging.StreamHandler()

    # 创建格式化器
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # 设置处理器的格式化器
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 清除现有处理器
    logger.handlers = []

    # 添加处理器到记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# 创建默认logger
logger = setup_logger()


def info(msg):
    """记录信息日志"""
    logger.info(msg)


def warning(msg):
    """记录警告日志"""
    logger.warning(msg)


def error(msg):
    """记录错误日志"""
    logger.error(msg)


def debug(msg):
    """记录调试日志"""
    logger.debug(msg)
