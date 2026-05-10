# TP1 Redis — Rapport

## 1. Comparaison des performances

### Cache MISS
Le premier accès aux données passe par PostgreSQL simulé.
Temps moyen : environ 2 secondes.

### Cache HIT
Les accès suivants passent par Redis.
Temps moyen : quelques millisecondes.

### Conclusion
Redis améliore fortement les performances et réduit la charge sur la base de données.

---

## 2. Choix des structures Redis

### Hash
Utilisé pour les produits et paniers car les données sont structurées en clé/valeur.

### List
Utilisé pour l’historique de navigation car l’ordre des visites est important.

### Set
Utilisé pour les catégories afin d’éviter les doublons.

### Sorted Set
Utilisé pour le classement des ventes avec un score numérique.

---

## 3. Gestion des sessions

Les sessions sont stockées avec un TTL de 30 minutes.
Le mécanisme de sliding expiration renouvelle automatiquement la session lors de l’activité utilisateur.

---

## 4. Pipeline et Transactions

### Pipeline
Permet de réduire les allers-retours réseau et accélérer les insertions massives.

### Transactions
Garantissent l’atomicité lors des commandes :
- diminution du stock
- mise à jour du classement

---

## 5. Questions de réflexion

### Que se passe-t-il si Redis redémarre ?

Les données en mémoire peuvent être perdues si la persistance Redis n’est pas activée.

---

### Comment gérer la cohérence cache/DB en cas d’accès concurrent ?

On peut utiliser :
- invalidation du cache
- transactions
- verrouillage
- stratégie write-through

---

### Quand un TTL trop court devient problématique ?

Un TTL trop court provoque :
- beaucoup de cache miss
- surcharge de la base PostgreSQL
- perte du bénéfice du cache
