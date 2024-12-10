import os
import openai
import webbrowser
import threading
from dotenv import load_dotenv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QWidget, QComboBox, QLabel
)
from PyQt5.QtGui import QTextCursor, QColor
from PyQt5.QtCore import Qt
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import ctypes
import platform
import webbrowser


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


class ChatGPTApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UzbekAI Yordamchi")
        self.setGeometry(100, 100, 800, 600)

        self.language = "uz"


        self.layout = QVBoxLayout()
        self.language_label = QLabel("Tilni tanlang:")
        self.layout.addWidget(self.language_label)

        self.language_menu = QComboBox()
        self.language_menu.addItems(["uz", "ru", "en"])
        self.language_menu.currentTextChanged.connect(self.update_language)
        self.layout.addWidget(self.language_menu)


        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)


        self.user_input = QLineEdit(self)
        self.user_input.setPlaceholderText("Xabaringizni kiriting...")
        self.user_input.returnPressed.connect(self.handle_user_input)
        self.layout.addWidget(self.user_input)


        self.send_button = QPushButton("Yuborish", self)
        self.send_button.clicked.connect(self.handle_user_input)
        self.layout.addWidget(self.send_button)


        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def update_language(self, lang):
        self.language = lang

    def handle_user_input(self):
        user_message = self.user_input.text().strip()
        if user_message:
            self.display_message("Siz", user_message, QColor(0, 0, 255))
            self.user_input.clear()
            if "qo'lingdan nima keladi" in user_message.lower():
                self.list_capabilities()
            else:
                self.process_command(user_message)

    def display_message(self, sender, message, color):
        self.chat_display.setTextColor(color)
        self.chat_display.append(f"{sender}: {message}")
        self.chat_display.setTextColor(Qt.black)
        self.chat_display.moveCursor(QTextCursor.End)

    def list_capabilities(self):
        capabilities = """
Men quyidagilarni qila olaman:
1. Kompyuteringizdagi fayl yoki papkalarni ochish.
2. Ilovalarni ishga tushirish.
3. Musiqa qo'yish.
4. Brauzerda saytlarni ochish.
5. Kompyuter ovozini ko'tarish yoki pasaytirish.
6. Kompyuter ekranini qulflash.
"""
        self.display_message("Yordamchi", capabilities, QColor(0, 128, 0))

    predefined_sites = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "facebook": "https://facebook.com",
        "github": "https://github.com",
        "stackoverflow": "https://stackoverflow.com",
    }

    def set_volume(level):
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            volume.SetMasterVolumeLevelScalar(level / 100.0, None)
            return True
        except Exception as e:
            return False, str(e)


    def process_command(self, command):
        if "fayl och" in command.lower():
            file_path = command.split("fayl och", 1)[-1].strip()
            if os.path.exists(file_path):
                os.startfile(file_path)
                self.display_message("Yordamchi", f"Fayl ochildi: {file_path}", QColor(0, 128, 0))
            else:
                self.display_message("Yordamchi", "Fayl topilmadi.", QColor(255, 0, 0))
        elif "sayt och" in command.lower():
            site_name = command.split("sayt och", 1)[-1].strip()
            if site_name in self.predefined_sites:
                site_name = self.predefined_sites[site_name]
            if not site_name.startswith("http://") and not site_name.startswith("https://"):
                site_name = f"https://{site_name}.com"

            try:
                webbrowser.open_new_tab(site_name)
                self.display_message("Yordamchi", f"Sayt ochildi: {site_name}", QColor(0, 128, 0))
            except Exception as e:
                self.display_message("Yordamchi", f"Saytni ochishda xatolik yuz berdi {e}", QColor(255, 0, 0))
        elif "musiqa qo'y" in command.lower():
            file_path = command.split("musiqa qo'y", 1)[-1].strip()
            if os.path.exists(file_path):
                os.startfile(file_path)
                self.display_message("Yordamchi", "Musiqa qo'yildi.", QColor(0, 128, 0))
            else:
                self.display_message("Yordamchi", "Musiqa fayli topilmadi.", QColor(255, 0, 0))
        elif "ekranni qulflash" in command.lower():
            if platform.system() == "Windows":
                ctypes.windll.user32.LockWorkStation()
                self.display_message("Yordamchi", "Ekran qulflandi.", QColor(0, 128, 0))
            else:
                self.display_message("Yordamchi", "Ushbu funksiya faqat Windows uchun ishlaydi.", QColor(255, 0, 0))
        elif "ovozni ko'tar" in command.lower():
            try:
                level = int(command.split("ko'tar", 1)[-1].strip())
                self.set_volume(level)
                self.display_message("Yordamchi", f"Ovoz darajasi {level}% ga ko'tarildi.", QColor(0, 128, 0))
            except ValueError:
                self.display_message("Yordamchi", "Iltimos, ovoz darajasini 0 dan 100 gacha kiritng.", QColor(255, 0, 0))
        elif "ovozni tushir" in command.lower():
            try:
                level = int(command.split("tushir", 1)[-1].strip())
                self.set_volume(level)
                self.display_message("Yordamchi", f"Ovoz darajasi {level}% ga tushirildi.", QColor(0, 128, 0))
            except ValueError:
                self.display_message("Yordamchi", "Iltimos, ovoz darajasini 0 dan 100 gacha kiritng.", QColor(255, 0, 0))
        else:
            self.ask_openai(command)


    def ask_openai(self, text):
        self.display_message("Yordamchi", "Javob o'ylayapman...", QColor(128, 128, 128))

        def get_response():
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": f"Siz {self.language} tilida yordam beradigan yordamchisiz."},
                        {"role": "user", "content": text}
                    ]
                )
                answer = response.choices[0].message.content.strip()
                self.display_message("Yordamchi", answer, QColor(0, 128, 0))
            except Exception as e:
                self.display_message("Yordamchi", f"Kechirasiz, javob olishda xatolik yuz berdi: {e}", QColor(255, 0, 0))
        threading.Thread(target=get_response).start()


if __name__ == "__main__":
    app = QApplication([])
    window = ChatGPTApp()
    window.show()
    app.exec()
