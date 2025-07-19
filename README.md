# LexQL

LexQL est un interpréteur SQL personnalisé qui permet d'effectuer des requêtes de type SQL sur des fichiers JSON. Il offre une syntaxe familière pour interroger et analyser des données JSON de manière simple et efficace, avec une interface web intégrée pour une utilisation plus conviviale.

## 🌟 Fonctionnalités

- Interface web interactive pour exécuter des requêtes
- Requêtes `SELECT` avec support des champs imbriqués
- Filtrage avec `WHERE` et opérateurs de comparaison (`==`, `>`, `<`, `>=`, `<=`, `!=`)
- Support des opérations logiques `AND` et `OR`
- Opérateur `IN` pour la recherche dans les listes
- Fonctions d'agrégation : `COUNT`, `AVG`, `SUM`, `MIN`, `MAX`
- Support des chemins imbriqués avec la notation point (.)
- Support des requêtes multiples (séparées par des points-virgules)
- Visualisation des résultats en format JSON

## 🚀 Installation

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

## 💻 Utilisation

### Interface Web

1. Lancez le serveur web :

```bash
python app.py
```

2. Ouvrez votre navigateur à l'adresse `http://localhost:5000`
3. Utilisez l'interface web pour :
   - Écrire et exécuter des requêtes
   - Visualiser les résultats en format JSON
   - Explorer vos données

### Ligne de commande

Pour exécuter des requêtes LexQL en ligne de commande :

```bash
python lexql.py <fichier.lql> <fichier.json>
```

## 📝 Exemples de requêtes

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

3. Requêtes d'agrégation :

```sql
-- Comptage avec condition
COUNT FROM users WHERE salary > 45000;

-- Moyenne des salaires
AVG salary FROM users;

-- Montant minimum des commandes
MIN amount FROM orders;

-- Montant maximum des commandes
MAX amount FROM orders;

-- Somme des montants
SUM amount FROM orders;
```

4. Requêtes multiples :

```sql
SELECT * FROM users WHERE age > 30;
COUNT FROM users WHERE city == "Paris";
```

## 📊 Structure des données JSON

Le fichier JSON doit être structuré comme un objet contenant des collections. Exemple :

```json
{
  "users": [
    {
      "id": 1,
      "name": "Alice",
      "details": {
        "skills": ["Python", "SQL"],
        "city": "Paris",
        "salary": 50000
      }
    }
  ],
  "orders": [
    {
      "id": 1,
      "user_id": 1,
      "amount": 150.5,
      "date": "2024-03-20"
    }
  ]
}
```

## 📚 Syntaxe détaillée

### Sélection de champs

- Champs multiples : `field1, field2`
- Champs imbriqués : `details.department`
- Sélection complète : `*`

### Conditions WHERE

- Opérateurs de comparaison :
  - Égalité : `==`
  - Supérieur : `>`
  - Inférieur : `<`
  - Supérieur ou égal : `>=`
  - Inférieur ou égal : `<=`
  - Différent : `!=`
- Opérateurs logiques :
  - `AND` : toutes les conditions doivent être vraies
  - `OR` : au moins une condition doit être vraie
- Opérateur `IN` : vérification d'appartenance à une liste

### Fonctions d'agrégation

- `COUNT` : nombre d'éléments
- `AVG` : moyenne arithmétique
- `SUM` : somme des valeurs
- `MIN` : valeur minimale
- `MAX` : valeur maximale

## ⚠️ Limitations

- Les requêtes doivent se terminer par un point-virgule (;)
- Pas de support pour les jointures entre collections
- Pas de support pour les sous-requêtes
- Pas de support pour GROUP BY et ORDER BY
- Les valeurs numériques dans les conditions doivent être sans guillemets
- Les chaînes de caractères dans les conditions doivent être entre guillemets doubles

## 🔧 Configuration

Le fichier de données par défaut doit être placé dans `data/data.json`. Pour utiliser un autre fichier :

- En ligne de commande : spécifiez le chemin en argument
- Via l'interface web : utilisez l'API `/api/data` pour visualiser les données chargées