#!/bin/bash

# ==============================================================================
# FANTASMA WI-FI PRO - OPERATOR INTERFACE 🕸️📶
# Version: 6.0 "The Brain Edition" - SI SABE LO QUE DICES
# ==============================================================================

# --- COLORES ---
RED='\033[0;31m'
L_RED='\033[1;31m'
GREEN='\033[0;32m'
L_GREEN='\033[1;32m'
QUEEN_PINK='\033[38;5;206m'
QUEEN_GOLD='\033[38;5;220m'
NC='\033[0m'
BOLD='\033[1m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'

CURRENT_THEME=$GREEN
HEADER_COLOR=$L_GREEN

# --- EL CEREBRO DEL FANTASMA (Manejador de lenguaje) ---
function ghost_brain() {
    local input=$(echo "$1" | tr '[:upper:]' '[:lower:]')
    
    if [[ "$input" == *"activar"* || "$input" == *"prender"* ]]; then
        if [[ "$input" == *"usb"* || "$input" == *"redmi"* ]]; then
            start_hotspot "MATRIX-USB"
        elif [[ "$input" == *"bluetooth"* ]]; then
            start_hotspot "QUEEN-BT"
        else
            echo -e "${YELLOW}AI >> ¿Activar qué, jefa? ¿USB o Bluetooth?${NC}"
        fi
    elif [[ "$input" == *"apagar"* || "$input" == *"detener"* ]]; then
        stop_all
    elif [[ "$input" == *"ayuda"* || "$input" == *"qué haces"* ]]; then
        echo -e "${CYAN}AI >> Soy el Fantasma. Repito el Wi-Fi de tu Mac al Redmi."
        echo -e "Puedes decirme: 'activar usb', 'apagar todo' o 'cambiar tema'.${NC}"
    elif [[ "$input" == *"tema"* || "$input" == *"queen"* || "$input" == *"matrix"* ]]; then
        toggle_theme
    else
        echo -e "${RED}AI >> No capto eso de '$1', pero sigo intentando ser inteligente...${NC}"
    fi
    sleep 2
}

# --- ANIMACIÓN Y HEADER ---
function snake_intro() {
    clear
    local head="${L_RED}◈${NC}" ; local body="${RED}●${NC}"
    for i in {1..8}; do
        clear ; printf "%.s " $(seq 1 $i) ; echo -e "${head}${body}${body}" ; sleep 0.05
    done
    clear ; echo -e "${L_RED}${BOLD}"
    echo "  ███╗   ███╗ █████╗ ███╗   ██╗███████╗ █████╗ ███╗   ██╗ █████╗ "
    echo "  ████╗ ████║██╔══██╗████╗  ██║╚══███╔╝██╔══██╗████╗  ██║██╔══██╗"
    echo "  ██╔████╔██║███████║██╔██╗ ██║  ███╔╝ ███████║██╔██╗ ██║███████║"
    echo "  ██║╚██╔╝██║██╔══██║██║╚██╗██║ ███╔╝  ██╔══██║██║╚██╗██║██╔══██║"
    echo "  ██║ ╚═╝ ██║██║  ██║██║ ╚████║███████╗██║  ██║██║ ╚████║██║  ██║"
    echo -e "${NC}\n${YELLOW}          [ EL FANTASMA AHORA TE ESCUCHA ]${NC}" ; sleep 1
}

function matrix_log() {
    local msg=$1 ; local color=${2:-$CURRENT_THEME}
    echo -e "${color}[$(date +%H:%M:%S)] ⚡ ${msg}${NC}"
    sleep 0.1
}

function show_header() {
    echo -e "${HEADER_COLOR}${BOLD}"
    echo " 🕸️  F A N T A S M A   W I - F I   P R O   v 6 . 0 🕸️ "
    echo -e "     OPERADORA: ${QUEEN_GOLD}IYARI${NC} | STATUS: ${GREEN}READY${NC}"
    echo -e " ---------------------------------------------------${NC}"
}

function stop_all() {
    matrix_log "PURGANDO SISTEMA..." "$RED"
    sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.NetworkSharing.plist 2>/dev/null
    matrix_log "Todo en silencio."
}

function toggle_theme() {
    if [ "$CURRENT_THEME" == "$GREEN" ]; then
        CURRENT_THEME=$QUEEN_PINK ; HEADER_COLOR=$QUEEN_PINK
        matrix_log "Tema QUEEN cargado." "$QUEEN_PINK"
    else
        CURRENT_THEME=$GREEN ; HEADER_COLOR=$L_GREEN
        matrix_log "Tema MATRIX cargado." "$GREEN"
    fi
}

function start_hotspot() {
    local mode=$1
    matrix_log "Configurando $mode..."
    # Configurar via CLI (Simulado para que sea rápido)
    sudo defaults write /Library/Preferences/SystemConfiguration/com.apple.nat NAT -dict-add Enabled -int 1
    matrix_log "Inyectando reglas de ruteo..."
    open "x-apple.systempreferences:com.apple.Sharing-Settings.extension?Sharing"
    matrix_log "¡LISTO! Confirma el interruptor en la ventana que se abrió."
}

# --- INICIO ---
if [ -z "$SESSION_STARTED" ]; then
    snake_intro
    export SESSION_STARTED=1
fi

# --- BUCLE INFINITO ---
while true; do
    clear
    show_header
    echo -e "${CYAN}Escribe un comando (ej: 'activar usb', 'ayuda', 'apagar' o 'tema')${NC}"
    echo -e "O usa números: [1] USB | [2] BT | [3] STOP | [4] TEMA | [0] SALIR"
    echo ""
    read -p "DIME QUÉ HACER >> " cmd

    if [[ "$cmd" =~ ^[0-9]$ ]]; then
        case $cmd in
            1) start_hotspot "USB" ;;
            2) start_hotspot "BT" ;;
            3) stop_all ;;
            4) toggle_theme ;;
            0) exit 0 ;;
        esac
    else
        ghost_brain "$cmd"
    fi
done
