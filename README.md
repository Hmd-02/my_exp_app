# Mes finances — app Streamlit

App perso de suivi de dépenses/revenus avec statistiques, accessible depuis
n'importe quel appareil via navigateur, données synchronisées via Supabase.

## 1. Créer le projet Supabase (5 min)

1. Va sur https://supabase.com → "Start your project" → connecte-toi avec GitHub
2. Crée un nouveau projet (note bien le mot de passe de la base, demandé une fois)
3. Une fois le projet créé, va dans **SQL Editor** (menu de gauche)
4. Colle le contenu de `schema.sql` (fourni dans ce dossier) et clique "Run"
   → ça crée les deux tables `categorie` et `transaction`
5. Va dans **Project Settings > API**
   → note ton **Project URL** et ta clé **anon public**
   (PAS la clé "service_role", celle-là ne doit jamais sortir du serveur)

## 2. Configurer les secrets en local

1. Dans le dossier `.streamlit/`, duplique `secrets.toml.example` en `secrets.toml`
2. Remplis avec ton URL et ta clé Supabase de l'étape 1, et choisis un mot de passe
   pour protéger ton app

`secrets.toml` est dans `.gitignore` : il ne sera jamais envoyé sur GitHub.

## 3. Installer et lancer en local

```bash
# Crée un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate        # sur Windows : venv\Scripts\activate

# Installe les dépendances
pip install -r requirements.txt

# Lance l'app
streamlit run app.py
```

Ton navigateur s'ouvre automatiquement sur `http://localhost:8501`. Teste
l'ajout d'une transaction, vérifie qu'elle apparaît dans l'historique et les
statistiques.

## 4. Déployer gratuitement sur Streamlit Community Cloud

1. Crée un repo GitHub (public) et pousse tout ce dossier dedans
   **sauf** `.streamlit/secrets.toml` (déjà exclu par `.gitignore`, vérifie
   bien qu'il n'apparaît pas avant de push)
2. Va sur https://share.streamlit.io → connecte-toi avec GitHub
3. "New app" → sélectionne ton repo → fichier principal : `app.py`
4. Dans **Advanced settings > Secrets**, colle le contenu de ton
   `secrets.toml` local (c'est l'équivalent cloud, séparé du fichier local)
5. Déploie. Tu obtiens une URL du type `https://ton-app.streamlit.app`

## 5. Utiliser sur ton téléphone

Ouvre l'URL dans le navigateur de ton téléphone, puis "Ajouter à l'écran
d'accueil" (Safari/Chrome) pour avoir une icône comme une vraie app.

## Structure du projet

```
budget-app/
├── app.py              # Écrans : saisie, historique, statistiques
├── database.py         # Toutes les requêtes Supabase
├── auth.py              # Protection par mot de passe
├── schema.sql           # SQL à exécuter dans Supabase (une fois)
├── requirements.txt      # Dépendances Python
└── .streamlit/
    └── secrets.toml.example   # Modèle à copier en secrets.toml
```

## Prochaines étapes possibles

- Ajouter une table `compte` si tu veux gérer plusieurs comptes
- Transactions récurrentes (loyer, abonnements)
- Budgets par catégorie avec alertes
- Export CSV des transactions
