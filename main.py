import os
import sys
import threading
from dotenv import load_dotenv
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton,
                             QVBoxLayout, QWidget, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPixmap, QMovie
from gtts import gTTS
import speech_recognition as sr
from playsound import playsound
from openai import OpenAI
import pyttsx3

load_dotenv()
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
)

class ChatGPTApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.language = "rus"
        self.setWindowTitle("Yordamchi ChatGPT")
        self.setGeometry(200, 200, 800, 600)

        # Background rasm
        self.background_label = QLabel(self)
        bg = QPixmap("ai_model/anime_office_bg.png")
        self.background_label.setPixmap(bg.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.lower()

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Avatar GIF o'rtada
        self.avatar_label = QLabel(objectName="avatar_label")
        self.avatar_label.setAlignment(Qt.AlignHCenter)
        self.movie = QMovie("ai_model/chibi_avatar.gif")
        self.avatar_label.setMovie(self.movie)
        self.movie.start()
        self.layout.addWidget(self.avatar_label)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.input_field = QLineEdit()
        self.send_button = QPushButton("Yuborish")
        self.voice_button = QPushButton("🎤")

        self.layout.addWidget(self.chat_display)
        self.layout.addWidget(self.input_field)
        self.layout.addWidget(self.send_button)
        self.layout.addWidget(self.voice_button)

        self.send_button.clicked.connect(self.send_message)
        self.voice_button.clicked.connect(self.voice_input)

        self.setStyleSheet("""
            QMainWindow { background: transparent; }
            #avatar_label { background: transparent; }
            QPushButton {
                background-color: #5E81AC;
                color: white;
                padding: 8px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #4C6680; }
            QTextEdit {
                background-color: rgba(255,255,255,0.85);
                font-family: Consolas;
            }
            QLineEdit {
                background-color: white;
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)

    def send_message(self):
        user_text = self.input_field.text()
        if user_text:
            self.display_message("Siz", user_text, QColor(0, 0, 255))
            self.input_field.clear()
            self.ask_openai(user_text)

    def display_message(self, sender, message, color):
        self.chat_display.setTextColor(color)
        self.chat_display.append(f"{sender}: {message}")



    def ask_openai(self, text):
        self.display_message("Yordamchi", "Javob o'ylayapman...", QColor(128, 128, 128))

        def get_response():
            try:
                completion = client.chat.completions.create(
                    model="meta-llama/llama-3-8b-instruct:nitro",
                    messages=[
                        {"role": "system", "content": f"Siz {self.language} tilida yordam beradigan yordamchisiz."},
                        {"role": "user", "content": text},
                    ]
                )
                answer = completion.choices[0].message.content.strip()
                self.display_message("Yordamchi", answer, QColor(0, 128, 0))
                self.text_to_speech(answer)
            except Exception as e:
                self.display_message("Yordamchi", f"Xatolik yuz berdi: {e}", QColor(255, 0, 0))

        threading.Thread(target=get_response).start()

    def text_to_speech(self, text):
        try:
            engine = pyttsx3.init()

            # Настройки: скорость, громкость, голос
            engine.setProperty('rate', 160)  # скорость речи
            engine.setProperty('volume', 1.0)  # громкость (0.0 до 1.0)

            voices = engine.getProperty('voices')

            for i, voice in enumerate(voices):
                print(f"{i}: {voice.name} — {voice.id}")

            # Пример: выбрать русский женский голос (может отличаться по системе)
            for voice in voices:
                if "russian" in voice.name.lower() or "рус" in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break

            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            self.display_message("TTS", f"Ovozda xatolik: {e}", QColor(255, 0, 0))

    def voice_input(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.display_message("Siz", "Iltimos, gapiring...", QColor(0, 0, 255))
            try:
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio, language="uz-UZ")
                self.input_field.setText(text)
                self.send_message()
            except sr.UnknownValueError:
                self.display_message("Xatolik", "Gapni tushunmadim.", QColor(255, 0, 0))
            except sr.RequestError as e:
                self.display_message("Xatolik", f"Xizmat ishlamadi: {e}", QColor(255, 0, 0))
            except Exception as e:
                self.display_message("Xatolik", str(e), QColor(255, 0, 0))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        bg = QPixmap("ai_model/anime_office_bg.png")
        self.background_label.setPixmap(bg.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        self.background_label.setGeometry(0, 0, self.width(), self.height())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatGPTApp()
    window.show()
    sys.exit(app.exec_())
