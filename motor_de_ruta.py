# Importing python libraries
import sys
import json


# Importing file libraries 
from config import *

#importing aditional libraries
import googlemaps


gmaps = googlemaps.Client(key=KEY)


#Un trayecto es una lista de caminos que se conectan entre si. Por ejemplo:
#Un trayecto puede Consistir en un camino desde Buenos aires a Cordoba y otro camino de Cordoba a Mendoza.
trayecto_esquema = []

#Esquema
ruta_esquema = {
            'origin_addresses': ['Buenos Aires, Autonomous City of Buenos Aires, Argentina'],
            'status': 'OK',
            'rows':
            [
                {'elements':
                    [
                        {
                            'distance': {'value': 1049668, 'text': '1,050 km'},
                            'status': 'OK',
                            'duration': {'value': 40136, 'text': '11 hours 9 mins'}
                        }
                    ]
                }
            ],
            'destination_addresses': ['Mendoza, Capital Department, Mendoza Province, Argentina']
          }

#Cuando no se encuentra una ruta entre 2 ciudades , la misma se crea con la siguiente informacion.
error = [{'elements': [{'status': 'ZERO_RESULTS'}]}]

# Conditions
# in order to make a route, the cities must be able to travel by car or any land vehicle
# a road from buenos aires and santiago is possible, but a route from buenos aires and Madrid is not.

class MotorDeRutas:


    def __init__(self):
        #un dict que almacena todos los trayectos que se van ingresando.
        self.trayectos = {}


    #Crea un nuevo trayecto con nombre y un camino, se almacena en la lista de trayectos
    def crear_trayecto(self, nombre_trayecto, origen, destino):

        ruta_uno = self.crear_camino(origen, destino)
        trayecto = []
        trayecto.append(ruta_uno)

        if (ruta_uno == None):
            pass
        else:
            if(self.trayectos.__contains__(nombre_trayecto)):
                print('Error: ya existe un trayecto con el nombre indicado')
            else:

                self.trayectos.update({nombre_trayecto: trayecto})
                print('Se ha creado con exito el nuevo trayecto.')
                self.mostrar_trayecto(nombre_trayecto)

    #Crear una nueva ruta con el origen y destino indicados
    def crear_camino(self, origen, destino):

        camino_uno = gmaps.distance_matrix(origen, destino)

        if (camino_uno["rows"] == error):
            print("Error: No se encontro una ruta con el origen y destino indicados.")
        else:

            origen = camino_uno['origin_addresses'][0]
            destino = camino_uno['destination_addresses'][0]
            distancia = camino_uno['rows'][0]['elements'][0]['distance']['value'] // 1000
            tiempo = camino_uno['rows'][0]['elements'][0]['duration']['value']
            camino_datos = {'origen': origen, 'destino': destino, 'distancia': distancia, 'tiempo': tiempo}
            return camino_datos


    # agrega una ciudad al final de  un trayecto ya existente
    def agregar_ciudad(self, nombre_trayecto, nueva_ciudad):
        try:

            buscado = self.trayectos[nombre_trayecto]

            ultimo_camino = buscado[len(buscado)-1]
            nuevo_origen = ultimo_camino['destino']

            nuevo_camino = self.crear_camino(nuevo_origen, nueva_ciudad)

            if(not nuevo_camino == None):

                self.trayectos[nombre_trayecto].append(nuevo_camino)
                print('Se ha agregado exitosamente la ciudad al trayecto solicitado.')
                self.mostrar_trayecto(nombre_trayecto)
        except KeyError:
            print('No se encontro el trayecto solicitado')


    # Agrega una ciudad intermedia antes de una ciudad existente en el trayecto.
    def agregar_ciudad_intermedia(self, nombre_trayecto, nombre_ciudad, nueva_ciudad):


        try:
            trayecto_buscado = self.trayectos[nombre_trayecto]
            camino_auxiliar = self.crear_camino(nueva_ciudad, nombre_ciudad)
            agrego = False

            for x in range(0, len(trayecto_buscado)):
                if trayecto_buscado[x]['destino'] == camino_auxiliar[
                        'destino'] and not agrego:
                    camino_auxiliar_2 = self.crear_camino(trayecto_buscado[x]['origen'], nueva_ciudad)

                    self.trayectos[nombre_trayecto].insert(x, camino_auxiliar_2)
                    self.trayectos[nombre_trayecto][x + 1] = camino_auxiliar

                    self.mostrar_trayecto(nombre_trayecto)
                    agrego = True
                    print('Se ha agregado exitosamente la ciudad al trayecto solicitado.')

            if(not agrego):
                print('No se ha encontrado la ciudad indicada en el trayecto.')

        except KeyError:
            print('Error: No se encontro el trayecto solicitado')


    #Concatena 2 trayectos si existe una ruta entre la ultima ciudad del
    #primer trayecto y la primera ciudad del segundo trayecto.
    def concatenar_trayectos(self, nombre_nuevo_trayecto, nombre_trayecto_1, nombre_trayecto_2):

        try:
            trayecto1 = self.trayectos[nombre_trayecto_1]
            trayecto2 = self.trayectos[nombre_trayecto_2]

            origen = trayecto1[len(trayecto1)-1]['destino']
            destino = trayecto2[0]['origen']
            nuevo_camino = self.crear_camino(origen, destino)
            lista_intermedia = [nuevo_camino]
            trayecto_nuevo = trayecto1 + lista_intermedia + trayecto2

            if (self.trayectos.__contains__(nombre_nuevo_trayecto)):
                print('Error: ya existe un trayecto con el nombre indicado')
            else:
                self.trayectos.update({nombre_nuevo_trayecto: trayecto_nuevo})
                self.mostrar_trayecto(nombre_nuevo_trayecto)
                print('Se ha creado correctamente el trayecto concatenado.')


        except KeyError:

            print('no se encontro el trayecto solicitado')


    #Compara 2 trayectos por distancia o por tiempo segun el parametro ingresado
    #Si se ingresa 'd' como parametro, compara por distancia. Si se ingresa 't' compara por tiempo.
    def comparar_trayectos(self,nombre_trayecto_uno, nombre_trayecto_dos, parametro):

        try:

            trayecto_1 = self.trayectos[nombre_trayecto_uno]
            trayecto_2 = self.trayectos[nombre_trayecto_dos]

            if parametro == 'd':

                if(self.obtener_distancia_trayecto(trayecto_1) > self.obtener_distancia_trayecto(trayecto_2)):
                    print(nombre_trayecto_uno + ' tiene mayor distancia que ' + nombre_trayecto_dos)
                elif(self.obtener_distancia_trayecto(trayecto_1) == self.obtener_distancia_trayecto(trayecto_2)):
                    print('ambos trayectos poseen la misma distancia')
                else:
                    print(nombre_trayecto_dos + ' tiene mayor distancia que ' + nombre_trayecto_uno)

                print('Distancia trayecto ' + nombre_trayecto_uno + ': '+ str(self.obtener_distancia_trayecto(trayecto_1)))
                print('Distancia trayecto ' + nombre_trayecto_dos + ': '+ str(self.obtener_distancia_trayecto(trayecto_2)))
            elif parametro == 't':
                tiempo_trayecto_1 = self.obtener_tiempo_trayecto(trayecto_1)
                tiempo_trayecto_2 = self.obtener_tiempo_trayecto(trayecto_2)

                if(tiempo_trayecto_1 > tiempo_trayecto_2):
                    print(nombre_trayecto_uno + ' tiene mayor tiempo de viaje que ' + nombre_trayecto_dos)
                elif(tiempo_trayecto_1 == tiempo_trayecto_2):
                    print('Ambos trayectos requieren la misma cantidad de tiempo para recorrerlos.')
                else:
                    print(nombre_trayecto_dos + ' tiene mayor tiempo de viaje que ' + nombre_trayecto_uno)


                print('Tiempo trayecto ' + nombre_trayecto_uno + ': '+ str(self.formatear_tiempo(tiempo_trayecto_1)))
                print('Tiempo trayecto ' + nombre_trayecto_dos + ': ' + str(self.formatear_tiempo(tiempo_trayecto_2)))
            else:
                print('ERROR: El parametro ingresado NO es valido')


        except KeyError:

            print('No se encontro el trayecto solicitado')



    #Devuelve la distancia(en metros) del trayecto.
    def obtener_distancia_trayecto(self,trayecto):
        distancia_total = 0

        for x in range(0, len(trayecto)):

            distancia_total = distancia_total + trayecto[x]['distancia']
        return distancia_total


    #Devuelve el tiempo(en segundos) que lleva recorrer un trayecto
    def obtener_tiempo_trayecto(self,trayecto):

        tiempo_total = 0
        for x in range(0, len(trayecto)):
            tiempo_total = tiempo_total + trayecto[x]['tiempo']

        return tiempo_total

    #devuelve un string con el tiempo en formato de horas, minutos y segundos
    def formatear_tiempo(self,tiempo_en_segundos):
        m, s = divmod(tiempo_en_segundos, 60)
        h, m = divmod(m, 60)
        tiempo_formateado = "%d:%02d:%02d" % (h, m, s)
        return tiempo_formateado


    #Muestra todos los trayectos que posee el motor de rutas.
    def mostrar_trayectos(self):
        for x in self.trayectos.keys():
            print(x)
            self.mostrar_trayecto(x)
            print("")


    #Muestra los datos del trayecto solicitado
    def mostrar_trayecto(self,nombre_trayecto):

        try:

            trayecto = self.trayectos[nombre_trayecto]
            nombre = nombre_trayecto
            ciudades = []
            distancia = self.obtener_distancia_trayecto(trayecto)
            tiempo = self.obtener_tiempo_trayecto(trayecto)
            tiempo_formateado = self.formatear_tiempo(tiempo)

            #agrega todas las ciudades a la lista
            for x in range(0, len(trayecto)):
                if x == 0:
                    ciudades.append(trayecto[x]['origen'])

                ciudades.append(trayecto[x]['destino'])

            print('Nombre del trayecto: ' + nombre)
            print("Ciudades: " + ' - '.join(ciudades))
            print('Distancia total: '+str(distancia) + "km")
            print('Tiempo estimado de viaje: '+ tiempo_formateado)
        except:
            print('ERROR: No se encontro el trayecto solicitado.')


    #Muestra los datos de las rutas que posee el trayecto
    def mostrar_rutas(self,nombre_trayecto):

        try:
            trayecto = self.trayectos[nombre_trayecto]

            for x in range(0, len(trayecto)):
                origen = trayecto[x]['origen']
                destino = trayecto[x]['destino']
                distancia = trayecto[x]['distancia']
                tiempo = trayecto[x]['tiempo']
                tiempo_formateado = self.formatear_tiempo(tiempo)

                print(origen+" - "+destino)
                print(str(distancia)+"km")
                print(tiempo_formateado)
                print("")
        except KeyError:
            print('ERROR: No existe el trayecto solicitado.')


    #guarda todos los trayectos del motor de rutas en un archivo JSON
    def almacenar_trayectos(self):

        json.dump(self.trayectos, open('trayectos.j', 'w'), ensure_ascii=False)


    #guarda el trayecto indicado en un archivo JSON
    def almacenar_trayecto(self, nombre_trayecto):

        try:
            trayecto = self.trayectos[nombre_trayecto]

            informacion_trayecto = {nombre_trayecto: trayecto}

            json.dump(informacion_trayecto, open('trayectos.j', 'w'), ensure_ascii=False)
            print('Se ha guardado con exito el trayecto solicitado.')
        except KeyError:
            print('ERROR: No se encontro el trayecto solicitado.')


    #Carga los trayectos del archivo JSON en el motor de rutas.
    def cargar_trayectos(self):
        trayectos_cargados = json.load(open('trayectos.j', 'r'))

        self.trayectos.update(trayectos_cargados)




instance = MotorDeRutas()

run = True
while run:
    print("""
        Choose an option:

            1. Add a route.
            2. Add a city into a existing route.
            3. Add a city in the middle of a route.
            4. Concatenate 2 routes.
            5. Campare routes.
            6. Show a route.
            7. Show the roads of a route.
            8. List calculated routes.
            9. Save a road.
            10. Import a route.
            11. Exit.
        """)
    ans = input("Seleccione una opcion: ")
    if ans == "1":
        print("\nAGREGAR UN TRAYECTO")

        print("Ingrese el nombre de su nuevo trayecto.")
        nombre = input()

        print("Ingrese el nombre de la ciudad de origen.")
        origen = input()

        print("Ingrese el nombre de la ciudad de destino.")
        destino = input()

        instance.crear_trayecto(nombre, origen, destino)

    elif ans == "2":
        print("\nAGREGAR CIUDAD A UN TRYECTO")

        print("Ingrese el nombre del trayecto a modificar.")
        nombre = input()

        print("Ingrese la ciudad que desea agregar a su trayecto.")
        destino = input()

        instance.agregar_ciudad(nombre, destino)

    elif ans == "3":
        print("\nAGREGAR CIUDAD INTERMEDIA A UN TRAYECTO")

        print("Ingrese el nombre del trayecto a modificar.")
        nombre = input()

        print('Ingrese una ciudad que pertenezca al trayecto (No debe ser la ciudad de origen del trayecto).')
        ciudad_trayecto = input()

        print('Ingrese una ciudad intermedia.')
        otra_ciudad_intermedia = input()

        instance.agregar_ciudad_intermedia(nombre, ciudad_trayecto, otra_ciudad_intermedia)

    elif ans == "4":
        print("\nCONCATENAR 2 TRAYECTOS")

        print('Ingrese nombre del trayecto concatenado')
        nombre = input()

        print('Ingrese nombre de trayecto a sumar.')
        tray1 = input()

        print('Ingrese nombre de trayecto a sumar.')
        tray2 = input()

        instance.concatenar_trayectos(nombre, tray1, tray2)

    elif ans == "5":

        print("""
            ¿Como desea comparar los trayectos:

                1. Comparar trayectos por distancia.
                2. Comparar trayectos pot tiempo.
            """)
        ans2 = input("Seleccione una opcion: ")

        if ans2 == "1":

            print("Ingrese el nombre del trayecto a comparar.")
            nombre = input()

            print('Ingrese el nombre del trayecto a comparar.')
            nombre2 = input()

            instance.comparar_trayectos(nombre,nombre2, 'd')

        elif ans2 == "2":
            print("Ingrese el nombre del trayecto a comparar.")
            nombre = input()

            print('Ingrese el nombre del trayecto a comparar.')
            nombre2 = input()

            instance.comparar_trayectos(nombre, nombre2, 't')

        elif ans != "":
            print("\nOpcion no valida: Elija un numero entre 1 y 2.")

    elif ans == "6":
        print('MOSTRAR UN TRAYECTO')

        print("Ingrese el nombre del trayecto a mostrar.")
        nombre = input()

        instance.mostrar_trayecto(nombre)

    elif ans == "7":
        print("\nMOSTRAR RUTAS")

        print("Ingrese el nombre del trayecto a mostrar.")
        nombre = input()

        instance.mostrar_rutas(nombre)

    elif ans == "8":
        print("\nLISTADO DE TRAYECTOS")

        instance.mostrar_trayectos()

    elif ans == "9":
        print("\nAlmacenar trayectos")

        print("Ingrese el nombre del trayecto a guardar. Si deja el campo vacio se almacenaran todos los trayectos.")

        nombre = input()
        print(nombre)

        if nombre == "":
            instance.almacenar_trayectos()
        else:
            instance.almacenar_trayecto(nombre)

    elif ans == "10":
        print("\nCARGAR TRAYECTOS DE ARCHIVO.")

        instance.cargar_trayectos()

    elif ans == "11":
        print("\nSALIR DEL SISTEMA.")

        instance.almacenar_trayectos()

        run = False

    elif ans != "":
        print("\nOpcion no valida: Ingrese un numero entre 1 y 11")

