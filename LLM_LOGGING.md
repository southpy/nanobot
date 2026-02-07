# nanobot LLM 调用日志功能

## 功能概述

现在 nanobot 支持查看模型调用的完整信息，包括：
- 📤 **请求信息**：模型名称、参数、消息内容、可用工具
- 📥 **响应信息**：生成内容、Token 使用量、工具调用、完成原因
- 🔄 **迭代过程**：Agent 循环的每次迭代详情

## 使用方法

### 1. 启用详细日志

使用 `--verbose` 参数启动 gateway 即可看到 LLM 调用信息：

```bash
nanobot gateway --verbose
```

### 2. 启用调试日志（最详细）

使用 `--debug` 参数可以看到更详细的信息，包括完整的消息内容和工具定义：

```bash
nanobot gateway --debug
```

## 日志输出示例

### INFO 级别（--verbose）

```
2026-02-07 10:30:15 | INFO     | nanobot.agent.loop:_process_message:189 - Starting agent loop for message from telegram:123456789
2026-02-07 10:30:15 | INFO     | nanobot.agent.loop:_process_message:193 - Agent iteration 1/20
================================================================================
🤖 LLM API Request
================================================================================
2026-02-07 10:30:15 | INFO     | nanobot.providers.litellm_provider:_log_request:219 - Model: openrouter/anthropic/claude-opus-4-5
2026-02-07 10:30:15 | INFO     | nanobot.providers.litellm_provider:_log_request:220 - Temperature: 0.7
2026-02-07 10:30:15 | INFO     | nanobot.providers.litellm_provider:_log_request:221 - Max Tokens: 4096
2026-02-07 10:30:15 | INFO     | nanobot.providers.litellm_provider:_log_request:227 - Messages: 3 total
2026-02-07 10:30:15 | INFO     | nanobot.providers.litellm_provider:_log_request:250 - Tools: 8 available - read_file, write_file, list_dir, exec, web_search, web_fetch, message, spawn
--------------------------------------------------------------------------------
📥 LLM API Response
================================================================================
2026-02-07 10:30:16 | INFO     | nanobot.providers.litellm_provider:_log_response:271 - Finish Reason: tool_calls
2026-02-07 10:30:16 | INFO     | nanobot.providers.litellm_provider:_log_response:275 - Token Usage:
2026-02-07 10:30:16 | INFO     | nanobot.providers.litellm_provider:_log_response:276 -   - Prompt: 1234
2026-02-07 10:30:16 | INFO     | nanobot.providers.litellm_provider:_log_response:277 -   - Completion: 56
2026-02-07 10:30:16 | INFO     | nanobot.providers.litellm_provider:_log_response:278 -   - Total: 1290
2026-02-07 10:30:16 | INFO     | nanobot.providers.litellm_provider:_log_response:287 - Content: I'll search for that information.
2026-02-07 10:30:16 | INFO     | nanobot.providers.litellm_provider:_log_response:292 - Tool Calls: 1
2026-02-07 10:30:16 | INFO     | nanobot.providers.litellm_provider:_log_response:294 -   [0] web_search
================================================================================
2026-02-07 10:30:16 | INFO     | nanobot.agent.loop:_process_message:202 - Iteration 1 completed - finish_reason: tool_calls
2026-02-07 10:30:16 | DEBUG    | nanobot.agent.loop:_process_message:226 - Executing tool: web_search with arguments: {"query": "nanobot AI assistant"}
```

### DEBUG 级别（--debug）

在 DEBUG 级别，你还会看到：

```
2026-02-07 10:30:15 | DEBUG    | nanobot.providers.litellm_provider:_log_request:237 -   [0] system: You are a helpful AI assistant...
2026-02-07 10:30:15 | DEBUG    | nanobot.providers.litellm_provider:_log_request:237 -   [1] user: What is nanobot?
2026-02-07 10:30:15 | DEBUG    | nanobot.providers.litellm_provider:_log_request:237 -   [2] assistant: [tool_calls: web_search]
2026-02-07 10:30:15 | DEBUG    | nanobot.providers.litellm_provider:_log_request:253 - Tool definitions:
2026-02-07 10:30:15 | DEBUG    | nanobot.providers.litellm_provider:_log_request:255 -   - read_file: Read contents of a file
2026-02-07 10:30:15 | DEBUG    | nanobot.providers.litellm_provider:_log_request:255 -   - write_file: Write content to a file
2026-02-07 10:30:15 | DEBUG    | nanobot.providers.litellm_provider:_log_request:255 -   - web_search: Search the web. Returns titles, URLs, and snippets.
2026-02-07 10:30:16 | DEBUG    | nanobot.providers.litellm_provider:_log_response:286 - Full content:
I'll search for that information.
2026-02-07 10:30:16 | DEBUG    | nanobot.providers.litellm_provider:_log_response:296 -       ID: call_abc123
2026-02-07 10:30:16 | DEBUG    | nanobot.providers.litellm_provider:_log_response:297 -       Arguments: {
  "query": "nanobot AI assistant"
}
```

## 日志信息详解

### 请求信息（🤖 LLM API Request）

| 字段 | 说明 | 示例 |
|------|------|------|
| Model | 使用的模型名称 | `openrouter/anthropic/claude-opus-4-5` |
| Temperature | 采样温度 | `0.7` |
| Max Tokens | 最大生成 token 数 | `4096` |
| API Base | API 端点（如果有） | `https://openrouter.ai/api/v1` |
| Messages | 消息数量和内容 | `3 total` |
| Tools | 可用工具列表 | `8 available - read_file, write_file, ...` |

### 响应信息（📥 LLM API Response）

| 字段 | 说明 | 可能的值 |
|------|------|----------|
| Finish Reason | 完成原因 | `stop`, `tool_calls`, `length`, `error` |
| Token Usage | Token 使用统计 | Prompt/Completion/Total |
| Content | 生成的文本内容 | 模型的回复文本 |
| Tool Calls | 工具调用列表 | 工具名称、ID、参数 |

### Agent 迭代信息

| 日志 | 说明 |
|------|------|
| `Starting agent loop` | 开始处理消息 |
| `Agent iteration X/Y` | 当前迭代次数 |
| `Iteration X completed` | 迭代完成及原因 |
| `Agent loop completed` | 成功完成所有处理 |
| `reached max iterations` | 达到最大迭代次数 |

## 使用场景

### 场景 1：调试模型行为

当模型没有按预期工作时，查看完整的请求和响应：

```bash
nanobot gateway --debug
```

可以看到：
- 模型收到了什么消息
- 模型生成了什么内容
- 模型调用了哪些工具
- Token 使用情况

### 场景 2：优化 Token 使用

查看每次调用的 Token 使用量：

```bash
nanobot gateway --verbose | grep "Token Usage" -A 3
```

### 场景 3：分析工具调用

查看模型如何使用工具：

```bash
nanobot gateway --verbose | grep "Tool Calls" -A 5
```

### 场景 4：监控 API 调用

记录所有 API 调用到文件以便后续分析：

```bash
nanobot gateway --verbose --log-file ~/.nanobot/logs/llm-calls.log
```

## 过滤日志

### 只看 LLM 请求

```bash
nanobot gateway --verbose 2>&1 | grep -A 20 "LLM API Request"
```

### 只看 Token 使用

```bash
nanobot gateway --verbose 2>&1 | grep "Token Usage" -A 3
```

### 只看工具调用

```bash
nanobot gateway --verbose 2>&1 | grep -E "(Tool Calls|Executing tool)"
```

## 性能影响

- **INFO 级别**：性能影响极小（<1%）
- **DEBUG 级别**：会记录完整消息内容，可能增加 2-5% 的开销
- **文件日志**：异步写入，几乎无性能影响

## 隐私注意事项

⚠️ **重要提示**：

1. 日志会包含完整的对话内容
2. 如果使用 `--log-file`，敏感信息会被保存到文件
3. 生产环境建议使用默认日志级别（WARNING）
4. 如需调试，使用后记得删除日志文件

## 配置建议

### 开发环境

```bash
nanobot gateway --debug --log-file ~/.nanobot/logs/dev.log
```

### 生产环境

```bash
nanobot gateway --log-file ~/.nanobot/logs/gateway.log
```

### 临时调试

```bash
nanobot gateway --verbose
```

## 相关文档

- [日志配置指南](./LOGGING.md)
- [日志问题解决方案](./日志问题解决方案.md)

