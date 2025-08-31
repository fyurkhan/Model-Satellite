import sys
import random
import os
import cv2
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui, QtWebEngineWidgets
from Başlangıç_Kod import Ui_MainWindow  # Qt Designer’dan çevirdiğin arayüz dosyan

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# --- Grafik widget sınıfı (sıcaklık, basınç, yükseklik ve iniş hızı için) ---
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(4, 3), dpi=100)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)
        fig.tight_layout()


class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # --- Eksen verilerini göstermek için label ---
        self.pitch_label = QtWidgets.QLabel(self.ui.widget_Pitch)
        self.roll_label = QtWidgets.QLabel(self.ui.widget_Roll)
        self.yaw_label = QtWidgets.QLabel(self.ui.widget_Yaw)
        self.altitude_label = QtWidgets.QLabel(self.ui.widget_Altitude)
        self.longitude_label = QtWidgets.QLabel(self.ui.widget_Longitude)

        font = QtGui.QFont()
        font.setPointSize(18)  # Yazı boyutunu büyütme

        self.pitch_label.setFont(font)
        self.roll_label.setFont(font)
        self.yaw_label.setFont(font)
        self.altitude_label.setFont(font)
        self.longitude_label.setFont(font)

        # Sola yaslama ve biraz yukarı kaydırma için hizalama
        self.pitch_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.roll_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.yaw_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.altitude_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.longitude_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.pitch_label.setMinimumSize(300, 100)
        self.roll_label.setMinimumSize(300, 100)
        self.yaw_label.setMinimumSize(300, 100)
        self.altitude_label.setMinimumSize(300, 100)
        self.longitude_label.setMinimumSize(300, 100)

        # Layout'ları oluştur
        layout_pitch = QtWidgets.QVBoxLayout(self.ui.widget_Pitch)
        layout_pitch.setContentsMargins(0, 0, 0, 0)
        layout_pitch.addWidget(self.pitch_label)

        layout_roll = QtWidgets.QVBoxLayout(self.ui.widget_Roll)
        layout_roll.setContentsMargins(0, 0, 0, 0)
        layout_roll.addWidget(self.roll_label)

        layout_yaw = QtWidgets.QVBoxLayout(self.ui.widget_Yaw)
        layout_yaw.setContentsMargins(0, 0, 0, 0)
        layout_yaw.addWidget(self.yaw_label)

        layout_altitude = QtWidgets.QVBoxLayout(self.ui.widget_Altitude)
        layout_altitude.setContentsMargins(0, 0, 0, 0)
        layout_altitude.addWidget(self.altitude_label)

        layout_longitude = QtWidgets.QVBoxLayout(self.ui.widget_Longitude)
        layout_longitude.setContentsMargins(0, 0, 0, 0)
        layout_longitude.addWidget(self.longitude_label)

        # --- Sıcaklık grafik setup ---
        self.sicaklik_canvas = MplCanvas(self.ui.widget_Sicaklik)
        layout_sicaklik = QtWidgets.QVBoxLayout(self.ui.widget_Sicaklik)
        layout_sicaklik.setContentsMargins(0, 0, 0, 0)
        layout_sicaklik.addWidget(self.sicaklik_canvas)

        self.sicaklik_xdata = []
        self.sicaklik_ydata = []

        # --- Basınç grafik setup ---
        self.basinç_canvas = MplCanvas(self.ui.widget_Basinc)
        layout_basinç = QtWidgets.QVBoxLayout(self.ui.widget_Basinc)
        layout_basinç.setContentsMargins(0, 0, 0, 0)
        layout_basinç.addWidget(self.basinç_canvas)

        self.basinç_xdata = []
        self.basinç_ydata = []

        # --- Yükseklik grafik setup ---
        self.yukseklik_canvas = MplCanvas(self.ui.widget_Yukseklik)
        layout_yukseklik = QtWidgets.QVBoxLayout(self.ui.widget_Yukseklik)
        layout_yukseklik.setContentsMargins(0, 0, 0, 0)
        layout_yukseklik.addWidget(self.yukseklik_canvas)

        self.yukseklik_xdata = []
        self.yukseklik_ydata = []

        # --- İniş Hızı grafik setup ---
        self.hiz_canvas = MplCanvas(self.ui.widget_Hiz)
        layout_hiz = QtWidgets.QVBoxLayout(self.ui.widget_Hiz)
        layout_hiz.setContentsMargins(0, 0, 0, 0)
        layout_hiz.addWidget(self.hiz_canvas)

        self.hiz_xdata = []
        self.hiz_ydata = []

        # --- Pil Gerilimi grafik setup ---
        self.pil_canvas = MplCanvas(self.ui.widget_pil)
        layout_pil = QtWidgets.QVBoxLayout(self.ui.widget_pil)
        layout_pil.setContentsMargins(0, 0, 0, 0)
        layout_pil.addWidget(self.pil_canvas)

        self.pil_xdata = []
        self.pil_ydata = []

        # --- Kamera setup ---
        self.cap = cv2.VideoCapture(0)
        self.camera_timer = QtCore.QTimer()
        self.camera_timer.timeout.connect(self.update_camera)
        self.camera_timer.start(30)

        self.camera_label = QtWidgets.QLabel(self.ui.widget_camera)
        self.camera_label.setAlignment(QtCore.Qt.AlignCenter)
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setScaledContents(True)

        layout_camera = QtWidgets.QVBoxLayout(self.ui.widget_camera)
        layout_camera.setContentsMargins(0, 0, 0, 0)
        layout_camera.addWidget(self.camera_label)

        # --- Harita setup ---
        self.webview = QtWebEngineWidgets.QWebEngineView(self.ui.widget_harita)
        layout_harita = QtWidgets.QVBoxLayout(self.ui.widget_harita)
        layout_harita.setContentsMargins(0, 0, 0, 0)
        layout_harita.addWidget(self.webview)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        harita_path = os.path.join(current_dir, "harita.html")
        self.webview.load(QtCore.QUrl.fromLocalFile(harita_path))

        # --- Timer: veri güncelleme ---
        self.data_timer = QtCore.QTimer()
        self.data_timer.timeout.connect(self.update_sensor_data)
        self.data_timer.start(2000)  # 2 saniyede bir

        self.time_counter = 0

    def update_sensor_data(self):
        self.time_counter += 2  # 2 saniyede bir artış

        # Rastgele sıcaklık verisi (örnek)
        new_temp = random.uniform(20.0, 30.0)
        self.sicaklik_xdata.append(self.time_counter)
        self.sicaklik_ydata.append(new_temp)

        self.sicaklik_canvas.axes.cla()
        self.sicaklik_canvas.axes.plot(self.sicaklik_xdata, self.sicaklik_ydata, 'r-', label="Sıcaklık (°C)")
        self.sicaklik_canvas.axes.set_ylabel("Sıcaklık (°C)")
        self.sicaklik_canvas.axes.set_xlabel("Zaman (sn)")
        self.sicaklik_canvas.axes.legend(loc="upper left")
        self.sicaklik_canvas.draw()

        # Rastgele basınç verisi (örnek)
        new_pressure = random.uniform(90000, 110000)  # Pascal cinsinden
        self.basinç_xdata.append(self.time_counter)
        self.basinç_ydata.append(new_pressure)

        self.basinç_canvas.axes.cla()
        self.basinç_canvas.axes.plot(self.basinç_xdata, self.basinç_ydata, 'b-', label="Basınç (Pa)")
        self.basinç_canvas.axes.set_ylabel("Basınç (Pa)")
        self.basinç_canvas.axes.set_xlabel("Zaman (sn)")
        self.basinç_canvas.axes.legend(loc="upper left")
        self.basinç_canvas.draw()

        # Rastgele yükseklik verisi (örnek)
        new_height = random.uniform(200.0, 400.0)  # 200 m ile 400 m arasında yükseklik
        self.yukseklik_xdata.append(self.time_counter)
        self.yukseklik_ydata.append(new_height)

        self.yukseklik_canvas.axes.cla()  # Grafiği temizle
        self.yukseklik_canvas.axes.plot(self.yukseklik_xdata, self.yukseklik_ydata, 'g-', label="Yükseklik (m)")
        self.yukseklik_canvas.axes.set_ylabel("Yükseklik (m)")
        self.yukseklik_canvas.axes.set_xlabel("Zaman (sn)")
        self.yukseklik_canvas.axes.legend(loc="upper left")
        self.yukseklik_canvas.draw()

        # Rastgele iniş hızı verisi (örnek)
        new_speed = random.uniform(10.0, 25.0)  # 10 m/s ile 25 m/s arasında pozitif hız
        self.hiz_xdata.append(self.time_counter)
        self.hiz_ydata.append(new_speed)

        self.hiz_canvas.axes.cla()  # Grafiği temizle
        self.hiz_canvas.axes.plot(self.hiz_xdata, self.hiz_ydata, 'y-', label="İniş Hızı (m/s)")
        self.hiz_canvas.axes.set_ylabel("İniş Hızı (m/s)")
        self.hiz_canvas.axes.set_xlabel("Zaman (sn)")
        self.hiz_canvas.axes.legend(loc="upper left")
        self.hiz_canvas.draw()

        # Rastgele pil gerilimi verisi (örnek)
        new_voltage = random.uniform(3.5, 4.2)  # 3.5V ile 4.2V arasında pil gerilimi
        self.pil_xdata.append(self.time_counter)
        self.pil_ydata.append(new_voltage)

        self.pil_canvas.axes.cla()  # Grafiği temizle
        self.pil_canvas.axes.plot(self.pil_xdata, self.pil_ydata, 'm-', label="Pil Gerilimi (V)")
        self.pil_canvas.axes.set_ylabel("Pil Gerilimi (V)")
        self.pil_canvas.axes.set_xlabel("Zaman (sn)")
        self.pil_canvas.axes.legend(loc="upper left")
        self.pil_canvas.draw()

        # Rastgele değerler oluştur (gerçek verilerle değiştirin)
        new_pitch = random.uniform(-180.0, 180.0)
        new_roll = random.uniform(-180.0, 180.0)
        new_yaw = random.uniform(-180.0, 180.0)
        new_altitude = random.uniform(200.0, 400.0)  # 200m ile 400m arasında yükseklik
        new_longitude = random.uniform(31.0, 32.0)  # Longitude örneği (gerçek koordinatlarla değiştirin)

        # Verileri ilgili widget'a yaz
        self.pitch_label.setText(f"Pitch: {new_pitch:.2f}°")
        self.roll_label.setText(f"Roll: {new_roll:.2f}°")
        self.yaw_label.setText(f"Yaw: {new_yaw:.2f}°")
        self.altitude_label.setText(f"GPS Altitude: {new_altitude:.2f} m")
        self.longitude_label.setText(f"GPS Longitude: {new_longitude:.6f}")

    def update_camera(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        frame = cv2.flip(frame, 1)  # Yatay aynalama düzeltme

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(qt_image)
        self.camera_label.setPixmap(pix)

    def closeEvent(self, event):
        self.cap.release()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())

