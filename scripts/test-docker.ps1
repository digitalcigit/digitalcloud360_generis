# Script PowerShell pour exécuter les tests avec Docker Test Profile T4.2

param(
    [string]$Command = "all"
)

Write-Host "🐋 Genesis AI - Docker Test Profile" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

# Fonction d'aide
function Show-Help {
    Write-Host "Usage: .\test-docker.ps1 [COMMAND]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Commandes disponibles:" -ForegroundColor Green
    Write-Host "  all            Exécuter tous les tests (défaut)" -ForegroundColor White
    Write-Host "  auth           Tests d'authentification uniquement" -ForegroundColor White
    Write-Host "  integrations   Tests d'intégration uniquement" -ForegroundColor White
    Write-Host "  coverage       Tests avec rapport de coverage" -ForegroundColor White
    Write-Host "  setup          Démarrer uniquement les services (test-db, redis)" -ForegroundColor White
    Write-Host "  cleanup        Nettoyer les conteneurs et volumes de test" -ForegroundColor White
    Write-Host "  logs           Voir les logs du service de test" -ForegroundColor White
    Write-Host "  shell          Ouvrir un shell dans le conteneur de test" -ForegroundColor White
    Write-Host ""
    Write-Host "Exemples:" -ForegroundColor Yellow
    Write-Host "  .\test-docker.ps1 all                    # Tous les tests" -ForegroundColor Gray
    Write-Host "  .\test-docker.ps1 auth                   # Tests auth seulement" -ForegroundColor Gray
    Write-Host "  .\test-docker.ps1 coverage               # Tests avec coverage" -ForegroundColor Gray
}

# Vérifier que Docker est disponible
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Erreur: docker-compose n'est pas installé" -ForegroundColor Red
    exit 1
}

switch ($Command.ToLower()) {
    "help" {
        Show-Help
        exit 0
    }
    
    "setup" {
        Write-Host "🚀 Démarrage des services de test..." -ForegroundColor Green
        docker-compose -f docker-compose.test.yml up -d test-db redis
        Write-Host "✅ Services test-db et redis démarrés" -ForegroundColor Green
        Write-Host "📊 Status:" -ForegroundColor Yellow
        docker-compose -f docker-compose.test.yml ps test-db redis
    }
    
    "all" {
        Write-Host "🧪 Exécution de tous les tests..." -ForegroundColor Green
        docker-compose -f docker-compose.test.yml up --build genesis-test
    }
    
    "auth" {
        Write-Host "🔐 Tests d'authentification..." -ForegroundColor Green
        docker-compose -f docker-compose.test.yml up --build genesis-test-auth
    }
    
    "integrations" {
        Write-Host "🔗 Tests d'intégration..." -ForegroundColor Green
        docker-compose -f docker-compose.test.yml up --build genesis-test-integrations
    }
    
    "coverage" {
        Write-Host "📊 Tests avec coverage..." -ForegroundColor Green
        docker-compose -f docker-compose.test.yml up --build genesis-test-coverage
    }
    
    "cleanup" {
        Write-Host "🧹 Nettoyage des ressources de test..." -ForegroundColor Yellow
        docker-compose -f docker-compose.test.yml down -v
        docker volume prune -f
        Write-Host "✅ Nettoyage terminé" -ForegroundColor Green
    }
    
    "logs" {
        Write-Host "📋 Logs du service de test..." -ForegroundColor Yellow
        docker-compose -f docker-compose.test.yml logs -f genesis-test
    }
    
    "shell" {
        Write-Host "🐚 Ouverture d'un shell dans le conteneur de test..." -ForegroundColor Yellow
        docker-compose -f docker-compose.test.yml run --rm genesis-test bash
    }
    
    default {
        Write-Host "❌ Commande inconnue: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
        exit 1
    }
}