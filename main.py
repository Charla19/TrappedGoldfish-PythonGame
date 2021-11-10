import pygame
from game import Game
from player import Player

pygame.init()


class Main:
    background_x = 0
    background_y = 0

    # définir une clock
    clock = pygame.time.Clock()
    FPS = 60

    # générer la fenêtre du jeu
    pygame.display.set_caption("TRAPPED GOLDFISH", "assets/icon.ico")
    screen = pygame.display.set_mode((961, 650))
    programIcon = pygame.image.load('assets/poisson.ico')
    pygame.display.set_icon(programIcon)

    # Importer l'arriere plan
    background = pygame.image.load("assets/as.jpg")

    # Charger la bannière
    banner = pygame.image.load('assets/sary.png')

    # Charger le bouton pour lancer la partie
    play_button = pygame.image.load('assets/play.png')
    play_button = pygame.transform.scale(play_button, (150, 150))
    play_button_rect = play_button.get_rect()
    play_button_rect.x = 390
    play_button_rect.y = 400

    # Charger le joueur
    player = Player

    # Charger le jeu
    game = Game()

    running = True

    # Boucle tant que cette condition est vrai
    while running:

        screen.blit(background, (0, 0))
        # Appliquer l'arrière son de notre jeu
        # game.sound_manager.play('fond_marin')

        # Vérifier si notre jeu a commmencé ou non
        if game.is_playing:
            # Déclancher les instructions de la partie

            background_rel_y = background_y % background.get_rect().width
            screen.blit(background, (background_rel_y, 0))
            if background_rel_y < 961:
                screen.blit(background, (background_rel_y - background.get_rect().width, 0))
            background_y -= 1
            game.update(screen)

        # Vérifier si le jeu n'a pas commencé
        else:
            # Ajouter écran de bienvenue
            screen.blit(banner, (0, 0))
            screen.blit(play_button, play_button_rect)

        print(game.player.rect.y)

        # Mettre à jour l'écran
        pygame.display.flip()

        # Si le joueur ferme cette fenêtre
        for event in pygame.event.get():
            # Que l'évènement est fermeture de fenêtre
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                print("Fermeture du jeu")

            # Détecter si un joueur lache une touche du clavier
            elif event.type == pygame.KEYDOWN:
                game.pressed[event.key] = True

                # Détecter si la touche espace a été enclanché pour lancer notre projectile
                if event.key == pygame.K_SPACE:
                    game.player.launch_projectile()

            elif event.type == pygame.KEYUP:
                game.pressed[event.key] = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Vérification si la souris est en collision avec le bouton jouer
                if play_button_rect.collidepoint(event.pos):
                    # Mettre le jeu en mode lancé
                    game.start()
                    # jouer le son
                    game.sound_manager.play('click')
                    # fixer le nombre de FPS sur ma clock
        clock.tick(FPS)
