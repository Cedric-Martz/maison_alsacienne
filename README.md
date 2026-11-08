# Parc de la Maison Alsacienne

Site statique publié par GitHub Pages et administré avec
[Pages CMS](https://pagescms.org/). Il ne nécessite ni serveur applicatif, ni
base de données, ni installation WordPress.

## Fonctionnement

1. Un membre modifie les informations, les actualités, les événements ou la
   galerie dans Pages CMS.
2. Pages CMS enregistre la modification dans le dépôt GitHub.
3. Le workflow `.github/workflows/pages.yml` génère le site statique à partir
   du dossier `content/`.
4. GitHub Pages publie automatiquement la nouvelle version.

Les pages allemandes, anglaises et espagnoles restent statiques. Le CMS gère
pour le moment le contenu éditorial français.

## Première mise en service

### Pages CMS

1. Aller sur <https://app.pagescms.org/> et se connecter avec GitHub.
2. Installer l’application GitHub Pages CMS uniquement sur ce dépôt.
3. Inviter les membres autorisés dans le dépôt ou l’organisation GitHub.
4. Activer la double authentification sur tous les comptes éditeurs.
5. Ouvrir le dépôt et la branche `main` dans Pages CMS.

La configuration des formulaires se trouve dans `.pages.yml`.

### GitHub Pages

Dans **Settings → Pages**, choisir **GitHub Actions** comme source de
publication. Le workflow fourni construit et déploie ensuite le site à chaque
modification de `main`.

Configurer `www.maisonalsacienne.fr` comme domaine personnalisé dans
**Settings → Pages**, puis activer **Enforce HTTPS** lorsque le certificat est
disponible. Le fichier `CNAME` est déjà inclus dans le site généré.

## Contenus éditables

- `content/informations.json` : horaires, tarifs et coordonnées ;
- `content/actualites/` : actualités avec date, photo et lien facultatif ;
- `content/evenements/` : programme chronologique ;
- `content/galerie.json` : photos, légendes et années.

Les images ajoutées depuis Pages CMS sont enregistrées dans `assets/media/`.
Les anciennes miniatures WebP sont réutilisées automatiquement ; une nouvelle
photo s’affiche directement avec son fichier original.

## Vérification locale

Générer le site :

```bash
python3 tools/build_site.py --output _site
```

Puis le prévisualiser :

```bash
python3 -m http.server 8000 --directory _site
```

Le dossier `_site/` est généré et ne doit pas être commité.
