import sys
import os
import json
import threading
import time
import random
import webbrowser
import subprocess
import platform
import urllib.parse
from datetime import datetime
import math

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import speech_recognition as sr
import pyttsx3
import pyautogui
import ctypes
import re

SYSTEM = platform.system()

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".dzhenya")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

LANGUAGES = {
    "en": {
        "app_name": "Dzhenya Assistant",
        "new_chat": "New Chat",
        "chat": "Chat",
        "commands": "Commands",
        "settings": "Settings",
        "profile": "Profile",
        "save": "Save Settings",
        "save_commands": "Save All Commands",
        "cancel": "Cancel",
        "shut_down": "Shut Down",
        "add_command": "Add Custom Command",
        "add": "Add Command",
        "delete": "Delete",
        "enabled": "Enabled",
        "apps": "Applications",
        "urls": "URLs (one per line)",
        "name": "Name",
        "speed": "Speed",
        "volume": "Volume",
        "language": "Language",
        "general": "General",
        "voice": "Voice",
        "welcome": "Welcome",
        "listening": "Listening...",
        "ready": "Ready",
        "processing": "Processing...",
        "speaking": "Speaking...",
        "mic_hint": "Press microphone and speak",
        "browse": "Browse",
        "phrase": "Voice phrase",
        "app_path": "Application path (optional)",
        "url_label": "URL to open (optional)",
        "preset_commands": "Preset Commands",
        "custom_commands": "Custom Commands",
        "im_here": "I'm here",
        "im_tired": "I'm tired",
        "computer_school": "Computer school",
        "school": "School",
        "shutdown_msg": "shut down the computer?",
        "unsaved": "All unsaved work will be lost.",
        "saved": "Settings saved successfully!",
        "commands_saved": "All commands saved successfully!",
        "no_mic": "Microphone not found!",
        "silent_on": "Silent mode activated. I won't respond until you wake me up.",
        "silent_off": "I'm listening again. How can I help you?",
        "windows_minimized": "All windows minimized.",
        "windows_restored": "Windows restored.",
        "welcome_back": "Welcome back.",
        "time_to_relax": "Time to relax.",
        "computer_school_mode": "Computer school mode activated.",
        "school_mode": "School mode activated.",
        "command_disabled": "This command is disabled.",
        "opening": "Opening",
        "cannot_find": "Cannot find",
        "searching": "Searching for",
        "weather": "Opening weather forecast",
        "time": "The time is",
        "goodbye": "Goodbye! Have a great day!",
        "shutting_down": "Shutting down the computer...",
        "shutdown_cancelled": "Shutdown cancelled.",
        "you": "You",
        "dzhenya": "Dzhenya",
        "hello_response": "Hello",
        "youre_welcome": "You're welcome.",
        "which_app": "Which application would you like to open?",
        "opened": "Opened",
        "commands_settings": "Commands Settings",
        "add_custom": "+ Add Custom Command",
        "browse_file": "Select Application",
        "executables": "Executable files (*.exe *.app);;All files (*)",
        "command_executed": "Command executed.",
        "move_to_other_monitor": "Window moved to other monitor",
        "move_monitor_error": "No active window found",
        "volume_increased": "Volume increased by {0} percent",
        "volume_decreased": "Volume decreased by {0} percent",
        "volume_error": "Could not change volume",
        "language_changed": "Keyboard language changed",
        "language_error": "Could not change language",
        "trash_cleared": "Recycle bin has been emptied",
        "trash_error": "Could not empty recycle bin"
    }
}

def load_config():
    default = {
        "username": os.getlogin(),
        "language": "en",
        "speed": 160,
        "volume": 0.9,
        "silent_mode": False,
        "custom_commands": [],
        "commands": {
            "im_here": {
                "enabled": True,
                "apps": ["spotify", "browser", "vscode"],
                "urls": []
            },
            "im_tired": {
                "enabled": True,
                "apps": ["spotify", "steam", "discord"],
                "urls": []
            },
            "computer_school": {
                "enabled": True,
                "apps": ["teams", "browser"],
                "urls": ["https://mystat.itstep.org"]
            },
            "school": {
                "enabled": True,
                "apps": [],
                "urls": ["https://mail.google.com"]
            }
        }
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                if "commands" not in saved:
                    saved["commands"] = default["commands"]
                if "custom_commands" not in saved:
                    saved["custom_commands"] = []
                if "language" not in saved:
                    saved["language"] = "en"
                default.update(saved)
        except:
            pass
    return default

config = load_config()

def save_config(cfg):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
    except:
        pass

def tr(key):
    lang = config.get("language", "en")
    if lang not in LANGUAGES:
        lang = "en"
    return LANGUAGES[lang].get(key, key)

class Colors:
    BG_MAIN = "#0A0A0F"
    BG_SIDEBAR = "#0F0F18"
    BG_CARD = "#141423"
    BG_HOVER = "#1E1E32"
    BG_INPUT = "#0F0F19"
    
    BORDER = "#202030"
    BORDER_LIGHT = "#151525"
    
    TEXT_PRIMARY = "#E8E8F0"
    TEXT_SECONDARY = "#9090A0"
    TEXT_TERTIARY = "#686878"
    
    BLUE = "#6B8CFF"
    BLUE_DARK = "#5A70D0"
    
    GREEN = "#4ADE80"
    GREEN_DARK = "#3AB868"
    
    PURPLE = "#A78BFA"
    PURPLE_DARK = "#8B6FE0"
    
    RED = "#F87171"
    RED_DARK = "#E05050"
    
    CYAN = "#22D3EE"


class SiriLikeOrb(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.setMaximumSize(300, 300)
        
        self.active = False
        self.speaking = False
        self.phase = 0
        self.intensity = 0.0
        self.hue = 0
        
        self.ripples = []
        for i in range(6):
            self.ripples.append({
                'radius': 0,
                'max_radius': 0,
                'alpha': 0,
                'speed': random.uniform(0.5, 1.5)
            })
        
        self.glowing = 0
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_anim)
        self.timer.start(16)
    
    def update_anim(self):
        self.phase += 0.05
        self.hue = (self.hue + 0.5)
        if self.hue >= 360:
            self.hue = 0
        
        if self.active or self.speaking:
            self.intensity = min(1.0, self.intensity + 0.025)
            self.glowing = min(1.0, self.glowing + 0.04)
            
            for ripple in self.ripples:
                if ripple['radius'] >= ripple['max_radius'] or ripple['alpha'] <= 0:
                    ripple['radius'] = 0
                    ripple['max_radius'] = random.uniform(40, 100)
                    ripple['alpha'] = 0.7
                else:
                    ripple['radius'] += ripple['speed'] * 2
                    ripple['alpha'] = max(0, ripple['alpha'] - 0.01)
        else:
            self.intensity = max(0.0, self.intensity - 0.015)
            self.glowing = max(0.0, self.glowing - 0.02)
            
            for ripple in self.ripples:
                ripple['radius'] = 0
                ripple['alpha'] = 0
        
        self.update()
    
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w/2, h/2
        base_r = min(w, h) * 0.2
        max_r = min(w, h) * 0.45
        
        p.fillRect(self.rect(), QColor(Colors.BG_MAIN))
        
        for ripple in self.ripples:
            if ripple['alpha'] > 0 and self.intensity > 0.1:
                r = base_r + ripple['radius'] * 1.5
                if r <= max_r:
                    color = QColor()
                    hue_val = int(self.hue + ripple['radius'] * 3) % 360
                    color.setHsv(hue_val, 255, 255, int(100 * ripple['alpha'] * self.intensity))
                    
                    p.setPen(QPen(color, 2))
                    p.setBrush(Qt.NoBrush)
                    p.drawEllipse(QPointF(cx, cy), r, r)
        
        if self.speaking:
            wave_amplitude = 8 * math.sin(self.phase * 6)
            r_variation = abs(math.sin(self.phase * 8)) * 6
        else:
            wave_amplitude = 0
            r_variation = 0
        
        grad_radius = base_r * 2 + self.intensity * 20 + r_variation
        
        if self.speaking:
            colors = []
            for i in range(5):
                angle = self.phase * 10 + i * 72
                h_val = int(self.hue + i * 30) % 360
                colors.append((h_val, 255, 255))
            
            radial_grad = QRadialGradient(cx - grad_radius*0.2, cy - grad_radius*0.3, grad_radius * 1.3)
            for i, (h, s, v) in enumerate(colors):
                pos = i / 4
                color = QColor()
                color.setHsv(h, s, v, 220)
                radial_grad.setColorAt(pos, color)
        elif self.active:
            radial_grad = QRadialGradient(cx - grad_radius*0.2, cy - grad_radius*0.3, grad_radius * 1.2)
            for i in range(3):
                pos = i / 2
                color = QColor()
                hue_val = int(self.hue + i * 60) % 360
                color.setHsv(hue_val, 200, 255, 200)
                radial_grad.setColorAt(pos, color)
        else:
            radial_grad = QRadialGradient(cx - grad_radius*0.2, cy - grad_radius*0.3, grad_radius)
            color1 = QColor()
            color1.setHsv(210, 180, 180, 180)
            color2 = QColor()
            color2.setHsv(240, 150, 150, 100)
            radial_grad.setColorAt(0, color1)
            radial_grad.setColorAt(1, color2)
        
        p.setBrush(QBrush(radial_grad))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx, cy), base_r + self.intensity * 12 + wave_amplitude, base_r + self.intensity * 12 + wave_amplitude)
        
        glow_grad = QRadialGradient(cx, cy, base_r * 1.5)
        glow_color = QColor()
        glow_color.setHsv(int(self.hue), 200, 255, int(60 * self.glowing))
        glow_grad.setColorAt(0, glow_color)
        glow_grad.setColorAt(1, QColor(0, 0, 0, 0))
        
        p.setBrush(QBrush(glow_grad))
        p.drawEllipse(QPointF(cx, cy), base_r * 1.5 + self.glowing * 20, base_r * 1.5 + self.glowing * 20)
        
        if self.active:
            p.setBrush(Qt.NoBrush)
            for i in range(3):
                angle_offset = self.phase * 8 + i * 120
                ellipse_wave = 5 * math.sin(angle_offset)
                ellipse_h = 5 * math.cos(angle_offset)
                color = QColor()
                hue_val = int(self.hue + i * 40) % 360
                color.setHsv(hue_val, 255, 255, 150)
                p.setPen(QPen(color, 2))
                p.drawEllipse(QPointF(cx, cy), base_r + 15 + ellipse_wave, base_r + 15 + ellipse_h)
    
    def set_active(self, a):
        self.active = a
    
    def set_speaking(self, s):
        self.speaking = s


class ShutdownDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.setWindowTitle("Dzhenya")
        self.setFixedSize(420, 240)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Colors.BG_CARD};
                border: 1px solid {Colors.BORDER};
                border-radius: 20px;
            }}
        """)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(16)
        
        icon = QLabel("!")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(44, 44)
        icon.setStyleSheet(f"""
            QLabel {{
                background-color: {Colors.RED};
                color: #fff;
                border-radius: 22px;
                font-size: 24px;
                font-weight: bold;
            }}
        """)
        
        title = QLabel(f"{self.username}, {tr('shutdown_msg')}")
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 14px;")
        
        sub = QLabel(tr("unsaved"))
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px;")
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        cancel_btn = QPushButton(tr("cancel"))
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.BG_HOVER};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
                padding: 10px 20px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {Colors.BG_CARD};
                border-color: {Colors.BLUE};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        
        confirm_btn = QPushButton(tr("shut_down"))
        confirm_btn.setCursor(Qt.PointingHandCursor)
        confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.RED};
                color: #fff;
                border: none;
                border-radius: 12px;
                padding: 10px 20px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {Colors.RED_DARK};
            }}
        """)
        confirm_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(confirm_btn)
        
        layout.addWidget(icon, alignment=Qt.AlignCenter)
        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addLayout(btn_layout)


class MessageWidget(QWidget):
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        self.text = text
        self.is_user = is_user
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 10, 24, 10)
        layout.setSpacing(14)
        
        avatar = QLabel()
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignCenter)
        
        if self.is_user:
            avatar.setStyleSheet(f"""
                QLabel {{
                    background-color: {Colors.BLUE};
                    border-radius: 18px;
                    color: #fff;
                    font-size: 15px;
                    font-weight: 600;
                }}
            """)
            avatar.setText(config.get("username", "U")[0].upper())
        else:
            avatar.setStyleSheet(f"""
                QLabel {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #6B8CFF, stop:1 #A78BFA);
                    border-radius: 18px;
                    color: #fff;
                    font-size: 16px;
                }}
            """)
            avatar.setText("D")
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(2)
        
        name = QLabel(tr("you") if self.is_user else tr("dzhenya"))
        name.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px; font-weight: 500; background: transparent;")
        
        msg = QLabel(self.text)
        msg.setWordWrap(True)
        msg.setMaximumWidth(520)
        msg.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 14px; background: transparent;")
        
        c_layout.addWidget(name)
        c_layout.addWidget(msg)
        
        if self.is_user:
            layout.addStretch()
            layout.addWidget(container)
            layout.addWidget(avatar)
        else:
            layout.addWidget(avatar)
            layout.addWidget(container)
            layout.addStretch()
        
        self.setStyleSheet("background: transparent;")


class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setFixedWidth(250)
        self.nav_buttons = []
        self.init_ui()
    
    def init_ui(self):
        if self.layout():
            while self.layout().count():
                item = self.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(8)
        
        self.setStyleSheet(f"background-color: {Colors.BG_SIDEBAR}; border-right: 1px solid {Colors.BORDER};")
        
        logo = QLabel(tr("app_name"))
        logo.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 17px; font-weight: 600; padding: 8px;")
        layout.addWidget(logo)
        
        layout.addSpacing(16)
        
        new_btn = QPushButton(tr("new_chat"))
        new_btn.setCursor(Qt.PointingHandCursor)
        new_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.BG_HOVER};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
                padding: 10px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {Colors.BG_CARD};
                border-color: {Colors.BLUE};
            }}
        """)
        new_btn.clicked.connect(self.new_chat)
        layout.addWidget(new_btn)
        
        layout.addSpacing(20)
        
        self.nav_buttons = []
        nav_items = [
            ("chat", self.show_chat),
            ("commands", self.show_commands),
            ("settings", self.show_settings),
            ("profile", self.show_profile),
        ]
        
        for key, handler in nav_items:
            btn = QPushButton(tr(key))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {Colors.TEXT_SECONDARY};
                    border: none;
                    border-radius: 10px;
                    padding: 10px;
                    font-size: 13px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {Colors.BG_HOVER};
                    color: {Colors.TEXT_PRIMARY};
                }}
            """)
            btn.clicked.connect(handler)
            layout.addWidget(btn)
            self.nav_buttons.append((btn, key))
        
        layout.addStretch()
        
        profile = QWidget()
        profile.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BG_HOVER};
                border: 1px solid {Colors.BORDER};
                border-radius: 14px;
            }}
        """)
        
        p_layout = QHBoxLayout(profile)
        p_layout.setContentsMargins(12, 10, 12, 10)
        p_layout.setSpacing(10)
        
        av = QLabel(config.get("username", "U")[0].upper())
        av.setFixedSize(32, 32)
        av.setAlignment(Qt.AlignCenter)
        av.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6B8CFF, stop:1 #A78BFA);
                border-radius: 16px;
                color: #fff;
                font-size: 13px;
                font-weight: 600;
            }}
        """)
        
        self.profile_name = QLabel(config.get("username", "User"))
        self.profile_name.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 12px;")
        
        p_layout.addWidget(av)
        p_layout.addWidget(self.profile_name)
        p_layout.addStretch()
        
        layout.addWidget(profile)
    
    def update_texts(self):
        for btn, key in self.nav_buttons:
            btn.setText(tr(key))
        
        for child in self.children():
            if isinstance(child, QPushButton) and child.text() in ["New Chat", "New Chat"]:
                child.setText(tr("new_chat"))
        
        self.profile_name.setText(config.get("username", "User"))
    
    def new_chat(self):
        if self.parent_window:
            while self.parent_window.chat_layout.count():
                item = self.parent_window.chat_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.parent_window.welcome()
    
    def show_chat(self):
        if self.parent_window:
            self.parent_window.stack.setCurrentIndex(0)
            self.parent_window.page_title.setText(tr("chat"))
    
    def show_commands(self):
        if self.parent_window:
            self.parent_window.stack.setCurrentIndex(1)
            self.parent_window.page_title.setText(tr("commands_settings"))
    
    def show_settings(self):
        if self.parent_window:
            self.parent_window.stack.setCurrentIndex(2)
            self.parent_window.page_title.setText(tr("settings"))
    
    def show_profile(self):
        if self.parent_window:
            self.parent_window.stack.setCurrentIndex(3)
            self.parent_window.page_title.setText(tr("profile"))


AVAILABLE_APPS = [
    "spotify", "steam", "discord", "vscode", "teams",
    "browser", "chrome", "notepad", "calculator",
    "cmd", "powershell", "explorer", "paint",
]


class AddCommandDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("add_command"))
        self.setFixedSize(500, 400)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Colors.BG_CARD};
                border: 1px solid {Colors.BORDER};
                border-radius: 20px;
            }}
        """)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(14)
        
        title = QLabel(tr("add_command"))
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 18px; font-weight: 600;")
        layout.addWidget(title)
        
        phrase_label = QLabel(tr("phrase") + ":")
        phrase_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(phrase_label)
        
        self.phrase_input = QLineEdit()
        self.phrase_input.setPlaceholderText("open my project")
        self.phrase_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 10px;
                padding: 10px;
                font-size: 13px;
            }}
            QLineEdit:focus {{ border-color: {Colors.BLUE}; }}
        """)
        layout.addWidget(self.phrase_input)
        
        app_label = QLabel(tr("app_path") + ":")
        app_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(app_label)
        
        app_layout = QHBoxLayout()
        self.app_input = QLineEdit()
        self.app_input.setPlaceholderText("C:\\Program Files\\App\\app.exe")
        self.app_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 10px;
                padding: 10px;
                font-size: 13px;
            }}
            QLineEdit:focus {{ border-color: {Colors.BLUE}; }}
        """)
        
        browse_btn = QPushButton(tr("browse"))
        browse_btn.setCursor(Qt.PointingHandCursor)
        browse_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.BG_HOVER};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 10px;
                padding: 10px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {Colors.BG_CARD};
            }}
        """)
        browse_btn.clicked.connect(self.browse_file)
        
        app_layout.addWidget(self.app_input)
        app_layout.addWidget(browse_btn)
        layout.addLayout(app_layout)
        
        url_label = QLabel(tr("url_label") + ":")
        url_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(url_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        self.url_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 10px;
                padding: 10px;
                font-size: 13px;
            }}
            QLineEdit:focus {{ border-color: {Colors.BLUE}; }}
        """)
        layout.addWidget(self.url_input)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        cancel_btn = QPushButton(tr("cancel"))
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.BG_HOVER};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
                padding: 10px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {Colors.BG_CARD};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        
        add_btn = QPushButton(tr("add"))
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.GREEN};
                color: #fff;
                border: none;
                border-radius: 12px;
                padding: 10px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {Colors.GREEN_DARK};
            }}
        """)
        add_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(add_btn)
        layout.addLayout(btn_layout)
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, tr("browse_file"), "", tr("executables"))
        if file_path:
            self.app_input.setText(file_path)
    
    def get_command(self):
        return {
            "phrase": self.phrase_input.text().strip(),
            "app_path": self.app_input.text().strip(),
            "url": self.url_input.text().strip()
        }


class CommandsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet(f"background-color: {Colors.BG_MAIN};")
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background-color: transparent; border: none;")
        
        scroll.verticalScrollBar().setStyleSheet(f"""
            QScrollBar:vertical {{
                background-color: transparent;
                width: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {Colors.BORDER};
                border-radius: 3px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        title = QLabel(tr("commands_settings"))
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 24px; font-weight: 600;")
        layout.addWidget(title)
        
        preset_label = QLabel(tr("preset_commands"))
        preset_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 16px; font-weight: 500; margin-top: 8px;")
        layout.addWidget(preset_label)
        
        self.im_here_section = self.create_command_section(tr("im_here"), "im_here")
        layout.addWidget(self.im_here_section)
        
        self.im_tired_section = self.create_command_section(tr("im_tired"), "im_tired")
        layout.addWidget(self.im_tired_section)
        
        self.comp_school_section = self.create_command_section(tr("computer_school"), "computer_school")
        layout.addWidget(self.comp_school_section)
        
        self.school_section = self.create_command_section(tr("school"), "school")
        layout.addWidget(self.school_section)
        
        layout.addSpacing(8)
        
        custom_label = QLabel(tr("custom_commands"))
        custom_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 16px; font-weight: 500; margin-top: 8px;")
        layout.addWidget(custom_label)
        
        self.custom_container = QWidget()
        self.custom_container.setStyleSheet("background: transparent;")
        self.custom_layout = QVBoxLayout(self.custom_container)
        self.custom_layout.setSpacing(8)
        layout.addWidget(self.custom_container)
        
        add_custom_btn = QPushButton(tr("add_custom"))
        add_custom_btn.setCursor(Qt.PointingHandCursor)
        add_custom_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.BLUE};
                border: 1px dashed {Colors.BORDER};
                border-radius: 14px;
                padding: 14px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {Colors.BG_HOVER};
                border-color: {Colors.BLUE};
            }}
        """)
        add_custom_btn.clicked.connect(self.add_custom_command)
        self.custom_layout.addWidget(add_custom_btn)
        
        self.load_custom_commands()
        
        layout.addStretch()
        
        save_btn = QPushButton(tr("save_commands"))
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.GREEN};
                color: #fff;
                border: none;
                border-radius: 16px;
                padding: 14px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {Colors.GREEN_DARK};
            }}
        """)
        save_btn.clicked.connect(self.save_all)
        layout.addWidget(save_btn)
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def create_command_section(self, title, command_key):
        cmd = config["commands"].get(command_key, {})
        
        section = QWidget()
        section.setStyleSheet("background: transparent;")
        
        bg = QWidget()
        bg.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(20, 20, 35, 0.8);
                border: 1px solid {Colors.BORDER};
                border-radius: 16px;
            }}
        """)
        
        b_layout = QVBoxLayout(bg)
        b_layout.setContentsMargins(18, 18, 18, 18)
        b_layout.setSpacing(12)
        
        header_layout = QHBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 16px; font-weight: 500;")
        
        self.__dict__[f"{command_key}_enabled"] = QCheckBox(tr("enabled"))
        self.__dict__[f"{command_key}_enabled"].setChecked(cmd.get("enabled", True))
        self.__dict__[f"{command_key}_enabled"].setCursor(Qt.PointingHandCursor)
        self.__dict__[f"{command_key}_enabled"].setStyleSheet(f"""
            QCheckBox {{
                color: {Colors.TEXT_PRIMARY};
                font-size: 13px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {Colors.BORDER};
                border-radius: 5px;
                background-color: {Colors.BG_INPUT};
            }}
            QCheckBox::indicator:checked {{
                background-color: {Colors.GREEN};
                border-color: {Colors.GREEN};
            }}
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.__dict__[f"{command_key}_enabled"])
        
        b_layout.addLayout(header_layout)
        
        apps_label = QLabel(tr("apps") + ":")
        apps_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; font-weight: 500;")
        b_layout.addWidget(apps_label)
        
        apps_container = QWidget()
        apps_container.setStyleSheet("background: transparent;")
        apps_layout = QVBoxLayout(apps_container)
        apps_layout.setSpacing(4)
        
        selected_apps = cmd.get("apps", [])
        self.__dict__[f"{command_key}_apps"] = {}
        
        for app in AVAILABLE_APPS:
            cb = QCheckBox(app.capitalize())
            cb.setChecked(app in selected_apps)
            cb.setCursor(Qt.PointingHandCursor)
            cb.setStyleSheet(f"""
                QCheckBox {{
                    color: {Colors.TEXT_SECONDARY};
                    font-size: 12px;
                    padding: 3px 0;
                }}
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                    border: 2px solid {Colors.BORDER};
                    border-radius: 4px;
                    background-color: {Colors.BG_INPUT};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {Colors.BLUE};
                    border-color: {Colors.BLUE};
                }}
            """)
            self.__dict__[f"{command_key}_apps"][app] = cb
            apps_layout.addWidget(cb)
        
        b_layout.addWidget(apps_container)
        
        urls_label = QLabel(tr("urls") + ":")
        urls_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; font-weight: 500; margin-top: 4px;")
        b_layout.addWidget(urls_label)
        
        self.__dict__[f"{command_key}_urls"] = QTextEdit()
        self.__dict__[f"{command_key}_urls"].setPlainText("\n".join(cmd.get("urls", [])))
        self.__dict__[f"{command_key}_urls"].setMaximumHeight(70)
        self.__dict__[f"{command_key}_urls"].setStyleSheet(f"""
            QTextEdit {{
                background-color: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 10px;
                padding: 8px;
                font-size: 12px;
            }}
            QTextEdit:focus {{
                border-color: {Colors.BLUE};
            }}
        """)
        b_layout.addWidget(self.__dict__[f"{command_key}_urls"])
        
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.addWidget(bg)
        
        return section
    
    def load_custom_commands(self):
        while self.custom_layout.count() > 1:
            item = self.custom_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        for i, cmd in enumerate(config.get("custom_commands", [])):
            self.add_custom_command_widget(cmd, i)
    
    def add_custom_command_widget(self, cmd, index):
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        
        bg = QWidget()
        bg.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(20, 20, 35, 0.8);
                border: 1px solid {Colors.BORDER};
                border-radius: 14px;
            }}
        """)
        
        layout = QHBoxLayout(bg)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(12)
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)
        
        phrase = QLabel(cmd.get("phrase", "Unknown"))
        phrase.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; font-weight: 500;")
        info_layout.addWidget(phrase)
        
        details = []
        if cmd.get("app_path"):
            details.append(f"App: {os.path.basename(cmd['app_path'])}")
        if cmd.get("url"):
            details.append(f"URL: {cmd['url']}")
        
        if details:
            detail_label = QLabel(" | ".join(details))
            detail_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px;")
            info_layout.addWidget(detail_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        delete_btn = QPushButton(tr("delete"))
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setFixedWidth(65)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.RED};
                border: 1px solid rgba(248, 113, 113, 0.3);
                border-radius: 10px;
                padding: 6px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: rgba(248, 113, 113, 0.1);
                border-color: {Colors.RED};
            }}
        """)
        delete_btn.clicked.connect(lambda checked, i=index: self.delete_custom_command(i))
        layout.addWidget(delete_btn)
        
        wrapper = QVBoxLayout(widget)
        wrapper.setContentsMargins(0, 0, 0, 0)
        wrapper.addWidget(bg)
        
        self.custom_layout.insertWidget(self.custom_layout.count() - 1, widget)
    
    def add_custom_command(self):
        dialog = AddCommandDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            cmd = dialog.get_command()
            if cmd["phrase"]:
                custom = config.get("custom_commands", [])
                custom.append(cmd)
                config["custom_commands"] = custom
                save_config(config)
                self.load_custom_commands()
    
    def delete_custom_command(self, index):
        custom = config.get("custom_commands", [])
        if 0 <= index < len(custom):
            custom.pop(index)
            config["custom_commands"] = custom
            save_config(config)
            self.load_custom_commands()
    
    def save_all(self):
        for cmd_key in ["im_here", "im_tired", "computer_school", "school"]:
            enabled = self.__dict__[f"{cmd_key}_enabled"].isChecked()
            
            apps = []
            for app in AVAILABLE_APPS:
                if self.__dict__[f"{cmd_key}_apps"][app].isChecked():
                    apps.append(app)
            
            urls_text = self.__dict__[f"{cmd_key}_urls"].toPlainText().strip()
            urls = [u.strip() for u in urls_text.split("\n") if u.strip()]
            
            config["commands"][cmd_key] = {
                "enabled": enabled,
                "apps": apps,
                "urls": urls
            }
        
        save_config(config)
        QMessageBox.information(self, "Dzhenya", tr("commands_saved"))


class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet(f"background-color: {Colors.BG_MAIN};")
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll.verticalScrollBar().setStyleSheet(f"""
            QScrollBar:vertical {{
                background-color: transparent;
                width: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {Colors.BORDER};
                border-radius: 3px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        title = QLabel(tr("settings"))
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 24px; font-weight: 600;")
        layout.addWidget(title)
        
        general = self.create_section(tr("general"))
        g_layout = general.layout()
        
        self.name_input = QLineEdit(config.get("username"))
        self.name_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 10px;
                padding: 10px;
                font-size: 13px;
            }}
            QLineEdit:focus {{ border-color: {Colors.BLUE}; }}
        """)
        g_layout.addWidget(self.create_row(tr("name"), self.name_input))
        
        layout.addWidget(general)
        
        voice = self.create_section(tr("voice"))
        v_layout = voice.layout()
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(100, 250)
        self.speed_slider.setValue(config.get("speed", 160))
        self.speed_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 4px;
                background-color: {Colors.BORDER};
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background-color: {Colors.BLUE};
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}
        """)
        self.speed_val = QLabel(str(config.get("speed", 160)))
        self.speed_val.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 13px;")
        self.speed_slider.valueChanged.connect(lambda v: self.speed_val.setText(str(v)))
        
        sw = QWidget()
        sw.setStyleSheet("background: transparent;")
        sl = QHBoxLayout(sw)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.addWidget(self.speed_slider)
        sl.addWidget(self.speed_val)
        v_layout.addWidget(self.create_row(tr("speed"), sw))
        
        self.vol_slider = QSlider(Qt.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(int(config.get("volume", 0.9) * 100))
        self.vol_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 4px;
                background-color: {Colors.BORDER};
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background-color: {Colors.GREEN};
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}
        """)
        self.vol_val = QLabel(str(int(config.get("volume", 0.9) * 100)))
        self.vol_val.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 13px;")
        self.vol_slider.valueChanged.connect(lambda v: self.vol_val.setText(str(v)))
        
        vw = QWidget()
        vw.setStyleSheet("background: transparent;")
        vl = QHBoxLayout(vw)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.addWidget(self.vol_slider)
        vl.addWidget(self.vol_val)
        v_layout.addWidget(self.create_row(tr("volume"), vw))
        
        layout.addWidget(voice)
        
        layout.addStretch()
        
        save_btn = QPushButton(tr("save"))
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.GREEN};
                color: #fff;
                border: none;
                border-radius: 16px;
                padding: 14px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {Colors.GREEN_DARK};
            }}
        """)
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def create_section(self, title):
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        
        bg = QWidget()
        bg.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(20, 20, 35, 0.8);
                border: 1px solid {Colors.BORDER};
                border-radius: 16px;
            }}
        """)
        
        l = QVBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        l.addWidget(bg)
        
        b_layout = QVBoxLayout(bg)
        b_layout.setContentsMargins(18, 18, 18, 18)
        b_layout.setSpacing(14)
        
        t = QLabel(title)
        t.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 15px; font-weight: 500;")
        b_layout.addWidget(t)
        
        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(10)
        b_layout.addWidget(inner)
        
        w.inner_layout = inner_layout
        
        return w
    
    def create_row(self, label, widget):
        r = QWidget()
        r.setStyleSheet("background: transparent;")
        rl = QHBoxLayout(r)
        rl.setContentsMargins(0, 0, 0, 0)
        
        lb = QLabel(label)
        lb.setFixedWidth(100)
        lb.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        
        rl.addWidget(lb)
        rl.addWidget(widget)
        rl.addStretch()
        
        return r
    
    def save(self):
        config["username"] = self.name_input.text()
        config["speed"] = self.speed_slider.value()
        config["volume"] = self.vol_slider.value() / 100
        save_config(config)
        QMessageBox.information(self, "Dzhenya", tr("saved"))


class ProfilePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet(f"background-color: {Colors.BG_MAIN};")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        title = QLabel(tr("profile"))
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 24px; font-weight: 600;")
        layout.addWidget(title)
        
        card = QWidget()
        card.setStyleSheet("background: transparent;")
        
        bg = QWidget()
        bg.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(20, 20, 35, 0.8);
                border: 1px solid {Colors.BORDER};
                border-radius: 20px;
            }}
        """)
        
        c_layout = QVBoxLayout(bg)
        c_layout.setAlignment(Qt.AlignCenter)
        c_layout.setContentsMargins(30, 30, 30, 30)
        c_layout.setSpacing(14)
        
        av = QLabel(config.get("username", "U")[0].upper())
        av.setFixedSize(80, 80)
        av.setAlignment(Qt.AlignCenter)
        av.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6B8CFF, stop:1 #A78BFA);
                border-radius: 40px;
                color: #fff;
                font-size: 34px;
                font-weight: 600;
            }}
        """)
        
        name = QLabel(config.get("username", "User"))
        name.setAlignment(Qt.AlignCenter)
        name.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 22px; font-weight: 500;")
        
        c_layout.addWidget(av, alignment=Qt.AlignCenter)
        c_layout.addWidget(name, alignment=Qt.AlignCenter)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.addWidget(bg)
        
        layout.addWidget(card)
        layout.addStretch()


class AppFinder:
    @staticmethod
    def find_app(name):
        name = name.lower().strip()
        
        special = {
            'spotify': [
                os.path.join(os.environ.get('APPDATA', ''), 'Spotify', 'Spotify.exe'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Spotify', 'Spotify.exe'),
                os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Spotify', 'Spotify.exe'),
            ],
            'steam': [
                os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'), 'Steam', 'Steam.exe'),
                os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Steam', 'Steam.exe'),
            ],
            'discord': [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Discord', 'Discord.exe'),
                os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Discord', 'Discord.exe'),
            ],
            'vscode': [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Microsoft VS Code', 'Code.exe'),
            ],
            'teams': [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Teams', 'Teams.exe'),
                os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Microsoft', 'Teams', 'Teams.exe'),
            ],
            'browser': [
                os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Google\\Chrome\\Application\\chrome.exe'),
            ],
            'chrome': [
                os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Google\\Chrome\\Application\\chrome.exe'),
            ],
        }
        
        if name in special:
            for path in special[name]:
                if os.path.exists(path):
                    return path
        
        system = {
            'notepad': 'notepad.exe', 'calculator': 'calc.exe',
            'cmd': 'cmd.exe', 'terminal': 'cmd.exe',
            'powershell': 'powershell.exe',
            'explorer': 'explorer.exe', 'taskmgr': 'taskmgr.exe',
            'control': 'control.exe', 'mspaint': 'mspaint.exe',
            'paint': 'mspaint.exe',
        }
        
        if name in system:
            return system[name]
        
        return None


class VoiceWorker(QThread):
    recognized = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        self.rec = sr.Recognizer()
        self.rec.energy_threshold = 4000
        self.rec.dynamic_energy_threshold = True
        self.running = False
        try:
            self.mic = sr.Microphone()
        except:
            self.mic = None
    
    def run(self):
        if not self.mic: return
        self.running = True
        with self.mic as s:
            self.rec.adjust_for_ambient_noise(s, duration=1)
        while self.running:
            try:
                with self.mic as s:
                    audio = self.rec.listen(s, timeout=1, phrase_time_limit=10)
                    try:
                        t = self.rec.recognize_google(audio, language="ru-RU")
                        if t: 
                            self.recognized.emit(t.lower(), "ru")
                            continue
                    except: 
                        pass
                    try:
                        t = self.rec.recognize_google(audio, language="en-US")
                        if t: 
                            self.recognized.emit(t.lower(), "en")
                    except: 
                        pass
            except sr.WaitTimeoutError: 
                continue
            except: 
                time.sleep(0.5)
    
    def stop(self):
        self.running = False


class SpeechWorker(QThread):
    started = pyqtSignal()
    finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.eng = pyttsx3.init()
        self.eng.setProperty('rate', config.get("speed", 160))
        self.eng.setProperty('volume', config.get("volume", 0.9))
        self.q = []
        self.should_stop = False
    
    def run(self):
        while True:
            if self.should_stop:
                self.eng.stop()
                self.should_stop = False
                continue
            if self.q:
                t, l = self.q.pop(0)
                self.started.emit()
                self.eng.setProperty('rate', config.get("speed", 160))
                self.eng.setProperty('volume', config.get("volume", 0.9))
                self.eng.say(t)
                self.eng.runAndWait()
                self.finished.emit()
            else:
                time.sleep(0.1)
    
    def speak(self, t, l="en"):
        self.q.append((t, l))
    
    def stop_speaking(self):
        self.should_stop = True
        self.eng.stop()


class AIWorker(QThread):
    ready = pyqtSignal(str, str)
    shutdown_requested = pyqtSignal()
    
    def process(self, t, l):
        self.t = t
        self.l = l
        self.start()
    
    def run(self):
        time.sleep(0.3)
        r = self.get_response(self.t, self.l)
        self.ready.emit(r, self.l)
    
    def open_app_safe(self, name):
        path = AppFinder.find_app(name)
        if path:
            try:
                subprocess.Popen(path, shell=True)
                return True
            except:
                pass
        return False
    
    def execute_command(self, command_key):
        cmd = config["commands"].get(command_key, {})
        if not cmd.get("enabled", True):
            return None
        
        apps_list = []
        
        for app in cmd.get("apps", []):
            if self.open_app_safe(app):
                apps_list.append(app.capitalize())
        
        for url in cmd.get("urls", []):
            if url.strip():
                webbrowser.open(url.strip())
                from urllib.parse import urlparse
                parsed = urlparse(url.strip())
                apps_list.append(parsed.netloc or url.strip())
        
        return apps_list
    
    def find_custom_command(self, text):
        for cmd in config.get("custom_commands", []):
            phrase = cmd.get("phrase", "").lower()
            if phrase and phrase in text:
                return cmd
        return None
    
    def move_window_to_other_monitor(self):
        try:
            if SYSTEM == "Windows":
                try:
                    import win32gui
                    import win32con
                    hwnd = win32gui.GetForegroundWindow()
                    if hwnd:
                        win32gui.SetWindowPos(hwnd, None, 2000, 300, 800, 600, win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)
                        return True
                except:
                    pyautogui.hotkey('win', 'shift', 'left')
                    return True
            return False
        except:
            return False
    
    def change_volume(self, delta):
        try:
            if SYSTEM == "Windows":
                for _ in range(abs(delta)):
                    if delta > 0:
                        pyautogui.press('volumeup')
                    else:
                        pyautogui.press('volumedown')
                return True
            elif SYSTEM == "Darwin":
                for _ in range(abs(delta)):
                    if delta > 0:
                        pyautogui.hotkey('volumeup')
                    else:
                        pyautogui.hotkey('volumedown')
                return True
            return False
        except:
            return False
    
    def change_keyboard_language(self):
        try:
            if SYSTEM == "Windows":
                pyautogui.hotkey('alt', 'shift')
                return True
            elif SYSTEM == "Darwin":
                pyautogui.hotkey('cmd', 'space')
                return True
            return False
        except:
            return False
    
    def empty_recycle_bin(self):
        try:
            if SYSTEM == "Windows":
                result = subprocess.run(
                    ['powershell', '-command', 'Clear-RecycleBin -Force'],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
            elif SYSTEM == "Darwin":
                subprocess.run(['rm', '-rf', os.path.expanduser('~/.Trash/*')], shell=True)
                return True
            return False
        except:
            return False
    
    def minimize_all_windows(self):
        try:
            if SYSTEM == "Windows":
                import ctypes
                ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)
                ctypes.windll.user32.keybd_event(0x44, 0, 0, 0)
                ctypes.windll.user32.keybd_event(0x44, 0, 2, 0)
                ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)
                return True
            elif SYSTEM == "Darwin":
                pyautogui.hotkey('command', 'm')
                return True
            else:
                subprocess.run(['xdotool', 'key', 'super+d'])
                return True
        except:
            try:
                pyautogui.hotkey('win', 'd')
                return True
            except:
                return False
    
    def restore_all_windows(self):
        try:
            if SYSTEM == "Windows":
                import ctypes
                ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)
                ctypes.windll.user32.keybd_event(0x44, 0, 0, 0)
                ctypes.windll.user32.keybd_event(0x44, 0, 2, 0)
                ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)
                return True
            elif SYSTEM == "Darwin":
                pyautogui.hotkey('command', 'm')
                return True
            else:
                subprocess.run(['xdotool', 'key', 'super+d'])
                return True
        except:
            try:
                pyautogui.hotkey('win', 'd')
                return True
            except:
                return False
    
    def get_response(self, text, lang):
        c = text.lower()
        username = config.get("username", "user")
        
        custom_cmd = self.find_custom_command(c)
        if custom_cmd:
            results = []
            if custom_cmd.get("app_path"):
                try:
                    subprocess.Popen(custom_cmd["app_path"], shell=True)
                    results.append(os.path.basename(custom_cmd["app_path"]))
                except:
                    pass
            if custom_cmd.get("url"):
                webbrowser.open(custom_cmd["url"])
                results.append(custom_cmd["url"])
            
            if results:
                response = f"{tr('opened')}:\n" + "\n".join(f"- {r}" for r in results)
                return response
            return tr("command_executed")
        
        silence_words = ["silence", "shut up", "замолчи", "молчи", "тихо", "заткнись"]
        speak_words = ["speak", "listen", "wake up", "говори", "проснись", "слушай"]
        shutdown_words = ["shut down", "shutdown", "turn off", "power off", "выключи компьютер", "выключи пк"]
        comp_school_words = ["computer school", "comp school", "компьютерная школа"]
        school_words = ["school", "classes", "школа", "уроки"]
        minimize_words = ["minimize all", "hide windows", "show desktop", "сверни все окна", "сверни окна", "покажи рабочий стол"]
        restore_words = ["restore windows", "show windows", "разверни окна", "покажи окна"]
        hello_words = ["hello", "hi", "hey", "dzhenya", "привет", "здравствуй"]
        here_words = ["i'm here", "im here", "я пришёл", "я пришел", "я пришла", "я тут"]
        tired_words = ["i'm tired", "im tired", "я устал", "я устала", "хочу отдохнуть"]
        time_words = ["time", "clock", "время", "который час"]
        date_words = ["date", "day", "дата", "число", "какой день"]
        open_words = ["open", "launch", "start", "run", "открой", "запусти", "старт"]
        search_words = ["search", "find", "google", "найди", "поищи", "погугли"]
        weather_words = ["weather", "погода"]
        joke_words = ["joke", "шутка", "анекдот"]
        thank_words = ["thank", "спасибо", "благодарю"]
        bye_words = ["bye", "goodbye", "пока", "до свидания"]
        move_monitor_words = ["move to other monitor", "move to second monitor", "перенеси на другой монитор", "на второй монитор"]
        empty_trash_words = ["empty trash", "clear recycle bin", "очисти корзину", "удали из корзины"]
        
        volume_pattern = r"(increase|raise|up|повысь|увеличь).*?(\d+)"
        volume_match = re.search(volume_pattern, c)
        if volume_match:
            amount = int(volume_match.group(2))
            amount = min(amount, 20)
            if self.change_volume(amount):
                return tr("volume_increased").format(amount)
            return tr("volume_error")
        
        volume_down_pattern = r"(decrease|lower|down|уменьши|понизь).*?(\d+)"
        volume_down_match = re.search(volume_down_pattern, c)
        if volume_down_match:
            amount = int(volume_down_match.group(2))
            amount = min(amount, 20)
            if self.change_volume(-amount):
                return tr("volume_decreased").format(amount)
            return tr("volume_error")
        
        language_words = ["change language", "switch language", "смени язык", "поменяй язык"]
        if any(w in c for w in language_words):
            if self.change_keyboard_language():
                return tr("language_changed")
            return tr("language_error")
        
        if any(w in c for w in move_monitor_words):
            if self.move_window_to_other_monitor():
                return tr("move_to_other_monitor")
            return tr("move_monitor_error")
        
        if any(w in c for w in empty_trash_words):
            if self.empty_recycle_bin():
                return tr("trash_cleared")
            return tr("trash_error")
        
        if any(w in c for w in minimize_words):
            if self.minimize_all_windows():
                return tr("windows_minimized")
            return "Failed to minimize windows"
        
        if any(w in c for w in restore_words):
            if self.restore_all_windows():
                return tr("windows_restored")
            return "Failed to restore windows"
        
        if any(w in c for w in silence_words):
            config["silent_mode"] = True
            save_config(config)
            return ""
        
        if any(w in c for w in speak_words):
            config["silent_mode"] = False
            save_config(config)
            return tr("silent_off")
        
        if config.get("silent_mode", False):
            return ""
        
        if any(w in c for w in shutdown_words):
            self.shutdown_requested.emit()
            return ""
        
        if any(w in c for w in comp_school_words):
            apps = self.execute_command("computer_school")
            if apps:
                return f"{tr('computer_school_mode')}\n\n" + "\n".join(f"- {a}" for a in apps)
            return tr("command_disabled")
        
        if any(w in c for w in school_words):
            apps = self.execute_command("school")
            if apps:
                return f"{tr('school_mode')}\n\n" + "\n".join(f"- {a}" for a in apps)
            return tr("command_disabled")
        
        if any(w in c for w in hello_words):
            return f"{tr('hello_response')}, {username}."
        
        if any(w in c for w in here_words):
            apps = self.execute_command("im_here")
            if apps:
                return f"{tr('welcome_back')}\n\n" + "\n".join(f"- {a}" for a in apps)
            return tr("command_disabled")
        
        if any(w in c for w in tired_words):
            apps = self.execute_command("im_tired")
            if apps:
                return f"{tr('time_to_relax')}\n\n" + "\n".join(f"- {a}" for a in apps)
            return tr("command_disabled")
        
        if any(w in c for w in time_words):
            now = datetime.now()
            return f"{tr('time')} {now.strftime('%H:%M:%S')}"
        
        if any(w in c for w in date_words):
            now = datetime.now()
            months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
            return f"{months[now.month-1]} {now.day}, {now.year}"
        
        if any(w in c for w in open_words):
            app = c
            for w in open_words + ["please", "пожалуйста"]:
                app = app.replace(w, "")
            app = app.strip()
            
            if not app:
                return tr("which_app")
            
            if self.open_app_safe(app):
                return f"{tr('opening')} {app}"
            return f"{tr('cannot_find')} {app}"
        
        if any(w in c for w in search_words):
            q = c
            for w in search_words + ["for", "в интернете"]:
                q = q.replace(w, "")
            q = q.strip()
            if q:
                webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(q)}")
                return f"{tr('searching')} {q}"
        
        if any(w in c for w in weather_words):
            webbrowser.open("https://www.google.com/search?q=weather+now")
            return tr("weather")
        
        if any(w in c for w in joke_words):
            return random.choice([
                "Why do programmers confuse Halloween and Christmas? Because 31 OCT equals 25 DEC!",
                "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
                "Why is Python so popular? Because it doesn't byte, it just snakes around!",
                "Why do programmers prefer dark mode? Because light attracts bugs!",
                "What's a programmer's favorite hangout place? The Foo Bar!",
            ])
        
        if any(w in c for w in thank_words):
            return tr("youre_welcome")
        
        if any(w in c for w in bye_words):
            return tr("goodbye")
        
        if self.open_app_safe(c):
            return f"{tr('opening')} {c}"
        
        webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(c)}")
        return f"{tr('searching')} {text}"


class DzhenyaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle(tr("app_name"))
        self.setMinimumSize(950, 650)
        self.resize(1050, 700)
        
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width()-1050)//2, (screen.height()-700)//2)
        
        self.listening = False
        self.speaking = False
        
        self.voice_worker = VoiceWorker()
        self.speech_worker = SpeechWorker()
        self.ai_worker = AIWorker()
        
        self.voice_worker.recognized.connect(self.on_recognized)
        self.speech_worker.started.connect(self.on_speech_start)
        self.speech_worker.finished.connect(self.on_speech_end)
        self.ai_worker.ready.connect(self.on_response)
        self.ai_worker.shutdown_requested.connect(self.show_shutdown_dialog)
        
        self.voice_worker.start()
        self.speech_worker.start()
        
        self.init_ui()
        self.create_tray()
        
        QTimer.singleShot(600, self.welcome)
    
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        self.setStyleSheet(f"background-color: {Colors.BG_MAIN};")
        
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.sidebar = Sidebar(self)
        layout.addWidget(self.sidebar)
        
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        top = QWidget()
        top.setFixedHeight(48)
        top.setStyleSheet(f"background-color: {Colors.BG_MAIN}; border-bottom: 1px solid {Colors.BORDER};")
        
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(20, 0, 20, 0)
        
        self.page_title = QLabel(tr("chat"))
        self.page_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 14px; font-weight: 500;")
        
        top_layout.addWidget(self.page_title)
        top_layout.addStretch()
        
        right_layout.addWidget(top)
        
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")
        
        chat_page = QWidget()
        chat_layout = QVBoxLayout(chat_page)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)
        
        self.orb = SiriLikeOrb(self)
        chat_layout.addWidget(self.orb, alignment=Qt.AlignCenter)
        
        self.status_label = QLabel(tr("mic_hint"))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; padding: 8px;")
        chat_layout.addWidget(self.status_label)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("background-color: transparent; border: none;")
        self.scroll.verticalScrollBar().setStyleSheet(f"""
            QScrollBar:vertical {{
                background-color: transparent;
                width: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {Colors.BORDER};
                border-radius: 3px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        self.chat_widget = QWidget()
        self.chat_widget.setStyleSheet("background: transparent;")
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(0)
        self.chat_layout.setContentsMargins(0, 8, 0, 8)
        
        self.scroll.setWidget(self.chat_widget)
        chat_layout.addWidget(self.scroll)
        
        bottom = QWidget()
        bottom.setFixedHeight(68)
        bottom.setStyleSheet(f"background-color: {Colors.BG_MAIN}; border-top: 1px solid {Colors.BORDER};")
        
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(20, 10, 20, 10)
        bottom_layout.setSpacing(12)
        
        self.mic_btn = QPushButton("MIC")
        self.mic_btn.setFixedSize(48, 48)
        self.mic_btn.setCursor(Qt.PointingHandCursor)
        self.mic_btn.clicked.connect(self.toggle_listening)
        
        self.stop_btn = QPushButton("STOP")
        self.stop_btn.setFixedSize(48, 48)
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.hide()
        self.stop_btn.clicked.connect(self.stop_speaking)
        
        hint = QLabel('Say "Hello Dzhenya" or "Привет Dzhenya" to start')
        hint.setStyleSheet(f"color: {Colors.TEXT_TERTIARY}; font-size: 11px;")
        
        bottom_layout.addWidget(self.mic_btn)
        bottom_layout.addWidget(self.stop_btn)
        bottom_layout.addWidget(hint)
        bottom_layout.addStretch()
        
        chat_layout.addWidget(bottom)
        
        self.stack.addWidget(chat_page)
        self.stack.addWidget(CommandsPage(self))
        self.stack.addWidget(SettingsPage(self))
        self.stack.addWidget(ProfilePage(self))
        
        right_layout.addWidget(self.stack)
        layout.addWidget(right)
        
        self.update_buttons()
    
    def refresh_ui(self):
        self.setWindowTitle(tr("app_name"))
        self.page_title.setText(tr("chat"))
        self.status_label.setText(tr("mic_hint"))
        
        self.sidebar.update_texts()
        
        current_index = self.stack.currentIndex()
        
        while self.stack.count() > 1:
            widget = self.stack.widget(1)
            self.stack.removeWidget(widget)
            widget.deleteLater()
        
        self.stack.addWidget(CommandsPage(self))
        self.stack.addWidget(SettingsPage(self))
        self.stack.addWidget(ProfilePage(self))
        
        if current_index > 0:
            self.stack.setCurrentIndex(current_index)
        else:
            self.stack.setCurrentIndex(0)
    
    def update_buttons(self):
        self.mic_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.BLUE};
                color: #fff;
                border: none;
                border-radius: 24px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.BLUE_DARK};
            }}
        """)
        
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.RED};
                color: #fff;
                border: none;
                border-radius: 24px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.RED_DARK};
            }}
        """)
    
    def create_tray(self):
        self.tray = QSystemTrayIcon(self)
        pix = QPixmap(64, 64)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        grad = QLinearGradient(12, 12, 52, 52)
        grad.setColorAt(0, QColor(107, 140, 255))
        grad.setColorAt(1, QColor(167, 139, 250))
        p.setBrush(QBrush(grad))
        p.drawEllipse(12, 12, 40, 40)
        p.end()
        self.tray.setIcon(QIcon(pix))
        self.tray.setToolTip(tr("app_name"))
        menu = QMenu()
        menu.addAction("Show", self.show)
        menu.addAction("Exit", self.quit)
        self.tray.setContextMenu(menu)
        self.tray.show()
    
    def quit(self):
        self.voice_worker.stop()
        self.speech_worker.terminate()
        self.tray.hide()
        QApplication.quit()
    
    def closeEvent(self, e):
        e.ignore()
        self.hide()
    
    def welcome(self):
        t = f"{tr('welcome')}, {config.get('username')}."
        self.add_message(t, False)
        self.speech_worker.speak(f"{tr('welcome')}, {config.get('username')}.", "en")
    
    def add_message(self, text, is_user):
        msg = MessageWidget(text, is_user)
        self.chat_layout.addWidget(msg)
        QTimer.singleShot(100, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()))
    
    def show_shutdown_dialog(self):
        dialog = ShutdownDialog(config.get("username"), self)
        if dialog.exec_() == QDialog.Accepted:
            self.add_message(tr("shutting_down"), False)
            self.speech_worker.speak(tr("shutting_down"), "en")
            if SYSTEM == "Windows":
                QTimer.singleShot(3000, lambda: os.system("shutdown /s /t 0"))
            elif SYSTEM == "Darwin":
                QTimer.singleShot(3000, lambda: os.system("osascript -e 'tell app \"System Events\" to shut down'"))
            else:
                QTimer.singleShot(3000, lambda: os.system("shutdown now"))
        else:
            self.add_message(tr("shutdown_cancelled"), False)
    
    def toggle_listening(self):
        if self.listening: self.stop_listening()
        else: self.start_listening()
    
    def start_listening(self):
        self.listening = True
        self.mic_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.RED};
                color: #fff;
                border: none;
                border-radius: 24px;
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        self.orb.set_active(True)
        self.status_label.setText(tr("listening"))
    
    def stop_listening(self):
        self.listening = False
        self.update_buttons()
        self.orb.set_active(False)
        self.status_label.setText(tr("ready"))
    
    def on_recognized(self, text, lang):
        self.add_message(text, True)
        self.orb.set_speaking(True)
        self.ai_worker.process(text, lang)
        self.stop_listening()
    
    def on_response(self, text, lang):
        if text:
            self.add_message(text, False)
            self.speech_worker.speak(text, "en")
        else:
            QTimer.singleShot(400, self.start_listening)
    
    def on_speech_start(self):
        self.speaking = True
        self.stop_btn.show()
        self.mic_btn.hide()
        self.orb.set_speaking(True)
    
    def on_speech_end(self):
        self.speaking = False
        self.stop_btn.hide()
        self.mic_btn.show()
        self.orb.set_speaking(False)
        QTimer.singleShot(400, self.start_listening)
    
    def stop_speaking(self):
        self.speech_worker.stop_speaking()
        self.on_speech_end()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Dzhenya Assistant")
    app.setQuitOnLastWindowClosed(False)
    
    try:
        with sr.Microphone(): pass
    except:
        QMessageBox.critical(None, "Error", tr("no_mic"))
        return
    
    window = DzhenyaApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()