#!/bin/bash
#
# 设置 V2ex 和 NodeSeek 自动签到环境
#
# 此脚本会自动：
# 1. 检查并安装 Chrome 浏览器
# 2. 创建专用的 Chrome Profile
# 3. 设置日志目录
# 4. 创建启动脚本
# 5. 配置开机自动启动
#

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 检查是否为 root 用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root. Some operations may require root privileges."
    fi
}

# 检查系统类型
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            OS="ubuntu"
        elif command -v yum &> /dev/null; then
            OS="centos"
        else
            OS="linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        OS="unknown"
    fi
    
    log_info "Detected OS: $OS"
}

# 检查 Chrome 是否已安装
check_chrome() {
    log_info "Checking if Chrome is installed..."
    
    if command -v google-chrome &> /dev/null; then
        CHROME_VERSION=$(google-chrome --version)
        log_success "Chrome is already installed: $CHROME_VERSION"
        return 0
    elif command -v google-chrome-stable &> /dev/null; then
        CHROME_VERSION=$(google-chrome-stable --version)
        log_success "Chrome is already installed: $CHROME_VERSION"
        return 0
    elif command -v chromium &> /dev/null; then
        CHROME_VERSION=$(chromium --version)
        log_success "Chromium is already installed: $CHROME_VERSION"
        return 0
    else
        log_warning "Chrome is not installed"
        return 1
    fi
}

# 安装 Chrome
install_chrome() {
    log_info "Installing Chrome..."
    
    case "$OS" in
        ubuntu)
            install_chrome_ubuntu
            ;;
        centos)
            install_chrome_centos
            ;;
        macos)
            install_chrome_macos
            ;;
        *)
            log_error "Unsupported OS for automatic Chrome installation"
            log_info "Please install Chrome manually from: https://www.google.com/chrome/"
            exit 1
            ;;
    esac
}

# 在 Ubuntu 上安装 Chrome
install_chrome_ubuntu() {
    log_info "Installing Chrome on Ubuntu/Debian..."
    
    # 添加 Chrome 官方仓库
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
    
    # 更新包列表并安装
    sudo apt-get update
    sudo apt-get install -y google-chrome-stable
    
    if [ $? -eq 0 ]; then
        log_success "Chrome installed successfully"
    else
        log_error "Failed to install Chrome"
        exit 1
    fi
}

# 在 CentOS 上安装 Chrome
install_chrome_centos() {
    log_info "Installing Chrome on CentOS/RHEL..."
    
    # 添加 Chrome 仓库
    sudo tee /etc/yum.repos.d/google-chrome.repo > /dev/null << 'EOF'
[google-chrome]
name=google-chrome
baseurl=http://dl.google.com/linux/chrome/rpm/stable/x86_64
enabled=1
gpgcheck=1
gpgkey=https://dl-ssl.google.com/linux/linux_signing_key.pub
EOF
    
    # 安装 Chrome
    sudo yum install -y google-chrome-stable
    
    if [ $? -eq 0 ]; then
        log_success "Chrome installed successfully"
    else
        log_error "Failed to install Chrome"
        exit 1
    fi
}

# 在 macOS 上安装 Chrome
install_chrome_macos() {
    log_info "Installing Chrome on macOS..."
    
    if command -v brew &> /dev/null; then
        brew install --cask google-chrome
        if [ $? -eq 0 ]; then
            log_success "Chrome installed successfully"
        else
            log_error "Failed to install Chrome with Homebrew"
            log_info "Please install Chrome manually from: https://www.google.com/chrome/"