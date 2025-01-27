#!/bin/bash

# Couleurs pour les messages
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Obtenir le chemin absolu du répertoire du script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${BLUE}🚀 Configuration de l'environnement EconoMarket...${NC}"

# Création de l'environnement virtuel s'il n'existe pas
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Création de l'environnement virtuel...${NC}"
    python3 -m venv venv
fi

# Activation de l'environnement virtuel
echo -e "${BLUE}🔧 Activation de l'environnement virtuel...${NC}"
source venv/bin/activate

# Mise à jour de pip
echo -e "${BLUE}⬆️  Mise à jour de pip...${NC}"
pip install --upgrade pip

# Installation des dépendances
echo -e "${BLUE}📚 Installation des dépendances...${NC}"
pip install -r requirements.txt

# Détection du shell actuel
CURRENT_SHELL=$(basename "$SHELL")
SHELL_PROFILE=""

case "$CURRENT_SHELL" in
    "zsh")
        SHELL_PROFILE="$HOME/.zshrc"
        ;;
    "bash")
        SHELL_PROFILE="$HOME/.bashrc"
        ;;
    *)
        echo -e "${RED}Shell non supporté ($CURRENT_SHELL). Veuillez activer manuellement l'environnement virtuel.${NC}"
        exit 1
        ;;
esac

# Vérifier si l'activation est déjà dans le fichier de profil
ACTIVATION_COMMAND="source $SCRIPT_DIR/venv/bin/activate"
if ! grep -q "$ACTIVATION_COMMAND" "$SHELL_PROFILE" 2>/dev/null; then
    echo -e "\n# EconoMarket Python Environment" >> "$SHELL_PROFILE"
    echo "$ACTIVATION_COMMAND" >> "$SHELL_PROFILE"
    echo -e "${GREEN}✅ Activation automatique ajoutée à $SHELL_PROFILE${NC}"
fi

echo -e "${GREEN}✅ Configuration terminée avec succès!${NC}"
echo -e "${BLUE}L'environnement virtuel sera automatiquement activé au prochain démarrage du terminal${NC}"
echo -e "${BLUE}Pour l'activer maintenant, exécutez:${NC}"
echo -e "${GREEN}source $SHELL_PROFILE${NC}"

# Activation immédiate
exec $SHELL 