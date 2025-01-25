import sys
import cv2
import numpy as np
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QLabel, QPushButton, QDialog, QLineEdit, QFileDialog, QTextEdit, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, QTimer, QPoint, QSize, QRect  # Asegúrate de importar QSize
from PyQt5.QtGui import QPixmap, QPainter, QRegion, QIcon, QImage


class CirculoLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap = None

    def setPixmap(self, pixmap):
        self.pixmap = pixmap
        self.update()

    def paintEvent(self, event):
        if self.pixmap:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setClipRegion(QRegion(self.rect(), QRegion.Ellipse))  # Recorte circular
            painter.drawPixmap(self.rect(), self.pixmap)
            painter.end()


class PlataformaVideojuegos(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Plataforma de Videojuegos")
        self.setGeometry(100, 100, 1200, 800)

        # Barra lateral
        self.setStyleSheet(""" 
            QMainWindow {
                background-color: #1c1c1c;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 18px;
            }
            QPushButton {
                background-color: #2c2c2c;
                color: white;
                padding: 10px;
                border-radius: 10px;
                font-size: 14px;
                border: none;
                transition: background-color 0.3s;
            }
            QPushButton:hover {
                background-color: #444;
            }
            QPushButton:pressed {
                background-color: #666;
            }
            QStackedWidget {
                border: none;
            }
            QLineEdit {
                padding: 8px;
                border-radius: 5px;
                border: 1px solid #444;
                background-color: #333;
                color: white;
            }
            QVBoxLayout {
                spacing: 10px;
            }
            QListWidget {
                background-color: #2c2c2c;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background-color: #ff5864;
            }
            QTextEdit {
                background-color: #333;
                color: white;
                font-size: 14px;
                border-radius: 5px;
                padding: 10px;
            }
        """)

        # Widget central
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Layout principal
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Barra lateral
        self.sidebar = QWidget(self)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar.setFixedWidth(200)
        
        self.btn_inicio = QPushButton(QIcon("home_icon.png"), "Inicio", self)
        self.sidebar_layout.addWidget(self.btn_inicio)
        self.btn_inicio.clicked.connect(self.show_inicio)

        self.btn_perfil = QPushButton(QIcon("profile_icon.png"), "Perfil", self)
        self.sidebar_layout.addWidget(self.btn_perfil)
        self.btn_perfil.clicked.connect(self.show_perfil)

        self.btn_juegos = QPushButton(QIcon("game_icon.png"), "Juegos", self)
        self.sidebar_layout.addWidget(self.btn_juegos)
        self.btn_juegos.clicked.connect(self.show_juegos)

        self.btn_streams = QPushButton(QIcon("stream_icon.png"), "Streams", self)
        self.sidebar_layout.addWidget(self.btn_streams)
        self.btn_streams.clicked.connect(self.show_streams)

        self.btn_publicaciones = QPushButton(QIcon("post_icon.png"), "Publicaciones", self)
        self.sidebar_layout.addWidget(self.btn_publicaciones)
        self.btn_publicaciones.clicked.connect(self.show_publicaciones)

        # Layout de contenido
        self.content_stack = QStackedWidget(self)
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_stack)

        # Pantallas de contenido
        self.pantalla_inicio = QWidget()
        self.pantalla_inicio_layout = QVBoxLayout(self.pantalla_inicio)

        # Pantalla de bienvenida mejorada
        bienvenida_text = QLabel("¡Bienvenido a la Plataforma de Videojuegos!\nConéctate, juega y transmite en vivo", self)
        bienvenida_text.setAlignment(Qt.AlignCenter)
        bienvenida_text.setStyleSheet("color: #ffffff; font-size: 24px; font-weight: bold; padding: 20px; background-color: #ff5864; border-radius: 10px;")
        self.pantalla_inicio_layout.addWidget(bienvenida_text)

        self.pantalla_perfil = QWidget()
        self.pantalla_perfil_layout = QVBoxLayout(self.pantalla_perfil)

        # Foto de perfil circular
        self.foto_perfil = CirculoLabel(self)
        self.foto_perfil.setPixmap(QPixmap("default_profile_pic.jpg").scaled(100, 100, Qt.KeepAspectRatio))
        self.pantalla_perfil_layout.addWidget(self.foto_perfil)

        # Campo de frase de perfil
        self.frase_perfil = QLineEdit(self)
        self.frase_perfil.setPlaceholderText("Escribe una frase sobre ti")
        self.pantalla_perfil_layout.addWidget(self.frase_perfil)

        # Agregar botón para cambiar la foto de perfil
        self.btn_cambiar_foto = QPushButton("Cambiar Foto", self)
        self.btn_cambiar_foto.clicked.connect(self.cambiar_foto)
        self.pantalla_perfil_layout.addWidget(self.btn_cambiar_foto)

        # Mostrar la frase de perfil
        self.label_frase = QLabel("", self)
        self.pantalla_perfil_layout.addWidget(self.label_frase)

        # Mostrar la frase cuando se escriba
        self.frase_perfil.textChanged.connect(self.actualizar_frase)

        # Pantalla de juegos
        self.pantalla_juegos = QWidget()
        self.pantalla_juegos_layout = QVBoxLayout(self.pantalla_juegos)
        self.pantalla_juegos_layout.addWidget(QLabel("Lista de Juegos", self))

        # Lista de juegos
        self.lista_juegos = QListWidget(self)
        self.lista_juegos.setStyleSheet("background-color: #333; color: white;")
        self.lista_juegos.addItem("Juego 1 - Aventura")
        self.lista_juegos.addItem("Juego 2 - Estrategia")
        self.lista_juegos.addItem("Juego 3 - Carreras")
        self.lista_juegos.addItem("Juego 4 - Deportes")
        self.lista_juegos.addItem("Juego 5 - Puzzle")
        self.lista_juegos.addItem("Tetris - Bloque Puzzle")  # Agregar Tetris a la lista
        self.lista_juegos.itemClicked.connect(self.iniciar_juego)
        self.pantalla_juegos_layout.addWidget(self.lista_juegos)

        # Pantalla de streams (con chat en vivo)
        self.pantalla_streams = QWidget()
        self.pantalla_streams_layout = QVBoxLayout(self.pantalla_streams)

        # Área de video (más pequeña)
        self.video_frame = QLabel(self)
        self.video_frame.setFixedSize(480, 360)  # Tamaño reducido
        self.video_frame.setStyleSheet("border: 2px solid white; background-color: black;")  # Estilo visual
        self.pantalla_streams_layout.addWidget(self.video_frame)

        # Chat en vivo (más grande)
        self.chat_area = QTextEdit(self)
        self.chat_area.setReadOnly(True)  # Solo lectura
        self.chat_area.setStyleSheet("background-color: #333; color: white; font-size: 14px;")
        self.pantalla_streams_layout.addWidget(self.chat_area)

        # Campo para escribir mensaje en el chat
        self.input_chat = QLineEdit(self)
        self.input_chat.setPlaceholderText("Escribe un mensaje...")
        self.pantalla_streams_layout.addWidget(self.input_chat)

        # Botón para enviar mensaje en el chat
        self.btn_enviar_chat = QPushButton("Enviar", self)  # Restaurado el botón de "Enviar"
        self.btn_enviar_chat.clicked.connect(self.enviar_mensaje_chat)
        self.pantalla_streams_layout.addWidget(self.btn_enviar_chat)

        # Botón para iniciar transmisión
        self.btn_iniciar_transmision = QPushButton("Iniciar Transmisión", self)
        self.btn_iniciar_transmision.clicked.connect(self.iniciar_transmision)
        self.pantalla_streams_layout.addWidget(self.btn_iniciar_transmision)

        # Botón para detener transmisión (discreto y pequeño)
        self.btn_detener_transmision = QPushButton("Detener", self)
        self.btn_detener_transmision.setStyleSheet("background-color: #ff5864; color: white; font-size: 12px; padding: 5px; border-radius: 8px;")
        self.btn_detener_transmision.clicked.connect(self.detener_transmision)
        self.pantalla_streams_layout.addWidget(self.btn_detener_transmision)

        # Agregar las pantallas al stack
        self.content_stack.addWidget(self.pantalla_inicio)
        self.content_stack.addWidget(self.pantalla_perfil)
        self.content_stack.addWidget(self.pantalla_juegos)
        self.content_stack.addWidget(self.pantalla_streams)
        # No agregamos la pantalla de publicaciones por ahora.

        self.content_stack.setCurrentWidget(self.pantalla_inicio)

        # Variables para la cámara
        self.capture = None
        self.timer = QTimer(self)

    def actualizar_frase(self):
        frase = self.frase_perfil.text()
        self.label_frase.setText(frase)

    def show_inicio(self):
        self.content_stack.setCurrentWidget(self.pantalla_inicio)

    def show_perfil(self):
        self.content_stack.setCurrentWidget(self.pantalla_perfil)

    def show_juegos(self):
        self.content_stack.setCurrentWidget(self.pantalla_juegos)

    def show_streams(self):
        self.content_stack.setCurrentWidget(self.pantalla_streams)

    def show_publicaciones(self):
        # Esta función no hace nada por ahora, ya que no tenemos una pantalla de publicaciones.
        pass

    def cambiar_foto(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Imagenes (*.png *.jpg *.bmp)")
        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            pixmap = QPixmap(selected_file)
            pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)  
            self.foto_perfil.setPixmap(pixmap)

    def enviar_mensaje_chat(self):
        mensaje = self.input_chat.text()
        if mensaje:
            self.chat_area.append(f"Usuario: {mensaje}")
            self.input_chat.clear()  # Limpiar el campo de entrada de texto

    def iniciar_transmision(self):
        # Simula la inicialización de la cámara y muestra el video
        self.capture = cv2.VideoCapture(0)  # Usa la cámara predeterminada
        self.timer.timeout.connect(self.mostrar_video)
        self.timer.start(30)  # Actualiza cada 30ms

    def mostrar_video(self):
        if self.capture:
            ret, frame = self.capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, _ = frame.shape
                frame = QImage(frame.data, width, height, 3 * width, QImage.Format_RGB888)

                # Actualizar el QLabel con el video
                pixmap = QPixmap.fromImage(frame)
                self.video_frame.setPixmap(pixmap.scaled(self.video_frame.width(), self.video_frame.height(), Qt.KeepAspectRatio))

    def iniciar_juego(self):
        item = self.lista_juegos.currentItem()
        if item:
            juego = item.text()
            print(f"Iniciando {juego}")

            # Comprobar si el juego seleccionado es Tetris
            if juego == "Tetris - Bloque Puzzle":
                self.abrir_tetris()
            else:
                # Aquí agregaríamos la lógica para abrir o iniciar el juego correspondiente
                print("Iniciar otro juego")
    
    def abrir_tetris(self):
        try:
            # Ruta del ejecutable de Tetris (ajusta la ruta según la ubicación de tu archivo)
            tetris_path = "./BLOQUE PUZZLE TETRIS - LADRILLO CLÁSICO Installer.exe"  # Cambiar la ruta si es diferente
            subprocess.Popen(tetris_path)  # Ejecutar el archivo

            print("Tetris se ha iniciado")
        except Exception as e:
            print(f"Error al iniciar Tetris: {e}")

    def detener_transmision(self):
        if self.capture:
            self.capture.release()
            self.capture = None
            self.timer.stop()
            print("Transmisión detenida")


# Inicialización de la aplicación
app = QApplication(sys.argv)
window = PlataformaVideojuegos()
window.show()
sys.exit(app.exec_())
