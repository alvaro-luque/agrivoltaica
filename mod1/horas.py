import numpy as np
import datetime


def diajuliano(dia,mes,año):
    fecha=datetime.date(año, mes, dia)
    origen=datetime.date(año,1,1)
    jul=(fecha-origen).days + 1
#se suma uno para contar el 1 de enero
    
    return jul


def horasolar(diajuliano, longitud, horacivil):
#convertimos horacivil de string a formato datetime
    hc=datetime.datetime.strptime(horacivil, '%H:%M:%S')
    gamma=(2*np.pi/365)*(diajuliano-1+(hc.hour-12)/24)
    
#término hora-12/24 corresponde a la parte decimal del día juliano
       
    #asi definido, delta son minutos (ec tiempo, NOAA)
    delta=229.18*(0.000075+0.001868*np.cos(gamma)-0.032077*np.sin(gamma)
                  -0.014615*np.cos(2*gamma)-0.040849*np.sin(2*gamma))
    
#el desfase total se calcula dependiendo de si es verano o invierno
   
    minsolar=delta-4*longitud-60+60*hc.hour+hc.minute+hc.second/60
   
    if diajuliano > 80 & diajuliano < 264:
        minsolar=minsolar-60
        
#convertimos el minuto solar al formato 'hs:ms:ss' como una string
#vamos a procurar que todas las horas usadas como argumentos de entrada
#sean de este tipo. Asimismo, todas las funciones que tengan una string 
#horaria como entrada, las convertirán a datetime para operar con ellas
    hmod=divmod(minsolar,60)
    
#np.floor() trunca a las unidades. No necesitamos truncar la primera 
#componente de hmod ya que divmod hace la división entera, hmod[0] siempre
#es un entero (se nos devuelve un float pero lo convertimos al crear hsolar)
    hs=hmod[0]
    ms=np.floor(hmod[1])
    ss=(hmod[1]-ms)*60
    hsolar='%.2d:%.2d:%.2d' % (hs,ms,ss) # %.2d : aquí va un entero con 2 cifras
    
    return hsolar


#ahora vamos a hacer la función "inversa"
def horacivil(diajuliano, longitud, horasolar) :
    hs=datetime.datetime.strptime(horasolar,'%H:%M:%S')
    gamma=(2*np.pi/365)*(diajuliano-1) 
    
    delta=229.18*(0.000075+0.001868*np.cos(gamma)-0.032077*np.sin(gamma)
                  -0.014615*np.cos(2*gamma)-0.040849*np.sin(2*gamma))
    
#despejar de minsolar en func anterior
    mincivil=60*hs.hour+hs.minute+hs.second/60+60+4*longitud-delta
    
    if diajuliano > 80 & diajuliano < 264:
        mincivil=mincivil+60
    
    hmod=divmod(mincivil,60)
    
    hc=hmod[0]
    mc=np.floor(hmod[1])
    sc=(hmod[1]-mc)*60
    hcivil='%.2d:%.2d:%.2d' % (hc,mc,sc)
    
    return hcivil


def horadecimal(horasolar):
#transforma una hora solar en formato string 'HH:MM:SS' a decimal
#por simplicidad el origen lo ponemos en el mediodía
    hora=datetime.datetime.strptime(horasolar, '%H:%M:%S')
    hh=hora.hour
    mm=hora.minute
    ss=hora.second
#ojo! restamos 12 horas para que el mediodía solar sea t=0
    hs=hh+mm/60+ss/3600-12 
    
#ojo de nuevo, esta va a ser la única función que devuelva horas como float64
#ya que la hora decimal se suele usar para otros cálculos
#también, el resultado está en HORAS (porque normalmente omega es horas^-1)
    return hs

from .solar import gammadec, vectorsolar #este import se tiene que quedar aquí

def horasdia(diajuliano, latitud):
    
#devuelve la duración del día en formato string 'HH:MM:SS' y decimal
    
    omega=2*np.pi/24 #unidades h^-1
    lat=latitud*np.pi/180 #convertimos la latitud a radianes
    
    dec=np.pi/180*gammadec(diajuliano)[1]
    
#comprobamos que no estamos en una situación polar (por si acaso)
#vamos a calcular la duración del día como la diferencia de tiempos entre
#orto y ocaso
    
    s=-np.tan(dec)*np.tan(lat)
    if np.abs(s) < 1:
        ort=-1/omega*np.arccos(s)
        oc=1/omega*np.arccos(s)
        dur=oc-ort 
#esta duración así expresada está en horas decimales 
#convertir a hh:mm:ss
        durmod=divmod(dur,1)
        hh=durmod[0]
        minmod=divmod(durmod[1],1/60)
        mm=minmod[0]
        ss=divmod(minmod[1],1/3600)[0]
        duracion='%.2d:%.2d:%.2d' % (hh,mm,ss)
        
    elif s<1:
        np.disp('Es un día polar. La duración del día es de 24 horas')
        duracion='%.2d:00:00' % 24
    
    elif s>1:
        np.disp('Es una noche polar. La duración del día es de 0 horas')
        duracion='%.2d:00:00' % 0
    
#comparado con suncalc.org, hay una diferencia (dia 322 en Córdoba, 37.87064ºN) 
#de unos 4 minutos
#en cálculos futuros es interesante tener a mano los valores de orto, ocaso
#y duración en formato decimal; por ello los devolvemos
#además, no podemos sacar un array porque nos lo pone todo con tipo string
#y no podemos hacer cálculos con ello. Por defecto devuelve una lista
#y cada objeto mantiene su tipo.
    return [ort,oc,dur,duracion]