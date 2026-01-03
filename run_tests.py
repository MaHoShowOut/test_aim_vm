#!/usr/bin/env python3
"""
靶机环境验证测试运行脚本

用于在Alibaba Cloud Linux 3.21.04靶机上执行完整的环境验证测试
"""

import subprocess
import sys
import argparse
from datetime import datetime
import os


def run_command(command, description):
    """执行命令并返回结果"""
    print(f"\n{'='*60}")
    print(f"执行: {description}")
    print(f"命令: {' '.join(command)}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*60)

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=300  # 5分钟超时
        )

        if result.returncode == 0:
            print("✓ 执行成功")
            if result.stdout:
                print("输出:")
                print(result.stdout)
        else:
            print("✗ 执行失败")
            print(f"错误码: {result.returncode}")
            if result.stderr:
                print("错误信息:")
                print(result.stderr)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("✗ 执行超时")
        return False
    except Exception as e:
        print(f"✗ 执行异常: {e}")
        return False


def check_environment():
    """检查测试环境"""
    print("\n检查测试环境...")

    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6):
        print(f"✗ Python版本过低: {python_version.major}.{python_version.minor}，需要3.6+")
        return False
    else:
        print(f"✓ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")

    # 检查虚拟环境状态
    in_venv = sys.prefix != sys.base_prefix
    if in_venv:
        print("✓ 正在虚拟环境中运行")
        print(f"  虚拟环境路径: {sys.prefix}")
        venv_recommended = False
    else:
        print("ℹ 正在系统Python环境中运行")
        print("  建议使用venv虚拟环境以获得更好的隔离性")
        venv_recommended = True

    # 检查是否为root用户
    if os.geteuid() != 0:
        print("⚠ 警告: 非root用户运行，某些测试可能失败")
    else:
        print("✓ 以root权限运行")

    # 检查操作系统
    try:
        with open('/etc/os-release', 'r') as f:
            os_info = f.read().lower()
            if 'alibaba cloud linux' in os_info:
                print("✓ 检测到Alibaba Cloud Linux")
            else:
                print("⚠ 警告: 未检测到Alibaba Cloud Linux，可能影响测试结果")
    except:
        print("✗ 无法读取操作系统信息")

    # 检查关键依赖包
    required_packages = ['pytest', 'psutil', 'requests']
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"✗ 缺少必要的依赖包: {', '.join(missing_packages)}")
        print("  建议运行: pip install -r requirements.txt")
        print("  或使用venv环境: ./run_tests_venv.sh")
        return False
    else:
        print("✓ 关键依赖包已安装")

    # 显示venv建议
    if venv_recommended:
        print("\n💡 venv使用提示:")
        print("  1. 创建虚拟环境: python3 -m venv test_env")
        print("  2. 激活环境: source test_env/bin/activate")
        print("  3. 安装依赖: pip install -r requirements.txt")
        print("  4. 运行测试: python run_tests.py")
        print("  或使用专用脚本: ./run_tests_venv.sh")

    return True


def install_dependencies():
    """安装测试依赖"""
    print("\n安装测试依赖...")

    # 检查pip
    if not run_command(['which', 'pip3'], '检查pip3可用性'):
        print("✗ 未找到pip3，请先安装pip")
        return False

    # 安装依赖
    if not run_command(['pip3', 'install', '-r', 'requirements.txt'], '安装Python依赖包'):
        print("✗ 依赖安装失败")
        return False

    return True


def run_tests(test_type=None, verbose=False, html_report=False):
    """运行测试"""
    command = ['python3', '-m', 'pytest']

    if test_type:
        if test_type == 'all':
            pass  # 运行所有测试
        else:
            command.extend(['-m', test_type])

    if verbose:
        command.append('-v')
        command.append('-s')

    if html_report:
        command.extend(['--html', 'test_report.html'])
        command.extend(['--self-contained-html'])

    # 设置测试路径
    command.append('tests/')

    return run_command(command, f'运行{test_type or "所有"}测试')


def main():
    parser = argparse.ArgumentParser(
        description='Alibaba Cloud Linux 3.21.04 靶机环境验证测试',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  %(prog)s                    # 运行所有测试
  %(prog)s -t system         # 只运行系统测试
  %(prog)s -v                # 详细输出
  %(prog)s --html            # 生成HTML报告
  %(prog)s --install-deps    # 安装依赖后运行测试
        '''
    )

    parser.add_argument(
        '-t', '--test-type',
        choices=['all', 'system', 'network', 'service', 'hardware'],
        default='all',
        help='测试类型 (默认: all)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='详细输出'
    )

    parser.add_argument(
        '--html',
        action='store_true',
        help='生成HTML测试报告'
    )

    parser.add_argument(
        '--install-deps',
        action='store_true',
        help='安装依赖包'
    )

    parser.add_argument(
        '--check-env',
        action='store_true',
        help='只检查环境，不运行测试'
    )

    args = parser.parse_args()

    print("Alibaba Cloud Linux 3.21.04 靶机环境验证测试")
    print("=" * 60)

    # 检查环境
    if not check_environment():
        print("\n✗ 环境检查失败，请修复问题后重试")
        sys.exit(1)

    if args.check_env:
        print("\n✓ 环境检查完成")
        sys.exit(0)

    # 安装依赖
    if args.install_deps:
        if not install_dependencies():
            print("\n✗ 依赖安装失败")
            sys.exit(1)

    # 运行测试
    print(f"\n开始运行{args.test_type}测试...")

    success = run_tests(
        test_type=None if args.test_type == 'all' else args.test_type,
        verbose=args.verbose,
        html_report=args.html
    )

    if success:
        print("\n✓ 所有测试执行完成")
        if args.html and os.path.exists('test_report.html'):
            print("✓ HTML报告已生成: test_report.html")
        sys.exit(0)
    else:
        print("\n✗ 测试执行失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
