from sympy.geometry import Plane, Point
from numpy import pi, array, sqrt, dot, sin, cos, arctan, arccos
from numpy.linalg import norm
from .solar import vectorsolar
import time 

class Placa:

    def __init__(self, p1,p2,p3):
#la función __init__() se ejecuta cuando se crea el objeto, otorgando
#las propiedades que nosotros queramos.

#p1,p2,p3 serán los puntos (3D) que definen el plano de la placa
#construiremos geométricamente el rectángulo de las dimensiones
#adecuadas a partir de líneas y estos puntos en tipo Point
        a=array(p1)
        b=array(p2)
        c=array(p3)
       
        lado1=a-b
        lado2=c-b
        
        d=lado1+lado2+b
        self.puntos=[tuple(a),tuple(b),tuple(c),tuple(d)]
                        
#asignamos como atributos las dimensiones de las placas (en m) 
#que es un dato de Excel(innecesario teniendo los puntos)
        
        self.largo=round(norm(lado1),2)
        self.alto=round(norm(lado2),2)
        
        self.puntomedio=tuple((1/2)*(d-b)+b)
            
        self.area=self.largo*self.alto #(m²)
        self.plano=Plane(Point(a),Point(b),Point(c)) #plano que contiene a la placa
        self.ecplano=self.plano.equation() #ecuación del plano que contiene a la placa
        #para las intersecciones
        self.normal=array(self.plano.normal_vector/norm(array(self.plano.normal_vector, \
                                                              dtype=float)), dtype=float)
        
        self.inclinacion=(180/pi)*arccos(self.normal[2])
        
        if self.normal[1]==0:
            self.azimut=0
            
        else:
            self.azimut=(180/pi)*arctan(self.normal[0]/self.normal[1])
    
    
    def interseca(self, p,u):
#en esta funcion calculamos si hay interseccion con la placa con un método analítico
        p=array(p, dtype=float)
        u=array(u, dtype=float)
        
        normal=array(self.plano.normal_vector, dtype=float)
        punto=array(self.plano.p1.coordinates, dtype=float)
        
        suma=normal[0]*(u[0]/u[2])+normal[1]*(u[1]/u[2])
        d=-dot(normal,punto)
        
        zinter=(1/(suma+normal[2]))*(suma*p[2]-normal[0]*p[0]-normal[1]*punto[1]-d)
        eta=zinter-p[2]
        
        xinter=(u[0]/u[2])*eta+p[0]
        yinter=(u[1]/u[2])*eta+p[1]
        
        inter=array([xinter, yinter, zinter])
        
        ref=array(self.puntos[0])
        u=array(self.puntos[1])-ref
        v=array(self.puntos[3])-ref
        vecint=inter-ref
        
        escu=dot(u,vecint)
        escv=dot(v,vecint)
        if escu>0 and escu<self.largo**2 \
        and escv>0 and escv<self.alto**2:
            sec=1
            
        else:
            sec=0
          
#la función devuelve 1 si hay intersección, 0 si no.

        return sec
   
    
    def seguiuneje(self, diajuliano, horasolar, latitud, eje=None):
#cuando se llame a esta función, el colector tendrá seguimiento a un eje
#la variable eje debe ser un vector (vx,vy,vz) que defina el eje de rotación
#por defecto, el eje de rotación lo consideramos horizontal
        if eje==None:
            eje=abs(array((self.lado2.midpoint-self.lado4.midpoint).coordinates, dtype=float))
            
        eje=array(eje/norm(eje))
        n0=array(self.plano.normal_vector/norm(array(self.plano.normal_vector,dtype=float)),dtype=float) 
#vector normal inicial, convertido a vector numpy y normalizado
        
        solar=vectorsolar(diajuliano,horasolar,latitud)
        
        mu=sqrt((1-dot(eje, n0)**2)/(1-dot(eje, solar)**2))
        lamb=dot(eje, n0)-mu*dot(solar,eje)
        
        n=array((lamb*eje+mu*solar)/(norm(array(lamb*eje+mu*solar,dtype=float))),dtype=float) #$\left\vert n \right\vert = 1$
        
#de momento nos vale con devolver el valor del vector normal para cada hora
#posteriormente se debe reformular la placa 
        return n 
        
        
    def crear_rotada(self,normal):
#el vector normal será el vector solar, ecuaciones de giro.
        start=time.time()
        normal=array(normal/norm(normal)) #normalizado por si acaso
        beta=(pi/180)*self.inclinacion #inclinacion
        alfa=(pi/180)*self.azimut #azimut en radianes
        
        puntos=array([self.puntos[i] for i in range(3)])
        puntos=puntos-array(self.puntomedio)
#defino matrices de rotacion rx para beta y rz para alfa
        rx=array([[1,0,0],[0, cos(beta), -sin(beta)],[0,sin(beta), cos(beta)]])
        rz=array([[cos(alfa),-sin(alfa), 0],[sin(alfa), cos(alfa),0],[0,0,1]]) 
#hallamos los productos correspondientes con numpy.dot()
        for i in range(3):
            puntos[i]=dot(dot(puntos[i],rx),rz)
            puntos[i]=puntos[i]+array(self.puntomedio)
        self.__init__(tuple(puntos[0]),tuple(puntos[1]),tuple(puntos[2]))
        print("--- %s seconds ---" % (time.time() - start))
        return (puntos, rx, rz)
            
    
    def reiniciar(self):
        normal=self.normal
        beta=(pi/180)*self.inclinacion #inclinacion
        alfa=arctan(normal[0]/normal[1]) #azimut
        puntos=array([self.puntos[i] for i in range(3)])
        puntos=puntos-array(self.puntomedio)
#defino matrices de rotacion rx para beta y rz para alfa
        rx=array([[1,0,0],[0, cos(beta), -sin(beta)],[0,sin(beta), cos(beta)]]).transpose()
        rz=array([[cos(alfa),-sin(alfa), 0],[sin(alfa), cos(alfa),0],[0,0,1]]).transpose()
        
#hallamos los productos correspondientes con numpy.dot()
        for i in range(3):
            puntos[i]=dot(dot(puntos[i],rz),rx)
            puntos[i]=puntos[i]+array(self.puntomedio)
        self.__init__(tuple(puntos[0]),tuple(puntos[1]),tuple(puntos[2]))