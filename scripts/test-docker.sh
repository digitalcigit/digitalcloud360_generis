#!/bin/bash
# Script pour exécuter les tests avec Docker Test Profile T4.2

echo "🐋 Genesis AI - Docker Test Profile"
echo "===================================="

# Fonction d'aide
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commandes disponibles:"
    echo "  all            Exécuter tous les tests (défaut)"
    echo "  auth           Tests d'authentification uniquement"
    echo "  integrations   Tests d'intégration uniquement"
    echo "  coverage       Tests avec rapport de coverage"
    echo "  setup          Démarrer uniquement les services (test-db, redis)"
    echo "  cleanup        Nettoyer les conteneurs et volumes de test"
    echo "  logs           Voir les logs du service de test"
    echo "  shell          Ouvrir un shell dans le conteneur de test"
    echo ""
    echo "Exemples:"
    echo "  $0 all                    # Tous les tests"
    echo "  $0 auth                   # Tests auth seulement"
    echo "  $0 coverage               # Tests avec coverage"
    echo ""
}

# Vérifier que Docker est disponible
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Erreur: docker-compose n'est pas installé"
    exit 1
fi

# Commande par défaut
COMMAND=${1:-all}

case $COMMAND in
    "help"|"-h"|"--help")
        show_help
        exit 0
        ;;
    
    "setup")
        echo "🚀 Démarrage des services de test..."
        docker-compose -f docker-compose.test.yml up -d test-db redis
        echo "✅ Services test-db et redis démarrés"
        echo "📊 Status:"
        docker-compose -f docker-compose.test.yml ps test-db redis
        ;;
    
    "all")
        echo "🧪 Exécution de tous les tests..."
        docker-compose -f docker-compose.test.yml up --build genesis-test
        ;;
    
    "auth")
        echo "🔐 Tests d'authentification..."
        docker-compose -f docker-compose.test.yml up --build genesis-test-auth
        ;;
    
    "integrations")
        echo "🔗 Tests d'intégration..."
        docker-compose -f docker-compose.test.yml up --build genesis-test-integrations
        ;;
    
    "coverage")
        echo "📊 Tests avec coverage..."
        docker-compose -f docker-compose.test.yml up --build genesis-test-coverage
        ;;
    
    "cleanup")
        echo "🧹 Nettoyage des ressources de test..."
        docker-compose -f docker-compose.test.yml down -v
        docker volume prune -f
        echo "✅ Nettoyage terminé"
        ;;
    
    "logs")
        echo "📋 Logs du service de test..."
        docker-compose -f docker-compose.test.yml logs -f genesis-test
        ;;
    
    "shell")
        echo "🐚 Ouverture d'un shell dans le conteneur de test..."
        docker-compose -f docker-compose.test.yml run --rm genesis-test bash
        ;;
    
    *)
        echo "❌ Commande inconnue: $COMMAND"
        echo ""
        show_help
        exit 1
        ;;
esac