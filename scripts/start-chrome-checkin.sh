#!/bin/bash
#
# 启动 Chrome 浏览器并开启 CDP，用于自动签到
# 
# 使用方法:
#   ./start-chrome-checkin.sh [command]
#
# 命令:
#   start     - 启动 Chrome（默认）
#   stop      - 停止 Chrome
#   restart   - 重启 Chrome
#   status    - 查看状态
#   checkin   - 立即运行签到脚本
#

# 配置
PROFILE_DIR="${HOME}/.agent-browser/profiles/v2ex-nodesign"
LOG_DIR="${HOME}/.agent-browser/logs"
CDP_PORT=9222
CHROME_PID_FILE="${HOME}/.agent-browser/chrome.pid"

# 确保目录存在
mkdir -p "$PROFILE_DIR"
mkdir -p "$LOG_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Chrome 是否运行
check_chrome_running() {
    if [ -f "$CHROME_PID_FILE" ]; then
        PID=$(cat "$CHROME_PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        fi
    fi
    
    # 也检查端口
    if lsof -Pi :$CDP_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    fi
    
    return 1
}

# 启动 Chrome
start_chrome() {
    log_info "Starting Chrome with CDP..."
    
    if check_chrome_running; then
        log_warning "Chrome is already running!"
        return 1
    fi
    
    # Chrome 启动参数
    CHROME_CMD=(
        "google-chrome"
        "--remote-debugging-port=$CDP_PORT"
        "--user-data-dir=$PROFILE_DIR"
        "--no-first-run"
        "--no-default-browser-check"
        "--start-maximized"
        "--disable-gpu"
        "--disable-software-rasterizer"
    )
    
    # 启动 Chrome（后台运行）
    nohup "${CHROME_CMD[@]}" > "$LOG_DIR/chrome.log" 2>&1 &
    CHROME_PID=$!
    
    # 保存 PID
    echo $CHROME_PID > "$CHROME_PID_FILE"
    
    # 等待 Chrome 启动
    log_info "Waiting for Chrome to start..."
    for i in {1..30}; do
        sleep 1
        if check_chrome_running; then
            log_success "Chrome started successfully!"
            log_info "Profile: $PROFILE_DIR"
            log_info "CDP Port: $CDP_PORT"
            log_info "Logs: $LOG_DIR/chrome.log"
            return 0
        fi
    done
    
    log_error "Chrome failed to start within 30 seconds"
    return 1
}

# 停止 Chrome
stop_chrome() {
    log_info "Stopping Chrome..."
    
    if ! check_chrome_running; then
        log_warning "Chrome is not running!"
        return 1
    fi
    
    # 读取 PID
    if [ -f "$CHROME_PID_FILE" ]; then
        PID=$(cat "$CHROME_PID_FILE")
        if kill "$PID" 2>/dev/null; then
            log_success "Chrome stopped (PID: $PID)"
        fi
        rm -f "$CHROME_PID_FILE"
    fi
    
    # 确保所有 Chrome 进程停止
    pkill -f "chrome.*--remote-debugging-port=$CDP_PORT" 2>/dev/null || true
    
    log_success "Chrome stopped successfully!"
    return 0
}

# 查看状态
show_status() {
    echo ""
    echo "========================================"
    echo "  Chrome Checkin Service Status"
    echo "========================================"
    echo ""
    
    # 检查 Chrome 状态
    if check_chrome_running; then
        echo -e "Chrome Status: ${GREEN}Running${NC}"
        
        if [ -f "$CHROME_PID_FILE" ]; then
            PID=$(cat "$CHROME_PID_FILE")
            echo "PID: $PID"
        fi
        
        echo "CDP Port: $CDP_PORT"
        echo "Profile: $PROFILE_DIR"
    else
        echo -e "Chrome Status: ${RED}Not Running${NC}"
    fi
    
    echo ""
    echo "Log Directory: $LOG_DIR"
    echo "Chrome Log: $LOG_DIR/chrome.log"
    echo ""
    echo "========================================"
}

# 运行签到脚本
run_checkin() {
    log_info "Running checkin script..."
    
    if ! check_chrome_running; then
        log_error "Chrome is not running! Please start Chrome first."
        return 1
    fi
    
    # 运行 Python 签到脚本
    PYTHON_SCRIPT="${HOME}/.openclaw/workspace/AgentHub/examples/v2ex_nodesign_checkin.py"
    
    if [ -f "$PYTHON_SCRIPT" ]; then
        python3 "$PYTHON_SCRIPT"
    else
        log_error "Checkin script not found: $PYTHON_SCRIPT"
        return 1
    fi
}

# 主函数
main() {
    COMMAND="${1:-start}"
    
    case "$COMMAND" in
        start)
            start_chrome
            ;;
        stop)
            stop_chrome
            ;;
        restart)
            stop_chrome
            sleep 2
            start_chrome
            ;;
        status)
            show_status
            ;;
        checkin)
            run_checkin
            ;;
        help|--help|-h)
            echo ""
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  start     - Start Chrome with CDP (default)"
            echo "  stop      - Stop Chrome"
            echo "  restart   - Restart Chrome"
            echo "  status    - Show service status"
            echo "  checkin   - Run checkin script"
            echo "  help      - Show this help"
            echo ""
            ;;
        *)
            echo "Unknown command: $COMMAND"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
