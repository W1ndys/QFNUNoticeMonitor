#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OneBot组件使用示例
演示如何使用OneBot组件向QQ群发送消息
"""

import sys
import os

# 添加父目录到Python路径，以便导入qfnu_monitor模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qfnu_monitor.utils.onebot import OneBotSender, onebot_send_all, onebot_send_groups


def example_class_usage():
    """使用类的方式发送消息示例"""
    print("=== 使用OneBotSender类发送消息 ===")

    try:
        # 创建OneBot发送器实例
        bot = OneBotSender()

        # 示例1: 向单个群组发送消息
        print("1. 向单个群组发送消息:")
        result = bot.send_group_message("123456789", "这是一条测试消息 🤖")
        print(f"发送结果: {result}")

        # 示例2: 向所有配置的群组发送消息
        print("\n2. 向所有配置的群组发送消息:")
        message = """📢 系统通知
        
这是一条通过OneBot发送的测试消息。

✅ 消息发送成功
📅 时间: 2024-01-01 12:00:00
🔗 详情: https://example.com"""

        result = bot.send_to_all_groups(message)
        print(f"批量发送结果: {result}")

        # 示例3: 向指定的群组列表发送消息
        print("\n3. 向指定群组列表发送消息:")
        target_groups = ["123456789", "987654321"]
        result = bot.send_to_specific_groups(
            target_groups, "这是向指定群组发送的消息 📨"
        )
        print(f"指定群组发送结果: {result}")

    except Exception as e:
        print(f"发送失败: {e}")


def example_function_usage():
    """使用便捷函数发送消息示例"""
    print("\n=== 使用便捷函数发送消息 ===")

    # 示例1: 使用便捷函数向所有群组发送消息
    print("1. 使用onebot_send_all函数:")
    message = "这是通过便捷函数发送的消息 🚀"
    result = onebot_send_all(message)
    print(f"发送结果: {result}")

    # 示例2: 使用便捷函数向指定群组发送消息
    print("\n2. 使用onebot_send_groups函数:")
    target_groups = ["123456789"]
    message = "这是向指定群组发送的消息 🎯"
    result = onebot_send_groups(target_groups, message)
    print(f"发送结果: {result}")


def example_error_handling():
    """错误处理示例"""
    print("\n=== 错误处理示例 ===")

    # 模拟配置错误的情况
    original_url = os.environ.get("ONEBOT_HTTP_URL")
    os.environ["ONEBOT_HTTP_URL"] = ""  # 清空配置

    try:
        bot = OneBotSender()
    except ValueError as e:
        print(f"配置错误: {e}")

    # 恢复原始配置
    if original_url:
        os.environ["ONEBOT_HTTP_URL"] = original_url


def main():
    """主函数"""
    print("OneBot组件使用示例")
    print("=" * 50)

    # 检查环境变量配置
    onebot_url = os.environ.get("ONEBOT_HTTP_URL")
    target_groups = os.environ.get("ONEBOT_TARGET_GROUPS")

    print(f"OneBot URL: {onebot_url or '未配置'}")
    print(f"目标群组: {target_groups or '未配置'}")
    print()

    if not onebot_url:
        print("⚠️  请先配置环境变量:")
        print("   ONEBOT_HTTP_URL=http://your-onebot-server:5700")
        print("   ONEBOT_TARGET_GROUPS=群组ID1,群组ID2")
        print("   ONEBOT_ACCESS_TOKEN=your-token (可选)")
        return

    # 运行示例
    example_class_usage()
    example_function_usage()
    example_error_handling()

    print("\n示例运行完成!")


if __name__ == "__main__":
    main()
