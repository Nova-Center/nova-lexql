# LexQL - JSON Query Language

LexQL est un langage de requête original conçu pour manipuler des documents JSON de manière intuitive, combinant la simplicité de SQL avec la flexibilité du JSON.

## Syntaxe de base

```
// Sélection simple
SELECT FROM users WHERE age > 30;

// Sélection avec projection
SELECT name, age FROM users WHERE city == "Paris";

// Sélection avec chemin JSON
SELECT details.skills FROM users WHERE details.department == "IT";

// Agrégation
COUNT FROM users WHERE salary > 45000;
AVG salary FROM users;

// Jointure
JOIN users, orders ON users.id == orders.user_id;

// Mise à jour
UPDATE users SET salary = 50000 WHERE id == 1;

// Insertion
INSERT INTO users VALUES {
    "id": 4,
    "name": "David",
    "age": 29
};

// Suppression
DELETE FROM users WHERE age < 25;
```

## Caractéristiques uniques

1. **Navigation JSON native**: Accès aux propriétés imbriquées avec la notation point
2. **Opérations sur les tableaux**: Manipulation directe des tableaux JSON
3. **Expressions conditionnelles flexibles**: Support des opérateurs logiques et de comparaison
4. **Format de sortie personnalisable**: Résultats en JSON ou en tableau

## Installation

1. Assurez-vous d'avoir Python 3.x installé
2. Installez les dépendances:

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
python lexql.py fichier.lql
```

## Exemple

```sql
// Exemple de requête LexQL
SELECT name, details.skills
FROM users
WHERE salary > 45000
AND "Python" IN details.skills;
```
