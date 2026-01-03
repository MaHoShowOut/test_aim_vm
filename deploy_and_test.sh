#!/bin/bash

# Alibaba Cloud Linux 3.21.04 测试环境自动部署和测试脚本
# 该脚本按顺序执行：解压环境包 -> 激活环境 -> 检查环境 -> 运行测试

# 设置脚本遇到错误时退出
set -e

# 输出分隔符函数
print_separator() {
    echo "============================================================"
}

# 输出带时间戳的日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 主函数
main() {
    log "开始 Alibaba Cloud Linux 3.21.04 测试环境部署和测试流程"

    # 步骤1: 切换到项目目录
    print_separator
    log "步骤1: 切换到项目目录 /opt/test_project"
    cd /opt/test_project || {
        log "错误: 无法切换到 /opt/test_project 目录"
        exit 1
    }
    log "成功切换到目录: $(pwd)"

    # 步骤2: 解压虚拟环境包
    print_separator
    log "步骤2: 解压虚拟环境包 test_env.tar.gz"
    if [ ! -f "test_env.tar.gz" ]; then
        log "错误: test_env.tar.gz 文件不存在"
        exit 1
    fi

    log "开始解压文件..."
    tar -xzf "test_env.tar.gz"
    log "虚拟环境解压完成"

    # 验证解压结果
    if [ ! -d "test_env" ]; then
        log "错误: test_env 目录未创建"
        exit 1
    fi
    log "验证解压结果: test_env 目录存在"

    # 步骤3: 激活虚拟环境
    print_separator
    log "步骤3: 激活Python虚拟环境"
    source test_env/bin/activate
    log "虚拟环境已激活: $VIRTUAL_ENV"

    # 验证Python版本
    PYTHON_VERSION=$(python --version 2>&1)
    log "Python版本: $PYTHON_VERSION"

    # 步骤4: 运行环境检查
    print_separator
    log "步骤4: 运行环境完整性检查"
    log "执行命令: python run_tests.py --check-env"

    # 执行环境检查并捕获输出
    ENV_CHECK_OUTPUT=$(python run_tests.py --check-env 2>&1)
    ENV_CHECK_EXIT_CODE=$?

    echo "$ENV_CHECK_OUTPUT"

    if [ $ENV_CHECK_EXIT_CODE -ne 0 ]; then
        log "错误: 环境检查失败 (退出码: $ENV_CHECK_EXIT_CODE)"
        exit 1
    fi
    log "环境检查通过"

    # 步骤5: 运行完整测试
    print_separator
    log "步骤5: 运行完整测试套件"
    log "执行命令: python run_tests.py"

    # 创建测试报告文件名（带时间戳）
    TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
    REPORT_FILE="test_report_${TIMESTAMP}.txt"

    log "测试报告将保存到: $REPORT_FILE"

    # 执行完整测试并同时输出到屏幕和文件
    {
        echo "Alibaba Cloud Linux 3.21.04 测试执行报告"
        echo "生成时间: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "执行环境: $VIRTUAL_ENV"
        echo "Python版本: $PYTHON_VERSION"
        echo ""
        print_separator
        echo "测试执行结果:"
        print_separator
    } > "$REPORT_FILE"

    # 执行测试并将输出同时发送到屏幕和文件
    python run_tests.py 2>&1 | tee -a "$REPORT_FILE"

    TEST_EXIT_CODE=${PIPESTATUS[0]}

    {
        echo ""
        print_separator
        echo "测试执行完成"
        echo "退出码: $TEST_EXIT_CODE"
        echo "报告文件: $REPORT_FILE"
        echo "完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
    } >> "$REPORT_FILE"

    print_separator
    log "测试执行完成"

    if [ $TEST_EXIT_CODE -eq 0 ]; then
        log "✅ 所有测试通过！"
        log "📄 详细报告已保存到: $REPORT_FILE"
        echo ""
        echo "🎉 部署和测试流程完全成功！"
        echo "📊 测试报告: $REPORT_FILE"
    else
        log "❌ 测试执行失败 (退出码: $TEST_EXIT_CODE)"
        log "📄 错误详情请查看: $REPORT_FILE"
        exit $TEST_EXIT_CODE
    fi
}

# 显示使用帮助
show_help() {
    echo "Alibaba Cloud Linux 3.21.04 测试环境自动部署和测试脚本"
    echo ""
    echo "此脚本按顺序执行以下步骤:"
    echo "  1. 切换到 /opt/test_project 目录"
    echo "  2. 解压 test_env.tar.gz 虚拟环境包"
    echo "  3. 激活Python虚拟环境"
    echo "  4. 运行环境完整性检查"
    echo "  5. 运行完整测试套件"
    echo ""
    echo "生成的测试报告将保存为 test_report_YYYYMMDD_HHMMSS.txt"
    echo ""
    echo "使用方法:"
    echo "  ./deploy_and_test.sh        # 运行完整流程"
    echo "  ./deploy_and_test.sh --help # 显示此帮助信息"
}

# 参数处理
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    *)
        # 执行主函数
        main "$@"
        ;;
esac
