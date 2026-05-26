# Dzhenya-Assistant
A voice assistant for your computer. You talk to it, it does things for you.

## Logo
<img width="400" height="400" alt="dzhenya" src="https://github.com/user-attachments/assets/32111484-32fb-4d2d-9aea-0d9f216bf272" />

## Screenshot
<img width="1059" height="736" alt="Снимок экрана 2026-05-25 224626" src="https://github.com/user-attachments/assets/5dfab6ad-81b8-4d3d-93a2-49465dfe343f" />

## Works on:
* **Windows** - everything works perfectly
* **Linux** - works, but some apps may need manual setup
* **macOS** - works, but some features are limited

## Key features:
* **Voice recognition in English and Russian**
* **Opens any application installed on your PC**
* **Searches the web via Google**
* **Minimizes and restores all windows**
* **Shuts down the computer with confirmation**
* **Silent mode to temporarily stop responses**
* **Customizable command settings for frequently used actions**
* **Animated Siri-like orb that reacts to speech**

## Built-in commands:
* **"I'm here" - opens your work apps (Spotify, browser, VS Code by default)**
* **"I'm tired" - opens relaxation apps (Spotify, Steam, Discord by default)** 
* **"Computer school" - opens study apps and websites (Teams, browser)**
* **"School" - opens Gmail**
* **"Minimize all" / "Restore windows"**
* **"Silence" / "Speak"**
* **"Shut down"**
* **"Open [app]" / "Search [query]"**
* **"Time" / "Date" / "Weather" / "Joke"**

## Technical:
* **Built with Python, PyQt5, SpeechRecognition, and pyttsx3. Works offline for basic commands, requires internet for voice recognition. Saves user preferences in a local config file.**

## How to install?
**Windows**

Download Python from python.org

Run the installer, check "Add Python to PATH", click Install

Open Command Prompt: press Win+R, type cmd, press Enter

Type and press Enter:

<text>pip install PyQt5 speechrecognition pyttsx3 pyautogui pyaudio pywin32 winshell pypiwin32<text>

Save the file (dzhenya.py) and run

**macOS**

Open Terminal: press Cmd+Space, type Terminal, press Enter

Install Homebrew (if not installed):

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

Install Python and audio support:

<text>brew install python3 portaudio<text>

Install the required packages:

<text>pip3 install PyQt5 pyttsx3 SpeechRecognition pyaudio pyautogui<text>

Save the assistant file to your Desktop as dzhenya.py

In Terminal

<text>cd Desktop

python3 dzhenya.py<text>

When asked, allow microphone access:

Open System Settings:

Go to Privacy & Security

Click Microphone

Enable Terminal

**Linux (Ubuntu / Debian)**

Open Terminal: press Ctrl+Alt+T

Update and install requirements:

<text>sudo apt update<text>

<text>sudo apt install python3 python3-pip python3-pyqt5 portaudio19-dev<text>

Install Python packages:

<text>pip3 install pyttsx3 SpeechRecognition pyaudio pyautogui<text>

Save the assistant file to your home folder as dzhenya.py

Run:

<text>python3 dzhenya.py<text>

**Linux (Fedora)**

Open Terminal

Install requirements:

<text>sudo dnf install python3 python3-pip python3-qt5 portaudio-devel

Install Python packages:

<text>pip3 install pyttsx3 SpeechRecognition pyaudio pyautogui<text>

Save the assistant file as dzhenya.py

Run:

<text>python3 dzhenya.py<text>

**Linux (Arch)**

Open Terminal

Install requirements:

<text>sudo pacman -S python python-pip python-pyqt5 portaudio<text>

Install Python packages:

<text>pip install pyttsx3 SpeechRecognition pyaudio pyautogui<text>

Save the assistant file as dzhenya.py

Run:

<text>python dzhenya.py<text>
