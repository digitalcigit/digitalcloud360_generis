#!/bin/bash

# Script de configuration des clés API - Genesis AI Staging
# Usage: ./setup-api-keys.sh

set -e

echo "🔑 Configuration des clés API Genesis AI"
echo "======================================"

ENV_FILE="/opt/genesis-ai/.env"

# Couleurs pour l'affichage
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier que le fichier .env existe
if [ ! -f "$ENV_FILE" ]; then
    log_error "Fichier .env non trouvé à $ENV_FILE"
    log_error "Exécutez d'abord le script deploy-staging.sh"
    exit 1
fi

log_info "Configuration des clés API dans $ENV_FILE"
echo ""

# Fonction pour mettre à jour une variable d'environnement
update_env_var() {
    local var_name=$1
    local var_description=$2
    local current_value=$(grep "^$var_name=" "$ENV_FILE" | cut -d'=' -f2)
    
    echo "----------------------------------------"
    echo "📝 Configuration: $var_description"
    echo "Variable: $var_name"
    
    if [ "$current_value" != "your_${var_name,,}_here" ] && [ "$current_value" != "" ]; then
        echo "Valeur actuelle: ${current_value:0:10}***"
        echo "Voulez-vous la modifier? (y/n) [n]: "
        read -r modify
        if [ "$modify" != "y" ] && [ "$modify" != "Y" ]; then
            log_info "Valeur conservée pour $var_name"
            return
        fi
    fi
    
    echo "Entrez la nouvelle valeur pour $var_name:"
    read -r new_value
    
    if [ -z "$new_value" ]; then
        log_warn "Valeur vide ignorée pour $var_name"
        return
    fi
    
    # Échapper les caractères spéciaux pour sed
    escaped_value=$(echo "$new_value" | sed 's/[[\.*^$()+?{|]/\\&/g')
    
    # Mettre à jour la variable dans le fichier .env
    if grep -q "^$var_name=" "$ENV_FILE"; then
        sudo sed -i "s|^$var_name=.*|$var_name=$escaped_value|" "$ENV_FILE"
    else
        echo "$var_name=$new_value" | sudo tee -a "$ENV_FILE" > /dev/null
    fi
    
    log_info "✅ $var_name configuré"
}

# Configuration des clés API une par une
echo "🚀 Nous allons configurer les clés API nécessaires pour Genesis AI"
echo ""

# 1. DigitalCloud360 Service Secret
update_env_var "DIGITALCLOUD360_SERVICE_SECRET" "Secret pour communication avec DigitalCloud360"

# 2. Genesis AI Secret Key
update_env_var "GENESIS_AI_SECRET_KEY" "Clé secrète Genesis AI (générer une clé forte)"

# 3. OpenAI API Key
echo ""
log_warn "Pour OpenAI API Key, rendez-vous sur: https://platform.openai.com/api-keys"
update_env_var "OPENAI_API_KEY" "Clé API OpenAI (commence par sk-)"

# 4. Tavily API Key
echo ""
log_warn "Pour Tavily API Key, rendez-vous sur: https://app.tavily.com/api-keys"
update_env_var "TAVILY_API_KEY" "Clé API Tavily pour recherche internet (commence par tvly-)"

# 5. LogoAI API Key
echo ""
log_warn "Pour LogoAI API Key, rendez-vous sur: https://www.logoai.com/api"
update_env_var "LOGOAI_API_KEY" "Clé API LogoAI pour génération de logos"

echo ""
echo "=========================================="
log_info "🎉 Configuration des clés API terminée!"
echo ""

# Afficher un résumé des variables configurées
log_info "Résumé des variables configurées:"
echo ""
grep -E "^(DIGITALCLOUD360_SERVICE_SECRET|GENESIS_AI_SECRET_KEY|OPENAI_API_KEY|TAVILY_API_KEY|LOGOAI_API_KEY)=" "$ENV_FILE" | while read -r line; do
    var_name=$(echo "$line" | cut -d'=' -f1)
    var_value=$(echo "$line" | cut -d'=' -f2)
    if [ "$var_value" != "your_${var_name,,}_here" ] && [ -n "$var_value" ]; then
        echo "  ✅ $var_name: ${var_value:0:10}***"
    else
        echo "  ❌ $var_name: NON CONFIGURÉ"
    fi
done

echo ""
log_info "Pour redémarrer Genesis AI avec les nouvelles clés:"
echo "  sudo docker-compose -f /opt/genesis-ai/docker-compose.staging.yml restart"
echo ""
log_info "Pour vérifier les logs:"
echo "  sudo docker-compose -f /opt/genesis-ai/docker-compose.staging.yml logs -f genesis-ai"
