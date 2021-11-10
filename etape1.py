from tkinter import *
root= Tk()
root.geometry("200x200")

## LIRE LE FICHIER
def fileRead():
    file=open("joueurs.txt","r")
    list=file.readline()
    while (list):
         print(list)
         list=file.readline()
    file.close()

## STRING DU FICHIER EN DICTIONNAIRE
def fileToDico(f):
    d={}
    for line in f:
        (key, val) = line.split()
        d[int(key)] = val
    # print(d)
    return d

## AFFICHAGE DICTIONNAIRE
with open("joueurs.txt") as file:
    d = (fileToDico(file))
    print("Dictionnaire: ",d)
file.close()

## DICTIONNAIRE (score,nom) EN LISTE DE TUPLE par ordre de score
def dicoToOrderList(dict):
    list=[]
    for i in dict:
        k = (i, dict[i])
        list.append(k)
        list.sort()
    return list
#label()
## Affichage liste de tuple (score,nom
l = dicoToOrderList(d)
print("Liste de tuple par score: ",l)

