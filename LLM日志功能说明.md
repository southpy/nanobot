# nanobot LLM 调用日志功能说明

## 🎯 功能概述

现在 nanobot 支持查看模型调用的**完整信息**，帮助你：
- 🔍 调试模型行为
- 📊 监控 Token 使用
- 🛠️ 分析工具调用
- 💰 优化成本

## 📋 可以看到什么信息

### 请求信息（🤖 LLM API Request）
- ✅ 使用的模型名称
- ✅ 温度、最大 Token 等参数
- ✅ 发送的消息数量和内容
- ✅ 可用的工具列表
- ✅ API 端点地址

### 响应信息（📥 LLM API Response）
- ✅ 生成的文本内容
- ✅ Token 使用量（Prompt/Completion/Total）
- ✅ 工具调用详情（名称、参数）
- ✅ 完成原因（stop/tool_calls/length/error）

### Agent 处理过程
- ✅ 迭代次数和进度
- ✅ 每次迭代的结果
- ✅ 工具执行情况

## 🚀 快速开始

### 方式 1：查看基本信息（推荐）

```bash
nanobot gateway --verbose
```

你会看到类似这样的输出：

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
Content: 我来帮你搜索这个信息。
Tool Calls: 1
  [0] web_search
================================================================================
```

### 方式 2：查看详细信息

```bash
nanobot gateway --debug
```

在 DEBUG 模式下，你还会看到：
- 完整的消息内容
- 每条消息的详细信息
- 工具的完整定义
- 工具调用的完整参数 JSON

### 方式 3：保存到文件

```bash
nanobot gateway --verbose --log-file ~/.nanobot/logs/llm-calls.log
```

## 📊 实用技巧

### 技巧 1：只看 Token 使用

```bash
nanobot gateway --verbose 2>&1 | grep "Token Usage" -A 3
```

输出：
```
Token Usage:
  - Prompt: 1234
  - Completion: 56
  - Total: 1290
```

### 技巧 2：只看工具调用

```bash
nanobot gateway --verbose 2>&1 | grep -E "(Tool Calls|Executing tool)"
```

### 技巧 3：统计 API 调用次数

```bash
nanobot gateway --verbose 2>&1 | grep "LLM API Request" | wc -l
```

### 技巧 4：监控实时日志

```bash
# 终端 1：启动 gateway 并记录日志
nanobot gateway --verbose --log-file llm.log

# 终端 2：实时查看日志
tail -f llm.log | grep --line-buffered "Token Usage" -A 3
```

## 🎓 使用场景

### 场景 1：调试为什么模型没有调用工具

**问题**：你期望模型调用某个工具，但它没有调用。

**解决**：
```bash
nanobot gateway --debug
```

查看：
1. 工具是否在 "Tools available" 列表中
2. 工具的描述是否清晰
3. 模型的响应中 "Tool Calls" 是否为 None

### 场景 2：优化 Token 使用降低成本

**问题**：API 费用太高，想知道哪里用了太多 Token。

**解决**：
```bash
nanobot gateway --verbose --log-file token-analysis.log
```

然后分析日志：
```bash
# 查看所有 Token 使用
grep "Token Usage" -A 3 token-analysis.log

# 找出 Token 使用最多的调用
grep "Total:" token-analysis.log | sort -t: -k2 -n
```

### 场景 3：分析模型如何使用工具

**问题**：想了解模型在什么情况下会调用哪些工具。

**解决**：
```bash
nanobot gateway --verbose 2>&1 | tee tool-usage.log
```

然后分析：
```bash
# 统计每个工具的调用次数
grep "Executing tool:" tool-usage.log | cut -d: -f4 | cut -d' ' -f2 | sort | uniq -c
```

### 场景 4：监控 API 错误

**问题**：偶尔出现 API 调用失败，想知道原因。

**解决**：
```bash
nanobot gateway --verbose --log-file api-errors.log
```

查看错误：
```bash
grep "ERROR" api-errors.log
grep "Finish Reason: error" api-errors.log
```

## ⚙️ 配置建议

### 开发环境
```bash
# 最详细的日志，方便调试
nanobot gateway --debug --log-file ~/.nanobot/logs/dev.log
```

### 测试环境
```bash
# 详细日志，记录到文件
nanobot gateway --verbose --log-file ~/.nanobot/logs/test.log
```

### 生产环境
```bash
# 只记录警告和错误，节省磁盘空间
nanobot gateway --log-file ~/.nanobot/logs/prod.log
```

### 临时调试
```bash
# 直接在终端查看，不保存文件
nanobot gateway --verbose
```

## ⚠️ 注意事项

### 隐私安全
- ⚠️ 日志会包含完整的对话内容
- ⚠️ 可能包含敏感信息（API Key 已自动隐藏）
- ⚠️ 生产环境建议使用默认日志级别
- ⚠️ 调试完成后记得删除日志文件

### 性能影响
- ✅ INFO 级别：几乎无影响（<1%）
- ✅ DEBUG 级别：轻微影响（2-5%）
- ✅ 文件日志：异步写入，无明显影响

### 磁盘空间
- 📁 日志文件会自动轮转（10MB/文件）
- 📁 自动保留 7 天
- 📁 旧日志自动压缩为 .zip
- 📁 建议定期检查 `~/.nanobot/logs/` 目录

## 🧪 测试功能

运行测试脚本验证日志功能：

```bash
python test_llm_logging.py
```

这会展示：
- INFO 级别的日志输出
- DEBUG 级别的日志输出
- 不同消息类型的日志格式

## 📚 相关文档

- [基础日志配置](./LOGGING.md) - 日志系统的基本使用
- [日志问题解决](./日志问题解决方案.md) - 常见问题和解决方案
- [LLM Logging (English)](./LLM_LOGGING.md) - English version

## 🆘 常见问题

### Q1: 看不到 LLM 日志？
**A:** 确保使用了 `--verbose` 或 `--debug` 参数。

### Q2: 日志太多怎么办？
**A:** 使用 grep 过滤或只记录到文件：
```bash
nanobot gateway --log-file llm.log  # 终端保持简洁
```

### Q3: 如何只看某个时间段的日志？
**A:** 使用时间戳过滤：
```bash
grep "2026-02-07 10:" llm.log
```

### Q4: Token 使用量不准确？
**A:** 某些模型提供商可能不返回 Token 使用量，这是正常的。

### Q5: 如何导出日志分析？
**A:** 日志是纯文本格式，可以用任何工具分析：
```bash
# 导出为 CSV
grep "Token Usage" -A 3 llm.log | grep "Total:" | sed 's/.*Total: //' > tokens.csv
```

## 💡 高级用法

### 实时监控 Token 使用

创建一个监控脚本 `monitor_tokens.sh`：

```bash
#!/bin/bash
tail -f ~/.nanobot/logs/llm.log | grep --line-buffered "Total:" | while read line; do
    tokens=$(echo $line | grep -o '[0-9]*')
    echo "$(date '+%H:%M:%S') - Tokens used: $tokens"
done
```

### 生成使用报告

```bash
#!/bin/bash
LOG_FILE=~/.nanobot/logs/llm.log

echo "=== LLM Usage Report ==="
echo "Total API calls: $(grep -c 'LLM API Request' $LOG_FILE)"
echo "Total tokens: $(grep 'Total:' $LOG_FILE | grep -o '[0-9]*' | awk '{s+=$1} END {print s}')"
echo "Most used tool: $(grep 'Executing tool:' $LOG_FILE | cut -d: -f4 | cut -d' ' -f2 | sort | uniq -c | sort -rn | head -1)"
```

## 🎉 总结

现在你可以：
- ✅ 实时查看模型调用详情
- ✅ 监控 Token 使用和成本
- ✅ 调试工具调用问题
- ✅ 分析模型行为模式

**立即尝试：**
```bash
nanobot gateway --verbose
```

