import numpy as np
from .horas import horasdia, horadecimal
from .solar import evar, gammadec, vectorsolar

def irradteorica(diajuliano, latitud):
#calculamos aquí la irradiación diaria teórica en J/m²  

    lat=np.pi/180*latitud
    dec=np.pi/180*gammadec(diajuliano)[1] #gammadec da los resutados en grados
    omega=2*np.pi/24 #h⁻¹ 
    cs=1361 #constante solar en W/m²
    var=evar(diajuliano) #variación energética relativa
    
#para la irradiación teórica diaria H0 necesitamos el tiempo de orto y ocaso
#los obtenemos con las entradas 0 y 1 de horasdia
#estas horas están expresadas con origen en el mediodía solar (son simétricas)
#lo cual es el formato necesario para introducirlos en funciones trigonométricas
#no necesitamos el tiempo de orto con la fórmula 1.10.3 Duffie
    
    oc=horasdia(diajuliano, latitud)[1]
    ws=omega*oc #radianes ?
    
    h0=cs*var*24*3600/np.pi*(np.sin(ws)*np.cos(dec)*np.cos(lat)+ws*np.sin(dec)*np.sin(lat))
#el 3600 convierte cs a J/hm² para que se vaya el tiempo con la omega, que está en h⁻¹
#con la corrección de la fórmula, pasa a 8 MJ/m² medido y 22 MJ/m² teoricos
    return h0


def fraccionradiacion(diajuliano,latitud,gmedida,horasolar):
#calcula la radiación diaria total y sus componentes directa y difusa en J
#usamos el modelo Collares-Pereira del índice de claridad para estimar
#la componente difusa
#gmedida es la radiación global medida en Julios/m²
    
#lo primero es convertir horasolar a decimal 
    hs=horadecimal(horasolar)
#gmedida debe ser la irradiación medida (H) en J/m²
    omega=2*np.pi/24
    h=irradteorica(diajuliano,latitud)
    kt=gmedida/h
    oc=horasdia(diajuliano,latitud)[1] #la segunda componente da la hora decimal del ocaso
#horasdia ya devuelve la hora con t=0 el mediodía
    if kt < 0.17:
        hdifusa=0.99*gmedida
    
    elif (kt > 0.17 and kt <= 0.8):
        hdifusa=(1.188-2.272*kt+9.473*kt**2-21.856*kt**3+14.648*kt**4)*gmedida
        
    elif kt > 0.8: #esta condicion podria resumirse en else :
        hdifusa=0.18*gmedida
    
    elif kt > 1:
        raise Exception('Índice de claridad mayor que 1. Revisar entrada de datos')
        return
    
    hdirecta=gmedida-hdifusa
#para la instantanea me baso en el Duffie, página 81: rg=inst/diaria
#NO consideramos la difusa y la global iguales como allí dice, relación
#rd=rg/(a+b*cos(omega*t)) con notación habitual
    a=0.409-0.5016*np.sin(omega*oc+1.047)
    b=0.6609-0.4767*np.sin(omega*oc+1.047)
    rg=np.pi/24*(a+b*np.cos(omega*hs))*(np.cos(omega*hs)-np.cos(omega*oc)) \
    /(np.sin(omega*oc)-omega*oc*np.cos(omega*oc))
    
    globalinst=rg*h
    difusainst=(rg/(a+b*np.cos(omega*hs)))*hdifusa
    directainst=globalinst-difusainst
    
    return np.array([hdirecta, hdifusa, globalinst, difusainst, directainst])

    
def instainc(diajuliano,horasolar,latitud,gmedida,ro,inclinacion,azimut):
#devuelve la radiación instantánea (J/hm²) en un plano inclinado con orientacion
#inclinacion,azimut; ro es el albedo, gmedida en J/m²
    
#convertimos todos los ángulos a radianes 
    inc=np.pi/180*inclinacion
    az=np.pi/180*azimut
    
#calculamos el coseno del angulo de indicidencia como prod escalar vsolar*normal
    
    normal=np.array([-np.sin(inc)*np.sin(az), np.sin(inc)*np.cos(az), np.cos(inc)])
    vs=vectorsolar(diajuliano,horasolar,latitud)
    
    cosin= np.dot(vs,normal) #coseno de theta
    rb=cosin/vs[2] 
    directainst=fraccionradiacion(diajuliano,latitud,gmedida,horasolar)[4]
    difusainst=fraccionradiacion(diajuliano,latitud,gmedida,horasolar)[3]
    globalinst=fraccionradiacion(diajuliano,latitud,gmedida,horasolar)[2]
    hinc=rb*directainst+(1+np.cos(inc))/2*difusainst+(1-np.cos(inc))/2*ro*globalinst
    
    return hinc