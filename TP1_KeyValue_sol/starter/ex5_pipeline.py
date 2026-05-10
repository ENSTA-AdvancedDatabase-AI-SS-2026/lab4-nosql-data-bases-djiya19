"""
TP1 - Exercice 5 : Pipeline & Transactions Redis
Use Case : Commandes atomiques ShopFast
"""

import redis
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def bulk_insert_products(r, n: int = 1000):
    """
    Insérer plusieurs produits avec un pipeline Redis

    Objectif :
    réduire les allers-retours réseau
    """

    start = time.time()

    # Création du pipeline
    pipe = r.pipeline()

    for i in range(1, n + 1):

        key = f"product:{i}"

        pipe.hset(key, mapping={
            "name": f"Produit {i}",
            "price": i * 100,
            "stock": 50
        })

    # Exécution groupée
    pipe.execute()

    elapsed = (time.time() - start) * 1000

    print(f"{n} produits insérés en {elapsed:.2f} ms")


def initialize_stock(r, product_id, stock):
    """
    Initialiser le stock d'un produit
    """

    key = f"stock:{product_id}"

    r.set(key, stock)


def get_stock(r, product_id):
    """
    Lire le stock actuel
    """

    key = f"stock:{product_id}"

    stock = r.get(key)

    if stock is None:
        return 0

    return int(stock)


def process_order(r, product_id, quantity):
    """
    Transaction atomique Redis :

    1. Vérifier le stock
    2. Décrémenter le stock
    3. Ajouter les ventes au leaderboard

    Utiliser :
    WATCH + MULTI + EXEC
    """

    stock_key = f"stock:{product_id}"

    leaderboard_key = "leaderboard:sales"

    pipe = r.pipeline()

    while True:

        try:

            # Surveiller le stock
            pipe.watch(stock_key)

            current_stock = int(r.get(stock_key) or 0)

            print(f"Stock actuel : {current_stock}")

            # Vérification stock
            if current_stock < quantity:

                pipe.unwatch()

                return "Stock insuffisant"

            # Début transaction
            pipe.multi()

            # Réduire stock
            pipe.decrby(stock_key, quantity)

            # Ajouter ventes classement
            pipe.zincrby(
                leaderboard_key,
                quantity,
                product_id
            )

            # Exécution atomique
            pipe.execute()

            return "Commande validée"

        except redis.WatchError:

            print("Conflit détecté, nouvelle tentative...")


def get_top_sales(r):
    """
    Lire le classement des ventes
    """

    return r.zrevrange(
        "leaderboard:sales",
        0,
        -1,
        withscores=True
    )


if __name__ == "__main__":

    # Nettoyer Redis
    r.flushdb()

    print("=== TEST PIPELINE ===")

    bulk_insert_products(r, 1000)

    print("\n=== INITIALISATION STOCK ===")

    initialize_stock(r, 1, 20)

    print("Stock produit 1 :", get_stock(r, 1))

    print("\n=== TEST TRANSACTION ===")

    result = process_order(r, 1, 5)

    print("Résultat :", result)

    print("Nouveau stock :", get_stock(r, 1))

    print("\n=== TEST COMMANDE IMPOSSIBLE ===")

    result = process_order(r, 1, 50)

    print("Résultat :", result)

    print("\n=== CLASSEMENT VENTES ===")

    sales = get_top_sales(r)

    for product_id, score in sales:

        print(
            f"Produit #{product_id} → "
            f"{int(score)} ventes"
        )
