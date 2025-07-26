# OneBot 组件使用说明

本项目集成了 OneBot v11 协议，支持向 QQ 群组发送通知消息。

## 功能特性

- ✅ 支持 OneBot v11 HTTP API 协议
- ✅ 向多个群组批量发送消息
- ✅ 支持指定群组发送消息  
- ✅ 环境变量配置
- ✅ 完善的错误处理和日志记录
- ✅ 与现有飞书通知兼容

## 环境变量配置

在项目根目录创建 `.env` 文件，添加以下配置：

```env
# OneBot v11 配置
# OneBot HTTP API 服务地址
ONEBOT_HTTP_URL=http://localhost:5700

# OneBot 访问令牌（可选，如果你的OneBot实例配置了访问令牌）
ONEBOT_ACCESS_TOKEN=your-access-token

# 目标群组ID列表，使用逗号分隔
ONEBOT_TARGET_GROUPS=123456789,987654321
```

### 配置说明

- `ONEBOT_HTTP_URL`: OneBot HTTP API 服务的地址，通常是 `http://localhost:5700`
- `ONEBOT_ACCESS_TOKEN`: 访问令牌，如果你的 OneBot 实例设置了访问验证，需要填写此项
- `ONEBOT_TARGET_GROUPS`: 目标群组的 QQ 群号，多个群号用逗号分隔

## 使用方法

### 1. 类方式使用

```python
from qfnu_monitor.utils.onebot import OneBotSender

# 创建发送器实例
bot = OneBotSender()

# 向单个群组发送消息
result = bot.send_group_message("123456789", "这是一条测试消息")

# 向所有配置的群组发送消息
result = bot.send_to_all_groups("这是群发消息")

# 向指定群组列表发送消息
target_groups = ["123456789", "987654321"]
result = bot.send_to_specific_groups(target_groups, "这是指定群组消息")
```

### 2. 便捷函数使用

```python
from qfnu_monitor.utils.onebot import onebot_send_all, onebot_send_groups

# 向所有配置的群组发送消息
result = onebot_send_all("这是便捷函数发送的消息")

# 向指定群组发送消息
result = onebot_send_groups(["123456789"], "这是指定群组消息")
```

### 3. 在监控模块中使用

OneBot 组件已经集成到监控模块中，当检测到新公告时会自动发送到配置的 QQ 群组。

## 返回值格式

### 单个群组发送结果

```python
# 成功
{
    "status": "ok",
    "retcode": 0,
    "data": {"message_id": 12345}
}

# 失败
{
    "error": "错误信息"
}
```

### 批量发送结果

```python
{
    "total_groups": 2,
    "success_count": 1,
    "failed_count": 1,
    "results": {
        "123456789": {"status": "ok", "retcode": 0, "data": {"message_id": 12345}},
        "987654321": {"error": "群组不存在"}
    }
}
```

## OneBot 服务配置

### 使用 go-cqhttp

1. 下载 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp)
2. 配置 `config.yml`:

```yaml
# 连接服务列表
servers:
  # HTTP 通信设置
  - http:
      # 服务端监听地址
      host: 127.0.0.1
      # 服务端监听端口
      port: 5700
      # 反向HTTP超时时间, 单位秒
      timeout: 5
      # 长轮询拓展
      long-polling:
        # 是否开启
        enabled: false
      middlewares:
        <<: *default
      # 反向HTTP POST地址列表
      post:
      #- url: ''
      #  secret: ''
```

3. 启动服务: `./go-cqhttp`

### 使用 NoneBot2 + OneBot

1. 安装依赖:
```bash
pip install nonebot2[fastapi] nonebot-adapter-onebot
```

2. 配置机器人并启动

## 注意事项

1. **权限要求**: 确保机器人在目标群组中有发言权限
2. **群组 ID**: 群组 ID 是 QQ 群的群号，可以在群设置中查看
3. **网络连接**: 确保应用能够访问 OneBot 服务地址
4. **错误处理**: 组件会自动处理网络错误和 API 错误，建议查看日志获取详细信息

## 故障排除

### 常见问题

1. **连接失败**
   - 检查 `ONEBOT_HTTP_URL` 是否正确
   - 确认 OneBot 服务是否正常运行
   - 检查网络连接

2. **发送失败**
   - 确认机器人在目标群组中
   - 检查群组 ID 是否正确
   - 确认机器人有发言权限

3. **配置问题**
   - 检查 `.env` 文件是否在正确位置
   - 确认环境变量名称拼写正确
   - 验证群组 ID 格式（纯数字，逗号分隔）

### 日志查看

OneBot 组件会记录详细的发送日志，包括：
- 发送成功/失败状态
- 具体错误信息
- 发送统计信息

建议查看应用日志来诊断问题。

## 示例代码

运行示例代码：

```bash
python examples/onebot_example.py
```

这个示例展示了所有主要功能的使用方法。 