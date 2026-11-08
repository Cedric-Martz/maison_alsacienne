# Parc de la Maison Alsacienne

Site statique sans dépendance, composé uniquement de fichiers HTML, CSS,
JavaScript et de ressources publiques. Il est prêt à être servi directement par
GitHub Pages depuis la branche `main` et le dossier racine.

## Publication

Dans les paramètres du dépôt GitHub :

1. ouvrir **Settings → Pages** ;
2. choisir **Deploy from a branch** ;
3. sélectionner la branche `main` et le dossier `/ (root)`.

Le site sera disponible à l’adresse
`https://cedric-martz.github.io/maison_alsacienne/`.

## Prévisualisation locale

Un serveur statique suffit :

```bash
python3 -m http.server 8000
```

Puis ouvrir `http://127.0.0.1:8000/maison_alsacienne/` depuis le dossier parent
du dépôt, afin de conserver le même sous-chemin que sur GitHub Pages.
