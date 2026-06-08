import os
from PIL import Image
import numpy as np
import typing


def tim2tiff(timml_model, xwin:tuple[int, int], ywin:tuple[int, int], gridsize:tuple[int, int] | int=None, resolution:tuple[int, int] | int=None,filename:str="vanuit_python", layer:int=0):
    """
    Saves a tim model to a georeferenced TIFF file to be used in GIS software. 
    This function requires GDAL to be installed and on PATH, most common GIS packages come with GDAL by default, in which case it only has to be added to PATH.
   
    Mandatory arguments:\\
    timml_model, the timflow model of which the headgrid is to be exported. The model should be in RD coordinates\\
    xwin, a tuple of two ints for the window in the x direction in RD coordinates\\
    ywin, a tuple of two ints for the window in the y direction in RD coordinates

    Optional arguments:
    gridsize in m as ints or (x,y) tuple\\
    resolution as int or (x,y) tuple\\
    (at most one of the optional arguments above should be given)\\
    filename as a string\\
    layer in the timflow model
    """
    #x van klein naar groot , 
    if xwin[0]<xwin[1]:
        x1=xwin[0]
        x2=xwin[1]
    else:
        x1=xwin[1]
        x2=xwin[0]

    #y van klein naar groot, 
    if ywin[0]<ywin[1]:
        y1=ywin[0]
        y2=ywin[1]
    else:
        y1=ywin[1]
        y2=ywin[0]

    #in meters
    if gridsize is not None and resolution is not None:
        raise Exception("gridsize and resolution can't both be defined, it is one or the other")
    elif gridsize is not None and resolution is None:
        if isinstance(gridsize, tuple):
            raise Exception("tuple gridsize is not yet implemented")
        elif isinstance(gridsize, int):
            x_aantal=int((x2-x1)/gridsize) #ik weet niet zeker hoe goed dit werkt als het afgerond moet worden
            y_aantal=int((y2-y1)/gridsize)#ik weet niet zeker hoe goed dit werkt als het afgerond moet worden
        else:
            raise Exception("gridsize should be a tuple with 2 components or an int")

    elif gridsize is None and resolution is not None:
        #check resolution scalar
        if isinstance(resolution, tuple):
            if len(resolution) == 2:
                x_aantal=resolution[0]
                y_aantal=resolution[1]
            else:
                raise Exception("resolution should be a tuple with 2 components or an int")
        elif isinstance(resolution, int):
            x_aantal=resolution
            y_aantal=resolution
        else:
            raise Exception("resolution should be a tuple with 2 components or an int")
        
        if (y2-y1)/y_aantal == (x2-x1)/x_aantal:
            gridsize=(y2-y1)/y_aantal
        else:
            raise Exception("different gridsizes for x and y are not yet implemented")
    
    elif gridsize is None and resolution is None:
        x_aantal=100
        y_aantal=100
        if (y2-y1)/y_aantal == (x2-x1)/x_aantal:
            gridsize=(y2-y1)/y_aantal
        else:
            raise Exception("different gridsizes for x and y are not yet implemented")

    heads=timml_model.headgrid(
        xg=np.arange(x1, x2, gridsize),
        yg=np.arange(y1, y2, gridsize)
    )
    #
    savetiff(heads[layer,:,:],filename,x1,y1,x2,y2,x_aantal,y_aantal)
 
    
def savetiff(array:np.ndarray,filename:str,x1:int,y1:int,x2:int,y2:int,x_aantal:int,y_aantal:int):
    """
    
    """
    delete_existing(filename+".tiff")
    delete_existing(filename+"2.tiff")
    delete_existing(filename+"_georeferenced.tif")

    #dit slaat het plaatje op als tiff
    Image.fromarray(array).save(filename+".tiff")

    #gebruik GDAL om de tiff te georeferencen
    os.system("gdal_translate -of GTiff -gcp 0 0 "+str(x1)+" "+str(y1)+" -gcp "+str(x_aantal)+" "+str(y_aantal)+" "+str(x2)+" "+str(y2)+" -gcp "+str(x_aantal)+" 0 "+str(x2)+" "+ str(y1)+" -gcp 0 "+str(y_aantal)+" "+ str(x1)+" "+ str(y2) +" "+filename+".tiff "+filename+"2.tiff")
    os.system("gdalwarp -r near -order 1 -co COMPRESS=None  -t_srs EPSG:28992 "+filename+"2.tiff "+filename+"_georeferenced.tif")
    
    delete_existing(filename+".tiff", silent=True)
    delete_existing(filename+"2.tiff",silent=True)


def delete_existing(filename, silent=False):
    if os.path.isfile(filename):
        if not silent:
            print("Found and deleted existing file: "+filename)
        os.remove(filename)