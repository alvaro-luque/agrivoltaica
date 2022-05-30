import numpy as np
from .horas import horadecimal 

def evar(diajuliano):
#devuelve la variación relativa energética (drtsol en VBA)
    e=1+0.33*np.cos(2*np.pi*diajuliano/365.24)
    
    return e
   
 
def gammadec(diajuliano):
#calcula el ángulo solar y la declinacion; se usan 
#en muchas funciones, luego es interesante calcularlo aparte para no repetir 
    gamma0=2*np.pi*(diajuliano+284)/365.24
    gamma=gamma0+0.07133*np.sin(gamma0)+0.03268*np.cos(gamma0)
    -0.000318*np.sin(2*gamma0)+0.000145*np.cos(2*gamma0)
    dec=np.arcsin(0.3979*np.sin(gamma))
    
#la función retorna un array con la componente 0=gamma y la 1=dec
#ambas expresadas en grados 
    return 180/np.pi*np.array([gamma, dec]) 
 
   
def vectorsolar(diajuliano,horasolar,latitud):
    
#lo primero siempre es convertir la hora de string a un formato manejable
    if type(horasolar)==str:
        hs=horadecimal(horasolar)
    else: #por si se mete como numeros de numpy
        hs=horasolar
    
    omega=2*np.pi/24
    lat=latitud*np.pi/180
    dec=np.pi/180*gammadec(diajuliano)[1]
    
#vamos a manejar el vector solar (unitario) como un array de numpy    
    vx=np.cos(dec)*np.sin(omega*hs)
    vy=np.cos(dec)*np.cos(omega*hs)*np.sin(lat)-np.sin(dec)*np.cos(lat)
    vz=np.cos(lat)*np.cos(dec)*np.cos(omega*hs)+np.sin(lat)*np.sin(dec)
    
    vector=np.array([vx,vy,vz])
    
    return vector


def coordsolar(diajuliano, horasolar, latitud):
#devuelve las coordenadas solares (azimut, altura) en grados
#no necesitamos convertir horasolar ya que lo hará vectorsolar
    vs=vectorsolar(diajuliano, horasolar, latitud)
    
    azimut=180/np.pi*np.arctan(-vs[1]/vs[0])
    altura=180/np.pi*np.arcsin(vs[2])
    
    return np.array([azimut,altura])


def esdedia(diajuliano, horasolar, latitud):
    
#devuelve 0 si es de noche y 1 si es de día dependiendo de la hora solar
#esta puede estar expresada en formato string 'HH:MM:SS' u hora decimal
#ya que vectorsolar las diferencia

#podríamos calcular t como la tercera componente de vectorsolar.
    t=vectorsolar(diajuliano,horasolar,latitud)[2]
    
    if t < 0:
        unocero=0
    else:
        unocero=1
        
    return unocero