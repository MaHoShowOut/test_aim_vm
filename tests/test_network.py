"""
网络连接性测试

验证Alibaba Cloud Linux 3.21.04系统的网络配置和连接状态
"""

import socket
import subprocess
import pytest
import requests
from config import Config


class TestNetworkConnectivity:
    """网络连接性测试类"""

    @pytest.mark.network
    def test_network_interfaces(self):
        """测试网络接口状态"""
        try:
            result = subprocess.run(
                ["ip", "addr", "show"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=Config.SERVICE_CHECK_TIMEOUT
            )

            assert result.returncode == 0, "无法获取网络接口信息"
            interface_output = result.stdout

            # 检查必需的网络接口
            for interface in Config.REQUIRED_NETWORK_INTERFACES:
                assert interface in interface_output, \
                    f"缺少必需的网络接口: {interface}"

        except subprocess.TimeoutExpired:
            pytest.fail("获取网络接口信息超时")

    @pytest.mark.network
    def test_dns_resolution(self):
        """测试DNS解析功能"""
        test_domains = [
            "www.aliyun.com",
            "www.baidu.com",
            "github.com"
        ]

        for domain in test_domains:
            try:
                socket.gethostbyname(domain)
            except socket.gaierror as e:
                pytest.fail(f"DNS解析失败 {domain}: {e}")

    @pytest.mark.network
    def test_internet_connectivity(self):
        """测试互联网连接性"""
        test_urls = [
            "https://www.aliyun.com",
            "https://www.baidu.com"
        ]

        for url in test_urls:
            try:
                response = requests.get(
                    url,
                    timeout=Config.NETWORK_TIMEOUT,
                    verify=False  # 在测试环境中可能没有证书
                )
                assert response.status_code == 200, \
                    f"无法访问 {url}, 状态码: {response.status_code}"
            except requests.RequestException as e:
                pytest.fail(f"网络连接失败 {url}: {e}")

    @pytest.mark.network
    def test_localhost_connectivity(self):
        """测试本地回环连接"""
        try:
            # 测试TCP连接到本地端口
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(Config.NETWORK_TIMEOUT)

            # 尝试连接到本地回环地址
            result = sock.connect_ex(("127.0.0.1", 22))  # SSH端口
            sock.close()

            # connect_ex返回0表示连接成功
            assert result == 0, "无法连接到本地SSH服务"

        except socket.error as e:
            pytest.fail(f"本地连接测试失败: {e}")

    @pytest.mark.network
    def test_network_configuration(self):
        """测试网络配置文件"""
        config_files = [
            "/etc/resolv.conf",
            "/etc/hosts",
            "/etc/sysconfig/network"
        ]

        for config_file in config_files:
            try:
                result = subprocess.run(
                    ["test", "-f", config_file],
                    timeout=Config.SERVICE_CHECK_TIMEOUT
                )
                assert result.returncode == 0, \
                    f"网络配置文件不存在: {config_file}"
            except subprocess.TimeoutExpired:
                pytest.fail(f"检查配置文件超时: {config_file}")

    @pytest.mark.network
    def test_firewall_status(self):
        """测试防火墙状态"""
        try:
            # 检查firewalld状态
            result = subprocess.run(
                ["systemctl", "is-active", "firewalld"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=Config.SERVICE_CHECK_TIMEOUT
            )

            # 防火墙可能是active或inactive，都可以接受
            assert result.returncode in [0, 3], \
                f"防火墙状态异常: {result.stdout.strip()}"

        except subprocess.TimeoutExpired:
            pytest.fail("检查防火墙状态超时")

    @pytest.mark.network
    def test_network_routes(self):
        """测试网络路由配置"""
        try:
            result = subprocess.run(
                ["ip", "route", "show"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=Config.SERVICE_CHECK_TIMEOUT
            )

            assert result.returncode == 0, "无法获取路由表"
            route_output = result.stdout

            # 检查是否存在默认路由
            assert "default" in route_output, "缺少默认路由"

        except subprocess.TimeoutExpired:
            pytest.fail("获取路由表超时")

    @pytest.mark.network
    def test_network_listening_ports(self):
        """测试网络监听端口"""
        try:
            result = subprocess.run(
                ["ss", "-tuln"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=Config.SERVICE_CHECK_TIMEOUT
            )

            assert result.returncode == 0, "无法获取监听端口信息"
            port_output = result.stdout

            # 检查SSH端口是否在监听
            assert ":22 " in port_output, "SSH端口(22)未在监听"

        except subprocess.TimeoutExpired:
            pytest.fail("获取监听端口信息超时")
