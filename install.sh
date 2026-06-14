#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# install.sh — Auto-installer for Google Drive Uploader Bot
# Tested on: Ubuntu 22.04 LTS
#
# ZERO-CONFLICT DESIGN:
#   Install dir : /opt/gdrive-uploader-bot          (unique name)
#   Python venv : /opt/gdrive-uploader-bot/.venv    (isolated)
#   systemd svc : gdrive-uploader.service           (unique name)
#   Docker ctr  : gdrive-bot-api                    (unique name)
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

info()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERR]${NC}   $*" >&2; exit 1; }

# ── Root check ────────────────────────────────────────────────────────────────
[[ $EUID -ne 0 ]] && error "Please run as root:  sudo bash install.sh"

# ── Unique identifiers ────────────────────────────────────────────────────────
INSTALL_DIR="/opt/gdrive-uploader-bot"
SERVICE_NAME="gdrive-uploader"
VENV_DIR="${INSTALL_DIR}/.venv"
DOCKER_CONTAINER="gdrive-bot-api"

echo -e "\n${BOLD}══════════════════════════════════════════════════${NC}"
echo -e "${BOLD}    Google Drive Uploader Bot — Auto Installer     ${NC}"
echo -e "${BOLD}══════════════════════════════════════════════════${NC}\n"

# ── Conflict detection ─────────────────────────────────────────────────────────
if systemctl is-active --quiet "${SERVICE_NAME}.service" 2>/dev/null; then
    warn "Service ${SERVICE_NAME}.service is already running."
    read -rp "$(echo -e "${YELLOW}Stop it and reinstall? [y/N]:${NC} ")" CONFIRM
    [[ "$CONFIRM" =~ ^[Yy]$ ]] || error "Aborted."
    systemctl stop "${SERVICE_NAME}.service" || true
fi

# ── 1. System packages ────────────────────────────────────────────────────────
info "Updating package lists…"
apt-get update -qq

info "Installing base system dependencies…"
apt-get install -y -qq \
    build-essential libssl-dev libffi-dev \
    git curl wget ca-certificates \
    gnupg lsb-release rsync software-properties-common

# ── Python 3.12 — required (Pyrogram + SQLAlchemy are incompatible with 3.14) ─
# Add deadsnakes PPA which provides Python 3.12 on all Ubuntu versions.
info "Adding deadsnakes PPA for Python 3.12…"
add-apt-repository -y ppa:deadsnakes/ppa
apt-get update -qq
apt-get install -y python3.12 python3.12-venv python3.12-dev

PYTHON_BIN="python3.12"
PY_VER=$("$PYTHON_BIN" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
success "Using Python $PY_VER"

# ── 2. Docker ─────────────────────────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
    info "Installing Docker…"
    curl -fsSL https://get.docker.com | bash -s
    systemctl enable --now docker
    success "Docker installed"
else
    success "Docker already present ($(docker --version | cut -d' ' -f3))"
fi

# ── 3. Collect configuration ───────────────────────────────────────────────────
echo -e "\n${BOLD}──── Required Bot Configuration ────${NC}\n"

prompt_required() {
    local var_name="$1" prompt_text="$2"
    local value=""
    while [[ -z "$value" ]]; do
        read -rp "$(echo -e "${YELLOW}${prompt_text}${NC}: ")" value
        [[ -z "$value" ]] && echo -e "  ${RED}This field is required.${NC}"
    done
    printf -v "$var_name" '%s' "$value"
}

prompt_optional() {
    local var_name="$1" prompt_text="$2" default="${3:-}"
    local value=""
    if [[ -n "$default" ]]; then
        read -rp "$(echo -e "${YELLOW}${prompt_text}${NC} [${default}]: ")" value
        value="${value:-$default}"
    else
        read -rp "$(echo -e "${YELLOW}${prompt_text}${NC} [skip]: ")" value
    fi
    printf -v "$var_name" '%s' "$value"
}

prompt_required BOT_TOKEN   "Telegram Bot Token (from @BotFather)"
prompt_required ADMIN_ID    "Your Telegram User ID (numeric)"
prompt_required API_ID      "Telegram API ID (from my.telegram.org)"
prompt_required API_HASH    "Telegram API Hash (from my.telegram.org)"

echo -e "\n${BOLD}──── Google OAuth2 — REQUIRED ────${NC}"
echo -e "  See ${CYAN}GOOGLE_SETUP.md${NC} for step-by-step instructions.\n"

prompt_required OAUTH_CLIENT_ID     "Google OAuth2 Client ID"
prompt_required OAUTH_CLIENT_SECRET "Google OAuth2 Client Secret"

echo -e "\n${BOLD}──── Optional ────${NC}\n"
prompt_optional LOCAL_API_URL   "Local Bot API Server URL" "http://localhost:8081"
prompt_optional FORCE_CH_1      "Force-join channel 1" "@webdw"
prompt_optional FORCE_CH_2      "Force-join channel 2" "@webdwCF"
prompt_optional RATE_MAX        "Rate limit: max uploads per window" "3"
prompt_optional RATE_WIN        "Rate limit: window seconds" "60"
prompt_optional DB_URL          "Database URL" "sqlite+aiosqlite:///bot.db"

# ── 4. Create install directory ────────────────────────────────────────────────
info "Creating install directory at ${INSTALL_DIR}…"
mkdir -p "${INSTALL_DIR}/temp"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
rsync -a --exclude='.git' --exclude='.venv' --exclude='__pycache__' \
    --exclude='*.session' --exclude='*.db' --exclude='.env' \
    "${SCRIPT_DIR}/" "${INSTALL_DIR}/"
success "Project files copied"

# ── 5. Python virtual environment ─────────────────────────────────────────────
info "Creating isolated Python virtual environment at ${VENV_DIR}…"
"$PYTHON_BIN" -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/pip" install --upgrade pip -q
"${VENV_DIR}/bin/pip" install -r "${INSTALL_DIR}/requirements.txt" -q
success "Python dependencies installed"

# ── 6. Write .env ─────────────────────────────────────────────────────────────
info "Writing .env (mode 600)…"
cat > "${INSTALL_DIR}/.env" <<EOF
# Auto-generated by install.sh on $(date '+%Y-%m-%d %H:%M:%S')

BOT_TOKEN=${BOT_TOKEN}
ADMIN_ID=${ADMIN_ID}
API_ID=${API_ID}
API_HASH=${API_HASH}

LOCAL_API_SERVER_URL=${LOCAL_API_URL}

FORCE_JOIN_CHANNEL_1=${FORCE_CH_1}
FORCE_JOIN_CHANNEL_2=${FORCE_CH_2}

DATABASE_URL=${DB_URL}

GOOGLE_OAUTH_CLIENT_ID=${OAUTH_CLIENT_ID}
GOOGLE_OAUTH_CLIENT_SECRET=${OAUTH_CLIENT_SECRET}
GOOGLE_OAUTH_REDIRECT_URI=http://localhost

RATE_LIMIT_MAX_UPLOADS=${RATE_MAX}
RATE_LIMIT_WINDOW_SECONDS=${RATE_WIN}
EOF
chmod 600 "${INSTALL_DIR}/.env"
success ".env written"

# ── 7. Local Telegram Bot API server (optional Docker container) ──────────────
info "Starting local Telegram Bot API container (${DOCKER_CONTAINER})…"
docker rm -f "${DOCKER_CONTAINER}" 2>/dev/null || true
docker run -d \
    --name "${DOCKER_CONTAINER}" \
    --restart unless-stopped \
    -p 8081:8081 \
    -e TELEGRAM_API_ID="${API_ID}" \
    -e TELEGRAM_API_HASH="${API_HASH}" \
    -v /var/lib/telegram-bot-api:/var/lib/telegram-bot-api \
    aiogram/telegram-bot-api:latest
success "Container ${DOCKER_CONTAINER} running on port 8081"

# ── 8. tgdrive CLI ────────────────────────────────────────────────────────────
info "Installing tgdrive management CLI…"
cp "${SCRIPT_DIR}/tgdrive" /usr/local/bin/tgdrive
chmod +x /usr/local/bin/tgdrive
success "tgdrive installed — use: tgdrive help"

# ── 9. systemd service ────────────────────────────────────────────────────────
info "Creating systemd service: ${SERVICE_NAME}.service…"
cat > "/etc/systemd/system/${SERVICE_NAME}.service" <<EOF
[Unit]
Description=Google Drive Uploader Telegram Bot
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=${INSTALL_DIR}
ExecStart=${VENV_DIR}/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "${SERVICE_NAME}"
systemctl restart "${SERVICE_NAME}"

sleep 3
if systemctl is-active --quiet "${SERVICE_NAME}"; then
    success "Service ${SERVICE_NAME} is RUNNING"
else
    warn "Service may still be starting. Check with:"
    echo -e "  journalctl -u ${SERVICE_NAME} -f"
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}  Installation complete!${NC}"
echo -e "${BOLD}══════════════════════════════════════════════════${NC}\n"
echo -e "  📂 Install path:     ${CYAN}${INSTALL_DIR}${NC}"
echo -e "  ⚙️  Service name:     ${CYAN}${SERVICE_NAME}.service${NC}"
echo -e ""
echo -e "  ${BOLD}tgdrive commands:${NC}"
echo -e "  📋 View logs:        ${CYAN}sudo tgdrive logs${NC}"
echo -e "  🔄 Restart:          ${CYAN}sudo tgdrive restart${NC}"
echo -e "  ⛔ Stop:             ${CYAN}sudo tgdrive stop${NC}"
echo -e "  ✏️  Edit config:      ${CYAN}sudo tgdrive env${NC}"
echo -e "  🔁 Update bot:       ${CYAN}sudo tgdrive update${NC}"
echo -e "\n  ⚠️  ${YELLOW}Make sure you followed GOOGLE_SETUP.md before starting the bot!${NC}\n"
