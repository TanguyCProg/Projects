import tkinter as tk
from Carte_Finale5 import Carte

def selected():
    val_Annee = str(Champ_Annee.get())
    val_Mois = str(Champ_Mois.get())
    val_Jour = str(Champ_Jour.get())
    n = int(Champ_n.get())
    liste_Pays = []
    liste_models = []
    if France.get() == 1:
        liste_Pays.append("France")
    if Canada.get() == 1:
        liste_Pays.append("Canada")
    if Inde.get() == 1:
        liste_Pays.append("Inde")
    if Somalie.get() == 1:
        liste_Pays.append("Somalie")
    if v_utci.get() == 1:
        liste_models.append('utci')
    if v_at.get() == 1:
        liste_models.append('at')
    if v_temp_dry_bulb.get() == 1:
        liste_models.append("Tdb")
    if v_humidex.get() == 1:
        liste_models.append('humidex')
    if v_mod_pers.get() == 1:
        liste_models.append("Modèle personnel")
    if v_WC.get() == 1:
        liste_models.append("Wind Chill")
    echelle = bool(v_echelle.get())
    Sauvegarder = bool(v_sauvegarder.get())
    Fenetre.destroy()
    date = val_Annee + val_Mois + val_Jour
    Carte(n, date, liste_Pays, liste_models, echelle, Sauvegarder)
    
    
    
    
Fenetre = tk.Tk()
Fenetre.geometry('600x750')

boutton = tk.Button(Fenetre, text='Valider', command = selected)
boutton.place(x='250',y='640')

Annee = tk.Label ( Fenetre , text ="Année",bg = 'black',fg='white',bd=5)
Champ_Annee = tk.Entry( Fenetre )
Annee.place(x='95', y = '150')
Champ_Annee.place(x='50', y = '200')

Mois = tk.Label ( Fenetre , text ="Mois",bg = 'black',fg='white',bd=5)
Champ_Mois = tk.Entry( Fenetre )
Mois.place(x='295', y = '150')
Champ_Mois.place(x='250', y = '200')

Jour = tk.Label ( Fenetre , text ="Jour",bg = 'black',fg='white',bd=5)
Champ_Jour = tk.Entry( Fenetre )
Jour.place(x='495', y = '150')
Champ_Jour.place(x='450', y = '200')

l_n = tk.Label ( Fenetre , text ="n",bg = 'black',fg='white',bd=5)
Champ_n = tk.Entry( Fenetre )
l_n.place(x='450', y = '350')
Champ_n.place(x='400', y = '400')

France = tk.IntVar()
boutton_France = tk.Checkbutton(Fenetre, text = 'France', variable = France)
boutton_France.place(x = '100', y = '320')

Canada = tk.IntVar()
boutton_Canada = tk.Checkbutton(Fenetre, text = 'Canada', variable = Canada)
boutton_Canada.place(x = '100', y = '340')

Inde = tk.IntVar()
boutton_Inde = tk.Checkbutton(Fenetre, text = 'Inde', variable = Inde)
boutton_Inde.place(x = '100', y = '360')

Somalie = tk.IntVar()
boutton_Somalie = tk.Checkbutton(Fenetre, text = 'Somalie', variable = Somalie)
boutton_Somalie.place(x = '100', y = '380')

v_utci = tk.IntVar()
boutton_utci = tk.Checkbutton(Fenetre, text = 'UTCI', variable = v_utci)
boutton_utci.place(x = '100', y = '400')

v_at = tk.IntVar()
boutton_at = tk.Checkbutton(Fenetre, text = 'Apparent Temperature', variable = v_at)
boutton_at.place(x = '100', y = '420')

v_temp_dry_bulb = tk.IntVar()
boutton_tdb = tk.Checkbutton(Fenetre, text = 'Dry Bulb Temperature', variable = v_temp_dry_bulb)
boutton_tdb.place(x = '100', y = '440')

v_humidex = tk.IntVar()
boutton_humidex = tk.Checkbutton(Fenetre, text = 'Humidex', variable = v_humidex)
boutton_humidex.place(x = '100', y = '460')

v_mod_pers = tk.IntVar()
boutton_mod_pers = tk.Checkbutton(Fenetre, text = 'Modèle personel', variable = v_mod_pers)
boutton_mod_pers.place(x = '100', y = '480')

v_WC = tk.IntVar()
boutton_WC = tk.Checkbutton(Fenetre, text = 'Wind Chill', variable = v_WC)
boutton_WC.place(x = '100', y = '500')

v_echelle = tk.IntVar()
boutton_echelle = tk.Checkbutton(Fenetre, text = 'Même échelle', variable = v_echelle)
boutton_echelle.place(x = '100', y = '520')

v_sauvegarder = tk.IntVar()
boutton_sauvegarder = tk.Checkbutton(Fenetre, text = 'Sauvegarder', variable = v_sauvegarder)
boutton_sauvegarder.place(x = '100', y = '540')

Fenetre.mainloop()
