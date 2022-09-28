This programme can draw weather maps of apparent temperatures, based on the datas of the NASA POWER API.
The Main.py file correspond to the Afficheur.py file so that were the program begins.
You will need to download those libraries:
-Tkinter
-numpy
-matplotlib.pyplot
-pythermalcomfort
-PIL
-json
-pickle
-copy
-scipy
-requests
Be awware that some libraries (pythermalcomfort) have been modified in order to make them compatible with the numpy module. Therefore in order to get this code to work,
you will need to change the libraries too.
Finally, you will need to create an account on the NASA POWER API, and put your key in the Recup_donnees2.py line 27 in order to make the code work.
The program works well for maps sizes around 2000x2000 pixels.
