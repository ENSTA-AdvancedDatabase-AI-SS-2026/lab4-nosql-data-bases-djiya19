"""
TP1 - Exercice 3 : Pattern Cache-Aside avec TTL
Use Case : Cache des pages produits ShopFast
"""

import redis
import json
import time
from typing import Optional

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def slow_db_get_product(product_id: int) -> Optional[dict]:
    """Simule une requête PostgreSQL lente (2 secondes)"""

    time.sleep(2)

    products = {
        1: {"id": 1, "name": "Samsung Galaxy A54", "price": 65000, "stock": 15},
        2: {"id": 2, "name": "Laptop HP 15-inch", "price": 120000, "stock": 8},
        3: {"id": 3, "name": "Casque JBL Bluetooth", "price": 12000, "stock": 50},
        4: {"id": 4, "name": "Clavier Mécanique", "price": 8000, "stock": 30},
    }

    return products.get(product_id)


def get_product_cached(r, product_id: int, ttl: int = 600) -> Optional[dict]:
    """
    Pattern Cache-Aside :
    1. Chercher dans Redis (clé: "product_cache:{product_id}")
    2. Si MISS → chercher dans slow_db → stocker dans Redis avec TTL
    3. Retourner le produit
    4. Afficher si c'est un HIT ou MISS avec la latence
    """

    start = time.time()

    key = f"product_cache:{product_id}"

    # -----------------------------------
    # Chercher dans le cache Redis
    # -----------------------------------
    cached_product = r.get(key)

    if cached_product:

        # CACHE HIT
        product = json.loads(cached_product)

        elapsed = (time.time() - start) * 1000

        print(f"CACHE HIT ({elapsed:.2f} ms)")

        return product

    # -----------------------------------
    # CACHE MISS
    # -----------------------------------
    product = slow_db_get_product(product_id)

    # Stocker dans Redis si produit trouvé
    if product:

        r.set(
            key,
            json.dumps(product),
            ex=ttl
        )

    elapsed = (time.time() - start) * 1000

    print(f"CACHE MISS ({elapsed:.2f} ms)")

    return product


def invalidate_product_cache(r, product_id: int):
    """Supprimer le cache d'un produit (après mise à jour en DB)"""

    key = f"product_cache:{product_id}"

    r.delete(key)

    print(f"Cache supprimé pour le produit {product_id}")


def benchmark_cache(r, product_id: int, iterations: int = 20):
    """
    Effectuer 'iterations' appels à get_product_cached
    Afficher :
    - Temps moyen cache HIT
    - Temps moyen cache MISS
    - Taux de cache hit (%)
    """

    hit_times = []
    miss_times = []

    hits = 0
    misses = 0

    # Nettoyer le cache avant benchmark
    invalidate_product_cache(r, product_id)

    for i in range(iterations):

        start = time.time()

        key = f"product_cache:{product_id}"

        # Vérifier avant appel si déjà en cache
        is_hit = r.exists(key)

        get_product_cached(r, product_id)

        elapsed = (time.time() - start) * 1000

        if is_hit:

            hits += 1
            hit_times.append(elapsed)

        else:

            misses += 1
            miss_times.append(elapsed)

    # -----------------------------------
    # Calculs statistiques
    # -----------------------------------
    avg_hit = sum(hit_times) / len(hit_times) if hit_times else 0

    avg_miss = sum(miss_times) / len(miss_times) if miss_times else 0

    hit_rate = (hits / iterations) * 100

    print("\n=== Résultats Benchmark ===")

    print(f"Nombre HIT : {hits}")
    print(f"Nombre MISS : {misses}")

    print(f"Temps moyen HIT : {avg_hit:.2f} ms")
    print(f"Temps moyen MISS : {avg_miss:.2f} ms")

    print(f"Taux de cache HIT : {hit_rate:.2f} %")


if __name__ == "__main__":

    r.flushdb()

    print("=== Test Cache-Aside ===")

    print("\nPremier appel (MISS attendu):")

    product = get_product_cached(r, 1)

    print(product)

    print("\nDeuxième appel (HIT attendu):")

    product = get_product_cached(r, 1)

    print(product)

    print("\n=== Benchmark ===")

    benchmark_cache(r, 1, iterations=10)
