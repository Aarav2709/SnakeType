import random
import time
import threading
import sys
import os
import json
import sqlite3
import math
import shutil
from collections import deque, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

try:
    import statistics
except ImportError:
    class statistics:
        @staticmethod
        def mean(data):
            return sum(data) / len(data) if data else 0
        
        @staticmethod
        def median(data):
            sorted_data = sorted(data)
            n = len(sorted_data)
            if n == 0:
                return 0
            return sorted_data[n//2] if n % 2 else (sorted_data[n//2-1] + sorted_data[n//2]) / 2
        
        @staticmethod
        def stdev(data):
            if len(data) < 2:
                return 0
            mean_val = statistics.mean(data)
            variance = sum((x - mean_val) ** 2 for x in data) / (len(data) - 1)
            return variance ** 0.5
        
        @staticmethod
        def variance(data):
            if len(data) < 2:
                return 0
            mean_val = statistics.mean(data)
            return sum((x - mean_val) ** 2 for x in data) / (len(data) - 1)
        
        @staticmethod
        def quantiles(data, n=4):
            """Simple quantiles implementation for compatibility"""
            if len(data) < 2:
                return [0] * (n-1)
            sorted_data = sorted(data)
            result = []
            for i in range(1, n):
                index = (i * len(sorted_data)) // n
                result.append(sorted_data[min(index, len(sorted_data) - 1)])
            return result

EASY_WORDS = ["cat", "dog", "run", "big", "sun", "car", "red", "box", "top", "mix", "cup", "bug", "hat", "pen", "egg", "jam", "win", "fix", "ten", "zip"]
MEDIUM_WORDS = ["python", "typing", "keyboard", "computer", "program", "function", "variable", "algorithm", "structure", "database", "network", "software", "hardware", "internet", "website", "application", "framework", "library", "module", "package"]
HARD_WORDS = ["programming", "development", "architecture", "implementation", "optimization", "documentation", "configuration", "authentication", "authorization", "synchronization", "asynchronous", "multithreading", "encapsulation", "inheritance", "polymorphism", "abstraction", "methodology", "infrastructure", "scalability", "maintainability"]

COMMON_WORDS = ["the", "of", "and", "to", "a", "in", "is", "it", "you", "that", "he", "was", "for", "on", "are", "as", "with", "his", "they", "i", "at", "be", "this", "have", "from", "or", "one", "had", "by", "word", "but", "not", "what", "all", "were", "we", "when", "your", "can", "said", "there", "each", "which", "she", "do", "how", "their", "if", "will", "up", "other", "about", "out", "many", "then", "them", "these", "so", "some", "her", "would", "make", "like", "into", "him", "has", "two", "more", "very", "after", "words", "first", "where", "been", "who", "its", "now", "find", "long", "down", "way", "may", "come", "could", "people", "my", "than", "water", "part", "time", "work", "right", "new", "take", "get", "place", "made", "live", "where", "after", "back", "little", "only", "round", "man", "year", "came", "show", "every", "good", "me", "give", "our", "under", "name", "very", "through", "just", "form", "sentence", "great", "think", "say", "help", "low", "line", "differ", "turn", "cause", "much", "mean", "before", "move", "right", "boy", "old", "too", "same", "tell", "does", "set", "three", "want", "air", "well", "also", "play", "small", "end", "put", "home", "read", "hand", "port", "large", "spell", "add", "even", "land", "here", "must", "big", "high", "such", "follow", "act", "why", "ask", "men", "change", "went", "light", "kind", "off", "need", "house", "picture", "try", "us", "again", "animal", "point", "mother", "world", "near", "build", "self", "earth", "father", "head", "stand", "own", "page", "should", "country", "found", "answer", "school", "grow", "study", "still", "learn", "plant", "cover", "food", "sun", "four", "between", "state", "keep", "eye", "never", "last", "let", "thought", "city", "tree", "cross", "farm", "hard", "start", "might", "story", "saw", "far", "sea", "draw", "left", "late", "run", "don't", "while", "press", "close", "night", "real", "life", "few", "north", "open", "seem", "together", "next", "white", "children", "begin", "got", "walk", "example", "ease", "paper", "group", "always", "music", "those", "both", "mark", "often", "letter", "until", "mile", "river", "car", "feet", "care", "second", "book", "carry", "took", "science", "eat", "room", "friend", "began", "idea", "fish", "mountain", "stop", "once", "base", "hear", "horse", "cut", "sure", "watch", "color", "face", "wood", "main", "enough", "plain", "girl", "usual", "young", "ready", "above", "ever", "red", "list", "though", "feel", "talk", "bird", "soon", "body", "dog", "family", "direct", "pose", "leave", "song", "measure", "door", "product", "black", "short", "numeral", "class", "wind", "question", "happen", "complete", "ship", "area", "half", "rock", "order", "fire", "south", "problem", "piece", "told", "knew", "pass", "since", "top", "whole", "king", "space", "heard", "best", "hour", "better", "during", "hundred", "five", "remember", "step", "early", "hold", "west", "ground", "interest", "reach", "fast", "verb", "sing", "listen", "six", "table", "travel", "less", "morning", "ten", "simple", "several", "vowel", "toward", "war", "lay", "against", "pattern", "slow", "center", "love", "person", "money", "serve", "appear", "road", "map", "rain", "rule", "govern", "pull", "cold", "notice", "voice", "unit", "power", "town", "fine", "certain", "fly", "fall", "lead", "cry", "dark", "machine", "note", "wait", "plan", "figure", "star", "box", "noun", "field", "rest", "correct", "able", "pound", "done", "beauty", "drive", "stood", "contain", "front", "teach", "week", "final", "gave", "green", "oh", "quick", "develop", "ocean", "warm", "free", "minute", "strong", "special", "mind", "behind", "clear", "tail", "produce", "fact", "street", "inch", "multiply", "nothing", "course", "stay", "wheel", "full", "force", "blue", "object", "decide", "surface", "deep", "moon", "island", "foot", "system", "busy", "test", "record", "boat", "common", "gold", "possible", "plane", "stead", "dry", "wonder", "laugh", "thousands", "ago", "ran", "check", "game", "shape", "equate", "hot", "miss", "brought", "heat", "snow", "tire", "bring", "yes", "distant", "fill", "east", "paint", "language", "among"]

ACHIEVEMENTS = {
    "speed_demon": {"name": "Speed Demon", "desc": "Reach 80+ WPM", "icon": "🚀"},
    "accuracy_master": {"name": "Accuracy Master", "desc": "Maintain 98%+ accuracy", "icon": "🎯"},
    "persistent": {"name": "Persistent", "desc": "Complete 10 tests", "icon": "🔥"},
    "marathon": {"name": "Marathon", "desc": "Type for 5 minutes straight", "icon": "🏃"},
    "perfectionist": {"name": "Perfectionist", "desc": "Complete a test with 100% accuracy", "icon": "💎"},
    "consistent": {"name": "Consistent", "desc": "5 tests in a row with >90% accuracy", "icon": "📈"},
    "speed_machine": {"name": "Speed Machine", "desc": "Reach 100+ WPM", "icon": "⚡"},
    "improver": {"name": "Improver", "desc": "Improve WPM by 20+ points", "icon": "📊"},
    "streak_master": {"name": "Streak Master", "desc": "Maintain a 7-day streak", "icon": "🔥"},
    "early_bird": {"name": "Early Bird", "desc": "Take a test before 8 AM", "icon": "🌅"},
    "night_owl": {"name": "Night Owl", "desc": "Take a test after 10 PM", "icon": "🦉"},
    "weekend_warrior": {"name": "Weekend Warrior", "desc": "Practice on weekends", "icon": "🎮"}
}

class DatabaseManager:
    def __init__(self, db_path="typing_stats.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection with timeout and safety checks"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
            conn.execute("PRAGMA journal_mode = WAL")  # Better concurrency
            return conn
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            raise
    
    def init_database(self):
        """Initialize database with improved error handling"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS test_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        wpm REAL NOT NULL CHECK(wpm >= 0),
                        accuracy REAL NOT NULL CHECK(accuracy >= 0 AND accuracy <= 100),
                        mistakes INTEGER NOT NULL CHECK(mistakes >= 0),
                        test_duration REAL NOT NULL CHECK(test_duration > 0),
                        difficulty TEXT NOT NULL,
                        word_count INTEGER NOT NULL CHECK(word_count > 0),
                        characters_typed INTEGER NOT NULL CHECK(characters_typed >= 0),
                        correct_characters INTEGER NOT NULL CHECK(correct_characters >= 0)
                    )
                ''')
                
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_test_results_date ON test_results(date)')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS achievements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        achievement_id TEXT NOT NULL,
                        date_earned TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(achievement_id)
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS error_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        test_id INTEGER NOT NULL,
                        character_intended TEXT NOT NULL,
                        character_typed TEXT NOT NULL,
                        position INTEGER NOT NULL CHECK(position >= 0),
                        word_context TEXT,
                        FOREIGN KEY (test_id) REFERENCES test_results (id) ON DELETE CASCADE
                    )
                ''')
                
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_error_patterns_chars ON error_patterns(character_intended, character_typed)')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS daily_streaks (
                        date DATE PRIMARY KEY,
                        tests_completed INTEGER DEFAULT 0 CHECK(tests_completed >= 0)
                    )
                ''')
                
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            try:
                import shutil
                shutil.copy(self.db_path, f"{self.db_path}.backup")
                print(f"Database backed up to {self.db_path}.backup")
            except Exception:
                pass
            raise
    
    def save_test_result(self, result_data):
        """Save test result with improved error handling and validation"""
        try:
            wpm, accuracy, mistakes, duration, difficulty, word_count, chars_typed, correct_chars = result_data
            
            if wpm < 0 or accuracy < 0 or accuracy > 100 or mistakes < 0 or duration <= 0:
                raise ValueError("Invalid test result data")
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO test_results 
                    (wpm, accuracy, mistakes, test_duration, difficulty, word_count, characters_typed, correct_characters)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', result_data)
                test_id = cursor.lastrowid
                
                today = datetime.now().date()
                cursor.execute('''
                    INSERT OR REPLACE INTO daily_streaks (date, tests_completed)
                    VALUES (?, COALESCE((SELECT tests_completed FROM daily_streaks WHERE date = ?) + 1, 1))
                ''', (today, today))
                
                conn.commit()
                return test_id
        except (sqlite3.Error, ValueError) as e:
            print(f"Error saving test result: {e}")
            return None
    
    def save_error_pattern(self, test_id, errors):
        """Save error patterns with batch processing for better performance"""
        if not test_id or not errors:
            return
            
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany('''
                    INSERT INTO error_patterns 
                    (test_id, character_intended, character_typed, position, word_context)
                    VALUES (?, ?, ?, ?, ?)
                ''', [(test_id,) + error for error in errors])
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving error patterns: {e}")
    
    def unlock_achievement(self, achievement_id):
        """Unlock achievement with better error handling"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO achievements (achievement_id) VALUES (?)', (achievement_id,))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False  # Already unlocked
        except sqlite3.Error as e:
            print(f"Error unlocking achievement: {e}")
            return False
    
    def get_achievements(self):
        """Get achievements with error handling"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT achievement_id, date_earned FROM achievements ORDER BY date_earned DESC')
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting achievements: {e}")
            return []
    
    def get_statistics(self, days=30):
        """Get statistics with parameterized queries for security"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM test_results 
                    WHERE date >= datetime('now', '-' || ? || ' days')
                    ORDER BY date DESC
                ''', (days,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting statistics: {e}")
            return []
    
    def get_error_analysis(self, days=30):
        """Get error analysis with improved query"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT character_intended, character_typed, COUNT(*) as frequency
                    FROM error_patterns ep
                    JOIN test_results tr ON ep.test_id = tr.id
                    WHERE tr.date >= datetime('now', '-' || ? || ' days')
                    GROUP BY character_intended, character_typed
                    ORDER BY frequency DESC
                    LIMIT 10
                ''', (days,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting error analysis: {e}")
            return []
    
    def get_streak_count(self):
        """Get streak count with better error handling"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM daily_streaks 
                    WHERE date >= date('now', '-7 days') AND tests_completed > 0
                ''')
                result = cursor.fetchone()
                return result[0] if result else 0
        except sqlite3.Error as e:
            print(f"Error getting streak count: {e}")
            return 0

class PerformanceTracker:
    def __init__(self):
        self.wpm_samples = deque(maxlen=50)  # For real-time WPM calculation
        self.last_update_time = None
        self.keystroke_times = []
        self.pause_threshold = 2.0  # seconds
        self.smoothing_factor = 0.3  # For exponential smoothing
        self.velocity_history = deque(maxlen=20)  # For rhythm analysis
        self.error_clusters = defaultdict(list)  # For error clustering analysis
        
    def add_keystroke(self, timestamp, char_count):
        """Add a keystroke sample for real-time WPM calculation with enhanced smoothing"""
        self.keystroke_times.append(timestamp)
        
        cutoff_time = timestamp - 10
        self.keystroke_times = [t for t in self.keystroke_times if t > cutoff_time]
        
        if len(self.keystroke_times) >= 2:
            time_span = self.keystroke_times[-1] - self.keystroke_times[0]
            if time_span > 0:
                chars_per_second = len(self.keystroke_times) / time_span
                raw_wpm = (chars_per_second * 60) / 5  # 5 chars = 1 word
                
                if self.wpm_samples:
                    smoothed_wpm = (self.smoothing_factor * raw_wpm) + \
                                 ((1 - self.smoothing_factor) * self.wpm_samples[-1])
                else:
                    smoothed_wpm = raw_wpm
                
                if self._is_valid_sample(smoothed_wpm):
                    self.wpm_samples.append(smoothed_wpm)
                    
                    if len(self.wpm_samples) >= 2:
                        velocity_change = self.wpm_samples[-1] - self.wpm_samples[-2]
                        self.velocity_history.append(velocity_change)
    
    def _is_valid_sample(self, wpm_value):
        """Filter outliers using Interquartile Range (IQR) method"""
        if len(self.wpm_samples) < 5:
            return True  # Not enough data for outlier detection
        
        recent_samples = list(self.wpm_samples)[-20:]  # Use last 20 samples
        q1 = statistics.quantiles(recent_samples, n=4)[0]  # 25th percentile
        q3 = statistics.quantiles(recent_samples, n=4)[2]  # 75th percentile
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        return lower_bound <= wpm_value <= upper_bound
    
    def get_current_wpm(self):
        """Get enhanced current WPM with multiple smoothing techniques"""
        if not self.wpm_samples:
            return 0
        
        recent_samples = list(self.wpm_samples)[-10:]
        if len(recent_samples) < 3:
            return statistics.median(recent_samples)
        
        weights = [i + 1 for i in range(len(recent_samples))]
        weighted_sum = sum(sample * weight for sample, weight in zip(recent_samples, weights))
        total_weight = sum(weights)
        
        return weighted_sum / total_weight if total_weight > 0 else 0
    
    def calculate_consistency_score(self):
        """Enhanced consistency calculation using coefficient of variation"""
        if len(self.wpm_samples) < 5:
            return 0
        
        mean_wpm = statistics.mean(self.wpm_samples)
        if mean_wpm == 0:
            return 0
        
        std_dev = statistics.stdev(self.wpm_samples)
        coefficient_of_variation = (std_dev / mean_wpm) * 100
        
        consistency_score = max(0, 100 - coefficient_of_variation)
        return min(100, consistency_score)
    
    def detect_typing_patterns(self, user_input, target_text):
        """Enhanced typing pattern analysis with advanced error detection"""
        patterns = {
            'bigram_errors': defaultdict(int),
            'trigram_errors': defaultdict(int),  # Enhanced: 3-character patterns
            'position_errors': defaultdict(int),
            'substitution_errors': defaultdict(int),
            'timing_inconsistencies': [],
            'finger_errors': defaultdict(int),    # Enhanced: finger-specific errors
            'error_clusters': [],                 # Enhanced: positional error clustering
            'velocity_analysis': self._analyze_velocity_patterns()
        }
        
        for i, (typed, target) in enumerate(zip(user_input, target_text)):
            if typed != target:
                if i > 0:
                    bigram = target_text[i-1:i+1]
                    patterns['bigram_errors'][bigram] += 1
                
                if i > 0 and i < len(target_text) - 1:
                    trigram = target_text[i-1:i+2]
                    patterns['trigram_errors'][trigram] += 1
                
                position_type = self._categorize_position(i, len(target_text))
                patterns['position_errors'][position_type] += 1
                
                patterns['substitution_errors'][f"{target}->{typed}"] += 1
                
                finger = self._map_char_to_finger(target.lower())
                if finger:
                    patterns['finger_errors'][finger] += 1
                
                self.error_clusters[i // 10].append(i)  # Group by 10-character windows
        
        patterns['error_clusters'] = self._analyze_error_clusters()
        
        return patterns
    
    def _categorize_position(self, position, total_length):
        """Enhanced position categorization"""
        ratio = position / total_length
        if ratio < 0.15:
            return 'beginning'
        elif ratio < 0.35:
            return 'early_middle'
        elif ratio < 0.65:
            return 'middle'
        elif ratio < 0.85:
            return 'late_middle'
        else:
            return 'end'
    
    def _map_char_to_finger(self, char):
        """Map characters to specific fingers for targeted training"""
        finger_map = {
            'left_pinky': 'qaz1',
            'left_ring': 'wsx2',
            'left_middle': 'edc3',
            'left_index': 'rfvtgb45',
            'right_index': 'yhnujm67',
            'right_middle': 'ik,8',
            'right_ring': 'ol.9',
            'right_pinky': 'p;/0-=[]\\\'"`'
        }
        
        for finger, chars in finger_map.items():
            if char in chars:
                return finger
        return 'unknown'
    
    def _analyze_error_clusters(self):
        """Analyze spatial clustering of errors for pattern recognition"""
        clusters = []
        for window, errors in self.error_clusters.items():
            if len(errors) >= 2:  # At least 2 errors in a 10-char window
                clusters.append({
                    'window_start': window * 10,
                    'error_count': len(errors),
                    'error_density': len(errors) / 10,
                    'positions': errors
                })
        return sorted(clusters, key=lambda x: x['error_density'], reverse=True)
    
    def _analyze_velocity_patterns(self):
        """Analyze typing velocity patterns for rhythm insights"""
        if len(self.velocity_history) < 5:
            return {'status': 'insufficient_data'}
        
        velocity_values = list(self.velocity_history)
        
        mean_velocity = statistics.mean(velocity_values)
        velocity_std = statistics.stdev(velocity_values)
        
        positive_changes = sum(1 for v in velocity_values if v > 0)
        negative_changes = sum(1 for v in velocity_values if v < 0)
        
        rhythm_score = 100 - min(100, (velocity_std / (abs(mean_velocity) + 1)) * 50)
        
        return {
            'mean_velocity_change': mean_velocity,
            'velocity_consistency': rhythm_score,
            'acceleration_ratio': positive_changes / len(velocity_values),
            'deceleration_ratio': negative_changes / len(velocity_values),
            'rhythm_category': self._categorize_rhythm(rhythm_score)
        }
    
    def _categorize_rhythm(self, rhythm_score):
        """Categorize typing rhythm for user feedback"""
        if rhythm_score >= 80:
            return 'very_consistent'
        elif rhythm_score >= 60:
            return 'consistent'
        elif rhythm_score >= 40:
            return 'somewhat_consistent'
        else:
            return 'inconsistent'
    
    def get_performance_insights(self):
        """Generate comprehensive performance insights"""
        if len(self.wpm_samples) < 5:
            return {'status': 'insufficient_data'}
        
        current_wpm = self.get_current_wpm()
        consistency = self.calculate_consistency_score()
        velocity_analysis = self._analyze_velocity_patterns()
        
        recent_trend = self._calculate_performance_trend()
        
        insights = {
            'current_performance': {
                'wpm': current_wpm,
                'consistency_score': consistency,
                'performance_trend': recent_trend
            },
            'rhythm_analysis': velocity_analysis,
            'recommendations': self._generate_recommendations(current_wpm, consistency, velocity_analysis)
        }
        
        return insights
    
    def _calculate_performance_trend(self):
        """Calculate performance trend over recent samples"""
        if len(self.wpm_samples) < 10:
            return 'stable'
        
        recent_half = list(self.wpm_samples)[-5:]
        older_half = list(self.wpm_samples)[-10:-5]
        
        recent_avg = statistics.mean(recent_half)
        older_avg = statistics.mean(older_half)
        
        change_percent = ((recent_avg - older_avg) / older_avg) * 100
        
        if change_percent > 5:
            return 'improving'
        elif change_percent < -5:
            return 'declining'
        else:
            return 'stable'
    
    def _generate_recommendations(self, wpm, consistency, velocity_analysis):
        """Generate personalized recommendations based on performance data"""
        recommendations = []
        
        if wpm < 30:
            recommendations.append("Focus on accuracy and proper finger placement before increasing speed")
        elif wpm < 50:
            recommendations.append("Practice common word patterns to build muscle memory")
        elif wpm < 70:
            recommendations.append("Work on maintaining consistent rhythm while increasing speed")
        
        if consistency < 60:
            recommendations.append("Practice at a slower, more controlled pace to improve consistency")
            recommendations.append("Focus on maintaining steady rhythm rather than burst typing")
        
        rhythm_category = velocity_analysis.get('rhythm_category', 'unknown')
        if rhythm_category == 'inconsistent':
            recommendations.append("Practice with a metronome to develop consistent typing rhythm")
        elif rhythm_category == 'somewhat_consistent':
            recommendations.append("Focus on smooth, even keystrokes without rushed bursts")
        
        return recommendations


class DifficultyAdjuster:
    def __init__(self):
        self.performance_history = deque(maxlen=10)
        self.current_level = 2  # Start at medium
        self.adjustment_threshold = 3  # Number of tests before adjustment
        
    def add_performance(self, wpm, accuracy):
        """Add a performance sample"""
        score = self.calculate_performance_score(wpm, accuracy)
        self.performance_history.append(score)
        
        if len(self.performance_history) >= self.adjustment_threshold:
            self.adjust_difficulty()
    
    def calculate_performance_score(self, wpm, accuracy):
        """Calculate a combined performance score"""
        return (wpm * 0.6) + (accuracy * 0.4)
    
    def adjust_difficulty(self):
        """Automatically adjust difficulty based on performance"""
        if len(self.performance_history) < self.adjustment_threshold:
            return
        
        avg_score = sum(self.performance_history) / len(self.performance_history)
        recent_trend = sum(list(self.performance_history)[-3:]) / 3
        
        if recent_trend > 75 and self.current_level < 4:
            self.current_level += 1
            return "increased"
        
        elif recent_trend < 45 and self.current_level > 1:
            self.current_level -= 1
            return "decreased"
        
        return "unchanged"
    
    def get_recommended_difficulty(self):
        """Get the current recommended difficulty level"""
        return self.current_level
    
    def get_word_mix_ratio(self):
        """Get the ratio of easy:medium:hard words based on current level"""
        ratios = {
            1: (0.8, 0.2, 0.0),  # Mostly easy
            2: (0.5, 0.4, 0.1),  # Balanced with some easy
            3: (0.2, 0.5, 0.3),  # Balanced with some hard
            4: (0.1, 0.3, 0.6)   # Mostly hard
        }
        return ratios.get(self.current_level, (0.5, 0.4, 0.1))

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    END = '\033[0m'

class TypingGame:
    def __init__(self):
        self.current_text = ""
        self.user_input = ""
        self.start_time = None
        self.end_time = None
        self.is_running = False
        
        self.performance_tracker = PerformanceTracker()
        self.db_manager = DatabaseManager()
        self.difficulty_adjuster = DifficultyAdjuster()
        
        self.wpm_history = deque(maxlen=50)
        self.accuracy_history = deque(maxlen=50)
        self.current_wpm = 0
        self.current_accuracy = 100
        self.live_wpm = 0
        self.typed_chars = 0
        self.correct_chars = 0
        self.mistakes = 0
        self.error_positions = []
        
        self.daily_goal = 5  # tests per day
        self.current_streak = 0
        self.achievements_unlocked = set()
        self.total_tests = 0
        self.total_time_typed = 0
        
        self.auto_difficulty = True
        self.show_live_wpm = True
        self.text_wrap_width = 80
        
        self.load_user_data()
        
        self.wpm_update_thread = None
        self.stop_wpm_thread = False
    
    def load_user_data(self):
        """Load user statistics and achievements from database"""
        try:
            achievements = self.db_manager.get_achievements()
            self.achievements_unlocked = {ach[0] for ach in achievements}
            
            recent_stats = self.db_manager.get_statistics(days=30)
            if recent_stats:
                self.total_tests = len(recent_stats)
                self.wpm_history.extend([stat[2] for stat in recent_stats[-10:]])
                self.accuracy_history.extend([stat[3] for stat in recent_stats[-10:]])
            
            self.current_streak = self.db_manager.get_streak_count()
            
        except Exception as e:
            print(f"Error loading user data: {e}")
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def start_real_time_wpm_thread(self):
        """Start thread for real-time WPM updates"""
        self.stop_wpm_thread = False
        if self.wpm_update_thread and self.wpm_update_thread.is_alive():
            self.stop_wpm_thread = True
            self.wpm_update_thread.join(timeout=1)
        
        self.wpm_update_thread = threading.Thread(target=self.update_live_wpm)
        self.wpm_update_thread.daemon = True
        self.wpm_update_thread.start()
    
    def update_live_wpm(self):
        """Update live WPM in real-time"""
        while not self.stop_wpm_thread and self.is_running:
            if self.start_time and self.user_input:
                current_time = time.time()
                elapsed_time = current_time - self.start_time
                if elapsed_time > 0:
                    chars_typed = len(self.user_input)
                    self.live_wpm = (chars_typed / 5) / (elapsed_time / 60)
                    
                    self.performance_tracker.add_keystroke(current_time, chars_typed)
            
            time.sleep(0.1)  # Update 10 times per second
    
    def get_adaptive_word_list(self, word_count=50):
        """Generate word list based on adaptive difficulty"""
        if not self.auto_difficulty:
            return self.get_word_list("4", word_count)  # Default to common words
        
        difficulty_level = self.difficulty_adjuster.get_recommended_difficulty()
        easy_ratio, medium_ratio, hard_ratio = self.difficulty_adjuster.get_word_mix_ratio()
        
        easy_count = int(word_count * easy_ratio)
        medium_count = int(word_count * medium_ratio)
        hard_count = word_count - easy_count - medium_count
        
        words = []
        words.extend(random.choices(EASY_WORDS, k=easy_count))
        words.extend(random.choices(MEDIUM_WORDS, k=medium_count))
        words.extend(random.choices(HARD_WORDS, k=hard_count))
        
        random.shuffle(words)
        return words
    
    def get_word_list(self, difficulty, word_count=50):
        if difficulty == "1":
            return random.choices(EASY_WORDS, k=word_count)
        elif difficulty == "2":
            return random.choices(MEDIUM_WORDS, k=word_count)
        elif difficulty == "3":
            return random.choices(HARD_WORDS, k=word_count)
        elif difficulty == "adaptive":
            return self.get_adaptive_word_list(word_count)
        else:  # Common words mode
            return random.choices(COMMON_WORDS, k=word_count)
    
    def load_custom_text(self, file_path):
        """Load custom text from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                words = []
                current_word = ""
                for char in content.lower():
                    if char.isalnum():
                        current_word += char
                    else:
                        if current_word:
                            words.append(current_word)
                            current_word = ""
                if current_word:
                    words.append(current_word)
                return words[:100]  # Limit to 100 words
        except Exception as e:
            print(f"Error loading custom text: {e}")
            return None
    
    def display_menu(self):
        self.clear_screen()
        
        print(f"{Colors.CYAN}{Colors.BOLD}╔════════════════════════════════════════════════════════════════╗")
        print(f"║                           SNAKETYPE                            ║")
        print(f"╚════════════════════════════════════════════════════════════════╝{Colors.END}")
        
        tests_today = len([t for t in self.db_manager.get_statistics(days=1)])
        progress_bar = "█" * tests_today + "░" * max(0, self.daily_goal - tests_today)
        
        print(f"\n{Colors.YELLOW}📊 Today: {tests_today}/{self.daily_goal} {progress_bar[:self.daily_goal]} | ")
        print(f"🔥 Streak: {self.current_streak} days | 🏆 Achievements: {len(self.achievements_unlocked)}{Colors.END}")
        
        if self.wpm_history:
            avg_wpm = sum(list(self.wpm_history)[-5:]) / min(5, len(self.wpm_history))
            print(f"{Colors.GRAY}Recent Average: {avg_wpm:.1f} WPM{Colors.END}")
        
        print(f"\n{Colors.YELLOW}🎯 Choose your test mode:{Colors.END}")
        print(f"{Colors.WHITE}1. Easy Words (3-5 letters){Colors.END}")
        print(f"{Colors.WHITE}2. Medium Words (6-8 letters){Colors.END}")
        print(f"{Colors.WHITE}3. Hard Words (10+ letters){Colors.END}")
        print(f"{Colors.WHITE}4. Common Words (mixed){Colors.END}")
        print(f"{Colors.WHITE}5. 🤖 Adaptive Difficulty{Colors.END}")
        print(f"{Colors.WHITE}6. Custom Test Length{Colors.END}")
        print(f"{Colors.WHITE}7. 📁 Import Custom Text{Colors.END}")
        print(f"{Colors.WHITE}8. 📊 Advanced Statistics{Colors.END}")
        print(f"{Colors.WHITE}9. 🏆 Achievements{Colors.END}")
        print(f"{Colors.WHITE}10. ⚙️  Settings{Colors.END}")
        print(f"{Colors.WHITE}11. 🎮 Typing Lessons{Colors.END}")
        print(f"{Colors.WHITE}12. Quit{Colors.END}")
        
        self.show_recent_achievements()
        
        return input(f"\n{Colors.CYAN}Enter your choice (1-12): {Colors.END}")
    
    def show_recent_achievements(self):
        """Show recently unlocked achievements"""
        recent_achievements = self.db_manager.get_achievements()
        if recent_achievements:
            recent = recent_achievements[:3]  # Show last 3
            print(f"\n{Colors.MAGENTA}🎉 Recent Achievements:{Colors.END}")
            for ach_id, date in recent:
                if ach_id in ACHIEVEMENTS:
                    ach = ACHIEVEMENTS[ach_id]
                    print(f"{Colors.YELLOW}{ach['icon']} {ach['name']}: {ach['desc']}{Colors.END}")
    
    def display_text_with_progress(self):
        self.clear_screen()
        
        elapsed = (time.time() - self.start_time) if self.start_time else 0
        
        print(f"{Colors.CYAN}{Colors.BOLD}╔═══════════════════════════════════════════════════════════════════════════╗")
        print(f"║          WPM: {self.live_wpm:6.1f}  │  Accuracy: {self.current_accuracy:5.1f}%  │  Time: {elapsed:5.1f}s                ║")
        print(f"╚═══════════════════════════════════════════════════════════════════════════╝{Colors.END}")
        print()
        
        self.display_enhanced_text()
        
        self.display_animated_progress_bar()
        
        self.show_contextual_tips()
    
    def display_enhanced_text(self):
        """Display text with improved color coding and wrapping"""
        typed_length = len(self.user_input)
        display_lines = []
        current_line = ""
        line_length = 0
        
        for i, char in enumerate(self.current_text):
            color_code = ""
            char_display = char
            
            if i < typed_length:
                if self.user_input[i] == char:
                    if i >= typed_length - 5:  # Recent characters
                        color_code = f"{Colors.GREEN}{Colors.BOLD}"
                    else:
                        color_code = Colors.GREEN
                else:
                    color_code = f"{Colors.RED}{Colors.BOLD}{Colors.REVERSE}"
                    if char == ' ':
                        char_display = '⎵'  # Better space indicator
            elif i == typed_length:
                color_code = f"{Colors.YELLOW}{Colors.BOLD}{Colors.UNDERLINE}{Colors.BLINK}"
                if char == ' ':
                    char_display = '⎵'
            else:
                if char == ' ':
                    char_display = '⎵'
                else:
                    color_code = Colors.GRAY
            
            if char == ' ' and line_length > self.text_wrap_width - 10:
                display_lines.append(current_line)
                current_line = ""
                line_length = 0
            else:
                current_line += f"{color_code}{char_display}{Colors.END}"
                line_length += 1
        
        if current_line:
            display_lines.append(current_line)
        
        for i, line in enumerate(display_lines[:8]):  # Show max 8 lines
            line_num = f"{Colors.GRAY}{i+1:2d}│{Colors.END}" if len(display_lines) > 1 else "  "
            print(f"{line_num} {line}")
        
        if len(display_lines) > 8:
            print(f"{Colors.GRAY}   ... {len(display_lines) - 8} more lines ...{Colors.END}")
        print()
    
    def display_animated_progress_bar(self):
        """Display animated progress bar with multiple indicators"""
        progress = len(self.user_input) / len(self.current_text) if len(self.current_text) > 0 else 0
        bar_length = 60
        filled_length = int(bar_length * progress)
        
        filled_part = ""
        for i in range(filled_length):
            if i < filled_length * 0.7:
                filled_part += f"{Colors.GREEN}█{Colors.END}"
            elif i < filled_length * 0.9:
                filled_part += f"{Colors.YELLOW}█{Colors.END}"
            else:
                filled_part += f"{Colors.CYAN}█{Colors.END}"
        
        empty_part = f"{Colors.GRAY}{'░' * (bar_length - filled_length)}{Colors.END}"
        
        milestone_positions = [bar_length//4, bar_length//2, 3*bar_length//4]
        bar_display = filled_part + empty_part
        
        print(f"Progress: {bar_display} {progress*100:.1f}%")
        
        if len(self.wpm_history) >= 2:
            recent_avg = sum(list(self.wpm_history)[-3:]) / min(3, len(self.wpm_history))
            older_avg = sum(list(self.wpm_history)[-6:-3]) / min(3, len(self.wpm_history) - 3) if len(self.wpm_history) > 3 else recent_avg
            
            if recent_avg > older_avg + 2:
                trend = f"{Colors.GREEN}📈 Improving{Colors.END}"
            elif recent_avg < older_avg - 2:
                trend = f"{Colors.RED}📉 Declining{Colors.END}"
            else:
                trend = f"{Colors.YELLOW}➡️  Stable{Colors.END}"
            
            print(f"Trend: {trend}")
    
    def show_contextual_tips(self):
        """Show helpful tips based on current typing performance"""
        tips = []
        
        if self.current_accuracy < 90:
            tips.append(f"{Colors.RED}💡 Tip: Slow down and focus on accuracy first{Colors.END}")
        elif self.live_wpm < 30:
            tips.append(f"{Colors.YELLOW}💡 Tip: Try to maintain a steady rhythm{Colors.END}")
        elif self.mistakes > len(self.user_input) * 0.1:
            tips.append(f"{Colors.BLUE}💡 Tip: Take a breath and reset your focus{Colors.END}")
        
        if tips:
            print(f"\n{random.choice(tips)}")
    
    def calculate_stats(self):
        if not self.start_time or not self.user_input:
            return
        
        elapsed_time = time.time() - self.start_time
        typed_length = len(self.user_input)
        
        if elapsed_time > 0:
            self.current_wpm = (typed_length / 5) / (elapsed_time / 60)
            self.live_wpm = self.performance_tracker.get_current_wpm()
        
        correct_chars = 0
        self.error_positions = []
        
        for i in range(min(typed_length, len(self.current_text))):
            if self.user_input[i] == self.current_text[i]:
                correct_chars += 1
            else:
                self.error_positions.append({
                    'position': i,
                    'expected': self.current_text[i],
                    'typed': self.user_input[i],
                    'context': self.current_text[max(0, i-2):i+3]
                })
        
        self.correct_chars = correct_chars
        self.mistakes = len(self.error_positions)
        
        if typed_length > 0:
            self.current_accuracy = (correct_chars / typed_length) * 100
        else:
            self.current_accuracy = 100
    
    def run_test(self, word_list, test_mode="standard"):
        self.current_text = " ".join(word_list)
        self.user_input = ""
        self.start_time = None
        self.end_time = None
        self.current_wpm = 0
        self.current_accuracy = 100
        self.live_wpm = 0
        self.mistakes = 0
        self.error_positions = []
        self.is_running = True
        
        self.performance_tracker = PerformanceTracker()
        
        self.display_text_with_progress()
        print(f"\n{Colors.YELLOW}🚀 Start typing to begin the test...{Colors.END}")
        print(f"{Colors.GRAY}Press Ctrl+C to stop the test early | ESC for menu{Colors.END}")
        
        self.start_real_time_wpm_thread()
        
        try:
            while self.is_running:
                char = self.get_char()
                
                if char == '\x03':  # Ctrl+C
                    break
                elif char == '\x1b':  # ESC
                    print(f"\n{Colors.YELLOW}Test paused. Press Enter to continue or 'q' to quit...{Colors.END}")
                    choice = input()
                    if choice.lower() == 'q':
                        break
                    continue
                elif char == '\r' or char == '\n':  # Enter
                    if self.user_input.strip():
                        self.user_input += " "
                elif char == '\x08' or char == '\x7f':  # Backspace
                    if self.user_input:
                        self.user_input = self.user_input[:-1]
                elif char.isprintable():
                    if not self.start_time:
                        self.start_time = time.time()
                    
                    self.user_input += char
                
                self.calculate_stats()
                self.display_text_with_progress()
                
                if len(self.user_input) >= len(self.current_text):
                    self.end_time = time.time()
                    break
        
        except KeyboardInterrupt:
            pass
        
        self.stop_wpm_thread = True
        if self.wpm_update_thread:
            self.wpm_update_thread.join(timeout=1)
        
        self.is_running = False
        
        self.show_enhanced_results()
    
    def show_enhanced_results(self):
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}╔═══════════════════════════════════════════════════════════════╗")
        print(f"║                        TEST RESULTS                          ║")
        print(f"╚═══════════════════════════════════════════════════════════════╝{Colors.END}")
        
        if not self.start_time:
            print(f"\n{Colors.RED}No test data to display.{Colors.END}")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            return
        
        test_duration = (self.end_time or time.time()) - self.start_time
        words_typed = len(self.user_input.split())
        chars_typed = len(self.user_input)
        
        performance_insights = self.performance_tracker.get_performance_insights()
        
        print(f"\n{Colors.YELLOW}⏱️  Time: {Colors.END}{test_duration:.1f} seconds")
        print(f"{Colors.YELLOW}🏃 WPM: {Colors.END}{self.current_wpm:.1f}")
        print(f"{Colors.YELLOW}🎯 Accuracy: {Colors.END}{self.current_accuracy:.1f}%")
        print(f"{Colors.YELLOW}❌ Mistakes: {Colors.END}{self.mistakes}")
        print(f"{Colors.YELLOW}📝 Words Typed: {Colors.END}{words_typed}")
        print(f"{Colors.YELLOW}🔤 Characters: {Colors.END}{chars_typed}")
        
        consistency = self.performance_tracker.calculate_consistency_score()
        print(f"{Colors.YELLOW}📊 Consistency: {Colors.END}{consistency:.1f}%")
        
        if performance_insights.get('status') != 'insufficient_data':
            rhythm_data = performance_insights.get('rhythm_analysis', {})
            if rhythm_data.get('status') != 'insufficient_data':
                rhythm_category = rhythm_data.get('rhythm_category', 'unknown')
                rhythm_score = rhythm_data.get('velocity_consistency', 0)
                print(f"{Colors.YELLOW}🎵 Rhythm: {Colors.END}{rhythm_category.replace('_', ' ').title()} ({rhythm_score:.1f}%)")
        
        input(f"\n{Colors.CYAN}📊 Core metrics displayed. Press Enter to see performance analysis...{Colors.END}")
        
        self.display_enhanced_performance_analysis(performance_insights)
        
        input(f"\n{Colors.CYAN}📈 Performance analysis complete. Press Enter to continue...{Colors.END}")
        
        result_data = (
            self.current_wpm, self.current_accuracy, self.mistakes,
            test_duration, "adaptive" if self.auto_difficulty else "manual",
            words_typed, chars_typed, self.correct_chars
        )
        test_id = self.db_manager.save_test_result(result_data)
        
        if self.error_positions:
            enhanced_patterns = self.performance_tracker.detect_typing_patterns(self.user_input, self.current_text)
            
            error_data = []
            for error in self.error_positions:
                error_data.append((
                    error['expected'], error['typed'], 
                    error['position'], error['context']
                ))
            self.db_manager.save_error_pattern(test_id, error_data)
            
            self.display_enhanced_error_analysis(enhanced_patterns)
        
        self.wpm_history.append(self.current_wpm)
        self.accuracy_history.append(self.current_accuracy)
        self.total_tests += 1
        self.total_time_typed += test_duration
        
        self.difficulty_adjuster.add_performance(self.current_wpm, self.current_accuracy)
        
        self.check_achievements(test_duration)
        
        if hasattr(self, '_new_achievements_displayed') and self._new_achievements_displayed:
            input(f"\n{Colors.CYAN}🎉 Achievement notifications shown. Press Enter for recommendations...{Colors.END}")
            self._new_achievements_displayed = False
        
        self.show_enhanced_performance_feedback(performance_insights)
        
        input(f"\n{Colors.CYAN}💡 Recommendations displayed. Press Enter to return to main menu...{Colors.END}")
    
    def display_enhanced_performance_analysis(self, performance_insights):
        """Display enhanced performance analysis with rhythm and pattern insights"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}📈 Enhanced Performance Analysis:{Colors.END}")
        
        if self.current_wpm >= 80:
            speed_rating = f"{Colors.GREEN}🚀 Excellent{Colors.END}"
        elif self.current_wpm >= 60:
            speed_rating = f"{Colors.YELLOW}💪 Good{Colors.END}"
        elif self.current_wpm >= 40:
            speed_rating = f"{Colors.BLUE}📈 Average{Colors.END}"
        else:
            speed_rating = f"{Colors.MAGENTA}🎯 Developing{Colors.END}"
        
        print(f"  Speed Rating: {speed_rating}")
        
        if self.current_accuracy >= 98:
            accuracy_rating = f"{Colors.GREEN}🎯 Perfect{Colors.END}"
        elif self.current_accuracy >= 95:
            accuracy_rating = f"{Colors.YELLOW}👍 Excellent{Colors.END}"
        elif self.current_accuracy >= 90:
            accuracy_rating = f"{Colors.BLUE}👌 Good{Colors.END}"
        else:
            accuracy_rating = f"{Colors.RED}🎯 Needs Work{Colors.END}"
        
        print(f"  Accuracy Rating: {accuracy_rating}")
        
        if performance_insights.get('status') != 'insufficient_data':
            current_perf = performance_insights.get('current_performance', {})
            trend = current_perf.get('performance_trend', 'stable')
            
            trend_display = {
                'improving': f"{Colors.GREEN}📈 Improving{Colors.END}",
                'declining': f"{Colors.RED}📉 Declining{Colors.END}",
                'stable': f"{Colors.YELLOW}➡️  Stable{Colors.END}"
            }
            
            print(f"  Performance Trend: {trend_display.get(trend, trend)}")
            
            rhythm_data = performance_insights.get('rhythm_analysis', {})
            if rhythm_data.get('status') != 'insufficient_data':
                accel_ratio = rhythm_data.get('acceleration_ratio', 0)
                decel_ratio = rhythm_data.get('deceleration_ratio', 0)
                
                if accel_ratio > 0.6:
                    print(f"  Typing Pattern: {Colors.GREEN}⚡ Accelerating{Colors.END} (building speed)")
                elif decel_ratio > 0.6:
                    print(f"  Typing Pattern: {Colors.YELLOW}🔽 Decelerating{Colors.END} (slowing down)")
                else:
                    print(f"  Typing Pattern: {Colors.BLUE}⚖️  Balanced{Colors.END} (steady pace)")
    
    def display_enhanced_error_analysis(self, enhanced_patterns):
        """Display enhanced error analysis with finger mapping and clustering"""
        print(f"\n{Colors.RED}🔍 Enhanced Error Analysis:{Colors.END}")
        
        if self.error_positions:
            common_errors = defaultdict(int)
            for error in self.error_positions:
                error_type = f"{error['expected']}→{error['typed']}"
                common_errors[error_type] += 1
            
            print(f"  Most Common Character Errors:")
            for error_type, count in sorted(common_errors.items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"    {error_type}: {count} times")
        
        finger_errors = enhanced_patterns.get('finger_errors', {})
        if finger_errors:
            print(f"\n  Finger-Specific Errors:")
            sorted_fingers = sorted(finger_errors.items(), key=lambda x: x[1], reverse=True)[:3]
            for finger, count in sorted_fingers:
                finger_name = finger.replace('_', ' ').title()
                print(f"    {finger_name}: {count} errors")
        
        error_clusters = enhanced_patterns.get('error_clusters', [])
        if error_clusters:
            print(f"\n  Error Hotspots:")
            for cluster in error_clusters[:2]:  # Show top 2 clusters
                start_pos = cluster['window_start']
                density = cluster['error_density'] * 100
                print(f"    Characters {start_pos}-{start_pos+10}: {density:.1f}% error rate")
        
        trigram_errors = enhanced_patterns.get('trigram_errors', {})
        if trigram_errors:
            print(f"\n  Problem Letter Combinations:")
            sorted_trigrams = sorted(trigram_errors.items(), key=lambda x: x[1], reverse=True)[:3]
            for trigram, count in sorted_trigrams:
                print(f"    '{trigram}': {count} errors")
    
    def show_enhanced_performance_feedback(self, performance_insights):
        """Show enhanced personalized performance feedback with AI-generated recommendations"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}💡 Enhanced Personalized Recommendations:{Colors.END}")
        
        if performance_insights.get('status') != 'insufficient_data':
            recommendations = performance_insights.get('recommendations', [])
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    print(f"  {i}. {rec}")
            else:
                self.show_traditional_recommendations()
        else:
            self.show_traditional_recommendations()
        
        if len(self.wpm_history) >= 5:
            recent_avg = sum(list(self.wpm_history)[-3:]) / 3
            older_avg = sum(list(self.wmp_history)[-6:-3]) / 3 if len(self.wpm_history) >= 6 else recent_avg
            
            if recent_avg > older_avg + 2:
                print(f"{Colors.GREEN}  🎉 Excellent! Your speed improved by {recent_avg - older_avg:.1f} WPM!{Colors.END}")
            elif recent_avg < older_avg - 2:
                print(f"{Colors.YELLOW}  📚 Consider taking a break and practicing fundamentals{Colors.END}")
            
        if performance_insights.get('status') != 'insufficient_data':
            rhythm_data = performance_insights.get('rhythm_analysis', {})
            if rhythm_data.get('status') != 'insufficient_data':
                rhythm_category = rhythm_data.get('rhythm_category', 'unknown')
                if rhythm_category == 'inconsistent':
                    print(f"{Colors.CYAN}  🎵 Try practicing with a steady rhythm - consistency beats speed!{Colors.END}")
                elif rhythm_category == 'very_consistent':
                    print(f"{Colors.GREEN}  🎵 Excellent rhythm! Your typing flow is very smooth.{Colors.END}")
    
    def show_traditional_recommendations(self):
        """Fallback traditional recommendations"""
        if self.current_wpm < 40:
            print(f"  • Focus on maintaining a steady rhythm rather than speed")
            print(f"  • Practice finger positioning and muscle memory")
        elif self.current_wpm < 60:
            print(f"  • Try typing without looking at the keyboard")
            print(f"  • Practice common word combinations")
        
        if self.current_accuracy < 95:
            print(f"  • Slow down and focus on accuracy first")
            print(f"  • Practice problematic character combinations")
        
        if self.error_positions:
            finger_errors = self.analyze_finger_errors()
            if finger_errors:
                print(f"  • Focus on training these fingers: {', '.join(finger_errors)}")
    
    def display_performance_analysis(self):
        """Display detailed performance analysis"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}📈 Performance Analysis:{Colors.END}")
        
        if self.current_wpm >= 80:
            speed_rating = f"{Colors.GREEN}🚀 Excellent{Colors.END}"
        elif self.current_wpm >= 60:
            speed_rating = f"{Colors.YELLOW}💪 Good{Colors.END}"
        elif self.current_wpm >= 40:
            speed_rating = f"{Colors.BLUE}📈 Average{Colors.END}"
        else:
            speed_rating = f"{Colors.MAGENTA}🎯 Developing{Colors.END}"
        
        print(f"  Speed Rating: {speed_rating}")
        
        if self.current_accuracy >= 98:
            accuracy_rating = f"{Colors.GREEN}🎯 Perfect{Colors.END}"
        elif self.current_accuracy >= 95:
            accuracy_rating = f"{Colors.YELLOW}👍 Excellent{Colors.END}"
        elif self.current_accuracy >= 90:
            accuracy_rating = f"{Colors.BLUE}👌 Good{Colors.END}"
        else:
            accuracy_rating = f"{Colors.RED}🎯 Needs Work{Colors.END}"
        
        print(f"  Accuracy Rating: {accuracy_rating}")
        
        if self.error_positions:
            common_errors = defaultdict(int)
            for error in self.error_positions:
                error_type = f"{error['expected']}→{error['typed']}"
                common_errors[error_type] += 1
            
            print(f"\n{Colors.RED}🔍 Most Common Errors:{Colors.END}")
            for error_type, count in sorted(common_errors.items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"    {error_type}: {count} times")
    
    def check_achievements(self, test_duration):
        """Check and unlock achievements"""
        new_achievements = []
        
        if self.current_wpm >= 100 and "speed_machine" not in self.achievements_unlocked:
            if self.db_manager.unlock_achievement("speed_machine"):
                new_achievements.append("speed_machine")
        elif self.current_wpm >= 80 and "speed_demon" not in self.achievements_unlocked:
            if self.db_manager.unlock_achievement("speed_demon"):
                new_achievements.append("speed_demon")
        
        if self.current_accuracy == 100 and "perfectionist" not in self.achievements_unlocked:
            if self.db_manager.unlock_achievement("perfectionist"):
                new_achievements.append("perfectionist")
        elif self.current_accuracy >= 98 and "accuracy_master" not in self.achievements_unlocked:
            if self.db_manager.unlock_achievement("accuracy_master"):
                new_achievements.append("accuracy_master")
        
        if test_duration >= 300 and "marathon" not in self.achievements_unlocked:  # 5 minutes
            if self.db_manager.unlock_achievement("marathon"):
                new_achievements.append("marathon")
        
        if self.total_tests >= 10 and "persistent" not in self.achievements_unlocked:
            if self.db_manager.unlock_achievement("persistent"):
                new_achievements.append("persistent")
        
        current_hour = datetime.now().hour
        if current_hour < 8 and "early_bird" not in self.achievements_unlocked:
            if self.db_manager.unlock_achievement("early_bird"):
                new_achievements.append("early_bird")
        elif current_hour >= 22 and "night_owl" not in self.achievements_unlocked:
            if self.db_manager.unlock_achievement("night_owl"):
                new_achievements.append("night_owl")
        
        if new_achievements:
            print(f"\n{Colors.MAGENTA}{Colors.BOLD}🎉 NEW ACHIEVEMENTS UNLOCKED! 🎉{Colors.END}")
            for ach_id in new_achievements:
                ach = ACHIEVEMENTS[ach_id]
                print(f"{Colors.YELLOW}{ach['icon']} {ach['name']}: {ach['desc']}{Colors.END}")
                self.achievements_unlocked.add(ach_id)
            self._new_achievements_displayed = True
        else:
            self._new_achievements_displayed = False
    
    def show_performance_feedback(self):
        """Show personalized performance feedback and recommendations"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}💡 Personalized Recommendations:{Colors.END}")
        
        if self.current_wpm < 40:
            print(f"  • Focus on maintaining a steady rhythm rather than speed")
            print(f"  • Practice finger positioning and muscle memory")
        elif self.current_wpm < 60:
            print(f"  • Try typing without looking at the keyboard")
            print(f"  • Practice common word combinations")
        
        if self.current_accuracy < 95:
            print(f"  • Slow down and focus on accuracy first")
            print(f"  • Practice problematic character combinations")
        
        if self.error_positions:
            finger_errors = self.analyze_finger_errors()
            if finger_errors:
                print(f"  • Focus on training these fingers: {', '.join(finger_errors)}")
        
        if len(self.wpm_history) >= 5:
            recent_avg = sum(list(self.wpm_history)[-3:]) / 3
            older_avg = sum(list(self.wpm_history)[-6:-3]) / 3 if len(self.wpm_history) >= 6 else recent_avg
            
            if recent_avg > older_avg + 2:
                print(f"{Colors.GREEN}  🎉 Great progress! Your speed is improving!{Colors.END}")
            elif recent_avg < older_avg - 2:
                print(f"{Colors.YELLOW}  📚 Consider taking a break and practicing fundamentals{Colors.END}")
    
    def analyze_finger_errors(self):
        """Analyze which fingers are making the most errors"""
        finger_map = {
            'left_pinky': 'qaz',
            'left_ring': 'wsx',
            'left_middle': 'edc',
            'left_index': 'rfvtgb',
            'right_index': 'yhnujm',
            'right_middle': 'ik,',
            'right_ring': 'ol.',
            'right_pinky': 'p;/[\']'
        }
        
        finger_errors = defaultdict(int)
        for error in self.error_positions:
            char = error['expected'].lower()
            for finger, chars in finger_map.items():
                if char in chars:
                    finger_errors[finger] += 1
                    break
        
        problem_fingers = sorted(finger_errors.items(), key=lambda x: x[1], reverse=True)[:2]
        return [finger.replace('_', ' ') for finger, count in problem_fingers if count > 1]
    
    def get_char(self):
        """Get a single character input with robust error handling"""
        try:
            if os.name == 'nt':  # Windows
                import msvcrt
                char = msvcrt.getch()
                if isinstance(char, bytes):
                    try:
                        return char.decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            return char.decode('cp1252')  # Windows fallback
                        except UnicodeDecodeError:
                            return char.decode('ascii', errors='ignore')
                return char
            else:  # Unix/Linux/macOS
                import termios, tty
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    char = sys.stdin.read(1)
                    return char
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except (UnicodeDecodeError, ImportError, OSError, AttributeError) as e:
            try:
                return input("Press Enter and type a character: ")[:1]
            except (EOFError, KeyboardInterrupt):
                return '\x03'  # Return Ctrl+C signal
    
    def show_advanced_statistics(self):
        """Display comprehensive statistics and analytics"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}╔═══════════════════════════════════════════════════════════════╗")
        print(f"║                    ADVANCED STATISTICS                       ║")
        print(f"╚═══════════════════════════════════════════════════════════════╝{Colors.END}")
        
        stats_30d = self.db_manager.get_statistics(days=30)
        stats_7d = self.db_manager.get_statistics(days=7)
        
        if not stats_30d:
            print(f"\n{Colors.YELLOW}No test results yet. Take some tests first!{Colors.END}")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            return
        
        wpm_scores = [stat[2] for stat in stats_30d]
        accuracy_scores = [stat[3] for stat in stats_30d]
        
        print(f"\n{Colors.YELLOW}📊 30-Day Performance Summary:{Colors.END}")
        print(f"  Tests completed: {len(stats_30d)}")
        print(f"  Average WPM: {statistics.mean(wpm_scores):.1f}")
        print(f"  Best WPM: {max(wpm_scores):.1f}")
        print(f"  WPM Standard Deviation: {statistics.stdev(wpm_scores) if len(wpm_scores) > 1 else 0:.1f}")
        print(f"  Average Accuracy: {statistics.mean(accuracy_scores):.1f}%")
        print(f"  Best Accuracy: {max(accuracy_scores):.1f}%")
        
        if stats_7d:
            week_wpm = [stat[2] for stat in stats_7d]
            week_acc = [stat[3] for stat in stats_7d]
            print(f"\n{Colors.BLUE}📈 This Week vs Last 30 Days:{Colors.END}")
            print(f"  Weekly WPM: {statistics.mean(week_wpm):.1f} (Δ{statistics.mean(week_wpm) - statistics.mean(wpm_scores):+.1f})")
            print(f"  Weekly Accuracy: {statistics.mean(week_acc):.1f}% (Δ{statistics.mean(week_acc) - statistics.mean(accuracy_scores):+.1f}%)")
        
        print(f"\n{Colors.RED}🔍 Error Analysis:{Colors.END}")
        error_patterns = self.db_manager.get_error_analysis(days=30)
        if error_patterns:
            print("  Most common mistakes:")
            for i, (intended, typed, frequency) in enumerate(error_patterns[:5]):
                print(f"    {i+1}. '{intended}' → '{typed}' ({frequency} times)")
        else:
            print("  No error data available")
        
        self.show_performance_trends(stats_30d)
        
        streak = self.db_manager.get_streak_count()
        print(f"\n{Colors.MAGENTA}🔥 Streak Information:{Colors.END}")
        print(f"  Current streak: {streak} days")
        print(f"  Daily goal progress: {len(self.db_manager.get_statistics(days=1))}/{self.daily_goal} tests today")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def show_performance_trends(self, stats):
        """Show performance trends over time"""
        print(f"\n{Colors.GREEN}📈 Performance Trends:{Colors.END}")
        
        if len(stats) < 5:
            print("  Need more data for trend analysis")
            return
        
        recent_stats = stats[:10]
        wpm_trend = [stat[2] for stat in recent_stats]
        acc_trend = [stat[3] for stat in recent_stats]
        
        x = list(range(len(wpm_trend)))
        wpm_slope = self.calculate_trend_slope(x, wpm_trend)
        acc_slope = self.calculate_trend_slope(x, acc_trend)
        
        wpm_direction = "📈 Improving" if wpm_slope > 0.5 else "📉 Declining" if wpm_slope < -0.5 else "➡️  Stable"
        acc_direction = "📈 Improving" if acc_slope > 0.1 else "📉 Declining" if acc_slope < -0.1 else "➡️  Stable"
        
        print(f"  WPM Trend: {wpm_direction} ({wpm_slope:+.1f} WPM per test)")
        print(f"  Accuracy Trend: {acc_direction} ({acc_slope:+.1f}% per test)")
    
    def calculate_trend_slope(self, x, y):
        """Calculate simple linear regression slope"""
        n = len(x)
        if n < 2:
            return 0
        
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        return numerator / denominator if denominator != 0 else 0
    
    def show_achievements_menu(self):
        """Display achievements menu with progress tracking"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}╔═══════════════════════════════════════════════════════════════╗")
        print(f"║                         ACHIEVEMENTS                         ║")
        print(f"╚═══════════════════════════════════════════════════════════════╝{Colors.END}")
        
        unlocked_achievements = self.db_manager.get_achievements()
        unlocked_ids = {ach[0] for ach in unlocked_achievements}
        
        print(f"\n{Colors.YELLOW}🏆 Unlocked: {len(unlocked_ids)}/{len(ACHIEVEMENTS)}{Colors.END}")
        
        categories = {
            "Speed": ["speed_demon", "speed_machine"],
            "Accuracy": ["accuracy_master", "perfectionist"],
            "Persistence": ["persistent", "marathon", "consistent", "streak_master"],
            "Time-based": ["early_bird", "night_owl", "weekend_warrior"],
            "Progress": ["improver"]
        }
        
        for category, achievement_ids in categories.items():
            print(f"\n{Colors.BLUE}{Colors.BOLD}{category}:{Colors.END}")
            for ach_id in achievement_ids:
                if ach_id in ACHIEVEMENTS:
                    ach = ACHIEVEMENTS[ach_id]
                    status = f"{Colors.GREEN}✓" if ach_id in unlocked_ids else f"{Colors.GRAY}✗"
                    print(f"  {status} {ach['icon']} {ach['name']}: {ach['desc']}{Colors.END}")
        
        print(f"\n{Colors.MAGENTA}📊 Progress towards next achievements:{Colors.END}")
        self.show_achievement_progress(unlocked_ids)
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def show_achievement_progress(self, unlocked_ids):
        """Show progress towards unlocking achievements"""
        stats = self.db_manager.get_statistics(days=30)
        
        if not stats:
            print("  Complete some tests to see progress!")
            return
        
        best_wpm = max(stat[2] for stat in stats) if stats else 0
        best_acc = max(stat[3] for stat in stats) if stats else 0
        test_count = len(stats)
        
        if "speed_demon" not in unlocked_ids:
            progress = min(100, (best_wpm / 80) * 100)
            print(f"  🚀 Speed Demon: {progress:.0f}% (Best: {best_wpm:.1f}/80 WPM)")
        
        if "speed_machine" not in unlocked_ids:
            progress = min(100, (best_wpm / 100) * 100)
            print(f"  ⚡ Speed Machine: {progress:.0f}% (Best: {best_wpm:.1f}/100 WPM)")
        
        if "accuracy_master" not in unlocked_ids:
            progress = min(100, (best_acc / 98) * 100)
            print(f"  🎯 Accuracy Master: {progress:.0f}% (Best: {best_acc:.1f}/98% accuracy)")
        
        if "persistent" not in unlocked_ids:
            progress = min(100, (test_count / 10) * 100)
            print(f"  🔥 Persistent: {progress:.0f}% ({test_count}/10 tests)")
    
    def show_settings_menu(self):
        """Display and handle settings menu"""
        while True:
            self.clear_screen()
            print(f"{Colors.CYAN}{Colors.BOLD}╔═══════════════════════════════════════════════════════════════╗")
            print(f"║                           SETTINGS                           ║")
            print(f"╚═══════════════════════════════════════════════════════════════╝{Colors.END}")
            
            print(f"\n{Colors.YELLOW}Current Settings:{Colors.END}")
            print(f"1. Auto Difficulty: {Colors.GREEN + 'ON' if self.auto_difficulty else Colors.RED + 'OFF'}{Colors.END}")
            print(f"2. Live WPM Display: {Colors.GREEN + 'ON' if self.show_live_wpm else Colors.RED + 'OFF'}{Colors.END}")
            print(f"3. Text Wrap Width: {self.text_wrap_width} characters")
            print(f"4. Daily Goal: {self.daily_goal} tests")
            print(f"5. Reset All Statistics")
            print(f"6. Export Statistics")
            print(f"7. Back to Main Menu")
            
            choice = input(f"\n{Colors.CYAN}Choose setting to change (1-7): {Colors.END}")
            
            if choice == "1":
                self.auto_difficulty = not self.auto_difficulty
                print(f"Auto difficulty {'enabled' if self.auto_difficulty else 'disabled'}")
                time.sleep(1)
            elif choice == "2":
                self.show_live_wpm = not self.show_live_wpm
                print(f"Live WPM display {'enabled' if self.show_live_wpm else 'disabled'}")
                time.sleep(1)
            elif choice == "3":
                try:
                    new_width = int(input("Enter new text wrap width (40-120): "))
                    self.text_wrap_width = max(40, min(120, new_width))
                    print(f"Text wrap width set to {self.text_wrap_width}")
                    time.sleep(1)
                except ValueError:
                    print("Invalid input")
                    time.sleep(1)
            elif choice == "4":
                try:
                    new_goal = int(input("Enter daily goal (1-20): "))
                    self.daily_goal = max(1, min(20, new_goal))
                    print(f"Daily goal set to {self.daily_goal}")
                    time.sleep(1)
                except ValueError:
                    print("Invalid input")
                    time.sleep(1)
            elif choice == "5":
                confirm = input("Reset ALL statistics? Type 'YES' to confirm: ")
                if confirm == "YES":
                    self.reset_statistics()
                    print("Statistics reset successfully")
                    time.sleep(2)
            elif choice == "6":
                self.export_statistics()
            elif choice == "7":
                break
            else:
                print("Invalid choice")
                time.sleep(1)
    
    def reset_statistics(self):
        """Reset all user statistics"""
        try:
            os.remove("typing_stats.db")
            self.db_manager = DatabaseManager()  # Recreate database
            self.wpm_history.clear()
            self.accuracy_history.clear()
            self.achievements_unlocked.clear()
            self.total_tests = 0
            self.current_streak = 0
        except Exception as e:
            print(f"Error resetting statistics: {e}")
    
    def export_statistics(self):
        """Export statistics to JSON file"""
        try:
            stats = self.db_manager.get_statistics(days=365)  # Last year
            achievements = self.db_manager.get_achievements()
            
            export_data = {
                "export_date": datetime.now().isoformat(),
                "total_tests": len(stats),
                "statistics": [
                    {
                        "date": stat[1],
                        "wpm": stat[2],
                        "accuracy": stat[3],
                        "mistakes": stat[4],
                        "duration": stat[5],
                        "difficulty": stat[6]
                    } for stat in stats
                ],
                "achievements": [
                    {
                        "achievement_id": ach[0],
                        "date_earned": ach[1]
                    } for ach in achievements
                ]
            }
            
            filename = f"typing_stats_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"Statistics exported to {filename}")
            time.sleep(2)
        except Exception as e:
            print(f"Error exporting statistics: {e}")
            time.sleep(2)
    
    def show_typing_lessons(self):
        """Display typing lessons menu"""
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}╔═══════════════════════════════════════════════════════════════╗")
        print(f"║                        TYPING LESSONS                        ║")
        print(f"╚═══════════════════════════════════════════════════════════════╝{Colors.END}")
        
        lessons = {
            "1": {
                "name": "Home Row Basics",
                "desc": "Practice ASDF JKL; keys",
                "words": ["as", "sad", "lad", "ask", "all", "fall", "las", "fad", "dal", "lass"]
            },
            "2": {
                "name": "Top Row Training",
                "desc": "Practice QWERT YUIOP keys",
                "words": ["quit", "type", "your", "power", "quote", "write", "quite", "worry", "prior", "tower"]
            },
            "3": {
                "name": "Bottom Row Challenge",
                "desc": "Practice ZXCVB NM keys",
                "words": ["zone", "copy", "move", "never", "come", "voice", "been", "name", "back", "music"]
            },
            "4": {
                "name": "Number Row",
                "desc": "Practice 1234567890 keys",
                "words": ["123", "456", "789", "012", "147", "258", "369", "159", "357", "246"]
            },
            "5": {
                "name": "Special Characters",
                "desc": "Practice punctuation and symbols",
                "words": ["hello!", "world?", "yes,", "no.", "it's", "can't", "won't", "i'm", "you're", "we'll"]
            },
            "6": {
                "name": "Speed Drills",
                "desc": "Fast common word combinations",
                "words": ["the quick", "brown fox", "jumps over", "lazy dog", "pack my", "box with", "five dozen", "liquor jugs"]
            }
        }
        
        print(f"\n{Colors.YELLOW}Choose a lesson:{Colors.END}")
        for key, lesson in lessons.items():
            print(f"{Colors.WHITE}{key}. {lesson['name']}: {lesson['desc']}{Colors.END}")
        print(f"{Colors.WHITE}7. Back to Main Menu{Colors.END}")
        
        choice = input(f"\n{Colors.CYAN}Enter your choice (1-7): {Colors.END}")
        
        if choice in lessons:
            lesson = lessons[choice]
            print(f"\n{Colors.GREEN}Starting lesson: {lesson['name']}{Colors.END}")
            print(f"{lesson['desc']}")
            input(f"\n{Colors.CYAN}Press Enter to begin...{Colors.END}")
            
            lesson_words = lesson['words'] * 3  # Repeat each word 3 times
            random.shuffle(lesson_words)
            self.run_test(lesson_words, test_mode="lesson")
        elif choice == "7":
            return
        else:
            print(f"{Colors.RED}Invalid choice{Colors.END}")
            time.sleep(1)
            self.show_typing_lessons()
    
    def run(self):
        """Main game loop with enhanced menu system"""
        print(f"{Colors.GREEN}Welcome to SNAKETYPE - Enhanced Typing Trainer!{Colors.END}")
        print(f"{Colors.GRAY}Loading your profile...{Colors.END}")
        time.sleep(1)
        
        while True:
            choice = self.display_menu()
            
            try:
                if choice == "1":
                    words = self.get_word_list("1")
                    self.run_test(words)
                elif choice == "2":
                    words = self.get_word_list("2")
                    self.run_test(words)
                elif choice == "3":
                    words = self.get_word_list("3")
                    self.run_test(words)
                elif choice == "4":
                    words = self.get_word_list("4")
                    self.run_test(words)
                elif choice == "5":
                    words = self.get_word_list("adaptive")
                    print(f"\n{Colors.BLUE}🤖 Using adaptive difficulty level {self.difficulty_adjuster.get_recommended_difficulty()}{Colors.END}")
                    time.sleep(1)
                    self.run_test(words)
                elif choice == "6":
                    try:
                        word_count = int(input("Enter number of words (10-200): "))
                        word_count = max(10, min(200, word_count))
                        difficulty = input("Choose difficulty (1-4) or 'adaptive': ")
                        words = self.get_word_list(difficulty, word_count)
                        self.run_test(words)
                    except ValueError:
                        print("Invalid input. Using default settings.")
                        words = self.get_word_list("4")
                        self.run_test(words)
                elif choice == "7":
                    file_path = input("Enter path to text file: ").strip()
                    custom_words = self.load_custom_text(file_path)
                    if custom_words:
                        print(f"Loaded {len(custom_words)} words from custom file")
                        time.sleep(1)
                        self.run_test(custom_words)
                    else:
                        print("Failed to load custom text. Using default words.")
                        time.sleep(1)
                        words = self.get_word_list("4")
                        self.run_test(words)
                elif choice == "8":
                    self.show_advanced_statistics()
                elif choice == "9":
                    self.show_achievements_menu()
                elif choice == "10":
                    self.show_settings_menu()
                elif choice == "11":
                    self.show_typing_lessons()
                elif choice == "12":
                    print(f"\n{Colors.CYAN}Thanks for using SNAKETYPE! Keep practicing to improve your typing skills!{Colors.END}")
                    print(f"{Colors.GRAY}Your progress has been saved automatically.{Colors.END}")
                    break
                else:
                    print(f"{Colors.RED}Invalid choice. Please try again.{Colors.END}")
                    time.sleep(1)
            
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Exiting SnakeType...{Colors.END}")
                break
            except Exception as e:
                print(f"{Colors.RED}An error occurred: {e}{Colors.END}")
                print(f"{Colors.GRAY}Please try again or restart the application.{Colors.END}")
                time.sleep(2)

if __name__ == "__main__":
    try:
        game = TypingGame()
        game.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.CYAN}Goodbye! Happy typing!{Colors.END}")
    except Exception as e:
        print(f"Fatal error: {e}")
        print("Please check your Python installation and try again.")