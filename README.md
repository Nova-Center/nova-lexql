# LexQL

LexQL est un interpréteur SQL personnalisé qui permet d'effectuer des requêtes de type SQL sur des fichiers JSON. Il offre une syntaxe familière pour interroger et analyser des données JSON de manière simple et efficace.

## Fonctionnalités

- Requêtes `SELECT` avec support des champs imbriqués
- Filtrage avec `WHERE` et opérateurs de comparaison
- Support des opérations logiques `AND` et `OR`
- Opérateur `IN` pour la recherche dans les listes
- Fonctions d'agrégation : `COUNT`, `AVG`, `SUM`, `MIN`, `MAX`
- Support des chemins imbriqués avec la notation point (.)

## Installation

1. Clonez le dépôt :

```bash
git clone [url-du-repo]
cd nova-lexql
```

2. Créez un environnement virtuel et activez-le :

```bash
python -m venv venv
# Sur Windows
venv\Scripts\activate
# Sur Unix/MacOS
source venv/bin/activate
```

3. Installez les dépendances :

```bash
pip install -r requirements.txt
```

## Utilisation

Pour exécuter des requêtes LexQL, vous avez besoin de deux fichiers :

- Un fichier `.lql` contenant vos requêtes
- Un fichier `.json` contenant vos données

Exécutez le script avec la commande :

```bash
python lexql.py <fichier.lql> <fichier.json>
```

### Exemples de requêtes

1. Sélection simple avec condition :

```sql
SELECT name, details
FROM users
WHERE city == "Paris";
```

2. Utilisation de l'opérateur IN avec des champs imbriqués :

```sql
SELECT name, details.skills
FROM users
WHERE "Python" IN details.skills;
```

3. Comptage avec condition :

```sql
COUNT FROM users
WHERE salary > 45000;
```

4. Calcul de moyenne :

```sql
AVG salary FROM users;
```

5. Calcul du minimum :

```sql
MIN amount FROM orders;
```

6. Calcul du maximum :

```sql
MAX salary FROM users;
```

7. Calcul de la somme :

```sql
SUM amount FROM orders;
```

8. Sélection de tous les champs :

```sql
SELECT *
FROM orders
WHERE amount > 100;
```

## Structure des données JSON

Le fichier JSON doit être structuré comme un objet contenant des collections. Exemple :

```json
{
  "users": [
    {
      "id": 1,
      "name": "Alice",
      "details": {
        "skills": ["Python", "SQL"]
      }
    }
  ]
}
```

## Syntaxe supportée

- `SELECT` : Sélection de champs

  - Support des champs multiples : `field1, field2`
  - Support des champs imbriqués : `details.department`
  - Sélection complète : `*`

- `FROM` : Spécification de la collection

- `WHERE` : Conditions de filtrage

  - Opérateurs de comparaison : `==`, `>`, `<`, `>=`, `<=`, `!=`
  - Opérateurs logiques : `AND`, `OR`
  - Opérateur `IN` pour les listes

- Fonctions d'agrégation :
  - `COUNT` : Compte le nombre d'éléments
  - `AVG` : Calcule la moyenne d'un champ numérique
  - `SUM` : Calcule la somme des valeurs d'un champ
  - `MIN` : Trouve la valeur minimale d'un champ
  - `MAX` : Trouve la valeur maximale d'un champ

## Limitations

- Les requêtes doivent se terminer par un point-virgule (;)
- Pas de support pour les jointures entre collections
