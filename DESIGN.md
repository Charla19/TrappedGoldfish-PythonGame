# Trapped Goldfish — affichage, commandes et fluidité

## Direction retenue

Conserver le poisson, les requins, le récif, la bannière et la palette marine. Harmoniser les nouvelles interfaces avec une palette bleu profond, turquoise et corail, une police sans empattement régulière, des panneaux à bord fin et des boutons aux dimensions stables.

## Recherches et application

| Source primaire | Recommandation retenue | Application dans le jeu |
| --- | --- | --- |
| [Xbox XAG 101 — Text display](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/101) | Hiérarchie et lecture claire du texte | Police régulière lisible, libellés persistants, noms longs tronqués dans leur espace |
| [Xbox XAG 102 — Contrast](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/102) | Contraste du HUD face aux scènes variables | Fond sombre presque opaque, texte clair, séparation du jeu et des commandes |
| [Xbox XAG 107 — Input](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/107) | Choix de commandes, menus accessibles au clavier, réduction des pressions répétitives | Flèches/lettres équivalentes, Entrée/Espace/clic pour tirer, flèche droite/E/clic droit pour protéger, tir maintenu, navigation et focus au clavier |
| [Xbox XAG 117 — Visual distractions and motion](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/117) | Limiter les mouvements secondaires et permettre de les désactiver | Pas de caméra qui tremble ou oscille, menus statiques, option de décor animé mémorisée |
| [Game Accessibility Guidelines — Interactive elements](https://gameaccessibilityguidelines.com/give-a-clear-indication-that-interactive-elements-are-interactive/) | Montrer les éléments actionnables | Survol doux, contour de focus, état indisponible et état prêt du bouclier |
| [Game Accessibility Guidelines — Colour alone](https://gameaccessibilityguidelines.com/ensure-no-essential-information-is-conveyed-by-a-fixed-colour-alone/) | Ne pas faire dépendre une information uniquement de sa couleur | Vie chiffrée et barre, combo numérique, protection avec texte et durée |
| [Glenn Fiedler — Fix Your Timestep!](https://gafferongames.com/post/fix_your_timestep/) | Séparer simulation et rendu, borner le rattrapage, interpoler | Pas de simulation de 1/120 seconde, accumulateur, positions interpolées, temps écoulé borné en cas de blocage |
| [Pygame — Clock](https://www.pygame.org/docs/ref/time.html) | Mesurer le temps entre images et contrôler la cadence | Temps en secondes, rendu limité à 60 images par seconde |
| [Pygame — Display](https://www.pygame.org/docs/ref/display.html) | Comprendre les limites du mode d'affichage et de la synchronisation | Aucune promesse de VSync universelle ; la cadence réelle dépend de la machine et du système |

Il s'agit d'une sélection de recommandations adaptées au jeu, pas d'une déclaration de conformité complète aux XAG.

## Apparition des perles

Un émetteur individuel remplace les blocs de cinq. Chaque apparition arrive par le bord droit. Les intervalles sont aléatoires entre 0,5 et 1,1 seconde. Environ 14 % des apparitions autorisent deux perles à des hauteurs distinctes. Les hauteurs suivent le plus souvent des écarts accessibles, avec parfois des variations plus larges. Un plafond de 18 perles limite l'encombrement et la mémoire. Les perles hors écran sont retirées.

## Fond et animations

La photo du récif n'est jamais répétée en mosaïque. Les mouvements décoratifs proviennent de particules à plusieurs vitesses et de rayons très discrets. Le déplacement des particules se reboucle hors champ ; il n'existe pas de raccord entre deux photos à masquer. L'option de mouvement réduit conserve les objets essentiels au gameplay mais supprime les couches décoratives animées.

## Vérification

Les tests couvrent la génération progressive, la variation des hauteurs, les deux commandes du bouclier, Entrée et le tir maintenu, la pause à la perte de focus, les menus au clavier, les préférences locales, la sauvegarde des scores et les mêmes résultats de simulation à 30, 60 et 144 images par seconde de rendu simulé. Les menus et une partie simulée sont capturés pour inspection visuelle. Le chronométrage hors écran mesure mise à jour et dessin ; il ne mesure pas la présentation réelle par Windows ou le moniteur.
