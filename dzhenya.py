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

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".dzhenya")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

def load_config():
    default = {
        "username": os.getlogin(),
        "language": "ru",
        "speed": 160,
        "volume": 0.9,
        "silent_mode": False,
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
                default.update(saved)
        except:
            pass
    return default

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

config = load_config()

class Colors:
    BG_MAIN = "#0D1117"
    BG_SIDEBAR = "#111820"
    BG_CARD = "#161B22"
    BG_HOVER = "#1C2333"
    BG_INPUT = "#1C2128"
    
    BORDER = "#30363D"
    BORDER_LIGHT = "#21262D"
    
    TEXT_PRIMARY = "#E6EDF3"
    TEXT_SECONDARY = "#8B949E"
    TEXT_TERTIARY = "#6E7681"
    
    BLUE = "#58A6FF"
    BLUE_DARK = "#1F6FEB"
    
    GREEN = "#3FB950"
    GREEN_DARK = "#238636"
    
    PURPLE = "#BC8CFF"
    PURPLE_DARK = "#8957E5"
    
    RED = "#F85149"
    RED_DARK = "#DA3633"
    
    ORANGE = "#D29922"
    CYAN = "#39D2C0"


class DzhenyaOrb(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.setMaximumSize(260, 260)
        
        self.active = False
        self.speaking = False
        self.phase = 0
        self.intensity = 0.0
        
        self.particles = []
        for _ in range(35):
            self.particles.append({
                'angle': random.uniform(0, 2*math.pi),
                'dist': random.uniform(35, 95),
                'size': random.uniform(2, 5),
                'speed': random.uniform(0.3, 1.5),
                'color': random.choice([Colors.BLUE, Colors.PURPLE, Colors.GREEN, Colors.CYAN])
            })
        
        self.waves = []
        for _ in range(4):
            self.waves.append({
                'radius': 0,
                'max_r': random.uniform(60, 120),
                'speed': random.uniform(0.4, 1.2),
                'opacity': 0,
                'color': random.choice([Colors.BLUE, Colors.PURPLE, Colors.GREEN, Colors.CYAN])
            })
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_anim)
        self.timer.start(16)
    
    def update_anim(self):
        self.phase += 0.04
        
        if self.active or self.speaking:
            self.intensity = min(1.0, self.intensity + 0.02)
        else:
            self.intensity = max(0.0, self.intensity - 0.015)
        
        for p in self.particles:
            p['angle'] += 0.012 * p['speed']
        
        for w in self.waves:
            if self.active or self.speaking:
                w['radius'] = min(w['max_r'], w['radius'] + w['speed'] * 3)
                w['opacity'] = min(0.5, w['opacity'] + 0.02)
            else:
                w['radius'] = max(0, w['radius'] - w['speed'] * 5)
                w['opacity'] = max(0, w['opacity'] - 0.03)
            
            if w['radius'] >= w['max_r']:
                w['radius'] = 0
                w['max_r'] = random.uniform(60, 120)
        
        self.update()
    
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w/2, h/2
        
        p.fillRect(self.rect(), QColor(Colors.BG_MAIN))
        
        if self.intensity > 0.01:
            for wave in self.waves:
                if wave['opacity'] > 0.01:
                    c = QColor(wave['color'])
                    c.setAlpha(int(200 * wave['opacity'] * self.intensity))
                    
                    pen = QPen(c, 1.5)
                    p.setPen(pen)
                    p.setBrush(Qt.NoBrush)
                    p.drawEllipse(QPointF(cx, cy), wave['radius'] * self.intensity, wave['radius'] * self.intensity)
        
        r = 32 + 14 * self.intensity
        if self.speaking:
            r += 6 * math.sin(self.phase * 5)
        
        grad = QRadialGradient(cx - r*0.2, cy - r*0.35, r * 1.8)
        
        if self.speaking:
            grad.setColorAt(0, QColor(160, 190, 255))
            grad.setColorAt(0.3, QColor(139, 87, 229))
            grad.setColorAt(0.6, QColor(56, 139, 253))
            grad.setColorAt(1, QColor(46, 160, 67))
        elif self.active:
            grad.setColorAt(0, QColor(140, 175, 255))
            grad.setColorAt(0.5, QColor(56, 139, 253))
            grad.setColorAt(1, QColor(31, 111, 235))
        else:
            grad.setColorAt(0, QColor(100, 140, 220))
            grad.setColorAt(0.5, QColor(56, 139, 253))
            grad.setColorAt(1, QColor(25, 80, 200))
        
        p.setBrush(QBrush(grad))
        p.setPen(QPen(QColor(255, 255, 255, 20), 1))
        p.drawEllipse(QPointF(cx, cy), r, r)
        
        hl = QRadialGradient(cx - r*0.35, cy - r*0.45, r*0.5)
        hl.setColorAt(0, QColor(255, 255, 255, 60))
        hl.setColorAt(1, QColor(255, 255, 255, 0))
        
        p.setBrush(QBrush(hl))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx, cy), r - 2, r - 2)
        
        if self.intensity > 0.25:
            for pt in self.particles:
                px = cx + pt['dist'] * math.cos(pt['angle']) * self.intensity
                py = cy + pt['dist'] * math.sin(pt['angle']) * self.intensity
                
                dist = math.sqrt((px-cx)**2 + (py-cy)**2)
                if dist > r + 10:
                    c = QColor(pt['color'])
                    c.setAlpha(int(150 * (0.3 + 0.7 * abs(math.sin(self.phase * pt['speed']))) * self.intensity))
                    
                    p.setBrush(QBrush(c))
                    p.setPen(Qt.NoPen)
                    size = pt['size'] * self.intensity
                    p.drawEllipse(QPointF(px, py), size, size)
    
    def set_active(self, a):
        self.active = a
    
    def set_speaking(self, s):
        self.speaking = s


class ShutdownDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.setWindowTitle("Dzhenya")
        self.setFixedSize(450, 250)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Colors.BG_CARD};
                border: 1px solid {Colors.BORDER};
                border-radius: 16px;
            }}
        """)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        icon = QLabel("!")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedSize(50, 50)
        icon.setStyleSheet(f"""
            QLabel {{
                background-color: {Colors.RED};
                color: #fff;
                border-radius: 25px;
                font-size: 28px;
                font-weight: bold;
            }}
        """)
        
        title = QLabel(f"{self.username}, shut down the computer?")
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 15px; background: transparent;")
        
        sub = QLabel("All unsaved work will be lost.")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {Colors.BG_HOVER};
                border-color: {Colors.BLUE}44;
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        
        confirm_btn = QPushButton("Shut Down")
        confirm_btn.setCursor(Qt.PointingHandCursor)
        confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.RED};
                color: #fff;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
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
                    background: {Colors.BLUE};
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
                        stop:0 {Colors.BLUE}, stop:0.5 {Colors.PURPLE}, stop:1 {Colors.GREEN});
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
        
        name = QLabel("You" if self.is_user else "Dzhenya")
        name.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px; font-weight: 500; background: transparent; padding: 0 2px;")
        
        msg = QLabel(self.text)
        msg.setWordWrap(True)
        msg.setMaximumWidth(520)
        msg.setTextFormat(Qt.RichText)
        msg.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 14px; line-height: 1.5; background: transparent; padding: 2px;")
        
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
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 16, 10, 16)
        layout.setSpacing(4)
        
        self.setStyleSheet(f"background-color: {Colors.BG_SIDEBAR}; border-right: 1px solid {Colors.BORDER_LIGHT};")
        
        logo = QLabel("Dzhenya Assistant")
        logo.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 18px; font-weight: 500; background: transparent; padding: 8px;")
        layout.addWidget(logo)
        
        layout.addSpacing(16)
        
        new_btn = QPushButton("New Chat")
        new_btn.setCursor(Qt.PointingHandCursor)
        new_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.BG_CARD};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 20px;
                padding: 10px 16px;
                font-size: 13px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {Colors.BG_HOVER};
                border-color: {Colors.BLUE}44;
            }}
        """)
        new_btn.clicked.connect(self.new_chat)
        layout.addWidget(new_btn)
        
        layout.addSpacing(20)
        
        nav = [
            ("Chat", self.show_chat),
            ("Commands", self.show_commands),
            ("Settings", self.show_settings),
            ("Profile", self.show_profile),
        ]
        
        for text, handler in nav:
            btn = QPushButton(text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {Colors.TEXT_SECONDARY};
                    border: none;
                    border-radius: 10px;
                    padding: 10px 14px;
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
        
        layout.addStretch()
        
        profile = QWidget()
        profile.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BG_CARD};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
            }}
        """)
        
        p_layout = QHBoxLayout(profile)
        p_layout.setContentsMargins(12, 10, 12, 10)
        p_layout.setSpacing(10)
        
        av = QLabel(config.get("username", "U")[0].upper())
        av.setFixedSize(32, 32)
        av.setAlignment(Qt.AlignCenter)
        av.setStyleSheet(f"background: {Colors.PURPLE}; border-radius: 16px; color: #fff; font-size: 13px; font-weight: 600;")
        
        nm = QLabel(config.get("username", "User"))
        nm.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; background: transparent;")
        
        p_layout.addWidget(av)
        p_layout.addWidget(nm)
        p_layout.addStretch()
        
        layout.addWidget(profile)
    
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
    
    def show_commands(self):
        if self.parent_window:
            self.parent_window.stack.setCurrentIndex(1)
    
    def show_settings(self):
        if self.parent_window:
            self.parent_window.stack.setCurrentIndex(2)
    
    def show_profile(self):
        if self.parent_window:
            self.parent_window.stack.setCurrentIndex(3)


AVAILABLE_APPS = [
    "spotify",
    "steam",
    "discord",
    "vscode",
    "teams",
    "browser",
    "chrome",
    "notepad",
    "calculator",
    "cmd",
    "powershell",
    "explorer",
    "paint",
]


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
        scroll.setStyleSheet(f"background-color: {Colors.BG_MAIN}; border: none;")
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(48, 32, 48, 32)
        layout.setSpacing(24)
        
        title = QLabel("Commands Settings")
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 26px; font-weight: 500; background: transparent;")
        layout.addWidget(title)
        
        self.im_here_section = self.create_command_section("I'm here", "im_here")
        layout.addWidget(self.im_here_section)
        
        self.im_tired_section = self.create_command_section("I'm tired", "im_tired")
        layout.addWidget(self.im_tired_section)
        
        self.comp_school_section = self.create_command_section("Computer school", "computer_school")
        layout.addWidget(self.comp_school_section)
        
        self.school_section = self.create_command_section("School", "school")
        layout.addWidget(self.school_section)
        
        layout.addStretch()
        
        save_btn = QPushButton("Save All Commands")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.GREEN};
                color: #fff;
                border: none;
                border-radius: 20px;
                padding: 14px 24px;
                font-size: 15px;
                font-weight: 500;
            }}
            QPushButton:hover {{ background-color: {Colors.GREEN_DARK}; }}
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
        section.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BG_CARD};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        
        s_layout = QVBoxLayout(section)
        s_layout.setSpacing(14)
        
        header_layout = QHBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 18px; font-weight: 500; background: transparent;")
        
        self.__dict__[f"{command_key}_enabled"] = QCheckBox("Enabled")
        self.__dict__[f"{command_key}_enabled"].setChecked(cmd.get("enabled", True))
        self.__dict__[f"{command_key}_enabled"].setCursor(Qt.PointingHandCursor)
        self.__dict__[f"{command_key}_enabled"].setStyleSheet(f"""
            QCheckBox {{
                color: {Colors.TEXT_PRIMARY};
                font-size: 14px;
                background: transparent;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {Colors.BORDER};
                border-radius: 4px;
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
        
        s_layout.addLayout(header_layout)
        
        apps_label = QLabel("Applications:")
        apps_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; font-weight: 500; background: transparent; margin-top: 8px;")
        s_layout.addWidget(apps_label)
        
        apps_container = QWidget()
        apps_container.setStyleSheet("background: transparent;")
        apps_layout = QVBoxLayout(apps_container)
        apps_layout.setSpacing(6)
        
        selected_apps = cmd.get("apps", [])
        self.__dict__[f"{command_key}_apps"] = {}
        
        for app in AVAILABLE_APPS:
            cb = QCheckBox(app.capitalize())
            cb.setChecked(app in selected_apps)
            cb.setCursor(Qt.PointingHandCursor)
            cb.setStyleSheet(f"""
                QCheckBox {{
                    color: {Colors.TEXT_SECONDARY};
                    font-size: 13px;
                    background: transparent;
                    padding: 4px 0;
                }}
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
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
        
        s_layout.addWidget(apps_container)
        
        urls_label = QLabel("URLs (one per line):")
        urls_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; font-weight: 500; background: transparent; margin-top: 8px;")
        s_layout.addWidget(urls_label)
        
        self.__dict__[f"{command_key}_urls"] = QTextEdit()
        self.__dict__[f"{command_key}_urls"].setPlainText("\n".join(cmd.get("urls", [])))
        self.__dict__[f"{command_key}_urls"].setMaximumHeight(80)
        self.__dict__[f"{command_key}_urls"].setStyleSheet(f"""
            QTextEdit {{
                background-color: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }}
            QTextEdit:focus {{
                border-color: {Colors.BLUE};
            }}
        """)
        s_layout.addWidget(self.__dict__[f"{command_key}_urls"])
        
        return section
    
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
        QMessageBox.information(self, "Saved", "All commands saved successfully!")


class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet(f"background-color: {Colors.BG_MAIN};")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 32, 48, 32)
        layout.setSpacing(20)
        
        title = QLabel("Settings")
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 26px; font-weight: 500; background: transparent;")
        layout.addWidget(title)
        
        general = self.create_section("General")
        g_layout = general.layout()
        
        self.name_input = QLineEdit(config.get("username"))
        self.name_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
            }}
            QLineEdit:focus {{ border-color: {Colors.BLUE}; }}
        """)
        g_layout.addWidget(self.create_row("Name", self.name_input))
        
        layout.addWidget(general)
        
        voice = self.create_section("Voice")
        v_layout = voice.layout()
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(100, 250)
        self.speed_slider.setValue(config.get("speed", 160))
        self.speed_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{ height: 4px; background: {Colors.BORDER}; border-radius: 2px; }}
            QSlider::handle:horizontal {{ background: {Colors.BLUE}; width: 16px; height: 16px; margin: -6px 0; border-radius: 8px; }}
        """)
        self.speed_val = QLabel(str(config.get("speed", 160)))
        self.speed_val.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 14px; background: transparent;")
        self.speed_slider.valueChanged.connect(lambda v: self.speed_val.setText(str(v)))
        
        sw = QWidget()
        sw.setStyleSheet("background: transparent;")
        sl = QHBoxLayout(sw)
        sl.addWidget(self.speed_slider)
        sl.addWidget(self.speed_val)
        v_layout.addWidget(self.create_row("Speed", sw))
        
        self.vol_slider = QSlider(Qt.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(int(config.get("volume", 0.9) * 100))
        self.vol_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{ height: 4px; background: {Colors.BORDER}; border-radius: 2px; }}
            QSlider::handle:horizontal {{ background: {Colors.GREEN}; width: 16px; height: 16px; margin: -6px 0; border-radius: 8px; }}
        """)
        self.vol_val = QLabel(str(int(config.get("volume", 0.9) * 100)))
        self.vol_val.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 14px; background: transparent;")
        self.vol_slider.valueChanged.connect(lambda v: self.vol_val.setText(str(v)))
        
        vw = QWidget()
        vw.setStyleSheet("background: transparent;")
        vl = QHBoxLayout(vw)
        vl.addWidget(self.vol_slider)
        vl.addWidget(self.vol_val)
        v_layout.addWidget(self.create_row("Volume", vw))
        
        layout.addWidget(voice)
        
        layout.addStretch()
        
        save_btn = QPushButton("Save Settings")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.GREEN};
                color: #fff;
                border: none;
                border-radius: 20px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{ background-color: {Colors.GREEN_DARK}; }}
        """)
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)
    
    def create_section(self, title):
        w = QWidget()
        w.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BG_CARD};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        
        l = QVBoxLayout(w)
        l.setSpacing(14)
        
        t = QLabel(title)
        t.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 16px; font-weight: 500; background: transparent;")
        l.addWidget(t)
        
        return w
    
    def create_row(self, label, widget):
        r = QWidget()
        r.setStyleSheet("background: transparent;")
        rl = QHBoxLayout(r)
        rl.setContentsMargins(0, 0, 0, 0)
        
        lb = QLabel(label)
        lb.setFixedWidth(100)
        lb.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px; background: transparent;")
        
        rl.addWidget(lb)
        rl.addWidget(widget)
        rl.addStretch()
        
        return r
    
    def save(self):
        config["username"] = self.name_input.text()
        config["speed"] = self.speed_slider.value()
        config["volume"] = self.vol_slider.value() / 100
        save_config(config)
        QMessageBox.information(self, "Saved", "Settings saved successfully!")


class ProfilePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet(f"background-color: {Colors.BG_MAIN};")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 32, 48, 32)
        layout.setSpacing(20)
        
        title = QLabel("Profile")
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 26px; font-weight: 500; background: transparent;")
        layout.addWidget(title)
        
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BG_CARD};
                border: 1px solid {Colors.BORDER};
                border-radius: 16px;
                padding: 32px;
            }}
        """)
        
        c_layout = QVBoxLayout(card)
        c_layout.setAlignment(Qt.AlignCenter)
        c_layout.setSpacing(14)
        
        av = QLabel(config.get("username", "U")[0].upper())
        av.setFixedSize(80, 80)
        av.setAlignment(Qt.AlignCenter)
        av.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {Colors.BLUE}, stop:0.5 {Colors.PURPLE}, stop:1 {Colors.GREEN});
                border-radius: 40px;
                color: #fff;
                font-size: 34px;
                font-weight: 500;
            }}
        """)
        
        name = QLabel(config.get("username", "User"))
        name.setAlignment(Qt.AlignCenter)
        name.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 22px; font-weight: 500; background: transparent;")
        
        c_layout.addWidget(av, alignment=Qt.AlignCenter)
        c_layout.addWidget(name, alignment=Qt.AlignCenter)
        
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
            'visual studio code': [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Microsoft VS Code', 'Code.exe'),
            ],
            'teams': [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Teams', 'Teams.exe'),
                os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Microsoft', 'Teams', 'Teams.exe'),
            ],
            'microsoft teams': [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Teams', 'Teams.exe'),
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
                        if t: self.recognized.emit(t.lower(), "ru"); continue
                    except: pass
                    try:
                        t = self.rec.recognize_google(audio, language="en-US")
                        if t: self.recognized.emit(t.lower(), "en")
                    except: pass
            except sr.WaitTimeoutError: continue
            except: time.sleep(0.5)
    
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
    
    def run(self):
        while True:
            if self.q:
                t, l = self.q.pop(0)
                self.started.emit()
                self.eng.setProperty('rate', config.get("speed", 160))
                self.eng.setProperty('volume', config.get("volume", 0.9))
                self.eng.say(t.replace('*','').replace('#',''))
                self.eng.runAndWait()
                self.finished.emit()
            else:
                time.sleep(0.1)
    
    def speak(self, t, l="ru"):
        self.q.append((t, l))


class AIWorker(QThread):
    ready = pyqtSignal(str, str)
    step = pyqtSignal(str)
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
    
    def get_response(self, text, lang):
        c = text.lower()
        username = config.get("username", "user")
        
        if any(w in c for w in ["замолчи","молчи","тихо","shut up","silence"]):
            config["silent_mode"] = True
            save_config(config)
            return "Silent mode activated."
        
        if any(w in c for w in ["говори","проснись","speak","listen","wake up"]):
            config["silent_mode"] = False
            save_config(config)
            return "Listening again."
        
        if config.get("silent_mode", False):
            return ""
        
        if any(w in c for w in ["выключи компьютер","выключить компьютер","выключи пк","shut down","shutdown","turn off","power off"]):
            self.shutdown_requested.emit()
            return ""
        
        if any(w in c for w in ["компьютерная школа","computer school","comp school"]):
            apps = self.execute_command("computer_school")
            if apps:
                return "Computer school mode.\n\n" + "\n".join(f"- {a}" for a in apps)
            return "Command is disabled."
        
        if any(w in c for w in ["школа","school","уроки","classes"]):
            apps = self.execute_command("school")
            if apps:
                return "School mode.\n\n" + "\n".join(f"- {a}" for a in apps)
            return "Command is disabled."
        
        if any(w in c for w in ["сверни все окна","сверни окна","minimize all","hide windows"]):
            pyautogui.hotkey('win', 'd')
            return "All windows minimized."
        
        if any(w in c for w in ["разверни все окна","разверни окна","restore windows","show windows"]):
            pyautogui.hotkey('win', 'd')
            return "Windows restored."
        
        if any(w in c for w in ["привет","здравствуй","dzhenya","hello","hi","hey"]):
            return f"Hello, {username}."
        
        if any(w in c for w in ["я пришёл","я пришел","я пришла","im here","i'm here"]):
            apps = self.execute_command("im_here")
            if apps:
                return "Welcome back.\n\n" + "\n".join(f"- {a}" for a in apps)
            return "Command is disabled."
        
        if any(w in c for w in ["я устал","я устала","im tired","i'm tired"]):
            apps = self.execute_command("im_tired")
            if apps:
                return "Time to relax.\n\n" + "\n".join(f"- {a}" for a in apps)
            return "Command is disabled."
        
        if any(w in c for w in ["время","time","clock"]):
            now = datetime.now()
            return f"Time: {now.strftime('%H:%M:%S')}"
        
        if any(w in c for w in ["дата","date","day"]):
            now = datetime.now()
            months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
            return f"{months[now.month-1]} {now.day}, {now.year}"
        
        if any(w in c for w in ["открой","open","launch","start","run"]):
            app = c
            for w in ["открой","open","launch","start","run","please"]:
                app = app.replace(w, "")
            app = app.strip()
            
            if not app:
                return "Which application?"
            
            if self.open_app_safe(app):
                return f"Opening {app}"
            return f"Cannot find {app}"
        
        if any(w in c for w in ["найди","search","find","google"]):
            q = c
            for w in ["найди","search","find","google","for"]:
                q = q.replace(w, "")
            q = q.strip()
            if q:
                webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(q)}")
                return f"Searching for {q}"
        
        if any(w in c for w in ["погода","weather"]):
            webbrowser.open("https://www.google.com/search?q=weather+now")
            return "Opening weather"
        
        if any(w in c for w in ["шутка","joke"]):
            return random.choice([
                "Why do programmers confuse Halloween and Christmas? 31 OCT = 25 DEC!",
                "How many programmers to change a light bulb? None, it's a hardware problem!",
                "Why is Python so popular? It doesn't bite!",
            ])
        
        if any(w in c for w in ["спасибо","thank"]):
            return "You're welcome."
        
        if any(w in c for w in ["пока","bye","goodbye"]):
            return "Goodbye."
        
        if self.open_app_safe(c):
            return f"Opening {c}"
        
        webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(c)}")
        return f"Searching for {text}"


class DzhenyaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Dzhenya Assistant")
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
        top.setStyleSheet(f"background-color: {Colors.BG_MAIN}; border-bottom: 1px solid {Colors.BORDER_LIGHT};")
        
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(20, 0, 20, 0)
        
        self.page_title = QLabel("Chat")
        self.page_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 14px; font-weight: 400; background: transparent;")
        
        top_layout.addWidget(self.page_title)
        top_layout.addStretch()
        
        right_layout.addWidget(top)
        
        self.stack = QStackedWidget()
        
        chat_page = QWidget()
        chat_layout = QVBoxLayout(chat_page)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)
        
        self.orb = DzhenyaOrb(self)
        chat_layout.addWidget(self.orb, alignment=Qt.AlignCenter)
        
        self.status_label = QLabel("Press microphone and speak")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; padding: 8px; background: transparent;")
        chat_layout.addWidget(self.status_label)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(f"background-color: {Colors.BG_MAIN}; border: none;")
        
        self.chat_widget = QWidget()
        self.chat_widget.setStyleSheet(f"background-color: {Colors.BG_MAIN};")
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(0)
        self.chat_layout.setContentsMargins(0, 8, 0, 8)
        
        self.scroll.setWidget(self.chat_widget)
        chat_layout.addWidget(self.scroll)
        
        bottom = QWidget()
        bottom.setFixedHeight(68)
        bottom.setStyleSheet(f"background-color: {Colors.BG_MAIN}; border-top: 1px solid {Colors.BORDER_LIGHT};")
        
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(20, 10, 20, 10)
        bottom_layout.setSpacing(12)
        
        self.mic_btn = QPushButton("mic")
        self.mic_btn.setFixedSize(48, 48)
        self.mic_btn.setCursor(Qt.PointingHandCursor)
        self.mic_btn.clicked.connect(self.toggle_listening)
        
        self.stop_btn = QPushButton("stop")
        self.stop_btn.setFixedSize(48, 48)
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.hide()
        self.stop_btn.clicked.connect(self.stop_speaking)
        
        hint = QLabel("\"Hello Dzhenya\", \"Computer school\", \"Shut down\"")
        hint.setStyleSheet(f"color: {Colors.TEXT_TERTIARY}; font-size: 12px; background: transparent;")
        
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
    
    def update_buttons(self):
        self.mic_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.BLUE};
                color: #fff;
                border: none;
                border-radius: 24px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {Colors.BLUE_DARK}; }}
        """)
        
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.RED};
                color: #fff;
                border: none;
                border-radius: 24px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {Colors.RED_DARK}; }}
        """)
    
    def create_tray(self):
        self.tray = QSystemTrayIcon(self)
        pix = QPixmap(64, 64)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setBrush(QColor(Colors.BLUE))
        p.drawEllipse(12, 12, 40, 40)
        p.end()
        self.tray.setIcon(QIcon(pix))
        self.tray.setToolTip("Dzhenya Assistant")
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
        t = f"Welcome, {config.get('username')}."
        self.add_message(t, False)
        self.speech_worker.speak(f"Welcome, {config.get('username')}.", "en")
    
    def add_message(self, text, is_user):
        msg = MessageWidget(text, is_user)
        self.chat_layout.addWidget(msg)
        QTimer.singleShot(100, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()))
    
    def show_shutdown_dialog(self):
        dialog = ShutdownDialog(config.get("username"), self)
        if dialog.exec_() == QDialog.Accepted:
            self.add_message("Shutting down...", False)
            self.speech_worker.speak("Shutting down.", "en")
            QTimer.singleShot(3000, lambda: os.system("shutdown /s /t 0"))
        else:
            self.add_message("Shutdown cancelled.", False)
    
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
                font-size: 12px;
                font-weight: 600;
            }}
        """)
        self.orb.set_active(True)
        self.status_label.setText("Listening...")
    
    def stop_listening(self):
        self.listening = False
        self.update_buttons()
        self.orb.set_active(False)
        self.status_label.setText("Ready")
    
    def on_recognized(self, text, lang):
        self.add_message(text, True)
        self.orb.set_speaking(True)
        self.ai_worker.process(text, lang)
        self.stop_listening()
    
    def on_response(self, text, lang):
        if text:
            self.add_message(text, False)
            self.speech_worker.speak(text, lang)
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
        self.speech_worker.eng.stop()
        self.on_speech_end()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Dzhenya Assistant")
    app.setQuitOnLastWindowClosed(False)
    
    try:
        with sr.Microphone(): pass
    except:
        QMessageBox.critical(None, "Error", "Microphone not found!")
        return
    
    window = DzhenyaApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()