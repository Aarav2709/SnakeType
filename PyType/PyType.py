import random
import time
import threading
import sys
import os
from collections import deque

# Word lists (you can expand these)
EASY_WORDS = ["cat", "dog", "run", "big", "sun", "car", "red", "box", "top", "mix", "cup", "bug", "hat", "pen", "egg", "jam", "win", "fix", "ten", "zip"]
MEDIUM_WORDS = ["python", "typing", "keyboard", "computer", "program", "function", "variable", "algorithm", "structure", "database", "network", "software", "hardware", "internet", "website", "application", "framework", "library", "module", "package"]
HARD_WORDS = ["programming", "development", "architecture", "implementation", "optimization", "documentation", "configuration", "authentication", "authorization", "synchronization", "asynchronous", "multithreading", "encapsulation", "inheritance", "polymorphism", "abstraction", "methodology", "infrastructure", "scalability", "maintainability"]

COMMON_WORDS = ["the", "of", "and", "to", "a", "in", "is", "it", "you", "that", "he", "was", "for", "on", "are", "as", "with", "his", "they", "i", "at", "be", "this", "have", "from", "or", "one", "had", "by", "word", "but", "not", "what", "all", "were", "we", "when", "your", "can", "said", "there", "each", "which", "she", "do", "how", "their", "if", "will", "up", "other", "about", "out", "many", "then", "them", "these", "so", "some", "her", "would", "make", "like", "into", "him", "has", "two", "more", "very", "after", "words", "first", "where", "been", "who", "its", "now", "find", "long", "down", "way", "may", "come", "could", "people", "my", "than", "water", "part", "time", "work", "right", "new", "take", "get", "place", "made", "live", "where", "after", "back", "little", "only", "round", "man", "year", "came", "show", "every", "good", "me", "give", "our", "under", "name", "very", "through", "just", "form", "sentence", "great", "think", "say", "help", "low", "line", "differ", "turn", "cause", "much", "mean", "before", "move", "right", "boy", "old", "too", "same", "tell", "does", "set", "three", "want", "air", "well", "also", "play", "small", "end", "put", "home", "read", "hand", "port", "large", "spell", "add", "even", "land", "here", "must", "big", "high", "such", "follow", "act", "why", "ask", "men", "change", "went", "light", "kind", "off", "need", "house", "picture", "try", "us", "again", "animal", "point", "mother", "world", "near", "build", "self", "earth", "father", "head", "stand", "own", "page", "should", "country", "found", "answer", "school", "grow", "study", "still", "learn", "plant", "cover", "food", "sun", "four", "between", "state", "keep", "eye", "never", "last", "let", "thought", "city", "tree", "cross", "farm", "hard", "start", "might", "story", "saw", "far", "sea", "draw", "left", "late", "run", "don't", "while", "press", "close", "night", "real", "life", "few", "north", "open", "seem", "together", "next", "white", "children", "begin", "got", "walk", "example", "ease", "paper", "group", "always", "music", "those", "both", "mark", "often", "letter", "until", "mile", "river", "car", "feet", "care", "second", "book", "carry", "took", "science", "eat", "room", "friend", "began", "idea", "fish", "mountain", "stop", "once", "base", "hear", "horse", "cut", "sure", "watch", "color", "face", "wood", "main", "enough", "plain", "girl", "usual", "young", "ready", "above", "ever", "red", "list", "though", "feel", "talk", "bird", "soon", "body", "dog", "family", "direct", "pose", "leave", "song", "measure", "door", "product", "black", "short", "numeral", "class", "wind", "question", "happen", "complete", "ship", "area", "half", "rock", "order", "fire", "south", "problem", "piece", "told", "knew", "pass", "since", "top", "whole", "king", "space", "heard", "best", "hour", "better", "during", "hundred", "five", "remember", "step", "early", "hold", "west", "ground", "interest", "reach", "fast", "verb", "sing", "listen", "six", "table", "travel", "less", "morning", "ten", "simple", "several", "vowel", "toward", "war", "lay", "against", "pattern", "slow", "center", "love", "person", "money", "serve", "appear", "road", "map", "rain", "rule", "govern", "pull", "cold", "notice", "voice", "unit", "power", "town", "fine", "certain", "fly", "fall", "lead", "cry", "dark", "machine", "note", "wait", "plan", "figure", "star", "box", "noun", "field", "rest", "correct", "able", "pound", "done", "beauty", "drive", "stood", "contain", "front", "teach", "week", "final", "gave", "green", "oh", "quick", "develop", "ocean", "warm", "free", "minute", "strong", "special", "mind", "behind", "clear", "tail", "produce", "fact", "street", "inch", "multiply", "nothing", "course", "stay", "wheel", "full", "force", "blue", "object", "decide", "surface", "deep", "moon", "island", "foot", "system", "busy", "test", "record", "boat", "common", "gold", "possible", "plane", "stead", "dry", "wonder", "laugh", "thousands", "ago", "ran", "check", "game", "shape", "equate", "hot", "miss", "brought", "heat", "snow", "tire", "bring", "yes", "distant", "fill", "east", "paint", "language", "among"]

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
    END = '\033[0m'

class TypingGame:
    def __init__(self):
        self.current_text = ""
        self.user_input = ""
        self.start_time = None
        self.wpm_history = deque(maxlen=10)
        self.accuracy_history = deque(maxlen=10)
        self.current_wpm = 0
        self.current_accuracy = 100
        self.typed_chars = 0
        self.correct_chars = 0
        self.mistakes = 0
        self.is_running = False
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_word_list(self, difficulty, word_count=50):
        if difficulty == "1":
            return random.choices(EASY_WORDS, k=word_count)
        elif difficulty == "2":
            return random.choices(MEDIUM_WORDS, k=word_count)
        elif difficulty == "3":
            return random.choices(HARD_WORDS, k=word_count)
        else:  # Common words mode
            return random.choices(COMMON_WORDS, k=word_count)
    
    def display_menu(self):
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}╔══════════════════════════════════════╗")
        print(f"║                PYTYPE                ║")
        print(f"╚══════════════════════════════════════╝{Colors.END}")
        print(f"\n{Colors.YELLOW}Choose your test mode:{Colors.END}")
        print(f"{Colors.WHITE}1. Easy Words (3-5 letters){Colors.END}")
        print(f"{Colors.WHITE}2. Medium Words (6-8 letters){Colors.END}")
        print(f"{Colors.WHITE}3. Hard Words (10+ letters){Colors.END}")
        print(f"{Colors.WHITE}4. Common Words (mixed){Colors.END}")
        print(f"{Colors.WHITE}5. Custom Test Length{Colors.END}")
        print(f"{Colors.WHITE}6. View Statistics{Colors.END}")
        print(f"{Colors.WHITE}7. Quit{Colors.END}")
        return input(f"\n{Colors.CYAN}Enter your choice (1-7): {Colors.END}")
    
    def display_text_with_progress(self):
        self.clear_screen()
        
        # Header with stats
        print(f"{Colors.CYAN}{Colors.BOLD}╔═══════════════════════════════════════════════════════════════╗")
        print(f"║  WPM: {self.current_wpm:3.0f}  │  Accuracy: {self.current_accuracy:5.1f}%  │  Mistakes: {self.mistakes:3d}  ║")
        print(f"╚═══════════════════════════════════════════════════════════════╝{Colors.END}")
        print()
        
        # Character-by-character comparison
        display_text = ""
        typed_length = len(self.user_input)
        
        for i, char in enumerate(self.current_text):
            if i < typed_length:
                # Character has been typed
                if self.user_input[i] == char:
                    # Correct character
                    if char == ' ':
                        display_text += f"{Colors.GREEN}·{Colors.END}"  # Show space as dot
                    else:
                        display_text += f"{Colors.GREEN}{char}{Colors.END}"
                else:
                    # Incorrect character
                    if char == ' ':
                        display_text += f"{Colors.RED}·{Colors.END}"  # Show space as dot
                    else:
                        display_text += f"{Colors.RED}{char}{Colors.END}"
            elif i == typed_length:
                # Current character to type (cursor position)
                if char == ' ':
                    display_text += f"{Colors.YELLOW}{Colors.UNDERLINE}·{Colors.END}"
                else:
                    display_text += f"{Colors.YELLOW}{Colors.UNDERLINE}{char}{Colors.END}"
            else:
                # Not yet typed
                if char == ' ':
                    display_text += "·"  # Show space as dot
                else:
                    display_text += f"{Colors.GRAY}{char}{Colors.END}"
        
        # Wrap text to fit screen better
        wrapped_text = ""
        line_length = 0
        max_line_length = 80
        
        i = 0
        while i < len(display_text):
            if display_text[i:i+7] == Colors:  # Color code detected
                # Find the end of the color code
                end_pos = display_text.find(f"{Colors.END}", i)
                if end_pos != -1:
                    wrapped_text += display_text[i:end_pos+len(f"{Colors.END}")]
                    i = end_pos + len(f"{Colors.END}")
                    line_length += 1
                else:
                    wrapped_text += display_text[i]
                    i += 1
                    line_length += 1
            else:
                wrapped_text += display_text[i]
                line_length += 1
                i += 1
            
            if line_length >= max_line_length and display_text[i-1:i] == " ":
                wrapped_text += "\n"
                line_length = 0
        
        print(f"{wrapped_text}\n")
        
        # Progress bar
        progress = typed_length / len(self.current_text) if len(self.current_text) > 0 else 0
        bar_length = 50
        filled_length = int(bar_length * progress)
        bar = f"{Colors.GREEN}{'█' * filled_length}{Colors.GRAY}{'░' * (bar_length - filled_length)}{Colors.END}"
        print(f"Progress: {bar} {progress*100:.1f}%")
    
    def calculate_stats(self):
        if not self.start_time or not self.user_input:
            return
        
        elapsed_time = time.time() - self.start_time
        typed_length = len(self.user_input)
        
        # Calculate WPM based on characters typed (standard is 5 chars = 1 word)
        if elapsed_time > 0:
            self.current_wpm = (typed_length / 5) / (elapsed_time / 60)
        
        # Calculate accuracy character by character
        correct_chars = 0
        total_chars = typed_length
        mistakes = 0
        
        for i in range(min(typed_length, len(self.current_text))):
            if self.user_input[i] == self.current_text[i]:
                correct_chars += 1
            else:
                mistakes += 1
        
        if total_chars > 0:
            self.current_accuracy = (correct_chars / total_chars) * 100
        else:
            self.current_accuracy = 100
            
        self.mistakes = mistakes
    
    def run_test(self, word_list):
        self.current_text = " ".join(word_list)
        self.user_input = ""
        self.start_time = None
        self.current_wpm = 0
        self.current_accuracy = 100
        self.mistakes = 0
        self.is_running = True
        
        self.display_text_with_progress()
        print(f"\n{Colors.YELLOW}Start typing to begin the test...{Colors.END}")
        print(f"{Colors.GRAY}Press Ctrl+C to stop the test early{Colors.END}")
        
        try:
            while self.is_running:
                char = self.get_char()
                
                if char == '\x03':  # Ctrl+C
                    break
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
                
                # Check if test is complete
                if len(self.user_input) >= len(self.current_text):
                    break
        
        except KeyboardInterrupt:
            pass
        
        self.is_running = False
        self.show_results()
    
    def get_char(self):
        try:
            if os.name == 'nt':  # Windows
                import msvcrt
                return msvcrt.getch().decode('utf-8')
            else:  # Unix/Linux/macOS
                import termios, tty
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    char = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                return char
        except:
            return input()
    
    def show_results(self):
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}╔═══════════════════════════════════════╗")
        print(f"║              TEST RESULTS             ║")
        print(f"╚═══════════════════════════════════════╝{Colors.END}")
        
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            print(f"\n{Colors.YELLOW}Time: {Colors.END}{elapsed_time:.1f} seconds")
        
        print(f"{Colors.YELLOW}WPM: {Colors.END}{self.current_wpm:.1f}")
        print(f"{Colors.YELLOW}Accuracy: {Colors.END}{self.current_accuracy:.1f}%")
        print(f"{Colors.YELLOW}Mistakes: {Colors.END}{self.mistakes}")
        
        # Store results
        self.wpm_history.append(self.current_wpm)
        self.accuracy_history.append(self.current_accuracy)
        
        # Performance feedback
        if self.current_wpm >= 60:
            print(f"\n{Colors.GREEN}🚀 Excellent speed! You're typing like a pro!{Colors.END}")
        elif self.current_wpm >= 40:
            print(f"\n{Colors.YELLOW}💪 Good speed! Keep practicing to reach 60+ WPM!{Colors.END}")
        elif self.current_wpm >= 20:
            print(f"\n{Colors.BLUE}📈 Nice progress! Practice more to improve speed!{Colors.END}")
        else:
            print(f"\n{Colors.MAGENTA}🎯 Focus on accuracy first, speed will follow!{Colors.END}")
        
        if self.current_accuracy >= 95:
            print(f"{Colors.GREEN}🎯 Outstanding accuracy!{Colors.END}")
        elif self.current_accuracy >= 85:
            print(f"{Colors.YELLOW}👍 Good accuracy! Try to reach 95%+{Colors.END}")
        else:
            print(f"{Colors.RED}🎯 Focus on accuracy - slow down and type carefully{Colors.END}")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def show_statistics(self):
        self.clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}╔═══════════════════════════════════════╗")
        print(f"║            YOUR STATISTICS            ║")
        print(f"╚═══════════════════════════════════════╝{Colors.END}")
        
        if not self.wpm_history:
            print(f"\n{Colors.YELLOW}No test results yet. Take a test first!{Colors.END}")
            input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            return
        
        avg_wpm = sum(self.wpm_history) / len(self.wpm_history)
        avg_accuracy = sum(self.accuracy_history) / len(self.accuracy_history)
        best_wpm = max(self.wpm_history)
        best_accuracy = max(self.accuracy_history)
        
        print(f"\n{Colors.YELLOW}Tests completed: {Colors.END}{len(self.wpm_history)}")
        print(f"{Colors.YELLOW}Average WPM: {Colors.END}{avg_wpm:.1f}")
        print(f"{Colors.YELLOW}Best WPM: {Colors.END}{best_wpm:.1f}")
        print(f"{Colors.YELLOW}Average Accuracy: {Colors.END}{avg_accuracy:.1f}%")
        print(f"{Colors.YELLOW}Best Accuracy: {Colors.END}{best_accuracy:.1f}%")
        
        print(f"\n{Colors.BLUE}Recent Results:{Colors.END}")
        for i, (wpm, acc) in enumerate(zip(list(self.wpm_history)[-5:], list(self.accuracy_history)[-5:])):
            print(f"{Colors.GRAY}Test {len(self.wpm_history)-4+i}: {Colors.END}{wpm:.1f} WPM, {acc:.1f}% accuracy")
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
    
    def run(self):
        while True:
            choice = self.display_menu()
            
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
                try:
                    word_count = int(input("Enter number of words (10-100): "))
                    word_count = max(10, min(100, word_count))
                    difficulty = input("Choose difficulty (1-4): ")
                    words = self.get_word_list(difficulty, word_count)
                    self.run_test(words)
                except ValueError:
                    print("Invalid input. Using default settings.")
                    words = self.get_word_list("4")
                    self.run_test(words)
            elif choice == "6":
                self.show_statistics()
            elif choice == "7":
                print(f"\n{Colors.CYAN}Thanks for playing! Keep practicing to improve your typing skills!{Colors.END}")
                break
            else:
                print(f"{Colors.RED}Invalid choice. Please try again.{Colors.END}")
                time.sleep(1)

if __name__ == "__main__":
    game = TypingGame()
    game.run()