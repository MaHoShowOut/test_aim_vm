"""
靶机测试配置文件
"""

import os
from typing import Dict, List

class Config:
    """测试配置类"""

    # 系统信息
    EXPECTED_OS = "Alibaba Cloud Linux"
    EXPECTED_VERSION = "3.21.04"
    MIN_KERNEL_VERSION = "5.10"

    # 网络配置
    EXPECTED_HOSTNAME_PATTERN = r"^[a-zA-Z0-9\-]+\.[a-zA-Z0-9\-]+\.[a-zA-Z0-9\-]+$"
    REQUIRED_NETWORK_INTERFACES = ["lo", "eth0"]

    # 存储配置
    REQUIRED_MOUNT_POINTS = ["/", "/boot", "/tmp", "/var", "/usr"]
    MIN_DISK_SPACE_GB = {
        "/": 10,
        "/var": 5,
        "/tmp": 2,
        "/usr": 8
    }

    # 服务配置
    REQUIRED_SERVICES = [
        "sshd",
        "chronyd",
        "systemd-journald",
        "systemd-logind"
    ]

    # 安全配置
    REQUIRED_SECURE_PERMISSIONS = {
        "/etc/passwd": 0o644,
        "/etc/shadow": 0o600,
        "/etc/sudoers": 0o440
    }

    # 硬件要求
    MIN_MEMORY_GB = 1
    MIN_CPU_CORES = 1

    # 测试超时设置
    NETWORK_TIMEOUT = 10
    SERVICE_CHECK_TIMEOUT = 5

    # 测试环境变量
    TEST_MODE = os.getenv("TEST_MODE", "local")  # local, remote
    REMOTE_HOST = os.getenv("REMOTE_HOST", "localhost")
    REMOTE_USER = os.getenv("REMOTE_USER", "root")
    SSH_KEY_PATH = os.getenv("SSH_KEY_PATH", "~/.ssh/id_rsa")

    # venv虚拟环境配置
    VENV_PATH = os.getenv("VENV_PATH", "/opt/test_env")  # 默认venv路径
    USE_VENV = os.getenv("USE_VENV", "auto").lower()  # auto, true, false
    VENV_AUTO_DETECT = os.getenv("VENV_AUTO_DETECT", "true").lower() == "true"
