#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alibaba Cloud Linux 3.21.04 测试框架上传脚本

# 推荐：分开传输以便版本控制
将本项目分三次上传至目标靶机对应目录
存放位置均为 /opt/test_project/

三次传输内容：
1. 环境包：test_env.tar.gz (Python虚拟环境)
2. 测试代码：tests/ 目录 (测试用例)
3. 主脚本：run_tests.py, pytest.ini, config.py等 (核心脚本)
"""

import os
import sys
import time
import paramiko
from scp import SCPClient
from pathlib import Path

# 靶机连接信息 (Python字典形式记录)
TARGET_HOSTS = {
    'primary': {
        'hostname': '47.100.32.213',  # 替换为实际IP地址
        'port': 22,
        'username': 'root',
        'password': 'Cyapp#2025',  # 使用密钥认证，设为None
        'key_filename': '~/.ssh/id_rsa',  # SSH私钥路径
        'description': '主测试靶机'
    },
    'backup': {
        'hostname': '192.168.1.101',  # 替换为实际IP地址
        'port': 22,
        'username': 'root',
        'password': None,
        'key_filename': '~/.ssh/id_rsa',
        'description': '备用测试靶机'
    }
}

# 项目配置
PROJECT_CONFIG = {
    'remote_base_path': '/opt/test_project',
    'local_project_root': Path(__file__).parent.parent.absolute(),  # 指向项目根目录

    # 传输批次配置
    'batches': {
        'env_package': {
            'name': '环境包',
            'files': ['test_env.tar.gz'],
            'description': 'Python虚拟环境压缩包'
        },
        'test_code': {
            'name': '测试代码',
            'files': ['tests'],
            'description': 'pytest测试用例目录'
        },
        'main_scripts': {
            'name': '主脚本',
            'files': [
                'run_tests.py',
                'pytest.ini',
                'config.py',
                'requirements.txt',
                'README.md',
                'DEPLOYMENT_README.txt',
                'deploy_and_test.sh'
            ],
            'description': '核心运行脚本和配置文件'
        }
    }
}


class ProjectUploader:
    """项目上传器"""

    def __init__(self, target_name='primary'):
        self.target_config = TARGET_HOSTS.get(target_name)
        if not self.target_config:
            raise ValueError(f"未找到目标主机配置: {target_name}")

        self.project_config = PROJECT_CONFIG
        self.local_root = self.project_config['local_project_root']
        self.remote_base = self.project_config['remote_base_path']

        # SSH客户端
        self.ssh_client = None
        self.scp_client = None

        print("[初始化上传器]")
        print(f"  目标主机: {self.target_config['hostname']}")
        print(f"  描述: {self.target_config['description']}")
        print(f"  本地路径: {self.local_root}")
        print(f"  远程路径: {self.remote_base}")

    def connect(self):
        """建立SSH连接"""
        try:
            print(f"\n🔗 连接到 {self.target_config['hostname']}...")

            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # 连接参数
            connect_kwargs = {
                'hostname': self.target_config['hostname'],
                'port': self.target_config['port'],
                'username': self.target_config['username']
            }

            # SSH密钥认证
            if self.target_config.get('key_filename'):
                key_path = os.path.expanduser(self.target_config['key_filename'])
                if os.path.exists(key_path):
                    connect_kwargs['key_filename'] = key_path
                    print(f"  使用SSH密钥: {key_path}")
                else:
                    print(f"  [警告] SSH密钥文件不存在: {key_path}")

            # 密码认证（备选）
            if self.target_config.get('password'):
                connect_kwargs['password'] = self.target_config['password']
                print("  使用密码认证")

            self.ssh_client.connect(**connect_kwargs)

            # 创建SCP客户端
            self.scp_client = SCPClient(self.ssh_client.get_transport())

            print("✅ SSH连接成功")

        except Exception as e:
            print(f"❌ SSH连接失败: {e}")
            raise

    def disconnect(self):
        """断开连接"""
        if self.scp_client:
            self.scp_client.close()
        if self.ssh_client:
            self.ssh_client.close()
        print("🔌 连接已断开")

    def ensure_remote_directory(self, remote_path):
        """确保远程目录存在"""
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(f'mkdir -p {remote_path}')
            exit_code = stdout.channel.recv_exit_status()

            if exit_code == 0:
                print(f"✅ 远程目录已准备: {remote_path}")
            else:
                error_msg = stderr.read().decode().strip()
                print(f"❌ 创建远程目录失败: {error_msg}")
                return False

        except Exception as e:
            print(f"❌ 远程目录操作失败: {e}")
            return False

        return True

    def upload_batch(self, batch_name, batch_config):
        """上传一个批次的文件"""
        print(f"\n📦 开始上传批次: {batch_config['name']}")
        print(f"  描述: {batch_config['description']}")

        success_count = 0
        total_files = len(batch_config['files'])

        for file_path in batch_config['files']:
            local_path = self.local_root / file_path

            if not local_path.exists():
                print(f"  ⚠️  本地文件不存在，跳过: {local_path}")
                continue

            # 远程路径
            remote_path = f"{self.remote_base}/{file_path}"

            # 确保远程目录存在
            remote_dir = os.path.dirname(remote_path)
            if not self.ensure_remote_directory(remote_dir):
                continue

            try:
                print(f"  📤 上传: {file_path}")

                # 记录开始时间
                start_time = time.time()

                # 上传文件/目录
                if local_path.is_dir():
                    # 上传目录
                    self.scp_client.put(str(local_path), remote_path, recursive=True)
                else:
                    # 上传文件
                    self.scp_client.put(str(local_path), remote_path)

                # 计算耗时
                elapsed = time.time() - start_time

                # 获取文件大小
                if local_path.is_file():
                    size_mb = local_path.stat().st_size / 1024 / 1024
                    print(f"    耗时: {elapsed:.1f}秒, 大小: {size_mb:.1f}MB")
                else:
                    print(f"    耗时: {elapsed:.1f}秒 (目录)")

                success_count += 1

            except Exception as e:
                print(f"  ❌ 上传失败 {file_path}: {e}")

        print(f"  结果: {success_count}/{total_files} 个文件上传成功")
        return success_count == total_files

    def verify_upload(self, batch_name, batch_config):
        """验证上传结果"""
        print(f"\n🔍 验证批次: {batch_config['name']}")

        all_verified = True

        for file_path in batch_config['files']:
            remote_path = f"{self.remote_base}/{file_path}"

            try:
                # 检查远程文件是否存在
                stdin, stdout, stderr = self.ssh_client.exec_command(f'ls -la "{remote_path}"')
                exit_code = stdout.channel.recv_exit_status()

                if exit_code == 0:
                    # 解析文件信息
                    output = stdout.read().decode().strip()
                    print(f"  ✅ 已验证: {file_path}")
                else:
                    print(f"  ❌ 验证失败: {file_path}")
                    all_verified = False

            except Exception as e:
                print(f"  ❌ 验证异常 {file_path}: {e}")
                all_verified = False

        return all_verified

    def run_deployment_checks(self):
        """运行部署后检查"""
        print("\n🔧 运行部署后检查")
        checks = [
            ("检查Python环境", "python3 --version"),
            ("检查磁盘空间", "df -h /opt"),
            ("检查网络连接", "ping -c 1 8.8.8.8"),
            ("验证项目目录", f"ls -la {self.remote_base}")
        ]

        for check_name, command in checks:
            try:
                stdin, stdout, stderr = self.ssh_client.exec_command(command)
                exit_code = stdout.channel.recv_exit_status()

                if exit_code == 0:
                    print(f"  ✅ {check_name}: 通过")
                else:
                    error_output = stderr.read().decode().strip()
                    print(f"  ❌ {check_name}: 失败 - {error_output}")

            except Exception as e:
                print(f"  ❌ {check_name}: 异常 - {e}")

    def upload_all(self):
        """执行完整上传流程"""
        print("\n🚀 开始完整项目上传流程")
        print("=" * 50)

        try:
            # 建立连接
            self.connect()

            # 执行三次上传
            batches = self.project_config['batches']
            results = {}

            for batch_key, batch_config in batches.items():
                print(f"\n{'='*20} 第{list(batches.keys()).index(batch_key) + 1}次传输 {'='*20}")

                # 上传批次
                upload_success = self.upload_batch(batch_key, batch_config)
                results[batch_key] = {'upload': upload_success}

                if upload_success:
                    # 验证上传
                    verify_success = self.verify_upload(batch_key, batch_config)
                    results[batch_key]['verify'] = verify_success

                    if verify_success:
                        print(f"🎉 批次 '{batch_config['name']}' 上传验证成功！")
                    else:
                        print(f"⚠️  批次 '{batch_config['name']}' 上传成功但验证失败")
                else:
                    print(f"❌ 批次 '{batch_config['name']}' 上传失败")
                    results[batch_key]['verify'] = False

            # 部署后检查
            print(f"\n{'='*20} 部署后检查 {'='*20}")
            self.run_deployment_checks()

            # 总结报告
            self.print_summary(results)

        except Exception as e:
            print(f"❌ 上传过程出现异常: {e}")
            return False
        finally:
            self.disconnect()

        return True

    def print_summary(self, results):
        """打印总结报告"""
        print(f"\n{'='*50}")
        print("📊 上传总结报告")
        print("=" * 50)

        total_batches = len(results)
        successful_batches = 0

        for batch_key, result in results.items():
            batch_config = self.project_config['batches'][batch_key]
            status = "✅ 成功" if result['upload'] and result.get('verify', False) else "❌ 失败"
            print(f"  {batch_config['name']}: {status}")

            if result['upload'] and result.get('verify', False):
                successful_batches += 1

        print(f"\n总体结果: {successful_batches}/{total_batches} 个批次成功")

        if successful_batches == total_batches:
            print("🎉 项目上传完全成功！")
            print(f"📁 远程项目路径: {self.remote_base}")
            print("💡 接下来可以在靶机上运行测试框架")
        else:
            print("⚠️  部分批次上传失败，请检查上述错误信息")

        print("=" * 50)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Alibaba Cloud Linux 3.21.04 测试框架上传工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python upload_project.py                    # 上传到主靶机
  python upload_project.py --target backup   # 上传到备用靶机
  python upload_project.py --dry-run         # 仅显示将要上传的文件

可用目标靶机:
""" + "\n".join([f"  {name}: {config['description']} ({config['hostname']})"
                for name, config in TARGET_HOSTS.items()])
    )

    parser.add_argument(
        '--target', '-t',
        choices=list(TARGET_HOSTS.keys()),
        default='primary',
        help='目标靶机名称 (默认: primary)'
    )

    parser.add_argument(
        '--dry-run', '-d',
        action='store_true',
        help='仅显示将要上传的文件，不执行实际上传'
    )

    parser.add_argument(
        '--batch',
        choices=list(PROJECT_CONFIG['batches'].keys()),
        help='只上传指定的批次'
    )

    args = parser.parse_args()

    # 创建上传器
    try:
        uploader = ProjectUploader(args.target)
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        return 1

    if args.dry_run:
        print("🔍 干运行模式 - 显示将要上传的文件:")
        print(f"目标主机: {uploader.target_config['hostname']}")
        print(f"远程路径: {uploader.remote_base}")
        print("\n将要上传的批次:")

        for batch_key, batch_config in PROJECT_CONFIG['batches'].items():
            print(f"\n📦 {batch_config['name']} ({batch_config['description']}):")
            for file_path in batch_config['files']:
                local_path = uploader.local_root / file_path
                exists = "✅" if local_path.exists() else "❌"
                print(f"  {exists} {file_path}")

        return 0

    if args.batch:
        # 只上传指定批次
        batch_config = PROJECT_CONFIG['batches'][args.batch]
        print(f"🎯 只上传批次: {batch_config['name']}")

        uploader.connect()
        try:
            success = uploader.upload_batch(args.batch, batch_config)
            if success:
                uploader.verify_upload(args.batch, batch_config)
        finally:
            uploader.disconnect()

        return 0 if success else 1

    # 执行完整上传
    success = uploader.upload_all()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
