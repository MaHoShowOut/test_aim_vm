"""
系统基本信息测试

验证Alibaba Cloud Linux 3.21.04系统的基本信息和启动状态
"""

import platform
import subprocess
import pytest
from config import Config


class TestSystemInfo:
    """系统基本信息测试类"""

    @pytest.mark.system
    def test_os_distribution(self):
        """测试操作系统发行版信息"""
        try:
            result = subprocess.run(
                ["cat", "/etc/os-release"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=Config.SERVICE_CHECK_TIMEOUT
            )

            assert result.returncode == 0, "无法读取操作系统信息"
            os_info = result.stdout.lower()

            assert Config.EXPECTED_OS.lower() in os_info, \
                f"期望的OS: {Config.EXPECTED_OS}, 实际: {os_info}"

        except subprocess.TimeoutExpired:
            pytest.fail("读取操作系统信息超时")
        except FileNotFoundError:
            pytest.fail("/etc/os-release文件不存在")

    @pytest.mark.system
    def test_kernel_version(self):
        """测试内核版本"""
        kernel_version = platform.release()

        # 提取主版本号 (例如: 5.10.0-123 从 5.10.0-123.4.2.al8.x86_64)
        major_minor = ".".join(kernel_version.split(".")[:2])

        assert major_minor >= Config.MIN_KERNEL_VERSION, \
            f"内核版本过低: {kernel_version}, 要求 >= {Config.MIN_KERNEL_VERSION}"

    @pytest.mark.system
    def test_system_uptime(self):
        """测试系统运行时间"""
        try:
            result = subprocess.run(
                ["uptime", "-p"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=Config.SERVICE_CHECK_TIMEOUT
            )

            assert result.returncode == 0, "无法获取系统运行时间"
            uptime_str = result.stdout.strip()

            # 验证uptime输出包含预期的格式
            assert "up" in uptime_str.lower() or "day" in uptime_str or "hour" in uptime_str, \
                f"无效的uptime输出: {uptime_str}"

        except subprocess.TimeoutExpired:
            pytest.fail("获取系统运行时间超时")

    @pytest.mark.system
    def test_hostname_resolution(self):
        """测试主机名解析"""
        import socket

        hostname = socket.gethostname()
        assert hostname, "无法获取主机名"

        try:
            # 测试本地主机名解析
            socket.gethostbyname(hostname)
        except socket.gaierror:
            pytest.fail(f"主机名 {hostname} 无法解析")

    @pytest.mark.system
    def test_system_load(self):
        """测试系统负载"""
        try:
            result = subprocess.run(
                ["uptime"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=Config.SERVICE_CHECK_TIMEOUT
            )

            assert result.returncode == 0, "无法获取系统负载"
            uptime_output = result.stdout

            # 解析负载平均值 (load average: 0.01, 0.02, 0.00)
            if "load average:" in uptime_output:
                load_part = uptime_output.split("load average:")[1].strip()
                load_values = load_part.split(",")[:3]

                for load in load_values:
                    load_float = float(load.strip())
                    assert load_float >= 0, f"无效的负载值: {load_float}"
            else:
                pytest.skip("无法解析系统负载信息")

        except subprocess.TimeoutExpired:
            pytest.fail("获取系统负载超时")
        except ValueError as e:
            pytest.fail(f"解析系统负载失败: {e}")

    @pytest.mark.system
    def test_selinux_status(self):
        """测试SELinux状态"""
        try:
            result = subprocess.run(
                ["sestatus"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=Config.SERVICE_CHECK_TIMEOUT
            )

            # SELinux可能被禁用，这是正常的
            if result.returncode == 0:
                selinux_output = result.stdout.lower()
                # 如果启用，确保状态是enforcing或permissive
                if "enabled" in selinux_output:
                    assert "enforcing" in selinux_output or "permissive" in selinux_output, \
                        f"SELinux状态异常: {selinux_output}"
            else:
                # SELinux被禁用，记录但不失败
                pytest.skip("SELinux已被禁用")

        except subprocess.TimeoutExpired:
            pytest.fail("检查SELinux状态超时")
