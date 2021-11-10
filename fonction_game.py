#!/usr/bin/python3
from tkinter import *
import time


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
        fenetre.destroy()
        return liste_score()
    

def liste_score():
    fenetre = Tk()
    champs_label_1 = Label(fenetre, text = "Les 5 meilleurs scores", width = 50)
    champs_label_1.pack()
    liste_a = Listbox(fenetre, width = 50, height = 10)
    Liste = DicoToOrderList(fileToDico("data_score.txt"))
    for item_liste in Liste[0:5]:
        liste_a.insert(END, item_liste)
    liste_a.curselection()
    liste_a.pack(fill = BOTH)
    bouton_jouer = Button(fenetre, text = "Jouer", command = jouer)
    bouton_jouer.pack(side = "right")
    bouton_quitter = Button(fenetre, text = "Quitter", command = fenetre.destroy)
    bouton_quitter.pack(side = "left")
    fenetre.mainloop()

    

def jouer():
    t1 = time.time()
    i = 0
    while i <= 10:
        print(i)
        time.sleep(1)
        i += 1
    t2 = time.time()
    score = int(t2 - t1)// 10
    
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


fenetre = Tk()
interface = Frame(fenetre, width = 50, height = 50)
interface.pack(fill = BOTH)
champs_label = Label(fenetre, text = "----------- Inscription: -----------", width = 50)
champs_label.pack()
texte = StringVar()
ligne_texte = Entry(fenetre, textvariable = texte, width = 50)
ligne_texte.pack()

error = Label(fenetre, text = "", width = 50)
error.pack()

inscrire = Button(fenetre, text = "S'incrire", command = lambda:nom_personnage(texte.get()))
inscrire.pack(side = "left")

bouton_quitter = Button(fenetre, text = "Quitter", command = fenetre.quit)
bouton_quitter.pack(side = "right")

fenetre.mainloop()
fenetre.destroy()

