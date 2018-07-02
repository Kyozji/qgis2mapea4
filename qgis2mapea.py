# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGIS2Mapea4
                                 A QGIS plugin
 Genera un visor usando la API de Mapea4
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2018-06-18
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Patricio Soriano :: SIGdeletras
        email                : pasoriano@sigdeletras.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
# from PyQt5.QtGui import QIcon
# from PyQt5.QtWidgets import QAction

from qgis.core import Qgis
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
# QT_VERSION=5
# os.environ['QT_API'] = 'pyqt5'

# Import the PyQt and QGIS libraries
from qgis.PyQt.QtCore import Qt
from qgis.core import *

# Initialize Qt resources from file resources.py
from .resources import *

from qgis.core import QgsProject #para captura listado de capas

# Import the code for the dialog
from .qgis2mapea_dialog import QGIS2Mapea4Dialog
import os.path

import unicodedata # para eliminar tildes

from .codehtml import *
from .codejs import *
from .listamuni_dict import *


listMunicipios = LISTMUNI
codmuni = ''

mapeaControlsList =[]
mapeaControls = str(mapeaControlsList)

baseMapsList = ['cdau','cdau_satelite','cdau_hibrido']
baseMapsControls = str(baseMapsList)

class QGIS2Mapea4:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.msgBar = iface.messageBar()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'QGIS2Mapea4_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = QGIS2Mapea4Dialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&QGIS to Mapea4')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'QGIS2Mapea4')
        self.toolbar.setObjectName(u'QGIS2Mapea4')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('QGIS2Mapea4', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToWebMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/qgis2mapea/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'QGIS to Mapea4'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.dlg.pushButton_select_path.clicked.connect(self.select_output_folder) #¿?
        self.dlg.pushButton_run.clicked.connect(self.createdFiles) #¿?


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr(u'&QGIS to Mapea4'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def select_output_folder(self):
        """Select output folder"""

        self.dlg.lineEdit_path.clear()
        folder = QFileDialog.getExistingDirectory(self.dlg , "Select folder")
        self.dlg.lineEdit_path.setText(folder)    

    def loadLayers(self):
        """Recupera capas cargados para desplegable"""
      
        lisLayers = QgsProject.instance().mapLayers().values()
        self.dlg.comboBox_layers.addItems([l.name() for l in lisLayers if l.type() == QgsMapLayer.VectorLayer]) # Solo capas vectoriales
        # and i.providerType == 'postgres' # subclases dentro los tipos vector

    def formatLayerName(self,layerName):
        """Formatea nombre de capa de espacios, tildes, eñes...
        Parámetro: layerName """

        s = unicodedata.normalize("NFKD", layerName).encode("ascii","ignore").decode("ascii")
        s2 = s.replace(' ', "_")
        return s2.lower()

    def layer2geojson(self,l,ruta):
        """Generar geojson de la capa cargada
        Parámetro: l y ruta 
        Si el check está marcado trabaja con selecionadas"""

        lgeojson = QgsProject.instance().mapLayersByName(l)
        #lgeojson = self.iface.activeLayer() ## sería capa activa
        crs25830 = QgsCoordinateReferenceSystem(25830, QgsCoordinateReferenceSystem.EpsgCrsId)

        if self.dlg.checkBox_selectedfeatures.isChecked():
            QgsVectorFileWriter.writeAsVectorFormat(lgeojson[0], ruta + '\\' + self.formatLayerName(l) + '.geojson', 'utf-8', crs25830 , 'GeoJSON', 1)
        else:
            QgsVectorFileWriter.writeAsVectorFormat(lgeojson[0], ruta + '\\' + self.formatLayerName(l) + '.geojson', 'utf-8', crs25830 , 'GeoJSON')

    def showList(self):
        """Genera lista de municipipios"""
        if self.dlg.checkBox_searchstreet.isChecked():
            self.dlg.comboBox_municipios.setEnabled(1)
            self.dlg.comboBox_municipios.addItems([k for k in listMunicipios.keys()])
        else:
            self.dlg.comboBox_municipios.setEnabled(0)

    def controlPanzoombar(self):
        if self.dlg.checkBox_panzoombar.isChecked():
            mapeaControlsList.append('panzoombar')
        else:  
            mapeaControlsList.remove('panzoombar')

        # self.msgBar.pushMessage(str(mapeaControlsList), level=Qgis.Info, duration=1)

    def controlMouse(self):
        if self.dlg.checkBox_mouse.isChecked():
            mapeaControlsList.append('mouse')
        else:  
            mapeaControlsList.remove('mouse')

        # self.msgBar.pushMessage(str(mapeaControlsList), level=Qgis.Info, duration=1)

    def controlLocation(self):

        if self.dlg.checkBox_location.isChecked():
            mapeaControlsList.append('location')
        else:  
            mapeaControlsList.remove('location')

        # self.msgBar.pushMessage(str(mapeaControlsList), level=Qgis.Info, duration=1)

    def controlScale(self):

        if self.dlg.checkBox_scale.isChecked():
            mapeaControlsList.append('scale')
        else:  
            mapeaControlsList.remove('scale')

        # self.msgBar.pushMessage(str(mapeaControlsList), level=Qgis.Info, duration=1)

    def controlScaleline(self):

        if self.dlg.checkBox_scaleline.isChecked():
            mapeaControlsList.append('Scaleline')
        else:  
            mapeaControlsList.remove('Scaleline')

        # self.msgBar.pushMessage(str(mapeaControlsList), level=Qgis.Info, duration=1)

    def controlLayerswitcher(self):

        if self.dlg.checkBox_layerswicher.isChecked():
            mapeaControlsList.append('layerswitcher')
        else:  
            mapeaControlsList.remove('layerswitcher')

        # self.msgBar.pushMessage(str(mapeaControlsList), level=Qgis.Info, duration=1)

    def mapBaseCDAU(self):

        if self.dlg.checkBox_cdau.isChecked():
            baseMapsList.append('cdau')
        else:  
            baseMapsList.remove('cdau')

        # self.msgBar.pushMessage(str(mapeaControlsList), level=Qgis.Info, duration=1)

    def mapBaseOrtho(self):

        if self.dlg.checkBox_ortho.isChecked():
            baseMapsList.append('cdau_satelite')
        else:  
            baseMapsList.remove('cdau_satelite')

        # self.msgBar.pushMessage(str(mapeaControlsList), level=Qgis.Info, duration=1)

    def mapBaseHybrid(self):

        if self.dlg.checkBox_hybrid.isChecked():
            baseMapsList.append('cdau_hibrido')
        else:  
            baseMapsList.remove('cdau_hibrido')

        # self.msgBar.pushMessage(str(mapeaControlsList), level=Qgis.Info, duration=1)


    def layerGeometryStyle(self,l):
        """Obtiene el tipo de geometría y devuelve variable de estilo"""

        layer = QgsProject.instance().mapLayersByName(l)

        if layer[0].geometryType() == QgsWkbTypes.PointGeometry:
           codStyleLayer = pointSyle
        elif layer[0].geometryType() == QgsWkbTypes.LineGeometry:
            codStyleLayer = lineStyle 
        elif layer[0].geometryType() == QgsWkbTypes.PolygonGeometry:
            codStyleLayer = polygonStyle 
        else:
            self.msgBar.pushMessage(u'Tipo de geometría incorrecta' , level=Qgis.Warning, duration=3)

        return codStyleLayer

    def layerExtend(self,l):
        """Obtiene el tipo de geometría y devuelve extensión bbox"""

        layer = QgsProject.instance().mapLayersByName(l)
        if self.dlg.checkBox_selectedfeatures.isChecked():
            ext = layer[0].boundingBoxOfSelected()
        else:
            ext = layer[0].extent()
        
        xmin = ext.xMinimum()
        xmax = ext.xMaximum()
        ymin = ext.yMinimum()
        ymax = ext.yMaximum()
        coords = "%f,%f,%f,%f" %(xmin, ymin,xmax,ymax)

        return coords
    
    def getColor(self, l):
        """Color de relleno"""

        layer = QgsProject.instance().mapLayersByName(l)
        renderer = layer[0].renderer()
        symbol = renderer.symbol()
        colorName = symbol.color().name()
        #borderColorName = symbol.color_border()
        # return symbol.properties() 
        return colorName

    def getINECod(self):
        """Obtiene cdo INE"""

        municipio = self.dlg.comboBox_municipios.currentText()
        codINE = listMunicipios[municipio]
        
        return codINE

    def createdFiles(self):
        """CreatedFiles data funtion"""
        
        layer = self.dlg.comboBox_layers.currentText()


        if self.dlg.lineEdit_path.text() == '' or layer == '': #revisa si no se ha seleccionado capa o ruta
            self.msgBar.pushMessage('Debe indicar una ruta donde crear los ficheros' , level=Qgis.Info, duration=3)
        else:
            projectpath = self.dlg.lineEdit_path.text()
            #self.msgBar.pushMessage(self.getColor(layer), level=Qgis.Info, duration=3)
            try:
                
                # Crea directorio
                wd = os.path.join(projectpath, 'qgis2mapea4_'+ self.formatLayerName(layer))

                if os.path.exists(wd) == False: #si el directorio ya existe avisa
                    os.makedirs(wd)

                    if layer:

                        appPath = os.path.join(wd, self.formatLayerName(layer))
                        htmlPathFile = os.path.join(wd,'index.html')
                        jsPathFile = os.path.join(wd,'qgis2mapea.js')
                       
                        # genera código HTML
                        with open(htmlPathFile, "w", encoding='utf-8') as htmlFile:
                            htmlFile.write(indexCode1)
                            htmlFile.write(self.dlg.lineEdit_title.text()) ## Inserta título del visor
                            # htmlFile.write(str(title, 'utf-8')) ## Inserta título del visor
                            htmlFile.write(indexCode2)                 
                            #htmlFile.write("\""+self.formatLayerName(layer)+".geojson\"") ## Inserta geojson para descarga
                            htmlFile.write(indexCode3)
                            htmlFile.write("\""+self.formatLayerName(layer)+".js\"") ## Inserta geojs
                            htmlFile.write(indexCode4)

                        htmlFile.close

                        # Genera código js de Geojson
                        jsGeojson = open(appPath +".js" , "w", encoding='utf-8')
                        jsGeojson.write('var geo = ')

                        self.layer2geojson(layer,wd)

                        # Copia geojson a js
                        geodataFile = open(appPath + '.geojson', "r", encoding='utf-8')

                        for line in geodataFile:
                            jsGeojson.write(line)
                        
                        geodataFile.close()
                        jsGeojson.close 

                        # Genera js con la API de Mapea
                        #unicode_title = self.dlg.lineEdit_title.text().decode('utf8')
                        unicode_title = self.dlg.lineEdit_title.text()
                        with open(jsPathFile, "w", encoding='utf-8') as jsFile:
                            # Generación de variables

                            jsFile.write("var layerName = \'%s\'\n" %(unicode_title))
                            jsFile.write("var fillColor = \'%s\'\n" %(self.getColor(layer)))
                            jsFile.write("var strokeColor = \'blue\'\n")
                            jsFile.write("var bb = [%s]\n" %(self.layerExtend(layer)))
                            jsFile.write("var basemaps = %s\n\n" %(str(baseMapsList)))

                            # Generación de variables
                            jsFile.write(codejs1)
                            jsFile.write(str(mapeaControlsList))
                            jsFile.write(codejs2)
                            if self.dlg.checkBox_searchstreet.isChecked():
                                jsFile.write("\nmapajs.addPlugin(new M.plugin.Searchstreet({\"locality\": \"%s\"}));\n" %(self.getINECod()))
                            jsFile.write(self.layerGeometryStyle(layer))
                            jsFile.write(codejs3)

                        jsFile.close                
                        

                        self.msgBar.pushMessage('<b>Ficheros creados correctamente</b>', level=Qgis.Success, duration=10)

                    else:
                        self.msgBar.pushMessage('No se ha seleccionado ninguna capa' , level=Qgis.Warning, duration=3)
                else:
                    self.msgBar.pushMessage('Ya existe ese directorio. Bórrelo antes o indique otro diferente' , level=Qgis.Warning, duration=3)

                
            except OSError:
                pass
            

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.lineEdit_title.setText('ej. Equipamientos municipales')

        self.dlg.lineEdit_path.clear()

        self.dlg.comboBox_layers.clear()

        self.dlg.checkBox_searchstreet.setChecked(0)
        self.dlg.checkBox_searchstreet.stateChanged.connect(self.showList)

        self.dlg.checkBox_panzoombar.setChecked(0)
        self.dlg.checkBox_panzoombar.stateChanged.connect(self.controlPanzoombar)

        self.dlg.checkBox_scale.setChecked(0)
        self.dlg.checkBox_scale.stateChanged.connect(self.controlScale)

        self.dlg.checkBox_location.setChecked(0)
        self.dlg.checkBox_location.stateChanged.connect(self.controlLocation)

        self.dlg.checkBox_scaleline.setChecked(0)
        self.dlg.checkBox_scaleline.stateChanged.connect(self.controlScaleline)

        self.dlg.checkBox_mouse.setChecked(0)
        self.dlg.checkBox_mouse.stateChanged.connect(self.controlMouse)

        self.dlg.checkBox_layerswicher.setChecked(0)
        self.dlg.checkBox_layerswicher.stateChanged.connect(self.controlLayerswitcher)

        self.dlg.checkBox_cdau.setChecked(1)
        self.dlg.checkBox_cdau.stateChanged.connect(self.mapBaseCDAU)

        self.dlg.checkBox_ortho.setChecked(1)
        self.dlg.checkBox_ortho.stateChanged.connect(self.mapBaseOrtho)

        self.dlg.checkBox_hybrid.setChecked(1)
        self.dlg.checkBox_hybrid.stateChanged.connect(self.mapBaseHybrid)

        self.dlg.comboBox_municipios.clear()
        self.dlg.comboBox_municipios.setEnabled(0)

        self.dlg.setWindowIcon(QIcon (':/plugins/qgis2mapea/icon.png')); 
        self.dlg.show()

        self.loadLayers()

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass