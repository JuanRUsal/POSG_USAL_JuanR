
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QMessageBox
from PyQt5.uic import loadUi

# Se importan mas librerías ###############################
import os
from PyQt5.QtGui import *
import re
import csv
import simplekml
from exif import Image

###############################################################
class JR_POS(QDialog):

    # Constructor al que pones el nombre de la ui creada con el QtDesigner
    def __init__(self):
        super(JR_POS, self).__init__()
        loadUi("JR_POS.ui", self)


        # Se empieza a introducir el código. ###################

        # Se declaran algunas variables 
        self.img_list = []
        self.imp_path = ""
        self.exp_path = ""

      
        # Se hacen no visibles los botones que crashearían la aplicación sin datos
        self.btn_view_imgs.setEnabled(False)
        self.btn_next_img.setEnabled(False)
        self.btn_prev_img.setEnabled(False)
        self.btn_export.setEnabled(False)
        self.btn_generate.setEnabled(False)

      
        # Se conecta los botones con sus funciones #################

        # Boton para importar las fotos
        self.btn_import.clicked.connect(self.get_import_path)

        # Botón para seleccionar la carpeta de resultados
        self.btn_export.clicked.connect(self.get_export_path)

        # Se asigna la función de cerrar al boton exit
        self.btn_exit.clicked.connect(QtCore.QCoreApplication.instance().quit)

        # Se le asigna la función de cargar las imágenes al boton mopstrar imágenes
        # uso lambda para que la función no se ejecute sola.
        self.btn_view_imgs.clicked.connect(lambda x:self.load_imgs(self.imp_path))

        # Se le asigna la funcion de mostrar la siguiente imagen o a la anterior a 
        # los botones correspondientes 
        self.btn_next_img.clicked.connect(self.next_img)
        self.btn_prev_img.clicked.connect(self.prev_img)

        # Se le asigna la funcion al boton generar kml y csv
        self.btn_generate.clicked.connect(
            lambda x:self.generate_kml(self.imp_path, self.exp_path)
            )

        

    # Se definen las funciones #####################

    # Función para seleccionar la carpeta de importación de las fotografías
    def get_import_path(self):

     self.imp_path = QFileDialog.getExistingDirectory(
            parent=self,
            caption="Seleccionar la carpeta que contiene las fotografías"
            )

     # Se muestra la dirección de la carpeta seleccionada en el line edit.
     self.le_import.setText(self.imp_path)

     #Se activa el boton de cargar imagenes y de exportar
     self.btn_view_imgs.setEnabled(True)
     self.btn_export.setEnabled(True)

    # Función para seleccionar la carpeta de exportación de resultados
    def get_export_path(self):
       
        self.exp_path = QFileDialog.getExistingDirectory(
                parent=self,
                caption="Seleccionar la carpeta de exportación para el KML y el CSV"
                )

        # Se muestra la dirección de la carpeta seleccionada en el line edit.
        self.le_export.setText(self.exp_path)

        # Se activa el boton de genear kml y csv
        self.btn_generate.setEnabled(True)

    # Funcion que muestra las imágenes en un visor.
    # Recibe como parámetro el path guardado en el line edit de importación   
    def load_imgs(self, imp_path):
       
       # Se vacía la lista y se resetea la posición
        self.img_list.clear()
        self.pos = 0 

        # Se crea lista con las direcciones de los archivos enla dirección guardada en imp_path
        folder = os.listdir(imp_path)

        #Se comprueba que hay elementos en la lista
        if len(folder) == 0:
            QMessageBox.about(self, "Error", "La carpeta está vacía.")
            return
        else:
            # Se recorre cada archivo de la lista y se le añade el nombre al path
            for file in folder:
                if (file.lower().endswith(('.jpg', '.jpeg'))):
                    self.img_list.append(f"{imp_path}/{file}")
                else: 
                    QMessageBox.about(self, "Error", "La carpeta no continene fotos")
                    return
                 
        #funciones para las que hay que incluir la libreria from PyQt5.QtGui import *
        # Se muestra en esta etiqueta la imagen conrrespondiente a la primera posicion
        # de la lista de imagenes
        self.lb_img_view_2.setPixmap(QPixmap(f"{self.img_list[self.pos]}"))
        #Se muestra en esta etiqueta el nombre de la imagen conrrespondiente a la primera posicion
        # de la lista de imagenes
        self.lb_img_name_2.setText(self.img_list[self.pos])

           # Se hace coincidir el tamaño de la imagen con el de la etiqueta
        self.lb_img_view_2.setScaledContents(True)
        
        #Se hacen no visibles los botones para navegar por las imágenes
        self.btn_next_img.setEnabled(True)
        self.btn_prev_img.setEnabled(True)

    # Funciones pde los botones para navegar ente imagenes
    def next_img(self):

        self.pos +=1
     
        self.lb_img_view_2.setPixmap(QPixmap(f"{self.img_list[self.pos]}"))
        self.lb_img_name_2.setText(self.img_list[self.pos])

      # Funciones de mostrar la imagen anterior
    def prev_img(self):

        self.pos -=1

        self.lb_img_view_2.setPixmap(QPixmap(f"{self.img_list[self.pos]}"))
        self.lb_img_name_2.setText(self.img_list[self.pos])


    # Función para generar el kml y el csv y guardarlo en la carpeta de exportación
    def generate_kml(self, imp_path, exp_path):

        # Se vacía la lista y se resetea la posición
        self.img_list.clear()

        # Se crea lista con las direcciones de los archivos en la dirección guardada en imp_path
        folder = os.listdir(imp_path) 

        #Se comprueba que hay elementos en la lista
        if len(folder) == 0:
            QMessageBox.about(self, "Error", "La carpeta está vacía.")
            return
        else:

            # Método para crear archivo csv con este nombre, para editar (w) y crear una nueva linea (newline)
            csv_f = open(f"{exp_path}/CSV_file.csv", "w", newline='')
            writer = csv.writer(csv_f)

            # Se crean dos variables para poder contabilizar los archivos creados
            imgs_ok = 0
            imgs_not_ok = 0

            # Se recorren los archivos de la lista buscando estos formatos
            for file in folder:
                if (file.lower().endswith(('.jpg', '.jpeg'))):
                    
                    #Si tiene este formato, se intenta extraer los metadatos
                    try:
                        with open(f"{imp_path}/{file}", 'rb') as img_file:
                            img = Image(img_file)
                  
                            # Se almacena en row los siguientes metadatos 
                            row = [
                                img.image_description,
                                img.gps_longitude,
                                img.gps_longitude_ref,
                                img.gps_latitude,
                                img.gps_latitude_ref,
                                img.gps_altitude,
                                img.make,
                                img.model,
                                img.datetime
                                ]

                            # Se escribe en una linea toda la informacion anterior
                            writer.writerow(row)
                            imgs_ok += 1

                            # Se guarda en img_list la ruta relativa a la imagen que estamos guardando
                            self.img_list.append(f"/{file}")

                    #Si hay algún error aumentamos el numero de errores
                    except AttributeError:
                        imgs_not_ok += 1                    

                else: 
                    QMessageBox.about(self, "Error", "La carpeta no continene fotos")
                    return

            csv_f.close()

        # El csv es abierto para leer (r), para poder crear el kml
        csv_data = csv.reader(open(f"{exp_path}/CSV_file.csv", 'r'))

        #intancia para crear el kml
        kml = simplekml.Kml()

        # funcion para identificar las comas dentro de un float
        p = re.compile(r'\d+\.\d+')  

        # recorre cada linea del csv
        for row in csv_data:

            # Recorre cada elemento (grados, min y seg) de las posiciones 4 y 6 
            longit = [float(i) for i in p.findall(row[1])]
            latit = [float(i) for i in p.findall(row[3])]

            # Llamada a la función de conversion de sexagesimal a decimal 
            dd_long = self.DMS_to_DD_coords(longit, row[2])
            dd_lat = self.DMS_to_DD_coords(latit, row[4])

            '''Se crea cada punto kml con el nombre correspondiente al primer 
            valor de los metadatos y coordenada con lo que ha devuelto el conversor'''
            kml.newpoint(name=row[0], coords=[(dd_long, dd_lat)])

        # Guardamos el kml en el path de exportación y con este nombre
        kml.save(f'{exp_path}/KML_file.kml')

        # Si hay alguna imagen correctamente procesada se muestra la siguiente ventana
        if imgs_ok > 0:
            img_msg = " Imágenes procesadas.\n"
            img_notok_msg = " Imágenes no procesadas.\n"
            csv_kml_ok = "CSV y KML generados.\n"

            QMessageBox.about(self,"Información de resultados", f"{imgs_ok}{img_msg}{csv_kml_ok}\n{imgs_not_ok}{img_notok_msg}")
            
        else:
            csv_kml_ok = "CSV y KML no generados."
            QMessageBox.about(self,
                "Información de resultados",
                 f"{imgs_ok}{img_msg}{csv_kml_ok}\n{imgs_not_ok}{img_notok_msg}")

    '''Función de conversion de sexagesimal a decimal recibiendo los parametros 
    de longitud y latitud y lo_ref y lat_ref'''
    def DMS_to_DD_coords(self, coords, ref):
      

        decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600

        if ref == "S" or ref == "W":
            decimal_degrees = -decimal_degrees

        return decimal_degrees

#################################################################
app = QApplication(sys.argv)

# instancia a la clase principal que hemos creado
mw = JR_POS()

widget = QtWidgets.QStackedWidget()
widget.addWidget(mw)

# Título del programa en la ui
widget.setWindowTitle("JR_POS")

#redimensionar la ventana por defecto
widget.resize(780, 650)

widget.show()

app.exec()