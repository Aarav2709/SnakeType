
<h1 align="center">🐍 SnakeType</h1>

<p align="center">
  SnakeType is a comprehensive, feature-rich terminal-based typing speed test game that goes beyond basic typing practice.  
  Built with Python, it offers an engaging and gamified approach to improving your typing skills with real-time feedback, adaptive difficulty, achievements, and detailed performance analytics.
</p>

<p align="center">
  <a href="https://pepy.tech/projects/SnakeType"><img src="https://static.pepy.tech/badge/SnakeType" alt="Downloads"></a>
  <a href="https://pypi.org/project/SnakeType/"><img src="https://img.shields.io/pypi/v/SnakeType.svg" alt="PyPI Version"></a>
  <a href="https://pypi.org/project/SnakeType/"><img src="https://img.shields.io/pypi/dm/SnakeType.svg" alt="Downloads"></a>
  <a href="https://pypi.org/project/SnakeType/"><img src="https://img.shields.io/pypi/pyversions/SnakeType.svg" alt="Python Versions"></a>
  <a href="https://github.com/Aarav2709/SnakeType/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Aarav2709/SnakeType" alt="License"></a>
</p>

---

## 🚀 Installation

### 📦 Terminal Version (PyPI Package)
```bash
pip install SnakeType
```

### 🌐 Web Application
```bash
# Clone repository
git clone https://github.com/Aarav2709/SnakeType.git
cd SnakeType

# Install dependencies
pip install -r requirements.txt

# Run locally
cd Website
python app.py
```
➡️ Open [http://localhost:5001](http://localhost:5001) in your browser  

**Optional: Deploy to Vercel**
- Connect GitHub repo → Vercel  
- Deployment handled automatically with `vercel.json`  

---

## ▶️ How to Play

### 🎮 Terminal Version
Create a file `play.py`:
```python
from SnakeType import main
main()
```
Run:
```bash
python play.py
```

### 🌐 Web Version
Visit `http://localhost:5001` or your deployed Vercel URL.  
Includes:  
- Real-time typing feedback  
- Visual statistics dashboard  
- Achievements with badges  
- Mobile + desktop responsive  

---

## ✨ Core Features
- ⚡ **Real-time feedback** on every character  
- 🎯 **Adaptive difficulty** adjusts to skill level  
- 📝 **Multiple test modes**: Easy, Medium, Hard, Common Words, Custom Text  
- 📊 **SQLite database tracking** for stats  
- 🏆 **Achievement system** (12+ unlockables)  
- 📈 **Live WPM, accuracy, consistency** monitoring  
- 🔍 **Error pattern analysis**  
- 🎓 **Typing lessons** (home row, number row, etc.)  
- 🔄 **Daily streaks & goals**  
- 📤 **Export/Import statistics**  

---

## 🎮 Game Modes
1. Easy, Medium, Hard (by word length)  
2. Common Words Mode  
3. Adaptive Mode (AI-powered)  
4. Custom Text Import  
5. Typing Lessons (structured training)  
6. Custom Length Tests (10–200 words)  

---

## 📊 Advanced Analytics
- 📈 Performance trends with regression analysis  
- 🧐 Error analysis (common mistakes, weak areas)  
- 🎵 Consistency scoring (typing rhythm)  
- 🖐️ Finger-specific error tracking  
- 🗓️ 30-day performance reports  
- ⌨️ Keystroke timing analysis  

---

## 🏆 Achievement System
Unlock rewards for:  
- **Speed**: Speed Demon (80+ WPM), Speed Machine (100+ WPM)  
- **Accuracy**: Accuracy Master (98%+), Perfectionist (100%)  
- **Persistence**: Marathon typer, Daily streaks, Test completions  
- **Time-based**: Early Bird, Night Owl, Weekend Warrior  
- **Improvement milestones**  

---

## ⚙️ Customization Options
- 🔀 Auto-difficulty toggle  
- 📐 Text wrap width (40–120 chars)  
- 🎯 Daily goals (1–20 tests/day)  
- ⚡ Live WPM display toggle  
- 📤 Statistics export for backup  

---

## 🎯 Key Technical Features
- 💾 SQLite storage for stats & progress  
- 🧵 Multi-threaded → lag-free updates  
- 💻 Cross-platform (Windows, macOS, Linux)  
- 🎨 Rich ANSI terminal colors  
- 🤖 Error pattern recognition (ML-inspired)  
- 🚀 Optimized for large datasets  

---

## 📈 Progress Tracking
- ⏱️ Real-time metrics (WPM, accuracy, mistakes)  
- 📂 Historical data (last 10 tests, trends)  
- 🔥 Daily streaks consistency tracker  
- 📊 Text-based charts for visualization  
- 📆 Week & month comparative stats  

---

<p align="center"><b>🚀 Level up your typing with SnakeType – Practice, Progress, and Dominate!</b></p>
