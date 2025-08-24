#!/bin/bash

# Script de déploiement automatisé Genesis AI - Staging
# Usage: ./deploy-staging.sh

set -e

echo "🚀 Déploiement Genesis AI Staging - Début"
echo "========================================"

# Variables
GENESIS_REPO="https://github.com/digitalcigit/digitalcloud360_generis.git"
DEPLOY_DIR="/opt/genesis-ai"
BACKUP_DIR="/opt/backups/genesis-ai"

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction d'affichage
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérification prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    if ! command -v git &> /dev/null; then
        log_error "Git n'est pas installé"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    log_info "✅ Tous les prérequis sont satisfaits"
}

# Backup de l'installation précédente si elle existe
backup_previous() {
    if [ -d "$DEPLOY_DIR" ]; then
        log_warn "Installation précédente détectée, création backup..."
        sudo mkdir -p "$BACKUP_DIR"
        sudo cp -r "$DEPLOY_DIR" "$BACKUP_DIR/genesis-ai-$(date +%Y%m%d_%H%M%S)"
        log_info "✅ Backup créé dans $BACKUP_DIR"
    fi
}

# Clone ou mise à jour du repository
setup_repository() {
    log_info "Configuration du repository..."
    
    if [ -d "$DEPLOY_DIR" ]; then
        log_info "Mise à jour du code existant..."
        cd "$DEPLOY_DIR"
        sudo git fetch origin
        sudo git reset --hard origin/master
    else
        log_info "Clone du repository Genesis AI..."
        sudo git clone "$GENESIS_REPO" "$DEPLOY_DIR"
    fi
    
    cd "$DEPLOY_DIR"
    log_info "✅ Repository configuré - Commit: $(git rev-parse --short HEAD)"
}

# Configuration des variables d'environnement
setup_environment() {
    log_info "Configuration de l'environnement staging..."
    
    cd "$DEPLOY_DIR"
    
    # Copier le fichier staging template
    sudo cp .env.staging .env
    
    log_warn "⚠️  IMPORTANT: Configurer les clés API dans .env"
    log_warn "   - DIGITALCLOUD360_SERVICE_SECRET"
    log_warn "   - GENESIS_AI_SECRET_KEY" 
    log_warn "   - OPENAI_API_KEY"
    log_warn "   - TAVILY_API_KEY"
    log_warn "   - LOGOAI_API_KEY"
    
    echo "Voulez-vous configurer les variables maintenant? (y/n)"
    read -r configure_now
    
    if [ "$configure_now" = "y" ] || [ "$configure_now" = "Y" ]; then
        sudo nano .env
    fi
}

# Arrêt des services existants
stop_existing_services() {
    log_info "Arrêt des services Genesis AI existants..."
    cd "$DEPLOY_DIR"
    
    if sudo docker-compose -f docker-compose.staging.yml ps | grep -q "Up"; then
        sudo docker-compose -f docker-compose.staging.yml down
        log_info "✅ Services arrêtés"
    else
        log_info "Aucun service en cours d'exécution"
    fi
}

# Construction et démarrage des services
start_services() {
    log_info "Construction et démarrage des services Genesis AI..."
    cd "$DEPLOY_DIR"
    
    # Construction des images
    sudo docker-compose -f docker-compose.staging.yml build --no-cache
    
    # Démarrage des services
    sudo docker-compose -f docker-compose.staging.yml up -d
    
    log_info "✅ Services Genesis AI démarrés"
}

# Vérification du déploiement
verify_deployment() {
    log_info "Vérification du déploiement..."
    
    # Attendre que les services démarrent
    sleep 30
    
    # Test health check
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        log_info "✅ Genesis AI répond sur http://localhost:8001"
    else
        log_error "❌ Genesis AI ne répond pas - Vérifier les logs"
        sudo docker-compose -f docker-compose.staging.yml logs genesis-ai
        exit 1
    fi
    
    # Affichage du statut des containers
    log_info "Statut des containers:"
    sudo docker-compose -f docker-compose.staging.yml ps
}

# Migration de la base de données
run_migrations() {
    log_info "Exécution des migrations de base de données..."
    cd "$DEPLOY_DIR"
    
    # Attendre que la DB soit prête
    sleep 10
    
    sudo docker-compose -f docker-compose.staging.yml exec -T genesis-ai alembic upgrade head
    log_info "✅ Migrations appliquées"
}

# Affichage des informations de connexion
show_connection_info() {
    log_info "🎉 Déploiement Genesis AI Staging terminé avec succès!"
    echo "========================================================"
    echo "📍 URL Genesis AI: http://$(hostname -I | awk '{print $1}'):8001"
    echo "📍 URL locale: http://localhost:8001"
    echo "📍 Health Check: http://localhost:8001/health"
    echo "📍 Documentation API: http://localhost:8001/docs"
    echo ""
    echo "🔍 Commandes utiles:"
    echo "   - Logs: sudo docker-compose -f docker-compose.staging.yml logs -f"
    echo "   - Arrêt: sudo docker-compose -f docker-compose.staging.yml down"  
    echo "   - Redémarrage: sudo docker-compose -f docker-compose.staging.yml restart"
    echo ""
    echo "⚠️  N'oubliez pas de configurer les clés API dans .env si pas fait"
}

# Exécution principale
main() {
    check_prerequisites
    backup_previous
    setup_repository
    setup_environment
    stop_existing_services
    start_services
    run_migrations
    verify_deployment
    show_connection_info
}

# Gestion des erreurs
trap 'log_error "Erreur durant le déploiement à la ligne $LINENO"' ERR

# Exécution
main "$@"
