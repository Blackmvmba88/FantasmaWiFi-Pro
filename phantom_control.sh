#!/bin/bash

# --- CONFIGURACIÓN ESTÉTICA ---
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

clear
echo -e "${PURPLE}${BOLD}"
echo "  __                  _                                     _  __ _ "
echo " / _|                | |                                   | |/ _(_) "
echo "| |_ _   _ _ __   ___| |_ __ _ ___ _ __ ___   __ _  __      _| |_| |_ "
echo "|  _| | | | '_ \ / __| __/ _' / __| '_ ' _ \ / _' | \ \ /\ / /  _| | |"
echo "| | | |_| | | | | (__| || (_| \__ \ | | | | | (_| |  \ V  V /| | | | |"
echo "|_|  \__,_|_| |_|\___|\__\__,_|___/_| |_| |_|\__,_|   \_/\_/ |_| |_|_|"
echo -e "                   PRO EDITION - BY IYARI GOMEZ${NC}\n"

function check_status() {
    sharing_on=$(launchctl list | grep InternetSharing)
    if [ -z "$sharing_on" ]; then
        echo -e "Estado: [${RED}OFFLINE${NC}]"
    else
        echo -e "Estado: [${GREEN}ACTIVO - TRANSMITIENDO${NC}]"
    fi
}

echo -e "${CYAN}--- PANEL DE CONTROL ---${NC}"
check_status
echo ""
echo -e "${BOLD}1)${NC} Activar Fantasma por USB (Redmi/Cable)"
echo -e "${BOLD}2)${NC} Activar Fantasma por Bluetooth"
echo -e "${BOLD}3)${NC} Activar Fantasma por Antena Externa (Wi-Fi 2)"
echo -e "${BOLD}4)${NC} Desactivar Todo"
echo -e "${BOLD}5)${NC} Escanear Interfaces Disponibles"
echo -e "${BOLD}6)${NC} Salir"
echo ""
read -p "Elige una opción [1-6]: " opt

case $opt in
    1)
        echo -e "\n${BLUE}Buscando dispositivo USB...${NC}"
        # Aquí iría la lógica de activación rápida via defaults write
        echo "Lanzando Panel de Compartir para validación final..."
        open "x-apple.systempreferences:com.apple.Sharing-Settings.extension?Sharing"
        ;;
    2)
        echo -e "\n${BLUE}Iniciando puente Bluetooth PAN...${NC}"
        open "x-apple.systempreferences:com.apple.Sharing-Settings.extension?Sharing"
        ;;
    3)
        echo -e "\n${BLUE}Configurando Interfaz Dual...${NC}"
        networksetup -listallhardwareports
        ;;
    4)
        echo -e "\n${RED}Apagando el Fantasma...${NC}"
        sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.NetworkSharing.plist 2>/dev/null
        echo "Servicios detenidos."
        ;;
    5)
        echo -e "\n${CYAN}Interfaces de Hardware:${NC}"
        networksetup -listallhardwareports
        read -p "Presiona Enter para volver..."
        ./phantom_control.sh
        ;;
    *)
        exit
        ;;
esac
