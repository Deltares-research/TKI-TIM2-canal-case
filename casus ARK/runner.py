import os
from PIL import Image
import numpy as np
import openpyxl as xl
import timtiff

def run_qgistim():
    import qgis_tim_python as qtp #de import draait het model en maakt de resultaten beschikbaar voor dit script
    #dit is wellicht niet helemaal correct gebruik van Python, maar het zorgt ervoor dat de qgistim export direct bruikbaar is zonder handmatige aanpassingen
    return qtp.timml_model


def save_peilbuizen(timml_model, filename):
    #dit stopt de resultaten in de peilbuizen excel file
    aantal_peilbuizen = 36
    peilbuizen=xl.load_workbook(filename)
    sheet=peilbuizen.active
    for i in range(2,aantal_peilbuizen+2):
        head = timml_model.head(x=sheet["D"+str(i)].value,y=sheet["E"+str(i)].value)
        sheet["I"+str(i)]=head[0]
        sheet["J"+str(i)]=head[1]
    peilbuizen.save(filename)

if __name__ == "__main__":
    timml_model=run_qgistim()
    xwin=(122150.0,135975.0)
    ywin=(463400.0,481775.0)
    timtiff.tim2tiff(timml_model,xwin,ywin, gridsize=50)
    save_peilbuizen(timml_model=timml_model,filename="peilbuizen.xlsx")





