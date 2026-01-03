"""
硬件资源可用性测试

验证Alibaba Cloud Linux 3.21.04系统的硬件资源状态
"""

import subprocess
import psutil
import pytest
from config import Config


class TestHardwareResources:
    """硬件资源测试类"""

    @pytest.mark.hardware
    def test_cpu_cores(self):
        """测试CPU核心数量"""
        cpu_count = psutil.cpu_count()
        assert cpu_count >= Config.MIN_CPU_CORES, \
            f"CPU核心数不足: {cpu_count} < {Config.MIN_CPU_CORES}"

    @pytest.mark.hardware
    def test_memory_size(self):
        """测试内存大小"""
        memory_gb = psutil.virtual_memory().total / (1024 ** 3)
        assert memory_gb >= Config.MIN_MEMORY_GB, \
            f"内存不足: {memory_gb:.1f}GB < {Config.MIN_MEMORY_GB}GB"

    @pytest.mark.hardware
    def test_memory_usage(self):
        """测试内存使用情况"""
        memory = psutil.virtual_memory()
        memory_usage_percent = memory.percent

        # 内存使用率不应该超过95%
        assert memory_usage_percent < 95, \
            f"内存使用率过高: {memory_usage_percent}%"

        # 确保有足够的可用内存 (至少100MB)
        available_mb = memory.available / (1024 ** 2)
        assert available_mb > 100, \
            f"可用内存不足: {available_mb:.0f}MB"

    @pytest.mark.hardware
    def test_cpu_usage(self):
        """测试CPU使用情况"""
        cpu_percent = psutil.cpu_percent(interval=1)

        # CPU使用率不应该持续超过90%
        assert cpu_percent < 90, \
            f"CPU使用率过高: {cpu_percent}%"

    @pytest.mark.hardware
    def test_hardware_info(self):
        """测试硬件基本信息"""
        try:
            result = subprocess.run(
                ["lscpu"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=Config.SERVICE_CHECK_TIMEOUT
            )

            assert result.returncode == 0, "无法获取CPU信息"
            cpu_info = result.stdout.lower()

            # 验证是x86_64架构
            assert "x86_64" in cpu_info, "不支持的CPU架构"

        except subprocess.TimeoutExpired:
            pytest.fail("获取硬件信息超时")
