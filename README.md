# Dzhenya-Assistant
A voice assistant for your computer. You talk to it, it does things for you.

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
Windows

    Download Python from python.org

    Run the installer, check "Add Python to PATH", click Install

    Open Command Prompt: press Win+R, type cmd, press Enter

    Type and press Enter:

text

pip install PyQt5 pyttsx3 SpeechRecognition pyaudio pyautogui

    Save the assistant code to your Desktop as dzhenya.py

    In Command Prompt type:

text

cd Desktop
python dzhenya.py

    The assistant will launch. Allow microphone access when asked.

macOS

    Open Terminal: press Cmd+Space, type Terminal, press Enter

    Install Homebrew (if not installed):

text

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    Install Python and audio support:

text

brew install python3 portaudio

    Install the required packages:

text

pip3 install PyQt5 pyttsx3 SpeechRecognition pyaudio pyautogui

    Save the assistant code to your Desktop as dzhenya.py

    In Terminal type:

text

cd Desktop
python3 dzhenya.py

    When asked, allow microphone access:

        Open System Settings

        Go to Privacy & Security

        Click Microphone

        Enable Terminal

Linux (Ubuntu / Debian)

    Open Terminal: press Ctrl+Alt+T

    Update and install requirements:

text

sudo apt update
sudo apt install python3 python3-pip python3-pyqt5 portaudio19-dev

    Install Python packages:

text

pip3 install pyttsx3 SpeechRecognition pyaudio pyautogui

    Save the assistant code to your home folder as dzhenya.py

    Run:

text

python3 dzhenya.py

Linux (Fedora)

    Open Terminal

    Install requirements:

text

sudo dnf install python3 python3-pip python3-qt5 portaudio-devel

    Install Python packages:

text

pip3 install pyttsx3 SpeechRecognition pyaudio pyautogui

    Save the assistant code as dzhenya.py

    Run:

text

<text>python3 dzhenya.py<text>

Linux (Arch)

    Open Terminal

    Install requirements:

text

sudo pacman -S python python-pip python-pyqt5 portaudio

    Install Python packages:

text

pip install pyttsx3 SpeechRecognition pyaudio pyautogui

    Save the assistant code as dzhenya.py

    Run:

text

python dzhenya.py
