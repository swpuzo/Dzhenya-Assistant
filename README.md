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
* **Built with Python, PyQt5, SpeechRecognition, and pyttsx3.**
* **Works offline for basic commands, requires internet for voice recognition.**
* **Saves user preferences in a local config file.**

## How to install?
### Windows

**Download Python from python.org**

**Run the installer, check "Add Python to PATH", click Install.**

**Open Command Prompt: press Win+R, type cmd, press Enter**

**Type and press Enter:**
```markdown
pip install PyQt5 speechrecognition pyttsx3 pyautogui pyaudio pywin32 winshell pypiwin32
```
**Save the file (dzhenya.py) and run**

### macOS

**Open Terminal: press Cmd+Space, type Terminal, press Enter**

**Install Homebrew (if not installed):**
```markdown
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
**Install Python and audio support:**
```markdown
brew install python3 portaudio
```
**Install the required packages:**
```markdown
pip3 install PyQt5 pyttsx3 SpeechRecognition pyaudio pyautogui
```
**Save the assistant file to your Desktop as dzhenya.py**

**In Terminal**
```markdown
cd Desktop

python3 dzhenya.py
```
**When asked, allow microphone access:**

**Open System Settings:**

**Go to Privacy & Security**

**Click Microphone**

**Enable Terminal**

### Linux (Ubuntu / Debian)

**Open Terminal: press Ctrl+Alt+T**

**Update and install requirements:**
```markdowm
sudo apt update ```
```markdown
sudo apt install python3 python3-pip python3-pyqt5 portaudio19-dev
```
**Install Python packages:**
```markdown
pip3 install pyttsx3 SpeechRecognition pyaudio pyautogui
```
**Save the assistant file to your home folder as dzhenya.py**

**Run:**
```markdown
python3 dzhenya.py
```
### Linux (Fedora)

**Open Terminal**

**Install requirements:**
```markdown
sudo dnf install python3 python3-pip python3-qt5 portaudio-devel
```
**Install Python packages:**
```markdown
pip3 install pyttsx3 SpeechRecognition pyaudio pyautogui
```
**Save the assistant file as dzhenya.py**

**Run:**
```markdown
python3 dzhenya.py
```
### Linux (Arch)

**Open Terminal**

**Install requirements:**
```markdown
sudo pacman -S python python-pip python-pyqt5 portaudio
```
**Install Python packages:**
```markdown
pip install pyttsx3 SpeechRecognition pyaudio pyautogui
```
**Save the assistant file as dzhenya.py**

**Run:**
```markdown
python dzhenya.py
```
