# nanobot 日志配置指南

## 问题描述

默认情况下，`nanobot gateway` 启动后在终端中看不到详细的日志信息，只能看到启动消息。这是因为 loguru 的默认日志级别设置为 WARNING。

## 解决方案

### 方案 1：启用详细日志（推荐）

使用 `--verbose` 或 `-v` 参数启动 gateway，可以看到 INFO 级别的日志：

```bash
nanobot gateway --verbose
```

**输出示例：**
```
🐈 Starting nanobot gateway on port 18790...
2026-02-07 10:30:15 | INFO     | nanobot.utils.logging:configure_logging:28 - Logging configured at INFO level
2026-02-07 10:30:15 | INFO     | nanobot.channels.manager:_init_channels:44 - Telegram channel enabled
2026-02-07 10:30:15 | INFO     | nanobot.agent.loop:run:112 - Agent loop started
2026-02-07 10:30:15 | INFO     | nanobot.channels.manager:start_all:93 - Starting telegram channel...
2026-02-07 10:30:15 | INFO     | nanobot.channels.manager:_dispatch_outbound:121 - Outbound dispatcher started
2026-02-07 10:30:16 | INFO     | nanobot.cron.service:start:154 - Cron service started with 0 jobs
```

### 方案 2：启用调试日志

使用 `--debug` 或 `-d` 参数可以看到更详细的 DEBUG 级别日志：

```bash
nanobot gateway --debug
```

**输出示例：**
```
🐈 Starting nanobot gateway on port 18790...
2026-02-07 10:30:15 | INFO     | nanobot.utils.logging:configure_logging:28 - Logging configured at DEBUG level
2026-02-07 10:30:15 | DEBUG    | nanobot.agent.loop:_process_message:158 - Processing message from telegram:123456789
2026-02-07 10:30:15 | DEBUG    | nanobot.agent.loop:_process_message:220 - Executing tool: read_file with arguments: {"path": "test.txt"}
```

### 方案 3：同时输出到文件

使用 `--log-file` 参数将日志同时保存到文件：

```bash
nanobot gateway --verbose --log-file ~/.nanobot/logs/gateway.log
```

这会：
- 在终端显示 INFO 级别日志
- 在文件中保存 DEBUG 级别日志
- 自动轮转（单个文件最大 10MB）
- 保留 7 天的日志
- 自动压缩旧日志

### 方案 4：组合使用

```bash
# 调试模式 + 文件日志
nanobot gateway --debug --log-file ~/.nanobot/logs/gateway.log

# 详细模式 + 自定义端口 + 文件日志
nanobot gateway -v -p 8080 -l ~/.nanobot/logs/gateway.log
```

## 日志级别说明

| 级别 | 参数 | 显示内容 | 适用场景 |
|------|------|----------|----------|
| **WARNING** | 默认 | 只显示警告和错误 | 生产环境 |
| **INFO** | `--verbose` / `-v` | 显示关键操作信息 | 日常使用 |
| **DEBUG** | `--debug` / `-d` | 显示所有调试信息 | 开发调试 |

## 日志格式

### 终端输出（彩色）
```
<时间> | <级别> | <模块>:<函数>:<行号> - <消息>
2026-02-07 10:30:15 | INFO     | nanobot.agent.loop:run:112 - Agent loop started
```

### 文件输出（纯文本）
```
2026-02-07 10:30:15 | INFO     | nanobot.agent.loop:run:112 - Agent loop started
```

## 常见日志消息

### 启动阶段
```
INFO     | nanobot.channels.manager:_init_channels:44 - Telegram channel enabled
INFO     | nanobot.agent.loop:run:112 - Agent loop started
INFO     | nanobot.cron.service:start:154 - Cron service started with 0 jobs
INFO     | nanobot.channels.manager:_dispatch_outbound:121 - Outbound dispatcher started
```

### 消息处理
```
INFO     | nanobot.agent.loop:_process_message:158 - Processing message from telegram:123456789
DEBUG    | nanobot.agent.loop:_process_message:220 - Executing tool: web_search with arguments: {"query": "..."}
```

### 错误信息
```
ERROR    | nanobot.agent.loop:_process_message:128 - Error processing message: Connection timeout
WARNING  | nanobot.channels.manager:_dispatch_outbound:137 - Unknown channel: unknown_channel
```

## 查看实时日志

如果使用了文件日志，可以使用 `tail` 命令实时查看：

```bash
# 实时查看日志
tail -f ~/.nanobot/logs/gateway.log

# 只看最近 100 行
tail -n 100 ~/.nanobot/logs/gateway.log

# 过滤特定内容
tail -f ~/.nanobot/logs/gateway.log | grep "ERROR"
```

## 环境变量配置（高级）

也可以通过环境变量配置 loguru：

```bash
# 设置日志级别
export LOGURU_LEVEL=DEBUG

# 启动 gateway
nanobot gateway
```

## 故障排查

### 问题：仍然看不到日志

**检查项：**
1. 确认使用了 `--verbose` 或 `--debug` 参数
2. 检查是否有其他程序捕获了 stderr
3. 尝试重定向到文件：`nanobot gateway -v 2>&1 | tee gateway.log`

### 问题：日志太多

**解决方法：**
1. 使用默认模式（不加 `-v` 或 `-d`）
2. 使用 `grep` 过滤：`nanobot gateway -v 2>&1 | grep -v "DEBUG"`
3. 只记录到文件：`nanobot gateway -l ~/.nanobot/logs/gateway.log`

### 问题：想看特定模块的日志

使用 `grep` 过滤：

```bash
# 只看 agent.loop 的日志
nanobot gateway -v 2>&1 | grep "agent.loop"

# 只看 ERROR 和 WARNING
nanobot gateway -v 2>&1 | grep -E "ERROR|WARNING"
```

## LLM 调用日志

从当前版本开始，nanobot 支持查看模型调用的完整信息！

### 查看 LLM 调用详情

使用 `--verbose` 可以看到：
- 🤖 每次 LLM API 请求的详细信息（模型、参数、消息数量、工具列表）
- 📥 每次 LLM API 响应的详细信息（内容、Token 使用量、工具调用）
- 🔄 Agent 迭代过程

```bash
nanobot gateway --verbose
```

**示例输出：**
```
================================================================================
🤖 LLM API Request
================================================================================
Model: openrouter/anthropic/claude-opus-4-5
Temperature: 0.7
Max Tokens: 4096
Messages: 3 total
Tools: 8 available - read_file, write_file, list_dir, exec, web_search, web_fetch, message, spawn
--------------------------------------------------------------------------------
📥 LLM API Response
================================================================================
Finish Reason: tool_calls
Token Usage:
  - Prompt: 1234
  - Completion: 56
  - Total: 1290
Content: I'll search for that information.
Tool Calls: 1
  [0] web_search
================================================================================
```

### 查看完整消息内容

使用 `--debug` 可以看到：
- 完整的消息内容（包括 system prompt、用户消息、助手回复）
- 详细的工具定义
- 工具调用的完整参数

```bash
nanobot gateway --debug
```

### 更多信息

详细的 LLM 日志功能说明请查看：[LLM_LOGGING.md](./LLM_LOGGING.md)

## 参考

- Loguru 文档：https://loguru.readthedocs.io/
- nanobot 配置：`~/.nanobot/config.json`
- LLM 日志功能：[LLM_LOGGING.md](./LLM_LOGGING.md)

