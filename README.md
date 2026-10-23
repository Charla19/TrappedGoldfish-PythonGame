# Trapped Goldfish

Un petit jeu d'évitement sous-marin en Python et Pygame : guider un poisson doré, esquiver les requins et riposter avec des bulles.

Le projet a commencé en juin 2021 lors d'un challenge d'école d'une semaine. Cette reprise conserve les personnages et l'univers marin d'origine, tout en améliorant le gameplay, les menus et la fluidité.

## Le jeu

- Des requins arrivent en continu, avec une difficulté progressive.
- Les perles apparaissent à des hauteurs et à des intervalles variés. Les enchaîner augmente le multiplicateur de score, jusqu'à ×5.
- Huit perles chargent un bouclier qui protège le poisson pendant cinq secondes.
- Une bulle de soin apparaît toutes les 30 secondes de jeu actif et rend jusqu'à 10 points de vie. Une seule peut être présente à la fois.
- Chaque joueur conserve son historique et son meilleur score. Le menu affiche le top 3 et permet de rejouer directement avec le dernier profil utilisé.

Une perle rapporte **5 points**, un requin éliminé **10 points**, une esquive **2 points** et chaque seconde de survie **1 point**. Le combo multiplie les points des perles, des éliminations et des esquives. Il retombe après un dégât ou 3,5 secondes sans perle.

## Installation

Testé sous Windows avec **Python 3.12** et **Pygame 2.6.1**.

Depuis le dossier du projet :

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Pour les lancements suivants, seule la dernière commande est nécessaire.

## Commandes

| Action | Commandes |
| --- | --- |
| Monter / descendre | Flèches haut / bas ou W / Z / S |
| Tirer | Entrée, Entrée du pavé numérique, Espace ou clic gauche ; maintien possible |
| Activer le bouclier | Flèche droite, E ou clic droit ; bouton également disponible à l'écran |
| Pause / reprendre | P ou Échap |
| Activer / désactiver le décor animé | M |
| Naviguer dans les menus | Haut / bas ou Tab, puis Entrée pour valider |

La partie se met automatiquement en pause lorsque la fenêtre perd le focus. Le réglage du décor animé est mémorisé.

## Joueurs et sauvegardes

Les profils et les scores sont enregistrés sur chaque appareil, pour le compte système qui lance le jeu. Ils restent disponibles après une mise à jour et ne sont pas partagés avec GitHub.

- **Windows** : `%LOCALAPPDATA%\TrappedGoldfish\scores.json`
- **macOS** : `~/Library/Application Support/TrappedGoldfish/scores.json`
- **Linux** : `$XDG_DATA_HOME/TrappedGoldfish/scores.json`, ou `~/.local/share/TrappedGoldfish/scores.json`

Un nouvel appareil démarre sans joueur. Le menu permet de créer un profil, d'en sélectionner un autre ou de reprendre avec le dernier utilisé.

## Construire l'exécutable Windows

Avec Python installé, lancer depuis le projet :

```powershell
.\build_windows.ps1
```

Le script crée un environnement de compilation séparé, installe les dépendances de `requirements-build.txt`, puis produit **`dist/TrappedGoldfish.exe`**. Cet exécutable se lance ensuite sans installation de Python. Le dossier `dist` est généré localement et n'est pas inclus dans le dépôt.

La compilation embarque uniquement les ressources utilisées et optimise les PNG sans perte, avec vérification des pixels. Elle vérifie aussi le démarrage et les fonctions principales de l'exécutable avec des profils temporaires. Les fichiers source et les illustrations d'origine sont conservés.

## Tests et choix techniques

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Les tests couvrent les apparitions d'ennemis et de bonus, les scores, les profils, le bouclier, le soin, la pause et les commandes. Ils utilisent un affichage virtuel et des sauvegardes temporaires.

La simulation avance à 120 pas par seconde, avec interpolation du rendu et une cible d'affichage de 60 images par seconde. Les ressources graphiques et sonores sont mises en cache. Le récif d'origine reste en fond, accompagné de lumières et de particules discrètes pour éviter les raccords visibles d'une image répétée.

Les choix d'interface et leurs références sont détaillés dans [DESIGN.md](DESIGN.md).
