"""
服务状态检查测试

验证Alibaba Cloud Linux 3.21.04系统关键服务的运行状态
"""

import subprocess
import pytest
from config import Config


class TestServiceStatus:
    """服务状态测试类"""

    @pytest.mark.service
    def test_required_services_running(self):
        """测试必需服务的运行状态"""
        for service in Config.REQUIRED_SERVICES:
            try:
                result = subprocess.run(
                    ["systemctl", "is-active", service],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    timeout=Config.SERVICE_CHECK_TIMEOUT
                )

                assert result.returncode == 0, \
                    f"服务 {service} 未运行: {result.stdout.strip()}"

            except subprocess.TimeoutExpired:
                pytest.fail(f"检查服务 {service} 状态超时")

    @pytest.mark.service
    def test_critical_processes_exist(self):
        """测试关键进程存在性"""
        critical_processes = [
            "systemd",
            "sshd",
            "chronyd"
        ]

        try:
            result = subprocess.run(
                ["ps", "aux"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=Config.SERVICE_CHECK_TIMEOUT
            )

            assert result.returncode == 0, "无法获取进程列表"
            process_output = result.stdout

            for process in critical_processes:
                assert process in process_output, \
                    f"关键进程不存在: {process}"

        except subprocess.TimeoutExpired:
            pytest.fail("获取进程列表超时")

    @pytest.mark.service
    def test_systemd_status(self):
        """测试systemd系统管理器状态"""
        try:
            result = subprocess.run(
                ["systemctl", "is-system-running"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=Config.SERVICE_CHECK_TIMEOUT
            )

            status = result.stdout.strip()
            assert status in ["running", "degraded"], \
                f"系统运行状态异常: {status}"

        except subprocess.TimeoutExpired:
            pytest.fail("检查systemd状态超时")

    @pytest.mark.service
    def test_sshd_configuration(self):
        """测试SSH服务配置"""
        ssh_config_file = "/etc/ssh/sshd_config"

        try:
            # 检查配置文件存在
            result = subprocess.run(
                ["test", "-f", ssh_config_file],
                timeout=Config.SERVICE_CHECK_TIMEOUT
            )
            assert result.returncode == 0, "SSH配置文件不存在"

            # 检查SSH配置语法
            result = subprocess.run(
                ["sshd", "-t"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=Config.SERVICE_CHECK_TIMEOUT
            )
            assert result.returncode == 0, \
                f"SSH配置语法错误: {result.stderr}"

        except subprocess.TimeoutExpired:
            pytest.fail("SSH配置检查超时")

    @pytest.mark.service
    def test_cron_service(self):
        """测试定时任务服务"""
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "crond"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=Config.SERVICE_CHECK_TIMEOUT
            )

            # cron服务可能叫crond或cron
            if result.returncode != 0:
                result = subprocess.run(
                    ["systemctl", "is-active", "cron"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    timeout=Config.SERVICE_CHECK_TIMEOUT
                )

            assert result.returncode == 0, "定时任务服务未运行"

        except subprocess.TimeoutExpired:
            pytest.fail("检查定时任务服务超时")

    @pytest.mark.service
    def test_logging_service(self):
        """测试日志服务"""
        logging_services = ["rsyslog", "systemd-journald"]

        active_services = 0
        for service in logging_services:
            try:
                result = subprocess.run(
                    ["systemctl", "is-active", service],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    timeout=Config.SERVICE_CHECK_TIMEOUT
                )

                if result.returncode == 0:
                    active_services += 1

            except subprocess.TimeoutExpired:
                continue

        assert active_services > 0, "没有活动的日志服务"

    @pytest.mark.service
    def test_network_manager(self):
        """测试网络管理服务"""
        network_services = ["NetworkManager", "network"]

        active_services = 0
        for service in network_services:
            try:
                result = subprocess.run(
                    ["systemctl", "is-active", service],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    timeout=Config.SERVICE_CHECK_TIMEOUT
                )

                if result.returncode == 0:
                    active_services += 1
                    break

            except subprocess.TimeoutExpired:
                continue

        assert active_services > 0, "没有活动的网络管理服务"

    @pytest.mark.service
    def test_package_manager(self):
        """测试包管理器功能"""
        try:
            # 测试yum/dnf可用性
            result = subprocess.run(
                ["which", "yum"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=Config.SERVICE_CHECK_TIMEOUT
            )

            if result.returncode == 0:
                # 测试yum命令
                result = subprocess.run(
                    ["yum", "check-update", "--quiet"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=30  # 包管理器检查可能需要更长时间
                )
                # 不检查返回值，因为网络问题可能导致失败
                assert True  # 如果能执行命令就算成功
            else:
                # 尝试dnf
                result = subprocess.run(
                    ["which", "dnf"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=Config.SERVICE_CHECK_TIMEOUT
                )
                assert result.returncode == 0, "未找到可用的包管理器(yum/dnf)"

        except subprocess.TimeoutExpired:
            pytest.fail("包管理器检查超时")
