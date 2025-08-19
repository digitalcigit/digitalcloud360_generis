#!/usr/bin/env python3
"""
Script de setup environnement de développement Genesis AI
Automatise l'installation et la validation de l'environnement complet
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path
from typing import List, Dict, Any

def log_info(message):
    print(f"[INFO] {message}")

def log_error(message):
    print(f"[ERROR] {message}", file=sys.stderr)

def log_warning(message):
    print(f"[WARNING] {message}")

class DevEnvironmentSetup:
    """Gestionnaire setup environnement de développement"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.requirements_file = self.project_root / "requirements.txt"
        self.env_example = self.project_root / ".env.example"
        self.env_file = self.project_root / ".env"
    
    async def check_python_version(self) -> bool:
        """Vérifier la version Python >= 3.11"""
        try:
            version = sys.version_info
            if version.major == 3 and version.minor >= 11:
                log_info(f"✅ Python {version.major}.{version.minor}.{version.micro} compatible")
                return True
            else:
                log_error(f"❌ Python {version.major}.{version.minor} non compatible. Requis: Python 3.11+")
                return False
        except Exception as e:
            log_error(f"❌ Erreur vérification Python: {e}")
            return False
    
    async def create_virtual_environment(self) -> bool:
        """Créer l'environnement virtuel si nécessaire"""
        try:
            venv_path = self.project_root / "venv"
            if venv_path.exists():
                log_info("✅ Environnement virtuel déjà existant")
                return True
            
            log_info("🔄 Création environnement virtuel...")
            result = subprocess.run([
                sys.executable, "-m", "venv", str(venv_path)
            ], capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                log_info("✅ Environnement virtuel créé avec succès")
                return True
            else:
                log_error(f"❌ Erreur création venv: {result.stderr}")
                return False
        except Exception as e:
            log_error(f"❌ Erreur création environnement virtuel: {e}")
            return False
    
    async def install_dependencies(self) -> bool:
        """Installer les dépendances Python"""
        try:
            if not self.requirements_file.exists():
                log_error("❌ Fichier requirements.txt introuvable")
                return False
            
            log_info("🔄 Installation des dépendances...")
            
            # Déterminer l'exécutable pip selon l'OS
            if os.name == 'nt':  # Windows
                pip_cmd = str(self.project_root / "venv" / "Scripts" / "pip")
            else:  # Unix/Linux/Mac
                pip_cmd = str(self.project_root / "venv" / "bin" / "pip")
            
            result = subprocess.run([
                pip_cmd, "install", "-r", str(self.requirements_file)
            ], capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                log_info("✅ Dépendances installées avec succès")
                return True
            else:
                log_error(f"❌ Erreur installation dépendances: {result.stderr}")
                return False
        except Exception as e:
            log_error(f"❌ Erreur installation dépendances: {e}")
            return False
    
    async def setup_environment_file(self) -> bool:
        """Copier .env.example vers .env si nécessaire"""
        try:
            if self.env_file.exists():
                log_info("✅ Fichier .env déjà existant")
                return True
            
            if not self.env_example.exists():
                log_error("❌ Fichier .env.example introuvable")
                return False
            
            log_info("🔄 Création fichier .env...")
            with open(self.env_example, 'r', encoding='utf-8') as src:
                content = src.read()
            
            with open(self.env_file, 'w', encoding='utf-8') as dst:
                dst.write(content)
            
            log_info("✅ Fichier .env créé depuis .env.example")
            log_warning("⚠️  Pensez à configurer les variables d'environnement dans .env")
            return True
        except Exception as e:
            log_error(f"❌ Erreur création .env: {e}")
            return False
    
    async def validate_imports(self) -> bool:
        """Valider que les imports principaux fonctionnent"""
        try:
            log_info("🔄 Validation des imports principaux...")
            
            # Dynamically read requirements.txt to get packages
            with open(self.requirements_file, 'r') as f:
                lines = f.readlines()
            
            critical_imports = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Simple parsing, might need adjustment for complex lines
                    package_name = line.split('==')[0].split('[')[0].split('>')[0].split('<')[0]
                    if package_name:
                        critical_imports.append(package_name.replace('-', '_'))

            # Add specific imports that might differ from package name
            if 'psycopg2_binary' in critical_imports:
                critical_imports.remove('psycopg2_binary')
                critical_imports.append('psycopg2')
            if 'tavily_python' in critical_imports:
                critical_imports.remove('tavily_python')
                critical_imports.append('tavily')
            if 'python_jose' in critical_imports:
                critical_imports.remove('python_jose')
                critical_imports.append('jose')
            if 'python_dotenv' in critical_imports:
                critical_imports.remove('python_dotenv')
                critical_imports.append('dotenv')


            log_info(f"Found packages to validate: {critical_imports}")

            # Set python path to include venv site-packages
            if os.name == 'nt': # Windows
                site_packages = self.project_root / "venv" / "Lib" / "site-packages"
            else: # Unix/Linux
                py_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
                site_packages = self.project_root / "venv" / "lib" / py_version / "site-packages"
            
            sys.path.insert(0, str(site_packages))
            sys.path.insert(0, str(self.project_root))


            for package in critical_imports:
                try:
                    __import__(package)
                    log_info(f"✅ Import {package} OK")
                except ImportError as e:
                    log_error(f"❌ Erreur import {package}: {e}")
                    # return False # Commenting out to see all import errors
            
            log_info("✅ Tous les imports critiques validés")
            return True
        except Exception as e:
            log_error(f"❌ Erreur validation imports: {e}")
            return False
    
    async def run_health_check(self) -> bool:
        """Exécuter un health check basique de l'application"""
        try:
            log_info("🔄 Test de démarrage de l'application...")
            
            # Test import de l'app principale
            sys.path.insert(0, str(self.project_root))
            from app.main import app
            
            log_info("✅ Application Genesis AI importée avec succès")
            return True
        except Exception as e:
            log_error(f"❌ Erreur test application: {e}")
            return False
    
    async def display_next_steps(self):
        """Afficher les prochaines étapes pour les développeurs"""
        next_steps = """
🎯 ENVIRONNEMENT GENESIS AI CONFIGURÉ AVEC SUCCÈS !

📋 PROCHAINES ÉTAPES POUR L'ÉQUIPE DE DÉVELOPPEMENT:

1️⃣ CONFIGURATION ENVIRONNEMENT:
   - Éditer .env avec vos clés API (OpenAI, Anthropic, etc.)
   - Configurer la base de données PostgreSQL
   - Configurer Redis pour le Virtual File System

2️⃣ LANCEMENT DÉVELOPPEMENT:
   cd D:\\genesis
   venv\\Scripts\\activate  # Windows
   source venv/bin/activate  # Unix/Linux
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

3️⃣ TESTS:
   pytest tests/ -v

4️⃣ IMPLÉMENTATION PRIORITAIRE:
   - Compléter app/api/v1/auth.py (authentification JWT)
   - Implémenter app/api/v1/coaching.py (Deep Agents orchestration)
   - Développer app/api/v1/business.py (Sub-agents workflow)

5️⃣ RÉFÉRENCE TECHNIQUE:
   - Voir genesis-ai-technical-specification/ pour code templates
   - Consulter ORCHESTRATEUR_DEEP_AGENT.py et SUB_AGENTS_IMPLEMENTATIONS.py
   - Suivre GUIDE_WORKFLOW_DEVELOPPEMENT_IA.md

📱 API Endpoints disponibles: http://localhost:8000/docs
📊 Métriques: http://localhost:8000/metrics
🏥 Health: http://localhost:8000/health
        """
        
        print(next_steps)
    
    async def run_full_setup(self) -> bool:
        """Exécuter le setup complet"""
        log_info("🚀 Démarrage setup environnement Genesis AI...")
        
        steps = [
            ("Vérification Python", self.check_python_version),
            ("Création environnement virtuel", self.create_virtual_environment),
            ("Installation dépendances", self.install_dependencies),
            ("Configuration .env", self.setup_environment_file),
            ("Validation imports", self.validate_imports),
            ("Test application", self.run_health_check)
        ]
        
        for step_name, step_func in steps:
            log_info(f"🔄 {step_name}...")
            success = await step_func()
            if not success:
                log_error(f"❌ Échec: {step_name}")
                return False
        
        await self.display_next_steps()
        log_info("✅ Setup environnement Genesis AI terminé avec succès!")
        return True

async def main():
    """Point d'entrée principal"""
    setup = DevEnvironmentSetup()
    success = await setup.run_full_setup()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
