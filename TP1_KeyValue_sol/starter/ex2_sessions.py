"""
TP1 - Exercice 2 : Gestion des sessions utilisateur avec TTL
Use Case : Sessions ShopFast
"""

import redis
import uuid
import time
from typing import Optional

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# TTL = 30 minutes = 1800 secondes
SESSION_TTL = 1800


def create_session(r, user_id) -> str:
    """
    Créer une nouvelle session utilisateur

    Clé Redis :
    "session:{session_id}"

    Valeur :
    user_id

    TTL :
    30 minutes
    """

    # Générer un identifiant unique
    session_id = str(uuid.uuid4())

    key = f"session:{session_id}"

    # Stocker avec expiration
    r.set(
        key,
        user_id,
        ex=SESSION_TTL
    )

    return session_id


def get_session(r, session_id) -> Optional[str]:
    """
    Récupérer une session

    Sliding expiration :
    si la session existe,
    renouveler automatiquement le TTL
    """

    key = f"session:{session_id}"

    user_id = r.get(key)

    # Session inexistante
    if not user_id:
        return None

    # Renouveler le TTL
    r.expire(key, SESSION_TTL)

    return user_id


def renew_session(r, session_id) -> bool:
    """
    Renouveler manuellement le TTL d'une session
    """

    key = f"session:{session_id}"

    # Vérifier existence
    if r.exists(key):

        r.expire(key, SESSION_TTL)

        return True

    return False


def delete_session(r, session_id):
    """
    Supprimer une session utilisateur
    """

    key = f"session:{session_id}"

    r.delete(key)


def get_session_ttl(r, session_id):
    """
    Retourner le TTL restant d'une session
    """

    key = f"session:{session_id}"

    return r.ttl(key)


if __name__ == "__main__":

    # Nettoyer Redis
    r.flushdb()

    print("=== Création Session ===")

    session_id = create_session(r, "user:42")

    print("Session ID :", session_id)

    print("\n=== Lecture Session ===")

    user = get_session(r, session_id)

    print("Utilisateur :", user)

    print("\n=== TTL restant ===")

    ttl = get_session_ttl(r, session_id)

    print(f"TTL : {ttl} secondes")

    print("\n=== Renouvellement Session ===")

    success = renew_session(r, session_id)

    print("Session renouvelée :", success)

    ttl = get_session_ttl(r, session_id)

    print(f"Nouveau TTL : {ttl} secondes")

    print("\n=== Suppression Session ===")

    delete_session(r, session_id)

    user = get_session(r, session_id)

    print("Session après suppression :", user)
