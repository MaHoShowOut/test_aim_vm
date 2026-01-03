"""
pytest配置文件
注册自定义测试标记
"""

import pytest

# 注册自定义测试标记
def pytest_configure(config):
    """注册自定义pytest标记"""
    config.addinivalue_line(
        "markers", "system: 系统基本信息测试"
    )
    config.addinivalue_line(
        "markers", "network: 网络连接性测试"
    )
    config.addinivalue_line(
        "markers", "service: 服务状态检查测试"
    )
    config.addinivalue_line(
        "markers", "hardware: 硬件资源可用性测试"
    )
    config.addinivalue_line(
        "markers", "security: 安全配置测试"
    )
