# 🐍 SnakeType
SnakeType is a comprehensive, feature-rich terminal-based typing speed test game that goes beyond basic typing practice. Built with Python, it offers an engaging and gamified approach to improving your typing skills with real-time feedback, adaptive difficulty, achievement systems, and detailed performance analytics.

[![PyPI Downloads](https://static.pepy.tech/badge/SnakeType)](https://pepy.tech/projects/SnakeType)
[![PyPI version](https://img.shields.io/pypi/v/SnakeType.svg)](https://pypi.org/project/SnakeType/)
[![Downloads](https://img.shields.io/pypi/dm/SnakeType.svg)](https://pypi.org/project/SnakeType/)
[![Python Version](https://img.shields.io/pypi/pyversions/SnakeType.svg)](https://pypi.org/project/SnakeType/)
[![License](https://img.shields.io/github/license/Aarav2709/SnakeType)](https://github.com/Aarav2709/SnakeType/blob/main/LICENSE)

---

## 🚀 Installation
To install the game, just use pip:
```bash
pip install SnakeType
```

---

## ▶️ How to Play
Once installed, create a new Python file (e.g., `play.py`) and add the following:
```python
from SnakeType import main
main()
```
Then run it with:
```bash
python play.py
```

## ✨ Core Features
- **Real-time Character-by-Character Feedback** with instant visual indicators
- **Adaptive Difficulty System** that adjusts to your skill level automatically
- **Multiple Test Modes**: Easy, Medium, Hard, Common Words, and Custom Text
- **Advanced Performance Tracking** with SQLite database storage
- **Achievement System** with 12+ unlockable achievements
- **Live Statistics**: Real-time WPM, accuracy, consistency scoring
- **Error Pattern Analysis** to identify and improve weak areas
- **Typing Lessons** for skill development (Home Row, Number Row, etc.)
- **Daily Streaks & Goals** for motivation and habit building
- **Export/Import Statistics** for data portability

### 🎮 Game Modes
1. **Difficulty Levels**: Easy (3-5 letter words), Medium (6-8 letters), Hard (10+ letters)
2. **Common Words Mode**: Practice with the most frequently used English words
3. **Adaptive Mode**: AI-powered difficulty adjustment based on performance
4. **Custom Text Import**: Load your own text files for practice
5. **Typing Lessons**: Structured lessons for finger training and skill building
6. **Custom Length Tests**: Choose anywhere from 10-200 words

### 📊 Advanced Analytics
- **Performance Trends**: Track improvement over time with regression analysis
- **Error Analysis**: Detailed breakdown of common mistakes and patterns
- **Consistency Scoring**: Measure typing rhythm and stability
- **Finger-specific Error Tracking**: Identify which fingers need more practice
- **30-day Performance Reports**: Comprehensive statistics and insights
- **Keystroke Timing Analysis**: Real-time rhythm detection

### 🏆 Achievement System
Unlock achievements for various milestones:
- **Speed Achievements**: Speed Demon (80+ WPM), Speed Machine (100+ WPM)
- **Accuracy Rewards**: Accuracy Master (98%+), Perfectionist (100%)
- **Persistence Badges**: Marathon typing, Daily streaks, Test completion milestones
- **Time-based Rewards**: Early Bird, Night Owl, Weekend Warrior
- **Progress Tracking**: Improvement-based achievements

### ⚙️ Customization Options
- **Auto-difficulty Toggle**: Enable/disable adaptive difficulty
- **Text Wrap Width**: Adjust display formatting (40-120 characters)
- **Daily Goals**: Set personal targets (1-20 tests per day)
- **Live WPM Display**: Toggle real-time speed updates
- **Statistics Export**: Backup your progress data

### 🎯 Key Technical Features
- **SQLite Database**: Persistent storage for all statistics and progress
- **Multi-threaded Performance**: Real-time updates without lag
- **Cross-platform Compatibility**: Works on Windows, macOS, and Linux
- **Enhanced Color Display**: Rich terminal UI with ANSI color support
- **Error Pattern Recognition**: Machine learning-inspired error analysis
- **Performance Optimization**: Efficient handling of large datasets

### 📈 Progress Tracking
- **Real-time Metrics**: Live WPM, accuracy percentage, mistake counting
- **Historical Data**: Store and analyze last 10 test results with trends
- **Streak Monitoring**: Track daily practice consistency
- **Performance Visualization**: Text-based charts and progress indicators
- **Comparative Analysis**: Week-over-week and month-over-month improvements

