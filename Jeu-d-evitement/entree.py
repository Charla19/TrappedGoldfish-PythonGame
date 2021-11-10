import game
from game import Game
from tkinter import *
#import time
import pygame
from player import Player
def fenetre_de_jeu():
    pygame.init()
    entree.destroy()
global screen

entree = Tk()
entree.geometry("961x650")
entree.maxsize(961, 650)
entree.minsize(961, 650)
entree.title("Trapped Goldfish")
entree.iconbitmap("assets/poisson.ico")
#can = Canvas(entree, width=961, height=650, background="#cff9f6")
#img = PhotoImage(file="assets/bg.gif")
#can.create_image(0, 0, anchor=NW, image=img)
#can.place(x=0, y=0)

# formulaire nom du joueur
#champs_label = Label(entree, text = "----------- Inscription: -----------", width = 50)
#champs_label.pack()
texte = StringVar()
ligne_texte = Entry(entree, textvariable = texte, width = 50)
ligne_texte.pack()

error = Label(entree, text = "", width = 50)
error.pack()

inscrire = Button(entree, text = "S'incrire", command = lambda:nom_personnage(texte.get()))
inscrire.pack(side = "left")

bouton_quitter = Button(entree, text = "Quitter", command = entree.quit)
bouton_quitter.pack(side = "left")


# fonctions utilisées
def fileToDico(nom_fichier):
    with open(nom_fichier, "r") as save:
        lignes = save.readlines()
    dictionnaire = {}
    for ligne in lignes:
        ligne_liste = list(ligne.split())
        dictionnaire[ligne_liste[1]] = int(ligne_liste[0])
    return(dictionnaire)


def DicoToOrderList(dictionnaire):
    new_dico = {}
    for item in dictionnaire:
        new_dico[dictionnaire[item]] = item
    new_liste = list(new_dico)
    new_liste.sort()
    new_liste.reverse()
    dico = {}
    for liste in new_liste:
           dico[new_dico[liste]] = liste
    liste = []
    for cle in dico:
        data = cle + " : " + str(dico[cle]) + ' points'
        liste.append(data)
    return liste


def nom_personnage(prenom):
    if prenom == '':
        error.config(text='Veuillez entrez un nom !!', fg = "red")
        error.update()
    else:
        save = open("prenom.txt", "w")
        save.write((str(prenom)).lower())
        save.close()
        #entree.destroy()
        return liste_score()


def jouer():

    score = game.score
    with open("prenom.txt", "r") as save:
        prenoms = save.readlines()
        for prenom_liste in prenoms:
            continue
        save.closed

    with open("data_score.txt", "r") as saveData:
        contenu = saveData.readlines()
        saveData.closed
    prenomListe = []
    for itemPrenom in contenu:
        listePrenom = itemPrenom.split()
        prenomListe.append(listePrenom[1])

    if prenom_liste in prenomListe:
        with open("data_score.txt", "r") as saveScore:
            contenuScore = saveScore.readlines()
            saveScore.closed

        b = prenomListe.index(prenom_liste)
        scoreListe = []
        for itemScore in contenuScore:
            listeScore = itemScore.split()
            scoreListe.append(listeScore[0])

        scoreListe.remove(scoreListe[b])
        scoreListe.insert(b, str(score))

        with open("data_score.txt", "w") as data_delete:
            data_delete.write("")
            data_delete.closed
        for scoreData, valuePrenom in zip(scoreListe, prenomListe):
            with open("data_score.txt", "a") as dataReconstitution:
                dataReconstitution.write(scoreData + " " + valuePrenom + "\n")
                dataReconstitution.closed

    else:
        with open("data_score.txt", "a") as score_liste:
            score_liste.write(str(score) + " " + str(prenom_liste) + "\n")
            score_liste.closed


#Montrer les scores des 5 meilleurs joueurs
def liste_score():
    #fenetre = Tk()
    champs_label_1 = Label(entree, text = "Les 5 meilleurs scores", width = 50)
    champs_label_1.pack()
    liste_a = Listbox(entree, width = 50, height = 10)
    Liste = DicoToOrderList(fileToDico("data_score.txt"))
    for item_liste in Liste[0:5]:
        liste_a.insert(END, item_liste)
    liste_a.curselection()
    liste_a.pack(fill = BOTH)
    bouton_jouer = Button(entree, text = "Jouer", command = jouer)
    bouton_jouer.pack(side = "right")
    bouton_quitter = Button(entree, text = "Quitter", command = fenetre_de_jeu)
    bouton_quitter.pack(side = "left")
    #entree.mainloop()

# Boutton "Start" du jeu
#bouton = Button(entree, text="Start the game", font=("Arial Black", 20), bg="#c593f3", bd=5 , relief=RAISED, command= fenetre_de_jeu)
#bouton.pack(side=BOTTOM)

entree.mainloop()


#from main import *
class Main:
    background_x = 0
    background_y = 0


    # définir une clock
    clock = pygame.time.Clock()
    FPS = 60

    # générer la fenêtre du jeu
    pygame.display.set_caption("Trapped Goldfish")
    screen = pygame.display.set_mode((961, 650))
    programIcon = pygame.image.load('assets/poisson.ico')
    pygame.display.set_icon(programIcon)

    # Importer changer l'arriere plan
    background = pygame.image.load("assets/as.jpg")

    # Charger notre bannière
    banner = pygame.image.load('assets/bg.png')

    # Charger notre bouton pour lancer la partie
    play_button = pygame.image.load('assets/play-button.png')
    play_button = pygame.transform.scale(play_button, (150, 150))
    play_button_rect = play_button.get_rect()
    play_button_rect.x = 390
    play_button_rect.y = 400

    # Charger notre joueur
    player = Player

    # Charger le jeu
    game = Game()


    running = True

    # Boucle tant que cette condition est vrai
    while running:
        # Appliquer l'arrière plan de notre jeu
        screen.blit(background, (0, 0))

        # Vérifier si notre jeu a commmencé ou non
        if game.is_playing:
            #game.sound_manager.play('fond_marin')
            background_rel_y = background_y % background.get_rect().width
            screen.blit(background, (background_rel_y, 0))
            if background_rel_y < 961:
                screen.blit(background, (background_rel_y - background.get_rect().width, 0))
            background_y -= 1
            # Déclancher les instructions de la partie
            game.update(screen)
        # Vérifier si notre jeu n'a pas commencé
        else:
            # Ajouter mon écran de bienvenue
            screen.blit(banner, (0, 0))
            screen.blit(play_button, play_button_rect)

        print(game.player.rect.y)

        # Mettre à jour l'écran
        pygame.display.flip()

        # Si le joueur ferme cette fenêtre
        for event in pygame.event.get():
            #Que l'évènement est fermeture de fenêtre
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                print("Fermeture du jeu")

            # Détecter si un joueur laceh une touche du clavier
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
                    game.sound_manager.play('click')
        # fixer le nombre de FPS sur ma clock
        clock.tick(FPS)