"""
Prompts utilisateur épurés (affichage UI) pour le coaching.
Séparés des prompts IA détaillés.
"""

from typing import Dict

UserMessage = Dict[str, str]

USER_MESSAGES: Dict[str, UserMessage] = {
    "vision": {
        "greeting": "👁️ Votre Vision",
        "question": "Quel rêve voulez-vous réaliser avec votre business ?",
        "choice1": "Créer un service qui facilite la vie de ma communauté",
        "choice2": "Lancer un projet à impact local",
        "choice3": "Développer une marque reconnue dans mon secteur",
    },
    "mission": {
        "greeting": "🎯 Votre Mission",
        "question": "Comment allez-vous concrétiser cette vision au quotidien ?",
        "choice1": "Offrir un service fiable et accessible",
        "choice2": "Proposer une expérience client remarquable",
        "choice3": "Innover pour résoudre un problème précis",
    },
    "clientele": {
        "greeting": "👥 Votre Clientèle",
        "question": "Qui voulez-vous servir en priorité ?",
        "choice1": "Familles et particuliers de mon quartier",
        "choice2": "Professionnels / bureaux environnants",
        "choice3": "Communauté en ligne ou niche spécialisée",
    },
    "differentiation": {
        "greeting": "⭐ Votre Différenciation",
        "question": "Qu’est-ce qui vous rend unique par rapport aux autres ?",
        "choice1": "Qualité supérieure et service personnalisé",
        "choice2": "Prix maîtrisé avec forte valeur ajoutée",
        "choice3": "Engagement local / durable / innovation produit",
    },
    "offre": {
        "greeting": "💼 Votre Offre",
        "question": "Quelle promesse concrète faites-vous à vos clients ?",
        "choice1": "Un forfait clair et facile à comprendre",
        "choice2": "Une solution clé en main avec support",
        "choice3": "Une offre flexible adaptée aux besoins",
    },
}


def get_user_message(step: str) -> Dict[str, str]:
    """
    Retourne un message épuré : greeting, question, choices.
    Fallback sur vision si step inconnu.
    """
    msg = USER_MESSAGES.get(step, USER_MESSAGES["vision"])
    return {
        "user_message": f"{msg['greeting']}\n\n{msg['question']}",
        "choices": [msg["choice1"], msg["choice2"], msg["choice3"]],
    }
