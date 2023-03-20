# -*- coding: utf-8 -*-
"""TP2_PSB_Alvarez,Criado, Navari.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IPM-aSPy3qRcO8Y0-BtU3gcYrVkrVa4n

TRABAJO PRACTICO Nº2 - PROCESAMIENTO DE SEÑALES BIOMEDICAS

Integrantes:


*   Alvarez Rottemberg, Malena Gisela - 59437
*   Criado, Lazaro - 59447
*   Navari, Agustin - 59288
"""

from google.colab import drive
drive.mount('/content/drive')

"""LIBRERIAS A USAR"""

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import matplotlib.ticker as tck
import scipy as sp
import scipy.signal as sig
from scipy.linalg import toeplitz
from scipy import io
from scipy.fftpack import fft, ifft, fftfreq

"""# EJERCICIO 1

El ejercicio pide encontrar un sistema equivalente a un sistema ARMA de forma tal que al ingresar con el mismo ruido blanco se obtenga una salida muy similar.


Para lograrlo se implementaron las ecuaciones de Wiener-Hopf para encontrar los coeficientes de un filtro que cumpla lo pedido. El ritmo alfa provisto como señal deseada y el ruido blanco (el mismo que se utilizó para generar el ritmo en el sistema ARMA) como entrada al sistema. 

Luego se utilizó el criterio de Akaike para encontrar el orden óptimo del filtro a implementar.

Primero cargamos el ritmo alfa y el ruido con el cual esta señal fue generada.
"""

data= sp.io.loadmat('/content/drive/MyDrive/PSB/tp2/EEG_alpha.mat')

print(data)

#Levantamos las señales

senal=data['eeg'][0]
fmuestreo=data['fs'][0]
x_ruido = data['x'][0]

"""A continuación se muestran las funciones de Wiener-Hopf y del criterio de Akaike que serán utilizadas en este ejercicio. \\
La función de Wiener devuelve los coeficientes del filtro a ser implementado. \\
La función de Akaike devuelve los valores AIC con los cuales se encontrará el orden óptimo. Para calcularlos se utilizó el error cuadrático medio. 
"""

def wiener(x,d,L):
  
  rxx= sig.correlate(x,x, mode='same')
  rxx = rxx[int(len(rxx)/2):int(len(rxx)/2)+L]/max(rxx)

  rxy=sig.correlate(x,d,mode='same')
  rxy= rxy[int(len(rxy)/2):int(len(rxy)/2)+L]/max(rxy)

  R= toeplitz(rxx)
  R_inv= sp.linalg.inv(R)
  condicionamiento= np.linalg.cond(R_inv)


  if condicionamiento < 500:
    h= R_inv.dot(rxy)
    
    return h #los coeficientes del filtro

  else:
    print("no cumple con el condicionamiento")
    return 



#Criterio de Akaike para encontrar el orden óptimo

def akaike_nuestro(sig_estimada, sig_deseada, orden):
    N = len(sig_deseada) 
    
    # Se toma el error cuadrático medio como parámetro de error
    ep2 = 0
    ep2=np.sum((sig_deseada - sig_estimada )**2)/N
 
    AIC = N * np.log(ep2) + 2 * orden
    
    return AIC,ep2

"""Encontramos el orden óptimo usando el criterio de Akaike. Para ello realizamos iteraciones en las cuales se va aumentando el orden que se le pasa a la función de Wiener y observamos para cual el valor de AIC es mínimo.

Luego de correr la siguiente ventana de código se observarán en este orden: el órden mínimo calculado con Akaike;la media y la varianza de ambas señales; un gráfico del criterio para distintos órdenes; Algunos segúndos de la señal deseada y estimada para visualizar las similitudes y finalmente un gráfico de los espectros de ambas señales. 


"""

#Vector de tiempos para la señal

tfinal= len(senal)/fmuestreo
N= int(tfinal *fmuestreo)
Ts = 1/fmuestreo

tiempo = np.arange(0,N)*Ts


#Criterio de Akaike para encontrar el orden óptimo

iteraciones = 100
A = np.array([])
ordenes = np.array([])

for i in range(2,iteraciones):
  
  coeficientes = wiener(x_ruido,senal,i)
  filtrada = sig.filtfilt(coeficientes,1,x_ruido)
  AIC,err2 = akaike_nuestro(filtrada,senal,i)
  A = np.append(A,AIC)

  ordenes = np.append(ordenes,i)


# Luego de las iteraciones, se busca el valor mínimo en el vector A en donde se guardaron los valores de AIC
    
Am = np.argmin(A) 
OrdenOptimo = ordenes[Am]
print('El orden óptimo hallado es:',OrdenOptimo)

# filtramos el ruido con el orden óptimo para visualizar los resultados

coeficientes = wiener(x_ruido,senal,i)
filtrada_min = sig.filtfilt(coeficientes,1,x_ruido)
filtrada_min = filtrada_min/(np.amax(filtrada_min))

senal = senal/np.max(senal)

print("Media del ritmo alfa", np.mean(senal), "\nMedia de la señal estimada", np.mean(filtrada_min))
print("Varianza del ritmo alfa", np.var(senal), "\nVarianza de la señal estimada", np.var(filtrada_min))


plt.figure()
plt.figure(figsize=(15,5))
plt.plot(ordenes,A)
plt.title('Gráfico del criterio de Akaike')
plt.ylabel('AIC')
plt.xlabel('orden')


plt.figure()
plt.figure(figsize=(25,5))
plt.plot(tiempo,filtrada_min)
plt.plot(tiempo,senal)
plt.title('Ritmo alfa y señal estimada')
plt.xlim([4,6])
plt.xlabel('tiempo [seg]')
plt.legend(['Señal estimada','Ritmo alfa'])


#espectro del ritmo alfa y la señal estimada:

vecf_original= np.linspace(0,fmuestreo, len(senal))

dep_original= (np.abs(np.fft.fft(senal))**2) * (1/len(senal))
dep_filtrada_min = (np.abs(np.fft.fft(filtrada_min))**2) * (1/len(filtrada_min))


plt.figure()
plt.figure(figsize=(10,5))
plt.title('Densidad espectral de potencia de la señal estimada y del ritmo alfa')
plt.plot(vecf_original,dep_original)
plt.plot(vecf_original,dep_filtrada_min)
plt.xlim(0,40)
plt.xlabel('Frecuencia [Hz]')
plt.legend(['Ritmo alfa','Señal estimada'])
plt.show()

"""Se llegó a la conclusión que el sistema equivalente es LTI.

Nota del ejercicio 1: a veces el orden mínimo de akaike no da bien si no se corren todas las cajas de código en orden desde la primera del ejercicio. En caso de que ocurra esto simplemente hay que correr desde la primera. El orden mínimo calculado debería ser 41.

# **EJERCICIO 2**
"""

data3= sp.io.loadmat('/content/drive/Shareddrives/PSB/EEG_ritmos2(1).mat')
ritmos=data3['eeg']
fmuestreo_2=data3['fs'][0,0]
t=np.linspace(0,16,4098) 
#print(fmuestreo_2)

def lpc(y, m):
    R = [y.dot(y)]
    if R[0] == 0:
        return [1] + [0] * (m-2) + [-1]
    else:
        for i in range(1, m + 1):
            r = y[i:].dot(y[:-i])
            R.append(r)
        R = np.array(R)
        A = np.array([1, -R[1] / R[0]])
        P = R[0] + R[1] * A[1]
        for k in range(1, m):
            if (P == 0):
                P = 10e-17
            ki = - A[:k+1].dot(R[k+1:0:-1]) / P
            A = np.hstack([A,0])
            A = A + ki * A[::-1]
            P *= (1 - ki**2)
        return A

#defino vref con el primer segundo de la señal y la corro
vref= np.transpose(ritmos[:256])[0]
vref_corrida= np.zeros_like(vref)

for i in range(1,len(vref)-1):
  vref_corrida[i-1]= vref[i]

L=50
Sistema_MA= lpc(vref,L)
paso= int(len(vref)/4)
#paso=1
filtro_lpc= sig.lfilter(Sistema_MA,1,vref_corrida)

#defino el termino de delta n correspondiente al valor maximo de la autocorrelacion del filtrado de vref 
#re_0= np.correlate(vref,vref,mode='full')/len(vref)
re_0= np.correlate(filtro_lpc,filtro_lpc,mode='full')/len(filtro_lpc)
re_00= re_0[int(re_0.shape[0]/2)]

DELTA = []

for i in range(paso, len(ritmos)-len(vref), paso):
  v_test = np.transpose(ritmos[i:i+len(vref)])[0]
  v_test_corrida=np.zeros_like(v_test)
 
  for k in range(1,len(v_test)-1):
    v_test_corrida[k-1] = v_test[k]
  
  filtrada_prueba= sig.lfilter(Sistema_MA,1, v_test_corrida)

  re_0n= np.correlate(filtrada_prueba,filtrada_prueba, mode='full')/len(filtrada_prueba)
  re_0n_s0= np.correlate(filtrada_prueba,filtrada_prueba, mode='full')/len(filtrada_prueba) # redfino la autocorrelacion para sacarle el
                                                                                            #valor central para ponerlo en la sumatoria de la formula de disimiltud.
  
  re_0n_s0[int(re_0n_s0.shape[0]/2)] = 0
  aux=(((re_00)/(np.max(re_0n)))**2 - 1)**2 +( 2/((np.max(re_0n))**2))*np.sum((re_0n_s0)**2) 
  DELTA.append(aux)

DELTA=DELTA/max(DELTA)
ritmos=ritmos/np.max(ritmos)
DELTA_0 = sp.signal.resample(DELTA, 4098)
umbral= 0.25*(np.max(DELTA)) 

#HAGO EL ESPECTROGRAMA DE LA SEÑAL RITMOS PARA VER LOS DISTINTOS TIEMPOS PARA SEGMENTAR 
ritmos=np.transpose(ritmos)
plt.specgram(ritmos[0], Fs=fmuestreo_2)
plt.title('Espectrograma de la señal de EEG')
plt.xlabel('Frecuencias (Hz)')
plt.ylabel('Tiempo (s)')

plt.figure(figsize=[35,7])
ritmos=np.transpose(ritmos)
plt.plot(t,ritmos)
plt.plot(t,DELTA_0,'r')

plt.title('Encefalograma superpuesto con la funcion de disimilutd')
plt.xlabel('Tiempo (s)')
plt.ylabel('Amplitud')
plt.show()

"""A partir del espectrograma puedo observar que el cambio frecuencial de la señal de EEG se da cada 4 segundos. Tambien a partir de este se puede empezar a sospechar que el primer segmento puede corresponder a ruido blanco o a un ritmo cerebral gamma, mientras que los demas solo pueden ser ritmos cerebrales. Esto ultimo hace coincidencia con lo obtenido en la funcion de disimilitud, ya que si se observa la figura 2, la funcion Delta nunca vuelve a tomar el valor cero, siemrpe se mantiene por arriba o debajo del umbral, pero nunca se anula. Entonces si se tratara de ruido blanco en el primer segmento, la funcion de disimilitud deberia volver a valer cero, pero no lo hace. 

Ahora se va a realizar la segmentacion de la señal cada 4 segundos, y tambien se van a buscar las densidades espectrales de potencia por el metodo del periodograma de cada segmento para corroborar la informacion que brindo el espectrograma. Decido analizar las varianzas de los segmentos para poder decidir sobre que tipo de señal se trata el segmento 1.


"""

def segmentacion (ritmo_EEG,fs):
  senal_segmentada=[]
  for i in range(0,len(ritmo_EEG)-2,1024):
      senal_segmentada.append((ritmo_EEG[i:i+1024]))
      print(f"La Varianza del segmento {int(i/1024)} es: {np.var(ritmo_EEG[i:i+1024])}")
  frecuencias= []  
  for k in range(0, np.shape(senal_segmentada)[0]):
    espectro= fft(np.transpose(senal_segmentada[k]))
    s_x= (np.abs(espectro**2))/(np.shape(espectro)[0])
    frecuencias.append(s_x)

  return senal_segmentada,frecuencias

senal_segmen ,frecuencias = segmentacion (ritmos,fmuestreo_2)

k=int(len(vref))
t1=np.linspace(0,4,k)
t2= np.linspace(4,8,k)
t3= np.linspace(8,12,k)
t4=np.linspace(12,16,k)

plt.figure(figsize=[39,7])
plt.title("Segmentos de EEG")
plt.plot(t1,ritmos[0:k], label='Segmento 1')
plt.plot(t2,ritmos[k:2*k], label= 'Segmento 2')
plt.plot(t3, ritmos[2*k:3*k],label='Segmento 3')
plt.plot(t4, ritmos[3*k:4*k], label = 'Segmento 4')
plt.legend()


for i in range (0,np.shape(frecuencias)[0]):
  dep= np.transpose(frecuencias[i])
  L = dep.shape[0]
  #vec_f= np.linspace(0,fmuestreo_2,np.shape(frecuencias[i])[0])
  vec_f = np.linspace(0,1,L) * fmuestreo_2
  x=int(len(vec_f)/2)
  
  plt.figure(figsize=[35,7])
  plt.plot(vec_f[0:x],dep[0:x])
  plt.title(f'Densidad Espectral de Potencia del Segmento {i}')
  plt.show()

m=len(segmento[0])
vec_f = np.linspace(0,1,m) * fmuestreo_2
plt.figure(figsize=[25,7])
plt.plot(vec_f,fft(senal_segmen[0]))
plt.title("Transformada de Fourier del Segmento 1")
plt.legend()
plt.show()

"""Para concluir, si se observan las distintas densidades espectrales, los 4 picos son coincidentes con lo que se vio en el Espectrograma, por lo que la segmentacion fue exitosa. Puntualmente, los picos de cada segmento se hallan en:
*   Segmento 0: 60 Hz
*   Segmento 1: 4.25 Hz
*   Segmento 2: 29.75 Hz
*   Segmento 3: 10 Hz 

Tambien se sabe que los ritmos cerebrales poseen las siguientes frecuencias:
*   Ritmo Beta: 13-30 Hz
*   Ritmo Alpha: 8-13 Hz
*   Ritmo Theta: 4-8 Hz
*   Ritmo Delta: 0.5-4 Hz
*   Ritmo Gamma: 30 Hz -100 Hz

Analizando las varianzas de los segmentos se puede pensar de que el segmento 1 es un ritmo cerebral, ya que por mas de que sea muy chica y aproxima a cero (varianza del ruido blanco), los demas segmentos poseen varianza muy similar. Ademas,al observar la transformada de fourier de este segmento podemos observar que no es constante para todas las frecuencias. Por ende, concluimos que el primer segmento corresponde a ritmo gamma, el segundo corresponde a un ritmo cerebral Theta, el tercero a un ritmo cerebral Beta, y el cuarto a un ritmo cerebral Alpha.

# **EJERCICIO 3**

Para resolver este ejercicio se planteo una funcion (*def **lpc**(y=señal de entrada,m=orden)*) que hace la prediccion lineal de coeficientes de un sistema de media movil (MA) usando el algoritmo de Levindon Durvin, para luego utilizar esos coeficientes, invertirlos y obtener un sistema autorregresivo (AR) que sintetice un ritmo ***α*** de EEG. La idea para obtener la ecuaciones de Yule Walker esta en que, por Wiener, sabemos que el filtro (el sistema MA) va a ser optimo cuando la salida del mismo sea perpendicular a la entrada, entonces las ecuaciones quedan#

$\sum_{l=0}^{L} a[l]\, R_{rr}[m-l]= \left\{
	       \begin{array}{ll}
		 0      & \mathrm{si\ }  1 \leq m \leq L \\
		 P_f^L     & \mathrm{si\ } m = 0
	       \end{array}
	     \right.$

Donde $a[l]$ son los coeficientes del sistema MA, $R_{rr}$ es la matriz toepliz de autocorrelacion de la entrada y $P_f^L $ es la potencia del error.

Finalmente se procede a calcular el orden optimo realizando iteraciones donde lo que varia es el orden del filtro. Se plantea un *loop* de 50 iteraciones en el que se llama a la funcion lpc con cada orden y se hace la estimacion de la señal. Con estas dos señales se calcula el para AIC del criterio de Akaike y se veriica si es el mimimo o no. De ser así, se guarda la ultima estimacion en una variable y se muestran los siguientes resultados#


*   Señal original vs señal estima
*   DEP de la señal original vs DEP de la señal estimada
*   Variacion del AIC del criterio de Akaike
"""

import scipy as sp
from scipy import signal , io
from scipy.io import loadmat
import numpy as np 
import matplotlib.pyplot as plt
from scipy.fftpack import fft, ifft, fftfreq

data= sp.io.loadmat('/content/drive/Shareddrives/PSB/EEG_alpha.mat') 
#print(sorted(data.keys()))

senal=data['eeg'][0:]
senal=senal[0]
N=len(senal)
fs=data['fs'][0,0]
x_ruido=data['x'][0]

# funcion para calculador el filtro blanqueador
def lpc(y, m):
  R = [y.dot(y)]
  if R[0] == 0:
      return [1] + [0] * (m-2) + [-1]
  else:
      for i in range(1, m + 1):
          r = y[i:].dot(y[:-i])
          R.append(r)
      R = np.array(R)
      A = np.array([1, -R[1] / R[0]])
      P = R[0] + R[1] * A[1]
      for k in range(1, m):
          if (P == 0):
              P = 10e-17
          ki = - A[:k+1].dot(R[k+1:0:-1]) / P
          A = np.hstack([A,0])
          A = A + ki * A[::-1]
          P *= (1 - ki**2)
      return A

def akaike(sig_estimada, sig_deseada, orden):
    N = len(sig_deseada) 
    ep2 = 0
    ep2=(np.sum(sig_estimada - sig_deseada )**2)
    
    AIC = N * np.log(ep2) + 2 * orden
    return AIC,ep2

iteraciones=50 #cantidad de ordenes con los que pruebo
A = np.array([])
ordenes = np.array([])
err = np.array([])

for ord in range(2,iteraciones):
  
  Sistema_MA=lpc(senal,ord)
  estimacion_senal=signal.filtfilt(1,Sistema_MA,x_ruido)
  AIC,error_cuad_medio = akaike(estimacion_senal,senal,ord)

  ordenes = np.append(ordenes,ord)
  A = np.append(A,AIC)
  
  if (AIC == np.min(A)):
    
    estimacion_senal_min = estimacion_senal
    pos_AIC_min = np.argmin(A)                #argmin me da la posicion del minimo de A
    orden_optimo = (ordenes[pos_AIC_min])  
  

print("El orden optimo es: ",orden_optimo)

#normalizacion de la señal y la estimacion
estimacion_senal_min= estimacion_senal_min/(np.max(estimacion_senal_min))
senal= senal/(np.max(senal))

#Densidades espectrales
DEP_senal=(1/N)*np.abs(np.fft.fft(senal)**2)
DEP_estimacion_senal_min = (1/N)*np.abs(np.fft.fft(estimacion_senal_min))**2 

vec_f=np.linspace(0,fs,3000)

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(25, 5))

ax1.plot(estimacion_senal_min)
ax1.plot(senal)
ax1.legend(['estimacion','ECG_alpha.mat'])

ax2.plot(vec_f,DEP_estimacion_senal_min)
ax2.plot(vec_f,DEP_senal)
ax2.set_xlim([0,int(fs/2)])
ax2.legend(['DEP_estimacion','DEP_ECG_alpha.mat'])

ax3.plot(ordenes,A)
ax3.set_title(f"Orden optimo: {orden_optimo}")
ax3.legend(['Akaike'])

"""## **EJERCICIO 4**

1) Para ruido blanco y para senos 

Se calcula el promedio exponencial de las 62 realizaciones con ruido blanco y con ruido de senos, luego se los grafica todos juntos para su respectiva comparación.
"""

import scipy as sp
from scipy import signal , io
from scipy.io import loadmat
import numpy as np 
import matplotlib.pyplot as plt
from scipy.fftpack import fft, ifft, fftfreq

data= sp.io.loadmat('/content/drive/Shareddrives/PSB/ECG_Delineado2.mat') 

Fs=data['Fs'][0][0]
d2=np.transpose(data['D2'][0:])[0]
qrs=np.transpose(data['qrs'][0:])[0]

tiempo=np.linspace(0,len(d2)/Fs,len(d2)) #para plotear la señal en tiempo en lugar de con muestras
qrs_tiempo=qrs*(1/Fs)                    #para plotear la señal en tiempo en lugar de con muestras

#calculo la cantidad de muestras que tienen que tener las realizaciones
#Tomamos 100ms para atras de la posicion del pico del wrs y 500ms para adelante (100 muestras)

N=len(qrs)
m_atras=20
m_adelante=100
realizaciones=np.zeros((N,m_atras+m_adelante))           
realizaciones_seno=np.zeros((N,m_atras+m_adelante))
realizaciones_sin_ruido=np.zeros((N,m_atras+m_adelante))

tiempo_realizaciones=np.linspace(0,realizaciones.shape[1]/Fs,realizaciones.shape[1]) #para plotear las realizaciones en tiempo en lugar de con muestras

for i in range(len(d2)):
  for k in range(N):
    if i==qrs[k]:
      muestras_qrs[k]=d2[i]
      pot_ruido=1
      ruido=pot_ruido*np.random.randn(realizaciones.shape[1])

      amp=1
      fase=np.random.randn(1)
      sen=amp*np.sin(2*np.pi*50*tiempo_realizaciones + fase)
      
      aux=d2[i-m_atras:i+m_adelante]
      realizaciones[k,:]=aux + ruido
      realizaciones_seno[k,:]=aux + sen
      realizaciones_sin_ruido[k,:]=aux

#Calculo el promedio exponencial recursivo
s_o=realizaciones[0,:] #shape (120,)
s_o_seno=realizaciones_seno[0,:]

for k in range(1,N):
  s_o=(k*s_o + realizaciones[k,:])/(k+1)
  s_o_seno=(k*s_o_seno + realizaciones_seno[k,:])/(k+1)
var_s=np.var(s_o)
var_s_seno=np.var(s_o_seno)

#FIGURA PARA LAS REALIZACIONES CON RUIDO BLANCO
plt.figure(figsize=(10,5))
for i in range(N):
    plt.plot(tiempo_realizaciones ,realizaciones[i,:])
    #plt.plot(tiempo_realizaciones,realizaciones_sin_ruido[i,:] - i*50, label=f'realizacion sin ruido {i}')
plt.plot(tiempo_realizaciones,s_o,'k',label=f'promedio de las {N} realizaciones con ruido blanco')  
plt.title('REALIZACIONES CON RUIDO BLANCO')
plt.xlim(0,0.3)
plt.legend() 
plt.show()


#FIGURA PARA LAS REALIZACIONES CON SENOS
plt.figure(figsize=(10,5))
for i in range(N):
    plt.plot(tiempo_realizaciones ,realizaciones_seno[i,:])
    #plt.plot(tiempo_realizaciones,realizaciones_sin_ruido[i,:] - i*50, label=f'realizacion sin ruido {i}')
plt.plot(tiempo_realizaciones,s_o_seno,'k',label=f'promedio de las {N} realizaciones con el ruido de senos')
plt.title('REALIZACIONES CON SENOS')
plt.xlim(0,0.3)
plt.legend()  
plt.show()

"""2) y 3) Para ruido blanco y para los senos

Se toma el intervalo de las primeras 10 muestras de las realizaciones debido a que es la unica parte en la que la señal es plana y respesta una linda base isoelectrica. Con el promedio calculado a medida que se van a agregando las realizaciones se va calculando la varianza de las primeras 10 muestras. Si se cumple la condicion que la varianza calculada es menor que la anterior, entonces esa realizacion se tiene en cuenta, si no, no.

Respecto a la comparacion de amos promedios se puede ver que dan muy similares entre si, pero claramente tiene una varianza mayor el de las realizaciones de los senos pues en las realizaciones de ruido blanco hay mayor cantidad que aportan a que la varianza disminuya.


"""

var_s_aux=np.zeros((N))             #vector de varianzas de la realizaciones con ruido blanco
var_s_aux_seno=np.zeros((N))        #vector de varianzas de la realizaciones con senos

s_o_menos_ruido=realizaciones[0,:]  #variable de promedio exponencial de las realiciones de ruido blanco que aportan para su disminucion
s_aux=realizaciones[0,:] 
s_o_menos_ruido_seno=realizaciones_seno[0,:] #variable de promedio exponencial de las realiciones de senos que aportan para su disminucion
s_aux_seno=realizaciones_seno[0,:]

#tomo las primeras 10 muestras de cada realizacion ya que es la parte donde la señal es mas plana, es decir, tienen una linea de base isoeléctrica
var_s_aux[0]=np.var(s_aux[0:10])
var_s_aux_seno[0]=np.var(s_aux_seno[0:10])
cant_realizaciones=0
cant_realizaciones_seno=0

for k in range(1,N):
  #calculos auxiliares

  s_aux=(k*s_aux + realizaciones[k,:])/(k+1)
  var_s_aux[k]=np.var(s_aux[0:10])

  s_aux_seno=(k*s_aux_seno + realizaciones_seno[k,:])/(k+1)
  var_s_aux_seno[k]=np.var(s_aux_seno[0:10])

  #si la varianza de S con la nueva realizacion me da mas chiquita que la anterior, la agrego, si no, no.
  #hago lo mismo dos veces, una para las realizaciones de ruido blanco y otra para las de los senos
  if (var_s_aux[k]<var_s_aux[k-1]):
    s_o_menos_ruido=(k*s_o_menos_ruido + realizaciones[k,:])/(k+1)
    cant_realizaciones+=1

  if (var_s_aux_seno[k]<var_s_aux_seno[k-1]):
    s_o_menos_ruido_seno=(k*s_o_menos_ruido_seno + realizaciones_seno[k,:])/(k+1)
    cant_realizaciones_seno+=1

tiempo_realizaciones=np.linspace(0,realizaciones.shape[1]/Fs,realizaciones.shape[1])

#FIGURA PARA REALIZACIONES CON RUIDO BLANCO
plt.figure(figsize=(10,5))
plt.plot(tiempo_realizaciones,s_o,label=f'promedio exponencial de {N} realizaciones con ruido blanco')
plt.plot(tiempo_realizaciones,s_o_menos_ruido,label=f'promedio exponencial con {cant_realizaciones} realizaciones con ruido blanco')
plt.title('REALIZACIONES CON RUIDO BLANCO')
plt.xlim(0,0.3)
plt.legend()  

#FIGURA PARA REALIZACIONES CON SENOS
plt.figure(figsize=(10,5))
plt.plot(tiempo_realizaciones,s_o_seno,label=f'promedio exponencial de {N} realizaciones con senos')
plt.plot(tiempo_realizaciones,s_o_menos_ruido_seno,label=f'promedio exponencial de {cant_realizaciones_seno} realizaciones con senos')
plt.title('REALIZACIONES CON SENOS')
plt.xlim(0,0.3)
plt.legend()  
plt.show()

#FIGURA DE COMPARACION
plt.figure(figsize=(10,5))
plt.plot(tiempo_realizaciones,s_o_menos_ruido,label=f'promedio exponencial con {cant_realizaciones} realizaciones con ruido blanco')
plt.plot(tiempo_realizaciones,s_o_menos_ruido_seno,label=f'promedio exponencial de {cant_realizaciones_seno} realizaciones con senos')
plt.title('REALIZACIONES CON SENOS VS REALIZACIONES CON RUIDO BLANCO')
plt.xlim(0,0.3)
plt.legend()  
plt.show()

"""# EJERCICIO 5

promedio general de la señal --> ensamble, alineacion de los latidos, promedio ordianrio de los latidos

Se toma cada latido y hacemos la correlacion del latido actual contra el promedio que acabode hacer sobre toda la gira de ECG (osea ensamble), hasta encontrr el maximo de la corelacion. Nos quedamos con ese valor de correlacion y vemos la amplitud. Los latidos que tienen un nivel de correlacion cruzada por debajo del 80% son ectopicos, por arriba sinusales. puede pasar que los latidos esten desalineados, entonces desplazo hasta 10 muestras del promedio/latido para buscar ese maximo de correlacion cruzada osea hago un vector de coeficiente de correlacion de pearson y le busco el maximo a eso. 

en cada tiempo de ocurrencia  debo segmentar el latido y ahi hacer el snable 

"""

!pip install wfdb

import wfdb
N=21600
path= '/content/drive/MyDrive/PSB/tp2/109'
signal, fields = wfdb.rdsamp(path,1,N)
print(fields)

fmuestreo3= fields['fs']
senal= signal[:,1]

L=len(senal)
t=np.linspace(0,L/fmuestreo3,L)
plt.figure(figsize=[25,7])
plt.plot(t,senal)
plt.title("Señal original")

#senal_postfiltraado= deteccionQRS(senal, 5, 20, fmuestreo, 100)
fc1=5
fc2=15
orden=40

#b3,a3=sig.iirfilter(95,[fc1,fc2],btype='bandpass',analog=False,ftype='butter',output = 'ba',fs=fmuestreo)
h_coef=sig.firwin(orden+1,[fc1,fc2],fs=fmuestreo3)
senal2=sig.filtfilt(h_coef,1,senal)

#derivador
derivada = 0
Fs = fmuestreo3
Ts = 1/Fs
aux = np.zeros(np.shape(senal2))
SF=30 

for i in range(SF,len(senal)-(1+SF)):
  derivada = (senal2[i+SF] -senal2[i-SF])/(2*SF*Ts)
  aux[i]=derivada
  if i==SF:
    aux[SF]=derivada

#elevo al cuadrado la señal
aux2= aux*aux

#integro la señal

aux3=np.zeros(np.shape(aux2))
aux3[0]=0
M=8
for k in range(1,len(aux2)-M):
  for p in range (k,k+M):
      Integral = aux3[p-1] + (aux2[p] + aux2[p-1])*(Ts)
  
  aux3[k]=Integral

print(type(aux3))
plt.figure(figsize=[25,7])
plt.plot(t,aux3)
plt.title("Señal de ECG luego del filtrado")
plt.show()

"""Para poder detectar los complejos QRS se planteo la idea de fijar un umbral, y entonces aquellos picos que pasen el mismo, se considerarian complejos QRS. Para este caso, se decidio usar como umbral $\frac{2}{5}$ $\cdot$ valor max

Busco las anotaciones realizadas por los dueños para observar los latidos. Cosnidero que los marcados como L son los sanos, osea provenientes del nodo sinusal, mientras que los que estan marcados como V y F son anormales, o ectopicos. 
"""

from wfdb import processing
umbral=(0.5)*np.max(aux3)
#umbral=np.mean(aux3)
#picos,_= sig.find_peaks(aux3,height=(umbral,np.max(aux3)),distance=30)
picos,_= sig.find_peaks(aux3,height=umbral,distance=150)
print(picos)
#picos= processing.find_local_peaks(aux3,200)

anotaciones= wfdb.rdann(path,'atr',1,N)
len(anotaciones.sample)
sim= anotaciones.symbol
sam=anotaciones.sample

plt.figure(figsize=[25,7])
plt.scatter(t[sam],aux3[sam],label='Profesional')
plt.scatter(t[picos],aux3[picos],label='Pan y Tompkins')
plt.plot(t,aux3,'y')
plt.title("Señal de ECG con los complejos WRS detectados por PT y por el profesional")
plt.legend()
plt.show()

print(f"Hay {np.shape(sam)[0]} complejos QRS anotados")
print(f"Se detectaron {np.shape(picos)[0]} complejos QRS")

"""Luego, realizo un algortimo para poder evaluar la sensibilidad y la prediccion positiva del algoritmo de deteccion de complejos QRS. Se siguieron las siguientes ecuaciones, teniendo en cuenta los verdaderos positivos (VP), falsos positivos (FP), falsos negativos (FN):

Sensibilidad = $\frac{VP}{VP+FN}$

Prediccion Positiva = $\frac{VP}{VP+FP}$

Donde los VP son aquellos complejos QRS que se dieron y fueron detectados, los FP son aquellos que fueron detectados pero en realidad no existian, y por ulitmo, los FN son aquellos que no detecte y en realidad existian. A partir de la figura anterior nos podemos dar cuenta que no hay falsos negativos en nuestro algoritmo de deteccion.

Para poder detectar los falsos positivos se toma un criterio de tolerancia del 20% entre las mismas posiciones de la lista de Detectados por Pan y Tompkins y la brindada en las anotaciones.
"""

FN=0
VP=0
FP=0

#Como la lista de los QRS detectados es distinta no puedo comparar punto a punto
#entonces creo dos arrays nuevos en donde se guarden los tiempos de ocurrencia de los complejos
tol=int(0.10*Fs)
detector=np.zeros(np.shape(aux3))
anotados=np.zeros(np.shape(aux3))
borro_detectados= detector

for i in range(0, len(picos)):
  detector[picos[i]]= True

for j in range(0,len(sam)):
  anotados[sam[j]]= True

for k in range(0,len(aux3)):
  if anotados[k] == True: #Se anoto la presencia de un complejo
    if np.any(detector[k-tol:k+tol]==True):
      VP+=1 #Yo detecte un complejo 
      borro_detectados[k-tol:k+tol]=0 
    else:
      FN+=1 #No detecte el complejo

for p in range (0, len(aux3)):
  if anotados[p]==0: #No se anoto la presencia de un complejo
    if np.any(detector[p-tol:p+tol]==True):
      FP+=1 #Mi detector lo detecto como positivo
      borro_detectados[p-tol:p+tol]=0

Sen= VP/(VP+FN)
PredicPos= VP/(VP+FP)

print(f"La Sensibilidad para el algoritmo de deteccion es: {np.round(Sen,3)} \nLa prediccion positiva para el algoritmo de deteccion es: {np.round(PredicPos,3)}")

"""Para determinar la especificidad del algoritmo de deteccion se deben tener en cuenta los verdaderos negativos, osea de todos los picos que no eran complejos QRS que realmente hay cuales mi algoritmo no detecto. Sin embargo, en este caso resulta bastante absurdo medir la especificidad ya que es mas conveniente una deteccion directa de complejos QRS.

Por ultimo, se quiere evaluar cuales latidos resultaron sanos, osea provenientes del nodo sinusal, y cuales fueron anormales. Para observar esa informacion se buscaron las anotaciones y lo encontrado fue L, V y F, refirinedo a lo siguiente:

*   L= Left bundle branch block beat 
*   V= Premature ventricular contraction
*   F= Fusion of ventricular and normal beat

Como el paciente dueño de este electrocardiograma posee una patologia de base que es un bloqueo de rama izquierda, se tomaron como L los latidos sanos, y V o F los latidos anormales. 

Entonces se segmentaron los latidos con una ventana de referencia de 400 ms, ya que al estar presente la condicion de bloqueo de rama izquierda, los complejos QRS se ven ensanchados, entonces lo ideal seria tomar una ventana del doble del ancho normal para poder detectarlos correctamente.
"""

def segmentacion_qrs(senal_ecg, complejos_qrs):
  condicion_inferior = int(0.01*Fs)
  condicion_superior = int(0.04*Fs)
  realizaciones = []

  for i in range(len(complejos_qrs)):
    seg= senal_ecg[complejos_qrs[i]-condicion_inferior:complejos_qrs[i]+condicion_superior]
    realizaciones.append(seg)

  return realizaciones

r=segmentacion_qrs(aux3,picos)
'''
plt.figure(figsize=[25,7])
for j in range(0,7):
  plt.plot(r[j])

plt.title("Realizaciones de los segmentos 0-7")
plt.show()
'''

"""Realizo el promedio ordinario de las realizaciones, para luego hacer la correlacion cruzada de ese promedio con cada segmento. Le busco el maximo a cada correlacion cruzada, y evaluo si es menor o mayor a 0.8. Si resulta menor a 0.8 entonces puedo considerar ese latido como ectopico, mientras que si da por encima de 0.8 lo considero sinusal, osea sano. """

k=np.shape(r)[0]
L=np.shape(r)[1]
promedio=np.zeros(np.shape(r)[1])

for i in range(0,k-1):
  for j in range(0,L):
    promedio+=r[i][0:L]

  promedio=promedio/len(promedio)

coeficientes_max=[]

for l in range(0,L):
  for w in range(0,k):
    correlacion_sen=np.correlate(r[l][0:L],promedio,mode='full')
  
    maximo=np.max(correlacion_sen)
  
  coeficientes_max.append(np.round(maximo,4))

print(f"Los valores maximos de cada correlacion son: {coeficientes_max}")

"""A partir de lo obtenido se puede ver que hay 4 valores maximos que estan por debajo de 0.8, por lo que puedo concluir de que hay 4 latidos que son ectopicos. Ahora comparemos con lo anotado en el archivo y analizamos la sensibilidad y la prediccion positiva de este algoritmo.

"""

anotaciones= wfdb.rdann(path,'atr',1,N)
len(anotaciones.sample)
sim= anotaciones.symbol

anormales= [i != 'L' and i != '+' for i in sim]
posicion_anormales= [i for i,j in zip(sam, anormales) if j]
normales = [i != '+' and i!= 'V' and i != 'F' for i in sim]

anormales_detec=[]
for u in range(0,len(coeficientes_max)):
  if coeficientes_max[u]<0.8:
    anormales_detec.append(coeficientes_max[u])

if len(posicion_anormales)>len(anormales_detec):
  VP=en(anormales_detec)
else:
  VP=len(posicion_anormales)

FP=0
FN=np.abs(len(posicion_anormales)-len(anormales_detec))
Sensibilidad= VP/(VP+FN)
PrediccionPositiva=VP/(VP+FP)

print(f"La Sensibilidad para el algoritmo de deteccion es: {np.round(Sensibilidad,3)} \nLa prediccion positiva para el algoritmo de deteccion es: {np.round(PrediccionPositiva,3)}")