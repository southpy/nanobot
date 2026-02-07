#!/usr/bin/env python3
"""验证日志功能是否已生效"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

print("🔍 检查日志功能是否已实现...\n")

# 1. 检查 litellm_provider.py 是否有日志方法
print("1. 检查 LiteLLMProvider 是否有日志方法...")
try:
    from nanobot.providers.litellm_provider import LiteLLMProvider
    
    provider = LiteLLMProvider(api_key="test", default_model="test")
    
    # 检查是否有新增的方法
    has_log_request = hasattr(provider, '_log_request')
    has_log_response = hasattr(provider, '_log_response')
    
    if has_log_request and has_log_response:
        print("   ✅ LiteLLMProvider 已添加日志方法")
    else:
        print("   ❌ LiteLLMProvider 缺少日志方法")
        print(f"      _log_request: {has_log_request}")
        print(f"      _log_response: {has_log_response}")
        print("\n   💡 解决方法：运行 'pip install -e .' 重新安装")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ 导入失败: {e}")
    sys.exit(1)

# 2. 检查是否导入了 logger
print("\n2. 检查是否导入了 loguru...")
try:
    import inspect
    source = inspect.getsource(LiteLLMProvider)
    
    if 'from loguru import logger' in source or 'import logger' in source:
        print("   ✅ 已导入 loguru")
    else:
        print("   ❌ 未导入 loguru")
        print("\n   💡 解决方法：运行 'pip install -e .' 重新安装")
        sys.exit(1)
        
except Exception as e:
    print(f"   ⚠️  无法检查源码: {e}")

# 3. 检查 logging.py 是否存在
print("\n3. 检查 logging.py 配置模块...")
try:
    from nanobot.utils.logging import configure_logging, configure_file_logging
    print("   ✅ logging.py 模块存在")
except ImportError as e:
    print(f"   ❌ logging.py 模块不存在: {e}")
    print("\n   💡 解决方法：运行 'pip install -e .' 重新安装")
    sys.exit(1)

# 4. 测试日志功能
print("\n4. 测试日志功能...")
try:
    configure_logging(verbose=True, debug=False)
    print("   ✅ 日志配置成功")
except Exception as e:
    print(f"   ❌ 日志配置失败: {e}")
    sys.exit(1)

# 5. 检查 gateway 命令是否有新参数
print("\n5. 检查 gateway 命令参数...")
try:
    from nanobot.cli.commands import gateway
    import inspect
    
    sig = inspect.signature(gateway)
    params = list(sig.parameters.keys())
    
    has_verbose = 'verbose' in params
    has_debug = 'debug' in params
    has_log_file = 'log_file' in params
    
    print(f"   verbose: {'✅' if has_verbose else '❌'}")
    print(f"   debug: {'✅' if has_debug else '❌'}")
    print(f"   log_file: {'✅' if has_log_file else '❌'}")
    
    if not (has_verbose and has_debug and has_log_file):
        print("\n   💡 解决方法：运行 'pip install -e .' 重新安装")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ 检查失败: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✅ 所有检查通过！日志功能已正确实现。")
print("="*60)
print("\n📝 下一步：")
print("   1. 重新安装: pip install -e .")
print("   2. 启动 gateway: nanobot gateway --verbose")
print("   3. 发送消息测试")
print("\n💡 如果还是不生效，请运行：")
print("   python -m nanobot.cli.commands gateway --verbose")

