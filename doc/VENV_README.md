# Python虚拟环境(venv)使用指南

## 概述

本项目使用Python虚拟环境(venv)来管理测试框架的依赖包，实现环境隔离，避免污染系统Python环境，并提供更好的可移植性和版本控制。

## 为什么使用venv？

### 🎯 优势

1. **环境隔离**：测试依赖与系统Python环境完全隔离
2. **版本控制**：精确控制每个包的版本
3. **可移植性**：venv可以打包和分发到不同机器
4. **安全性**：减少对系统包的意外修改
5. **易维护**：依赖关系清晰，便于升级和回滚

### 📊 对比传统方式

| 方面 | 传统方式 (pip install) | venv方式 |
|------|----------------------|----------|
| 环境影响 | 污染系统环境 | 完全隔离 |
| 版本冲突 | 可能与其他应用冲突 | 无冲突 |
| 卸载清理 | 困难，可能残留 | 直接删除venv目录 |
| 多版本并存 | 复杂 | 简单 |
| 部署分发 | 需要重复安装 | 打包分发 |

## 快速开始

### 1. 创建虚拟环境

```bash
# 在项目根目录下创建venv
python -m venv test_env

# 激活虚拟环境
source test_env/bin/activate  # Linux/macOS
# test_env\Scripts\activate   # Windows

# 验证激活成功 (提示符会显示 (test_env))
(test_env) user@host:~/project$
```

### 2. 配置虚拟环境

```bash
# 升级pip到最新版本（推荐）
pip install --upgrade pip

# 安装wheel包（可选，提高后续包安装速度）
pip install wheel

# 安装项目依赖
pip install -r requirements.txt

# 验证安装
python -c "import pytest, psutil, requests, paramiko; print('✅ 依赖安装成功')"
```

### 3. 运行测试

```bash
# 在激活venv后运行测试
python run_tests.py

# 或使用venv路径直接运行
./test_env/bin/python3 run_tests.py

# 或使用专用脚本（推荐）
./run_tests_venv.sh
```

### 4. 退出虚拟环境

```bash
# 退出venv
deactivate
```

### 5. 打包环境（用于部署）

```bash
# 可选：生成已安装包的清单
source test_env/bin/activate
pip freeze > test_env/requirements_installed.txt
deactivate

# 打包整个venv目录用于分发
tar -czf test_env.tar.gz test_env/
```

## 详细使用指南

### 📁 venv目录结构

创建venv后，目录结构如下：

```
test_env/
├── bin/                    # 可执行文件 (Linux/macOS)
│   ├── python3            # Python解释器
│   ├── pip               # pip包管理器
│   └── pytest            # 安装的包
├── lib/                   # Python库文件
│   └── python3.x/
│       └── site-packages/ # 安装的包
├── include/              # 头文件
└── pyvenv.cfg           # 配置文件
```

### 🔧 常用命令

#### 创建和管理venv

```bash
# 创建venv (指定Python版本)
python3.9 -m venv test_env

# 创建venv (不继承系统包)
python3 -m venv --clear test_env

# 删除venv
rm -rf test_env

# 重命名venv
mv test_env test_env_backup
```

#### 包管理

```bash
# 查看已安装包
pip list

# 查看包详细信息
pip show pytest

# 升级特定包
pip install --upgrade pytest

# 卸载包
pip uninstall pytest

# 生成requirements.txt (当前环境)
pip freeze > requirements.txt

# 安装requirements.txt
pip install -r requirements.txt
```

#### 环境信息

```bash
# 检查是否在venv中
python -c "import sys; print('在venv中' if sys.prefix != sys.base_prefix else '不在venv中')"

# 查看Python路径
python -c "import sys; print(sys.path)"

# 查看venv路径
python -c "import sys; print(sys.prefix)"
```

## 高级用法

### 🔄 环境复制和迁移

#### 方法1：完整复制venv

```bash
# 在源机器上
tar -czf test_env.tar.gz test_env/

# 在目标机器上
scp test_env.tar.gz target:/tmp/
ssh target
cd /opt/
sudo tar -xzf /tmp/test_env.tar.gz
sudo chown -R root:root test_env
```

#### 方法2：只复制site-packages (更小)

```bash
# 提取site-packages
mkdir test_packages
cp -r test_env/lib/python3.*/site-packages/* test_packages/
tar -czf test_packages.tar.gz test_packages/

# 在目标机器上恢复
# 1. 确保Python版本相同
# 2. 创建基础venv
python3 -m venv target_env
# 3. 替换site-packages
cp -r test_packages/* target_env/lib/python3.*/site-packages/
```

### 🚀 自动化部署脚本

#### 部署脚本 `deploy_venv.sh`

```bash
#!/bin/bash
# venv自动部署脚本

TARGET_HOST=$1
VENV_PACKAGE="test_env.tar.gz"
REMOTE_PATH="/opt/test_env"

if [ -z "$TARGET_HOST" ]; then
    echo "用法: $0 <target_host>"
    exit 1
fi

echo "部署venv到靶机: $TARGET_HOST"

# 检查包是否存在
if [ ! -f "$VENV_PACKAGE" ]; then
    echo "❌ venv包不存在: $VENV_PACKAGE"
    exit 1
fi

# 上传包
echo "📤 上传venv包..."
scp $VENV_PACKAGE root@$TARGET_HOST:/tmp/

# 远程部署
ssh root@$TARGET_HOST << EOF
echo "🔧 部署venv环境..."

# 创建目录
mkdir -p $REMOTE_PATH

# 解压
cd $(dirname $REMOTE_PATH)
tar -xzf /tmp/$VENV_PACKAGE

# 设置权限
chown -R root:root $(basename $REMOTE_PATH)

# 清理
rm /tmp/$VENV_PACKAGE

# 验证
if [ -x "$REMOTE_PATH/bin/python3" ]; then
    echo "✅ venv部署成功"
    $REMOTE_PATH/bin/python3 --version
else
    echo "❌ venv部署失败"
    exit 1
fi
EOF

echo "🎉 部署完成！"
```

#### 使用部署脚本

```bash
# 给脚本执行权限
chmod +x deploy_venv.sh

# 部署到单台机器
./deploy_venv.sh target-host-01

# 批量部署
for host in target-01 target-02 target-03; do
    ./deploy_venv.sh $host
done
```

### 🔍 故障排除

#### 问题1：激活venv后命令找不到

```bash
# 症状：激活后python命令找不到
(test_env) $ python --version
# bash: python: command not found

# 解决：使用python3
(test_env) $ python3 --version
# 或重新创建venv
python3 -m venv --clear test_env
```

#### 问题2：包安装失败

```bash
# 网络问题：使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 权限问题：使用--user或sudo
pip install --user -r requirements.txt
# 或
sudo pip install -r requirements.txt
```

#### 问题3：Python版本不匹配

```bash
# 检查Python版本
python3 --version

# 指定Python版本创建venv
python3.9 -m venv test_env
python3.8 -m venv test_env
```

#### 问题4：venv损坏

```bash
# 删除并重新创建
rm -rf test_env
python3 -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt
```

#### 问题5：Windows PowerShell执行策略错误

**现象**：
```powershell
.\test_env\Scripts\Activate.ps1 : 无法加载文件 ... Activate.ps1，因为在此系统上禁止运行脚本
```

**解决**：
```powershell
# 方法1：临时修改执行策略（推荐）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# 方法2：永久修改执行策略（需要管理员权限）
# 以管理员身份运行PowerShell，然后执行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned

# 然后激活venv
.\test_env\Scripts\Activate.ps1
```

**执行策略说明**：
- `Restricted`：默认值，不允许运行脚本
- `RemoteSigned`：允许运行本地脚本和签名的远程脚本（推荐）
- `Unrestricted`：允许运行所有脚本（风险较高）

### 📋 最佳实践

#### 1. 版本管理

```bash
# 使用requirements.txt锁定版本
pytest==7.4.0
psutil==5.9.4
requests==2.31.0

# 安装时指定版本
pip install pytest==7.4.0
```

#### 2. 环境一致性

```bash
# 在相同Python版本的机器上创建venv
python3 --version  # 检查版本
python3 -m venv test_env

# 避免在不同架构间迁移venv
# (如x86_64到arm64)
```

#### 3. 目录结构

```
/project/
├── requirements.txt      # 依赖声明
├── test_env/            # 虚拟环境 (可选)
├── test_env.tar.gz      # venv压缩包 (用于部署)
├── deploy_venv.sh       # 部署脚本
└── docs/
    └── venv/           # venv相关文档
```

#### 4. CI/CD集成

```yaml
# .github/workflows/test.yml
- name: Setup Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.9'

- name: Create venv
  run: |
    python -m venv test_env
    source test_env/bin/activate
    pip install --upgrade pip
    pip install wheel
    pip install -r requirements.txt

- name: Package venv (optional)
  run: |
    source test_env/bin/activate
    pip freeze > test_env/requirements_installed.txt
    deactivate
    tar -czf test_env.tar.gz test_env/

- name: Run tests
  run: |
    source test_env/bin/activate
    python run_tests.py

# 或者使用项目专用脚本
- name: Run tests with project script
  run: ./run_tests_venv.sh
```

### 🎯 项目集成

#### 自动venv检测

项目中的 `run_tests.py` 已集成venv检测：

```python
def check_environment():
    """检查测试环境"""
    in_venv = sys.prefix != sys.base_prefix
    if in_venv:
        print("✓ 正在虚拟环境中运行")
        print(f"  虚拟环境路径: {sys.prefix}")
    else:
        print("⚠ 警告: 不在虚拟环境中运行")
```

#### 使用方法

```bash
# 方法1：激活venv后运行
source test_env/bin/activate
python run_tests.py

# 方法2：使用绝对路径
/opt/test_env/bin/python3 run_tests.py

# 方法3：使用专用脚本 (推荐)
./run_tests_venv.sh
```

### 📚 相关资源

- [Python venv官方文档](https://docs.python.org/3/library/venv.html)
- [pip用户指南](https://pip.pypa.io/en/stable/user_guide/)
- [requirements.txt格式](https://pip.pypa.io/en/stable/reference/requirements-file-format/)

### 🔐 安全注意事项

1. **不要提交venv目录**到版本控制系统
2. **定期更新依赖包**修复安全漏洞
3. **验证包来源**避免恶意包
4. **限制venv权限**在生产环境中

### 📞 支持

如果在使用venv过程中遇到问题，请：

1. 检查Python版本兼容性
2. 验证requirements.txt语法
3. 查看错误日志详细信息
4. 参考本文档的故障排除部分

---

**最后更新**: 2025-01-01
**版本**: v1.0.0
