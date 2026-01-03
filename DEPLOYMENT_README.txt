# Alibaba Cloud Linux 3.21.04 测试环境部署指南

## 文件概述

`test_env.tar.gz` 是包含完整Python虚拟环境的压缩包，专门用于在Alibaba Cloud Linux 3.21.04靶机上运行自动化测试。该包已预先配置好所有必要的依赖包和测试脚本。

**自动化部署脚本**: `deploy_and_test.sh` - 一键执行完整部署和测试流程的自动化脚本。

## 环境要求

- **操作系统**: Alibaba Cloud Linux 3.21.04
- **Python**: 3.6+ (虚拟环境已包含Python 3.14)
- **磁盘空间**: 至少2GB可用空间
- **权限**: root用户权限（推荐）

## 部署步骤

### 快速部署（推荐）

如果您想一键完成所有部署步骤，可以使用自动化脚本：

```bash
# 1. 传输脚本和环境包到靶机
scp deploy_and_test.sh test_env.tar.gz root@target-host:/opt/

# 2. 在靶机上运行自动化脚本
ssh root@target-host 'cd /opt && chmod +x deploy_and_test.sh && ./deploy_and_test.sh'
```

自动化脚本将按顺序执行：
1. 切换到项目目录
2. 解压虚拟环境包
3. 激活虚拟环境
4. 检查环境完整性
5. 运行完整测试套件
6. 生成详细的测试报告

### 手动部署步骤

如果需要手动执行每个步骤，请按照以下说明操作：

#### 步骤1：传输文件到靶机

将 `test_env.tar.gz` 和 `deploy_and_test.sh` 文件传输到靶机：

```bash
# 使用scp传输（推荐）
scp test_env.tar.gz root@target-host:/opt/

# 同时传输自动化脚本
scp deploy_and_test.sh root@target-host:/opt/
```

### 步骤2：解压虚拟环境

在靶机上解压文件：

```bash
# 进入目标目录
cd /opt/test_project

# 解压tar.gz文件
tar -xzf test_env.tar.gz

# 验证解压结果
ls -la test_env/
```

解压后应包含以下结构：
```
test_env/
├── bin/              # 可执行文件和激活脚本
├── lib/              # Python库文件
├── pyvenv.cfg        # 虚拟环境配置
├── requirements_installed.txt  # 已安装包列表
├── run_tests.py      # 主测试脚本
├── pytest.ini        # pytest配置
├── config.py         # 测试配置
├── tests/            # 测试用例目录
└── doc/              # 文档目录
```

### 步骤3：激活虚拟环境

```bash
# 激活虚拟环境
source test_env/bin/activate

# 验证激活成功（提示符应显示 (test_env)）
(test_env) [root@iZuf645ple8o071r4ygsnvZ test_env]#
```

### 步骤4：运行环境检查

```bash
# 检查环境完整性
python run_tests.py --check-env

# 预期输出：
# Alibaba Cloud Linux 3.21.04 靶机环境验证测试
# ================================================================
#
# 检查测试环境...
# ✓ Python版本: 3.14.x
# ✓ 正在虚拟环境中运行
#   虚拟环境路径: /opt/test_env
# ✓ 以root权限运行
# ✓ 检测到Alibaba Cloud Linux
# ✓ 关键依赖包已安装
#
# ✓ 环境检查完成
```

### 步骤5：运行完整测试

```bash
# 运行所有测试
python run_tests.py

# 或运行特定类型的测试
python run_tests.py -t system     # 只运行系统测试
python run_tests.py -t network    # 只运行网络测试
python run_tests.py -t service    # 只运行服务测试
python run_tests.py -t hardware   # 只运行硬件测试

# 生成HTML测试报告
python run_tests.py --html
```

### 步骤6：查看测试结果

测试执行完成后，会显示详细的测试结果：

```bash
# 成功示例
============================================================
执行: 运行所有测试
命令: python3 -m pytest tests/
时间: 2025-01-02 12:30:00
============================================================
tests/test_system_info.py .....                           [ 22%]
tests/test_network.py ......                              [ 44%]
tests/test_services.py ........                           [ 74%]
tests/test_hardware.py .....                              [100%]

======================= 27 passed in 12.34s =======================

✓ 所有测试执行完成
```

## 测试覆盖范围

该测试框架涵盖以下领域：

### 1. 系统信息测试
- 操作系统发行版验证
- 内核版本检查
- 系统运行时间监控
- 主机名解析测试
- 系统负载监控
- SELinux状态检查

### 2. 网络连接性测试
- 网络接口状态检查
- DNS解析功能验证
- 互联网连接测试
- 防火墙状态监控
- 网络路由配置验证
- 网络监听端口检查

### 3. 服务状态测试
- 关键系统服务检查
- SSH服务配置验证
- 定时任务服务监控
- 包管理器功能测试

### 4. 硬件资源测试
- CPU信息验证
- 内存使用情况检查

## 故障排除

### 问题1：解压失败
```bash
# 检查文件完整性
ls -lh test_env\ .tar.gz

# 重新传输文件
scp test_env\ .tar.gz root@target-host:/opt/
```

### 问题2：激活环境失败
```bash
# 检查文件权限
ls -la test_env/bin/activate

# 修复权限
chmod +x test_env/bin/*

# 检查Python路径
test_env/bin/python --version
```

### 问题3：依赖包缺失
```bash
# 检查虚拟环境包
source test_env/bin/activate
pip list | grep pytest

# 如果缺失，重新安装
pip install -r requirements.txt
```

### 问题4：权限不足
```bash
# 确保以root用户运行
whoami

# 切换到root用户
sudo su -
```

### 问题5：测试执行失败
```bash
# 查看详细错误信息
python run_tests.py -v

# 检查系统状态
python run_tests.py --check-env

# 查看系统日志
journalctl -n 50
```

### 问题6：网络连接问题
```bash
# 检查网络状态
ping -c 3 8.8.8.8

# 检查DNS解析
nslookup www.baidu.com

# 检查防火墙
systemctl status firewalld
```

## 验证部署成功

运行以下命令验证部署完全成功：

```bash
# 1. 环境激活测试
cd /opt/test_env
source bin/activate
echo $VIRTUAL_ENV  # 应显示 /opt/test_env

# 2. 包导入测试
python -c "import pytest, psutil, requests, paramiko; print('✓ 依赖包正常')"

# 3. 基本功能测试
python run_tests.py --check-env

# 4. 完整测试运行
python run_tests.py -t system

# 5. 退出环境
deactivate
```

## 清理和维护

### 清理测试环境
```bash
# 退出虚拟环境
deactivate

# 删除测试环境（如果需要）
cd /opt
rm -rf test_env/
```

### 重新部署
如果需要重新部署，只需：
1. 删除旧的test_env目录
2. 重新解压tar.gz文件
3. 重新激活环境并运行测试

## 技术支持

如果遇到无法解决的问题，请：

1. 收集错误信息和日志
2. 检查系统状态：`uname -a`, `cat /etc/os-release`
3. 联系技术支持并提供完整错误信息

## 自动化脚本详细说明

### deploy_and_test.sh 功能特性

`deploy_and_test.sh` 脚本提供以下功能：

#### 执行流程
1. **环境验证**: 检查必要的文件和目录是否存在
2. **解压环境**: 自动解压 `test_env.tar.gz` 虚拟环境包
3. **环境激活**: 激活Python虚拟环境并验证配置
4. **完整性检查**: 运行环境检查确保所有组件正常
5. **测试执行**: 运行完整的测试套件
6. **报告生成**: 自动生成带时间戳的详细测试报告

#### 输出内容
- 实时显示执行进度和状态
- 完整的测试结果输出
- 自动生成的TXT格式测试报告
- 详细的错误信息和故障排除提示

#### 错误处理
- 遇到错误时自动停止执行
- 提供清晰的错误信息和解决建议
- 保留部分完成的工作以便调试

### 使用示例

```bash
# 基本使用（推荐）
./deploy_and_test.sh

# 查看帮助信息
./deploy_and_test.sh --help

# 脚本会自动生成类似以下文件名的报告：
# test_report_20250102_143052.txt
```

### 报告文件内容

生成的测试报告包含：
- 执行时间和环境信息
- 完整的测试输出
- 成功/失败统计
- 警告和错误信息
- 执行摘要

---

**部署包版本**: v1.0.0
**适用系统**: Alibaba Cloud Linux 3.21.04
**Python版本**: 3.14 (虚拟环境)
**自动化脚本**: deploy_and_test.sh
**最后更新**: 2025-01-02
