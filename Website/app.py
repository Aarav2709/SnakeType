from flask import Flask, render_template, request, jsonify, session, url_for
from flask_socketio import SocketIO, emit
import random
import time
import json
import sqlite3
from datetime import datetime
import os
from pathlib import Path

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# For Vercel deployment
import tempfile
import shutil

# Create a temporary database path for Vercel
TEMP_DB_PATH = os.path.join(tempfile.gettempdir(), 'typing_stats.db')

def get_db_path():
    """Get the database path, handling Vercel's read-only filesystem"""
    if os.getenv('VERCEL'):
        # In Vercel, copy DB to temp if it doesn't exist
        if not os.path.exists(TEMP_DB_PATH):
            db_source = os.path.join(os.path.dirname(__file__), 'typing_stats.db')
            if os.path.exists(db_source):
                shutil.copy2(db_source, TEMP_DB_PATH)
            else:
                # Create new DB if source doesn't exist
                init_database(TEMP_DB_PATH)
        return TEMP_DB_PATH
    else:
        # Local development
        return os.path.join(os.path.dirname(__file__), 'typing_stats.db')

def init_database(db_path):
    """Initialize database tables"""
    try:
        conn = sqlite3.connect(db_path, timeout=30.0)
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
                correct_characters INTEGER NOT NULL CHECK(correct_characters >= 0),
                raw_wpm REAL DEFAULT 0,
                consistency_score REAL DEFAULT 0,
                test_mode TEXT DEFAULT 'standard'
            )
        ''')

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
                finger_mapped TEXT,
                bigram_context TEXT,
                FOREIGN KEY (test_id) REFERENCES test_results (id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_streaks (
                date DATE PRIMARY KEY,
                tests_completed INTEGER DEFAULT 0 CHECK(tests_completed >= 0)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        raise

EASY_WORDS = [
    "cat", "dog", "run", "big", "sun", "car", "red", "box", "top", "mix", "cup", "bug", "hat", "pen", "egg", "jam", "win", "fix", "ten", "zip",
    "art", "bat", "ban", "bad", "bag", "bed", "bet", "bid", "bit", "bow", "boy", "bus", "buy", "can", "cap", "cod", "cop", "cow", "cry", "cut",
    "dad", "day", "den", "dew", "did", "die", "dig", "dim", "dot", "dry", "due", "ear", "eat", "end", "eye", "far", "fat", "few", "fig", "fin",
    "fit", "fly", "for", "fox", "fun", "gap", "gas", "get", "got", "gun", "guy", "gym", "had", "ham", "has", "her", "hey", "hid", "him", "hip",
    "his", "hit", "hot", "how", "hug", "hut", "ice", "ill", "ink", "inn", "its", "jaw", "jet", "job", "joy", "key", "kid", "lab", "lap", "law",
    "lay", "leg", "let", "lid", "lie", "lip", "log", "lot", "low", "mad", "man", "map", "mat", "may", "men", "met", "mix", "mob", "mod", "mom",
    "mud", "nap", "net", "new", "nod", "nor", "not", "now", "nut", "oak", "odd", "off", "oil", "old", "one", "our", "out", "own", "pad", "pan",
    "pat", "pay", "pea", "pet", "pie", "pig", "pin", "pit", "pot", "pub", "put", "ran", "rap", "rat", "raw", "ray", "rib", "rid", "rip", "rob",
    "rot", "row", "rub", "rug", "sad", "sat", "saw", "say", "sea", "see", "set", "sew", "she", "shy", "sin", "sip", "sir", "sit", "six", "sky",
    "sly", "sob", "son", "sow", "spy", "sum", "tab", "tag", "tap", "tar", "tax", "tea", "the", "tie", "tin", "tip", "toe", "ton", "too", "toy",
    "try", "tub", "two", "use", "van", "war", "was", "way", "web", "wet", "who", "why", "wig", "win", "wit", "won", "wow", "yes", "yet", "you",
    "zip", "zoo", "age", "air", "all", "and", "any", "are", "arm", "ask", "ate", "bee", "bit", "but", "bye", "did", "dig", "dog", "eat", "egg"
]

MEDIUM_WORDS = [
    "python", "typing", "keyboard", "computer", "program", "function", "variable", "algorithm", "structure", "database", "network", "software", "hardware", "internet", "website", "application", "framework", "library", "module", "package",
    "about", "above", "abuse", "actor", "acute", "admit", "adopt", "adult", "after", "again", "agent", "agree", "ahead", "alarm", "album", "alert", "alien", "align", "alike", "alive", "allow", "alone", "along", "alter", "among", "anger", "angle", "angry", "apart", "apple", "apply", "arena", "argue", "arise", "array", "arrow", "aside", "asset", "avoid", "awake", "award", "aware", "badly", "baker", "bases", "basic", "beach", "began", "begin", "being", "below", "bench", "billy", "birth", "black", "blame", "blank", "blind", "block", "blood", "board", "boast", "bonus", "boost", "booth", "bound", "brain", "brand", "brass", "brave", "bread", "break", "breed", "brief", "bring", "broad", "broke", "brown", "build", "built", "buyer", "cable", "calif", "carry", "catch", "cause", "chain", "chair", "chaos", "charm", "chart", "chase", "cheap", "check", "chest", "chief", "child", "china", "chose", "civil", "claim", "class", "clean", "clear", "click", "climb", "clock", "close", "cloud", "coach", "coast", "could", "count", "court", "cover", "craft", "crash", "crazy", "cream", "crime", "cross", "crowd", "crown", "crude", "curve", "cycle", "daily", "dance", "dated", "dealt", "death", "debut", "delay", "depth", "doing", "doubt", "dozen", "draft", "drama", "drank", "drawn", "dream", "dress", "drill", "drink", "drive", "drove", "dying", "eager", "early", "earth", "eight", "elite", "empty", "enemy", "enjoy", "enter", "entry", "equal", "error", "event", "every", "exact", "exist", "extra", "faith", "false", "fault", "fiber", "field", "fifth", "fifty", "fight", "final", "first", "fixed", "flash", "fleet", "floor", "fluid", "focus", "force", "forth", "forty", "forum", "found", "frame", "frank", "fraud", "fresh", "front", "fruit", "fully", "funny", "giant", "given", "glass", "globe", "going", "grace", "grade", "grand", "grant", "grass", "grave", "great", "green", "gross", "group", "grown", "guard", "guess", "guest", "guide", "happy", "harry", "heart", "heavy", "hence", "henry", "horse", "hotel", "house", "human", "ideal", "image", "index", "inner", "input", "issue", "japan", "jimmy", "joint", "jones", "judge", "known", "label", "large", "laser", "later", "laugh", "layer", "learn", "lease", "least", "leave", "legal", "level", "lewis", "light", "limit", "links", "lives", "local", "loose", "lower", "lucky", "lunch", "lying", "magic", "major", "maker", "march", "maria", "match", "maybe", "mayor", "meant", "media", "metal", "might", "minor", "minus", "mixed", "model", "money", "month", "moral", "motor", "mount", "mouse", "mouth", "moved", "movie", "music", "needs", "never", "newly", "night", "noise", "north", "noted", "novel", "nurse", "occur", "ocean", "offer", "often", "order", "other", "ought", "paint", "panel", "paper", "party", "peace", "peter", "phase", "phone", "photo", "piano", "picked", "piece", "pilot", "pitch", "place", "plain", "plane", "plant", "plate", "plays", "plaza", "point", "pound", "power", "press", "price", "pride", "prime", "print", "prior", "prize", "proof", "proud", "prove", "queen", "quick", "quiet", "quite", "radio", "raise", "range", "rapid", "ratio", "reach", "ready", "realm", "rebel", "refer", "relax", "repay", "reply", "right", "rigid", "river", "robot", "roger", "roman", "rough", "round", "route", "royal", "rural", "sales", "scale", "scene", "scope", "score", "sense", "serve", "seven", "shall", "shape", "share", "sharp", "sheet", "shelf", "shell", "shift", "shine", "shirt", "shock", "shoot", "short", "shown", "sight", "silly", "since", "sixth", "sixty", "sized", "skill", "sleep", "slide", "small", "smart", "smile", "smith", "smoke", "snake", "snow", "solar", "solid", "solve", "sorry", "sound", "south", "space", "spare", "speak", "speed", "spend", "spent", "split", "spoke", "sport", "staff", "stage", "stake", "stand", "start", "state", "stays", "steal", "steel", "stick", "still", "stock", "stone", "stood", "store", "storm", "story", "strip", "stuck", "study", "stuff", "style", "sugar", "suite", "super", "sweet", "swift", "swing", "sword", "table", "taken", "taste", "taxes", "teach", "teams", "teens", "teeth", "terry", "texas", "thank", "theft", "their", "theme", "there", "these", "thick", "thing", "think", "third", "those", "three", "threw", "throw", "thumb", "tiger", "tight", "timer", "tired", "title", "today", "topic", "total", "touch", "tough", "tower", "track", "trade", "train", "treat", "trend", "trial", "tribe", "trick", "tried", "tries", "truck", "truly", "trust", "truth", "twice", "under", "undue", "union", "unity", "until", "upper", "upset", "urban", "usage", "usual", "valid", "value", "video", "virus", "visit", "vital", "vocal", "voice", "waste", "watch", "water", "wheel", "where", "which", "while", "white", "whole", "whose", "woman", "women", "world", "worry", "worse", "worst", "worth", "would", "write", "wrong", "wrote", "young", "youth"
]

HARD_WORDS = [
    "programming", "development", "architecture", "implementation", "optimization", "documentation", "configuration", "authentication", "authorization", "synchronization", "asynchronous", "multithreading", "encapsulation", "inheritance", "polymorphism", "abstraction", "methodology", "infrastructure", "scalability", "maintainability",
    "abandoned", "abilities", "absolutely", "abundance", "acceptable", "accessible", "accidentally", "accordance", "accounting", "accurately", "achievement", "acknowledge", "acquisition", "activities", "additional", "adequately", "adjustment", "admiration", "admissions", "advantages", "adventures", "advertising", "affection", "affordable", "afterwards", "aggressive", "agricultural", "algorithms", "allegiance", "allocation", "alternative", "ambiguous", "amendments", "ammunition", "analytical", "anniversary", "announcements", "answering", "anticipate", "apologized", "apparently", "appearance", "applicable", "application", "appointment", "appreciate", "approaching", "appropriate", "approximate", "arrangement", "artificial", "assessment", "assignment", "assistance", "associated", "assumption", "atmosphere", "attachment", "attractive", "attributes", "automotive", "background", "basketball", "battlefield", "beautiful", "beginning", "behaviour", "beneficial", "bibliography", "biological", "boundaries", "breakfast", "breathing", "brilliant", "broadcasting", "buildings", "businesses", "calculator", "campaigns", "candidates", "capabilities", "capacity", "carefully", "categories", "celebrate", "celebrity", "certainly", "challenge", "champions", "championship", "character", "characteristic", "charges", "charitable", "chemicals", "childhood", "chocolate", "christmas", "cigarette", "circumstances", "classical", "classroom", "clearance", "clearly", "climate", "clothing", "coalition", "cognitive", "collection", "collective", "colleges", "comfortable", "commander", "commentary", "commercial", "commission", "commitment", "committee", "commodity", "communicate", "communities", "companies", "comparison", "compatible", "compensation", "competence", "competition", "competitive", "complaints", "complement", "completely", "complexity", "compliance", "components", "composition", "compounds", "comprehensive", "compromise", "computers", "conceived", "concentration", "concepts", "concerned", "concluded", "conclusions", "condition", "conditional", "conducted", "conference", "confidence", "confident", "configure", "confirmation", "conflict", "confused", "congress", "connected", "connection", "consciousness", "consensus", "consequences", "conservation", "conservative", "considerable", "consideration", "consistent", "consolidate", "conspiracy", "constantly", "constitute", "constitution", "constraints", "constructed", "construction", "consulting", "consumption", "contained", "container", "contemporary", "content", "contest", "context", "continued", "continues", "continuous", "contract", "contrary", "contrast", "contribute", "contribution", "control", "controversial", "convention", "conversation", "conversion", "conviction", "cooperation", "coordination", "copyright", "corporate", "corporation", "correct", "correction", "correlation", "corruption", "counseling", "countries", "countless", "creativity", "credentials", "criteria", "criticism", "cultures", "currently", "curriculum", "customers", "dangerous", "database", "daughter", "decisions", "declaration", "dedicated", "definition", "definitely", "democracy", "democratic", "demonstrate", "department", "departure", "dependent", "depending", "deployment", "depression", "described", "description", "designed", "designer", "desperate", "destruction", "detailed", "detection", "determined", "developers", "developing", "development", "deviation", "devices", "diagnosis", "dialogue", "dictionary", "difference", "different", "difficult", "difficulty", "dimension", "dimensions", "dining", "direction", "directly", "director", "directory", "disabled", "disagree", "disappear", "disappointed", "disaster", "discipline", "discourse", "discover", "discovery", "discrimination", "discussion", "disease", "disguised", "dishonest", "disorders", "display", "disposal", "disposed", "disposition", "distance", "distinct", "distinction", "distinguish", "distribute", "distribution", "diversity", "dividend", "division", "document", "domestic", "dominant", "dominate", "donation", "downtown", "dramatic", "dramatically", "drawing", "dressed", "drinking", "driving", "dropped", "duration", "dynamic", "dynamics", "earnings", "earthquake", "eastern", "economic", "economics", "economies", "economy", "educated", "education", "educational", "effective", "effectively", "efficiency", "efficient", "efforts", "elderly", "elected", "election", "electric", "electrical", "electricity", "electronic", "electronics", "elements", "eligible", "eliminate", "elimination", "emergency", "emission", "emotions", "emphasis", "employee", "employees", "employer", "employment", "enables", "encoding", "encounter", "encourage", "enforcement", "engaging", "engineer", "engineering", "engines", "enhanced", "enhancement", "enormous", "enterprise", "entertaining", "entertainment", "enthusiasm", "entirely", "entities", "environment", "environmental", "episode", "equation", "equipment", "equivalent", "especially", "essential", "establish", "establishment", "estimated", "estimation", "ethical", "ethics", "evaluate", "evaluation", "evening", "events", "eventually", "everything", "evidence", "evolution", "exactly", "examination", "examined", "example", "excellence", "excellent", "exception", "exceptional", "exchange", "excitement", "exciting", "excluded", "exclusion", "exclusive", "excused", "executed", "execution", "executive", "executives", "exercise", "exercises", "exhibition", "existence", "existing", "expansion", "expectations", "expected", "expedite", "expensive", "experience", "experienced", "experiment", "experimental", "expert", "expertise", "explanation", "exploration", "explore", "explosion", "export", "exports", "exposed", "exposure", "expressed", "expression", "extension", "extensive", "external", "extraordinary", "extreme", "extremely", "facilities", "facility", "factors", "faculty", "failure", "familiar", "families", "famous", "fantastic", "fashion", "father", "feature", "featured", "features", "federal", "feedback", "feeling", "feelings", "festival", "fiction", "fifteen", "fighting", "figures", "finally", "finance", "financial", "findings", "finished", "firefox", "fishing", "fitness", "flexible", "floating", "flowers", "flowing", "foreign", "forever", "formation", "former", "formula", "fortune", "forward", "foundation", "founded", "founder", "fraction", "framework", "franchise", "freedom", "frequency", "frequent", "frequently", "friends", "friendship", "function", "functional", "functions", "fundamental", "funding", "furniture", "furthermore", "future", "gallery", "gaming", "garage", "garbage", "garden", "gathered", "general", "generally", "generate", "generation", "generator", "genetic", "gentleman", "gently", "genuine", "geography", "getting", "giving", "glasses", "global", "golden", "government", "governor", "grabbed", "gradually", "graduate", "graduation", "grammar", "granted", "graphics", "greater", "greatest", "greeting", "grocery", "ground", "growing", "growth", "guaranteed", "guardian", "guidance", "guidelines", "guilty", "habitat", "hammer", "handbook", "handle", "handled", "handles", "handling", "happened", "happening", "happiness", "hardware", "heading", "headlines", "headquarters", "health", "healthy", "hearing", "heated", "heavily", "height", "helpful", "helping", "heritage", "herself", "hidden", "highlight", "highly", "highway", "himself", "hispanic", "historic", "historical", "history", "holding", "holdings", "holiday", "homeless", "homepage", "honest", "horizontal", "horrible", "hospital", "household", "housing", "however", "hundred", "hungry", "hunting", "husband", "hypothesis", "identical", "identification", "identify", "identity", "ideology", "illegal", "illness", "illustrated", "illustration", "images", "imagination", "imagine", "immediate", "immediately", "immigrant", "immigration", "impact", "implement", "implementation", "implications", "implied", "importance", "important", "imposed", "impossible", "impressed", "impression", "impressive", "improve", "improved", "improvement", "improvements", "incident", "include", "included", "includes", "including", "income", "incorporate", "incorporated", "increase", "increased", "increases", "increasing", "increasingly", "incredible", "indeed", "independence", "independent", "indicate", "indicated", "indicates", "indication", "individual", "individuals", "industrial", "industries", "industry", "infection", "inflation", "influence", "influenced", "inform", "informal", "information", "informed", "infrastructure", "initial", "initially", "initiative", "injection", "injured", "injury", "inner", "innocent", "innovation", "innovative", "input", "inquiry", "inside", "insight", "inspection", "inspiration", "inspire", "install", "installation", "installed", "instance", "instant", "instead", "institute", "institution", "institutional", "instruction", "instructions", "instructor", "instrument", "instruments", "insurance", "intellectual", "intelligence", "intelligent", "intended", "intense", "intensity", "intention", "interaction", "interest", "interested", "interesting", "interests", "interface", "interference", "internal", "international", "internet", "interpretation", "interpreted", "interrupt", "interval", "interview", "interviews", "introduce", "introduced", "introduction", "invasion", "invention", "inventory", "investigate", "investigation", "investigator", "investment", "investor", "investors", "invisible", "invitation", "involve", "involved", "involvement", "island", "isolated", "issue", "issues", "itself", "jacket", "japanese", "jewelry", "joined", "joining", "journal", "journalism", "journalist", "journey", "judgment", "judicial", "junction", "junior", "justice", "justify", "keeping", "keyboard", "killed", "killing", "kitchen", "knowledge", "known", "label", "labeled", "laboratory", "labour", "ladder", "ladies", "landscape", "language", "languages", "largely", "larger", "largest", "lasting", "lately", "later", "latest", "latter", "laugh", "laughed", "laughing", "laughter", "launch", "launched", "laundry", "lawsuit", "lawyer", "lawyers", "leader", "leaders", "leadership", "leading", "league", "learned", "learning", "leather", "leave", "leaving", "lecture", "legal", "legally", "legend", "legislation", "legislative", "legislature", "legitimate", "length", "lesson", "lessons", "letter", "letters", "level", "levels", "liability", "liberal", "liberty", "library", "license", "licensed", "lifestyle", "lifetime", "light", "lighting", "lights", "likely", "limitation", "limitations", "limited", "limits", "linear", "lines", "linking", "links", "liquid", "listed", "listen", "listened", "listening", "literally", "literature", "living", "loaded", "loading", "loans", "local", "locally", "located", "location", "locations", "locked", "locking", "logic", "logical", "longer", "looking", "loosely", "losing", "lovely", "lovers", "loves", "loving", "lower", "lucky", "lunch", "machine", "machinery", "machines", "magazine", "magazines", "magic", "magical", "magnetic", "magnificent", "magnitude", "maiden", "mailed", "mailing", "maintain", "maintained", "maintaining", "maintenance", "major", "majority", "makers", "making", "managed", "management", "manager", "managers", "managing", "mandatory", "manner", "manual", "manufacturer", "manufacturing", "mapping", "marble", "march", "margin", "marine", "marked", "marker", "market", "marketing", "markets", "marriage", "married", "married", "massive", "master", "masters", "match", "matched", "matches", "matching", "material", "materials", "mathematical", "mathematics", "matter", "matters", "maximum", "maybe", "mayor", "meals", "meaning", "meaningful", "means", "meant", "meantime", "meanwhile", "measure", "measured", "measurement", "measures", "measuring", "mechanical", "mechanism", "media", "medical", "medicine", "medium", "meeting", "meetings", "member", "members", "membership", "memorial", "memories", "memory", "mental", "mention", "mentioned", "menu", "merchant", "merely", "merger", "merit", "message", "messages", "metal", "metals", "metaphor", "method", "methods", "metropolitan", "middle", "might", "military", "million", "millions", "minds", "mineral", "minerals", "minimum", "mining", "minister", "minor", "minority", "minute", "minutes", "miracle", "mirror", "missing", "mission", "mistake", "mistakes", "mixture", "mobile", "mode", "model", "modeling", "models", "moderate", "modern", "modest", "modification", "modified", "modify", "module", "modules", "moment", "moments", "momentum", "money", "monitor", "monitoring", "month", "monthly", "months", "monument", "mood", "moral", "morale", "morning", "mortality", "mortgage", "mostly", "mother", "motion", "motivation", "motor", "mount", "mountain", "mountains", "mouse", "mouth", "move", "moved", "movement", "movements", "moves", "movie", "movies", "moving", "multiple", "municipal", "muscle", "muscles", "museum", "music", "musical", "musician", "musicians", "myself", "mysterious", "mystery", "named", "names", "narrative", "narrow", "nation", "national", "nationally", "nations", "native", "natural", "naturally", "nature", "navigate", "navigation", "nearby", "nearest", "nearly", "necessarily", "necessary", "necessity", "neck", "needed", "needs", "negative", "negotiate", "negotiation", "neighbor", "neighborhood", "neighbors", "neither", "nervous", "network", "networks", "neutral", "never", "nevertheless", "newly", "news", "newspaper", "newspapers", "night", "nights", "nobody", "noise", "nomination", "none", "nonetheless", "normal", "normally", "north", "northern", "nose", "notable", "noted", "notes", "nothing", "notice", "noticed", "notification", "notify", "notion", "novel", "novels", "nowhere", "nuclear", "number", "numbers", "numerous", "nurse", "nursing", "nutrition", "objective", "objectives", "obligation", "observation", "observe", "observed", "observer", "obtain", "obtained", "obvious", "obviously", "occasion", "occasionally", "occasions", "occupation", "occupied", "occur", "occurred", "occurrence", "occurring", "occurs", "ocean", "october", "offense", "offensive", "offer", "offered", "offering", "offers", "office", "officer", "officers", "offices", "official", "officially", "officials", "often", "ongoing", "online", "opening", "operate", "operated", "operates", "operating", "operation", "operational", "operations", "operator", "operators", "opinion", "opinions", "opponent", "opportunities", "opportunity", "opposed", "opposite", "opposition", "optical", "optimal", "optimization", "option", "options", "orange", "order", "ordered", "ordering", "orders", "ordinary", "organic", "organization", "organizational", "organizations", "organize", "organized", "organizing", "orientation", "oriented", "origin", "original", "originally", "origins", "others", "otherwise", "ought", "outcomes", "outdoor", "outer", "outlet", "outline", "outlook", "output", "outside", "outstanding", "overall", "overcome", "overhead", "overview", "owned", "owner", "owners", "ownership", "pacific", "package", "packages", "packaging", "packed", "packet", "packets", "page", "pages", "paid", "pain", "painful", "paint", "painted", "painting", "paintings", "pair", "pairs", "palace", "panel", "panels", "paper", "papers", "paragraph", "parallel", "parameter", "parameters", "parent", "parents", "park", "parking", "parks", "part", "participant", "participants", "participate", "participated", "participating", "participation", "particular", "particularly", "parties", "partly", "partner", "partners", "partnership", "parts", "party", "pass", "passage", "passed", "passenger", "passengers", "passes", "passing", "passion", "passive", "password", "past", "patch", "path", "paths", "patience", "patient", "patients", "pattern", "patterns", "pause", "payment", "payments", "peace", "peaceful", "peak", "peaks", "pension", "people", "peoples", "percent", "percentage", "perception", "perfect", "perfectly", "perform", "performance", "performances", "performed", "performer", "performing", "performs", "perhaps", "period", "periods", "permanent", "permission", "permit", "permits", "person", "personal", "personality", "personally", "personnel", "persons", "perspective", "perspectives", "phase", "phases", "phenomenon", "philosophy", "phone", "phones", "photo", "photograph", "photographer", "photographs", "photography", "photos", "phrase", "phrases", "physical", "physically", "physician", "physicians", "physics", "piano", "picked", "picking", "picture", "pictures", "piece", "pieces", "pile", "pilot", "pine", "pink", "pipe", "pipes", "pitch", "place", "placed", "placement", "places", "placing", "plain", "plan", "plane", "planes", "planet", "planets", "planned", "planning", "plans", "plant", "plants", "plastic", "plate", "plates", "platform", "platforms", "play", "played", "player", "players", "playing", "plays", "plaza", "pleasant", "please", "pleased", "pleasure", "plenty", "plot", "plus", "pocket", "poem", "poems", "poet", "poetry", "poets", "point", "pointed", "pointing", "points", "pole", "poles", "police", "policies", "policy", "political", "politically", "politician", "politicians", "politics", "poll", "polls", "pollution", "pool", "pools", "poor", "popular", "popularity", "population", "populations", "port", "portable", "portal", "portion", "portions", "portrait", "ports", "pose", "posed", "position", "positioning", "positions", "positive", "possess", "possession", "possibilities", "possibility", "possible", "possibly", "post", "postal", "posted", "posting", "posts", "potato", "potential", "potentially", "pound", "pounds", "poverty", "powder", "power", "powerful", "powers", "practical", "practice", "practices", "practicing", "praise", "prayer", "prayers", "precise", "precisely", "precision", "predict", "predicted", "prediction", "predictions", "prefer", "preference", "preferences", "preferred", "preliminary", "premier", "premium", "preparation", "prepare", "prepared", "preparing", "prescribed", "presence", "present", "presentation", "presentations", "presented", "presenting", "presently", "presents", "preservation", "preserve", "preserved", "president", "presidential", "press", "pressed", "pressure", "presumably", "pretty", "prevent", "prevented", "preventing", "prevention", "previous", "previously", "price", "prices", "pricing", "pride", "primarily", "primary", "prime", "principal", "principally", "principals", "principle", "principles", "print", "printed", "printer", "printing", "prints", "prior", "priorities", "priority", "prison", "prisoner", "prisoners", "privacy", "private", "privately", "privilege", "privileges", "prize", "prizes", "probably", "problem", "problems", "procedure", "procedures", "proceed", "proceeded", "proceeding", "proceedings", "proceeds", "process", "processed", "processes", "processing", "processor", "processors", "produce", "produced", "producer", "producers", "produces", "producing", "product", "production", "productions", "productive", "productivity", "products", "profession", "professional", "professionals", "professor", "professors", "profile", "profiles", "profit", "profits", "program", "programme", "programs", "progress", "project", "projected", "projection", "projections", "projects", "promise", "promised", "promises", "promote", "promoted", "promoting", "promotion", "promotional", "prompt", "proof", "proper", "properly", "properties", "property", "proportion", "proportions", "proposal", "proposals", "propose", "proposed", "proposition", "prospect", "prospects", "protect", "protected", "protecting", "protection", "protective", "protein", "proteins", "protest", "protocol", "protocols", "proud", "prove", "proved", "proven", "proves", "provide", "provided", "provider", "providers", "provides", "providing", "province", "provinces", "provision", "provisions", "psychological", "psychology", "public", "publication", "publications", "publicity", "publicly", "publish", "published", "publisher", "publishers", "publishing", "pulled", "pulling", "purchase", "purchased", "purchases", "purchasing", "pure", "purely", "purple", "purpose", "purposes", "push", "pushed", "pushing", "putting", "qualified", "qualify", "qualifying", "quality", "quantities", "quantity", "quarter", "quarterly", "quarters", "queen", "question", "questioned", "questioning", "questions", "quick", "quickly", "quiet", "quietly", "quite", "quote", "quoted", "quotes", "race", "races", "racing", "radio", "rail", "railroad", "rain", "raise", "raised", "raises", "raising", "random", "range", "ranges", "ranging", "rank", "ranked", "ranking", "ranks", "rapid", "rapidly", "rare", "rarely", "rate", "rated", "rates", "rating", "ratings", "ratio", "rational", "reach", "reached", "reaches", "reaching", "reaction", "reactions", "read", "reader", "readers", "readily", "reading", "readings", "ready", "real", "realistic", "reality", "realize", "realized", "really", "reason", "reasonable", "reasonably", "reasoning", "reasons", "rebate", "recall", "receive", "received", "receiver", "receivers", "receives", "receiving", "recent", "recently", "reception", "recipe", "recipes", "recipient", "recognition", "recognize", "recognized", "recommend", "recommendation", "recommendations", "recommended", "record", "recorded", "recording", "recordings", "records", "recover", "recovered", "recovery", "recreation", "recreational", "recruit", "recruiting", "recruitment", "reduce", "reduced", "reduces", "reducing", "reduction", "reductions", "refer", "reference", "references", "referendum", "referred", "referring", "refers", "reflect", "reflected", "reflecting", "reflection", "reflections", "reflects", "reform", "reforms", "refuse", "refused", "refuses", "refusing", "regard", "regarded", "regarding", "regardless", "regards", "region", "regional", "regions", "register", "registered", "registration", "regular", "regularly", "regulation", "regulations", "regulatory", "reject", "rejected", "relate", "related", "relates", "relating", "relation", "relations", "relationship", "relationships", "relative", "relatively", "relatives", "relax", "relaxed", "release", "released", "releases", "releasing", "relevant", "reliability", "reliable", "relief", "religion", "religious", "reluctant", "rely", "relying", "remain", "remainder", "remained", "remaining", "remains", "remark", "remarkable", "remarks", "remember", "remembered", "remind", "reminded", "reminder", "reminders", "reminds", "remote", "removal", "remove", "removed", "removing", "repair", "repairs", "repeat", "repeated", "repeatedly", "replace", "replaced", "replacement", "replacing", "replied", "replies", "reply", "report", "reported", "reporter", "reporters", "reporting", "reports", "represent", "representation", "representative", "representatives", "represented", "representing", "represents", "reputation", "request", "requested", "requesting", "requests", "require", "required", "requirement", "requirements", "requires", "requiring", "rescue", "research", "researcher", "researchers", "resembled", "reservation", "reservations", "reserve", "reserved", "reserves", "reservoir", "residence", "resident", "residential", "residents", "resist", "resistance", "resolution", "resolutions", "resolve", "resolved", "resource", "resources", "respect", "respected", "respective", "respectively", "respond", "responded", "responding", "responds", "response", "responses", "responsibility", "responsible", "rest", "restaurant", "restaurants", "restore", "restored", "restriction", "restrictions", "result", "resulted", "resulting", "results", "resume", "retail", "retain", "retained", "retire", "retired", "retirement", "return", "returned", "returning", "returns", "reveal", "revealed", "revealing", "reveals", "revelation", "revenue", "revenues", "reverse", "review", "reviewed", "reviewing", "reviews", "revolution", "revolutionary", "reward", "rewards", "rice", "rich", "ride", "rider", "rides", "riding", "right", "rights", "ring", "rings", "rise", "rising", "risk", "risks", "river", "rivers", "road", "roads", "robot", "robots", "rock", "rocks", "role", "roles", "roll", "rolled", "rolling", "rolls", "roman", "roof", "room", "rooms", "root", "roots", "rope", "rose", "rotating", "rotation", "rough", "roughly", "round", "rounds", "route", "routes", "routine", "routines", "row", "rows", "royal", "rule", "ruled", "rules", "ruling", "run", "running", "runs", "rural", "rushed", "russian", "sacred", "sacrifice", "sad", "safe", "safely", "safer", "safety", "said", "sake", "salad", "salads", "salary", "sale", "sales", "salmon", "salt", "same", "sample", "samples", "satellite", "satisfaction", "satisfied", "satisfy", "sauce", "save", "saved", "saving", "savings", "scale", "scales", "scandal", "scared", "scenario", "scenarios", "scene", "scenes", "schedule", "scheduled", "schedules", "scheduling", "scheme", "schemes", "scholar", "scholars", "scholarship", "scholarships", "school", "schools", "science", "sciences", "scientific", "scientist", "scientists", "scope", "score", "scored", "scores", "scoring", "screen", "screens", "script", "scripts", "scroll", "search", "searched", "searches", "searching", "season", "seasons", "seat", "seated", "seats", "second", "secondary", "seconds", "secret", "secretary", "secrets", "section", "sections", "sector", "sectors", "secure", "secured", "security", "see", "seed", "seeds", "seeing", "seek", "seeking", "seeks", "seem", "seemed", "seems", "seen", "select", "selected", "selecting", "selection", "selections", "self", "sell", "selling", "sells", "semester", "senate", "senator", "senators", "send", "sending", "sends", "senior", "seniors", "sense", "senses", "sensitive", "sensitivity", "sent", "sentence", "sentences", "separate", "separated", "separately", "separation", "september", "sequence", "sequences", "series", "serious", "seriously", "serve", "served", "server", "servers", "serves", "service", "services", "serving", "session", "sessions", "set", "sets", "setting", "settings", "settle", "settled", "settlement", "settlements", "setup", "seven", "several", "severe", "severely", "sex", "sexual", "shade", "shadow", "shadows", "shake", "shall", "shame", "shape", "shaped", "shapes", "shaping", "share", "shared", "shares", "sharing", "sharp", "she", "sheet", "sheets", "shelf", "shell", "shelter", "shift", "shifted", "shifting", "shifts", "shine", "ship", "shipped", "shipping", "ships", "shirt", "shirts", "shock", "shocked", "shoe", "shoes", "shoot", "shooting", "shop", "shopping", "shops", "shore", "short", "shortly", "shot", "shots", "should", "shoulder", "shoulders", "shout", "show", "showed", "showing", "shown", "shows", "shut", "sick", "side", "sides", "sight", "sign", "signal", "signals", "signed", "significant", "significantly", "signing", "signs", "silence", "silent", "silver", "similar", "similarly", "simple", "simply", "simultaneously", "since", "sing", "singer", "singers", "singing", "single", "sink", "sister", "sisters", "sit", "site", "sites", "sitting", "situation", "situations", "six", "size", "sized", "sizes", "skill", "skilled", "skills", "skin", "sky", "slave", "slaves", "sleep", "sleeping", "slice", "slide", "slides", "slight", "slightly", "slow", "slowly", "small", "smaller", "smallest", "smart", "smell", "smile", "smiled", "smiling", "smoke", "smoking", "smooth", "snap", "snow", "so", "soap", "soccer", "social", "socially", "societies", "society", "sociology", "sock", "socks", "soft", "software", "soil", "solar", "sold", "sole", "solely", "solid", "solution", "solutions", "solve", "solved", "solving", "some", "somebody", "somehow", "someone", "something", "sometimes", "somewhat", "somewhere", "son", "song", "songs", "sons", "soon", "sophisticated", "sorry", "sort", "sorts", "soul", "souls", "sound", "sounding", "sounds", "soup", "source", "sources", "south", "southern", "space", "spaces", "spare", "speak", "speaker", "speakers", "speaking", "speaks", "special", "specialist", "specialists", "specially", "species", "specific", "specifically", "specification", "specifications", "specified", "specify", "speech", "speeches", "speed", "speeds", "spell", "spelling", "spend", "spending", "spent", "spin", "spirit", "spirits", "spiritual", "split", "spoke", "spoken", "sponsor", "sponsored", "sponsors", "sport", "sports", "spot", "spots", "spread", "spreading", "spring", "square", "squares", "stable", "stack", "staff", "stage", "stages", "stair", "stairs", "stake", "stakes", "stand", "standard", "standards", "standing", "stands", "star", "stars", "start", "started", "starting", "starts", "state", "stated", "statement", "statements", "states", "static", "stating", "station", "stations", "statistics", "status", "stay", "stayed", "staying", "stays", "steady", "steal", "steel", "step", "steps", "stick", "still", "stock", "stocks", "stomach", "stone", "stones", "stood", "stop", "stopped", "stopping", "stops", "storage", "store", "stored", "stores", "stories", "storing", "storm", "storms", "story", "straight", "strain", "strand", "strange", "stranger", "strangers", "strategy", "stream", "streams", "street", "streets", "strength", "strengthen", "stress", "stretch", "strike", "strikes", "striking", "string", "strings", "strip", "strips", "stroke", "strong", "stronger", "strongest", "strongly", "structure", "structures", "struggle", "struggling", "stuck", "student", "students", "studied", "studies", "studio", "studios", "study", "studying", "stuff", "stupid", "style", "styles", "subject", "subjects", "submission", "submit", "submitted", "subsequent", "subsequently", "substance", "substances", "substantial", "substantially", "substitute", "subtle", "suburb", "suburban", "suburbs", "succeed", "succeeded", "success", "successes", "successful", "successfully", "such", "sudden", "suddenly", "suffer", "suffered", "suffering", "sufficient", "sugar", "suggest", "suggested", "suggesting", "suggestion", "suggestions", "suggests", "suit", "suitable", "suited", "suits", "summary", "summer", "summit", "sun", "super", "superior", "supervision", "supervisor", "supervisors", "supper", "supplement", "supplemental", "supplements", "supplied", "supplier", "suppliers", "supplies", "supply", "support", "supported", "supporting", "supportive", "supports", "suppose", "supposed", "suppress", "sure", "surely", "surface", "surfaces", "surgery", "surprise", "surprised", "surprising", "surprisingly", "surrounded", "surrounding", "survey", "surveys", "survival", "survive", "survived", "surviving", "survivor", "survivors", "suspect", "suspected", "suspend", "suspended", "suspension", "suspicious", "sustain", "sustained", "swear", "sweep", "sweet", "swept", "swift", "swing", "switch", "switched", "switching", "symbol", "symbols", "sympathy", "symphony", "symptoms", "syndrome", "synthesis", "system", "systematic", "systems", "table", "tables", "tackle", "tail", "take", "taken", "takes", "taking", "tale", "tales", "talent", "talented", "talents", "talk", "talked", "talking", "talks", "tall", "tank", "tanks", "tap", "tape", "tapes", "target", "targeted", "targets", "task", "tasks", "taste", "tastes", "taught", "tax", "taxation", "taxes", "taxpayer", "teach", "teacher", "teachers", "teaches", "teaching", "team", "teams", "tear", "tears", "technical", "technically", "technique", "techniques", "technology", "telephone", "television", "tell", "telling", "tells", "temperature", "temperatures", "temple", "temporary", "ten", "tend", "tendency", "tends", "tennis", "tension", "tent", "term", "terminal", "terminals", "terms", "terrible", "territory", "terror", "terrorism", "terrorist", "test", "tested", "testing", "tests", "text", "texts", "than", "thank", "thanks", "that", "theatre", "their", "them", "theme", "themes", "themselves", "then", "theology", "theoretical", "theory", "therapy", "there", "thereby", "therefore", "these", "they", "thick", "thin", "thing", "things", "think", "thinking", "thinks", "third", "thirty", "this", "those", "though", "thought", "thoughts", "thousand", "thousands", "threat", "threats", "three", "threw", "through", "throughout", "throw", "thrown", "throws", "thumb", "thus", "ticket", "tickets", "tide", "tie", "tied", "ties", "tight", "time", "timed", "timeline", "times", "timing", "tiny", "tip", "tips", "tire", "tired", "tissue", "tissues", "title", "titles", "to", "tobacco", "today", "toe", "together", "toilet", "told", "tolerance", "toll", "tomato", "tomatoes", "tomorrow", "tone", "tones", "tongue", "tonight", "tons", "too", "took", "tool", "tools", "tooth", "top", "topic", "topics", "tops", "total", "totally", "touch", "touched", "touching", "tough", "tour", "touring", "tourism", "tourist", "tourists", "tournament", "tournaments", "tours", "toward", "towards", "town", "towns", "toy", "toys", "trace", "track", "tracked", "tracking", "tracks", "tract", "trade", "trading", "tradition", "traditional", "traditionally", "traditions", "traffic", "tragedy", "trail", "trails", "train", "trained", "training", "trains", "transfer", "transferred", "transfers", "transform", "transformation", "transformed", "transition", "translate", "translated", "translation", "transmission", "transport", "transportation", "trap", "travel", "traveled", "traveling", "travels", "treat", "treated", "treating", "treatment", "treatments", "treaty", "tree", "trees", "tremendous", "trend", "trends", "trial", "trials", "tribe", "tribes", "trick", "tricks", "tried", "tries", "trip", "trips", "troops", "trouble", "troubles", "truck", "trucks", "true", "truly", "trunk", "trust", "trusted", "truth", "try", "trying", "tube", "tubes", "tune", "tunnel", "turn", "turned", "turning", "turns", "twelve", "twenty", "twice", "twin", "two", "type", "types", "typical", "typically", "ultimate", "ultimately", "unable", "uncle", "under", "undergo", "underground", "underlying", "understand", "understanding", "understood", "undertake", "undertaken", "unemployment", "unexpected", "unfortunately", "uniform", "union", "unions", "unique", "unit", "united", "units", "unity", "universal", "universe", "universities", "university", "unknown", "unless", "unlike", "unlikely", "until", "unusual", "up", "update", "updated", "updates", "updating", "upgrade", "upon", "upper", "urban", "urge", "urged", "urgent", "us", "usage", "use", "used", "useful", "user", "users", "uses", "using", "usual", "usually", "utility", "vacation", "vacations", "valley", "valuable", "value", "valued", "values", "variable", "variables", "variation", "variations", "varied", "variety", "various", "vary", "vast", "vegetable", "vegetables", "vehicle", "vehicles", "venture", "ventures", "version", "versions", "versus", "very", "vessel", "vessels", "veteran", "veterans", "via", "victim", "victims", "video", "videos", "view", "viewed", "viewing", "views", "village", "villages", "violence", "violent", "virtual", "virtually", "virtue", "virus", "viruses", "visible", "vision", "visit", "visited", "visiting", "visitor", "visitors", "visits", "visual", "vital", "vitamin", "vitamins", "voice", "voices", "volume", "volumes", "vote", "voted", "voter", "voters", "votes", "voting", "wage", "wages", "wait", "waited", "waiting", "wake", "walk", "walked", "walking", "walks", "wall", "walls", "want", "wanted", "wanting", "wants", "war", "ward", "warm", "warming", "warn", "warned", "warning", "warnings", "wars", "was", "wash", "waste", "watch", "watched", "watches", "watching", "water", "waters", "wave", "waves", "way", "ways", "we", "weak", "wealth", "weapon", "weapons", "wear", "wearing", "weather", "web", "website", "websites", "wedding", "week", "weekend", "weekends", "weekly", "weeks", "weight", "weights", "welcome", "welfare", "well", "west", "western", "wet", "what", "whatever", "wheel", "wheels", "when", "whenever", "where", "whereas", "whereby", "wherever", "whether", "which", "while", "white", "who", "whoever", "whole", "whom", "whose", "why", "wide", "widely", "wider", "widespread", "wife", "wild", "will", "willing", "win", "wind", "window", "windows", "winds", "wine", "wines", "wing", "wings", "winner", "winners", "winning", "wins", "winter", "wire", "wires", "wisdom", "wise", "wish", "wished", "wishes", "with", "withdraw", "withdrawal", "within", "without", "witness", "witnesses", "woman", "women", "won", "wonder", "wonderful", "wondering", "wood", "wooden", "woods", "wool", "word", "words", "work", "worked", "worker", "workers", "working", "works", "workshop", "workshops", "world", "worlds", "worldwide", "worn", "worried", "worry", "worse", "worship", "worst", "worth", "worthy", "would", "wound", "wounds", "write", "writer", "writers", "writes", "writing", "writings", "written", "wrong", "wrote", "yard", "yards", "yeah", "year", "years", "yellow", "yes", "yesterday", "yet", "yield", "young", "younger", "youngest", "your", "yours", "yourself", "youth", "zone", "zones"
]

COMMON_WORDS = ["the", "of", "and", "to", "a", "in", "is", "it", "you", "that", "he", "was", "for", "on", "are", "as", "with", "his", "they", "i", "at", "be", "this", "have", "from", "or", "one", "had", "by", "word", "but", "not", "what", "all", "were", "we", "when", "your", "can", "said", "there", "each", "which", "she", "do", "how", "their", "if", "will", "up", "other", "about", "out", "many", "then", "them", "these", "so", "some", "her", "would", "make", "like", "into", "him", "has", "two", "more", "very", "after", "words", "first", "where", "been", "who", "its", "now", "find", "long", "down", "way", "may", "come", "could", "people", "my", "than", "water", "part", "time", "work", "right", "new", "take", "get", "place", "made", "live", "where", "after", "back", "little", "only", "round", "man", "year", "came", "show", "every", "good", "me", "give", "our", "under", "name", "very", "through", "just", "form", "sentence", "great", "think", "say", "help", "low", "line", "differ", "turn", "cause", "much", "mean", "before", "move", "right", "boy", "old", "too", "same", "tell", "does", "set", "three", "want", "air", "well", "also", "play", "small", "end", "put", "home", "read", "hand", "port", "large", "spell", "add", "even", "land", "here", "must", "big", "high", "such", "follow", "act", "why", "ask", "men", "change", "went", "light", "kind", "off", "need", "house", "picture", "try", "us", "again", "animal", "point", "mother", "world", "near", "build", "self", "earth", "father", "head", "stand", "own", "page", "should", "country", "found", "answer", "school", "grow", "study", "still", "learn", "plant", "cover", "food", "sun", "four", "between", "state", "keep", "eye", "never", "last", "let", "thought", "city", "tree", "cross", "farm", "hard", "start", "might", "story", "saw", "far", "sea", "draw", "left", "late", "run", "don't", "while", "press", "close", "night", "real", "life", "few", "north", "open", "seem", "together", "next", "white", "children", "begin", "got", "walk", "example", "ease", "paper", "group", "always", "music", "those", "both", "mark", "often", "letter", "until", "mile", "river", "car", "feet", "care", "second", "book", "carry", "took", "science", "eat", "room", "friend", "began", "idea", "fish", "mountain", "stop", "once", "base", "hear", "horse", "cut", "sure", "watch", "color", "face", "wood", "main", "enough", "plain", "girl", "usual", "young", "ready", "above", "ever", "red", "list", "though", "feel", "talk", "bird", "soon", "body", "dog", "family", "direct", "pose", "leave", "song", "measure", "door", "product", "black", "short", "numeral", "class", "wind", "question", "happen", "complete", "ship", "area", "half", "rock", "order", "fire", "south", "problem", "piece", "told", "knew", "pass", "since", "top", "whole", "king", "space", "heard", "best", "hour", "better", "during", "hundred", "five", "remember", "step", "early", "hold", "west", "ground", "interest", "reach", "fast", "verb", "sing", "listen", "six", "table", "travel", "less", "morning", "ten", "simple", "several", "vowel", "toward", "war", "lay", "against", "pattern", "slow", "center", "love", "person", "money", "serve", "appear", "road", "map", "rain", "rule", "govern", "pull", "cold", "notice", "voice", "unit", "power", "town", "fine", "certain", "fly", "fall", "lead", "cry", "dark", "machine", "note", "wait", "plan", "figure", "star", "box", "noun", "field", "rest", "correct", "able", "pound", "done", "beauty", "drive", "stood", "contain", "front", "teach", "week", "final", "gave", "green", "oh", "quick", "develop", "ocean", "warm", "free", "minute", "strong", "special", "mind", "behind", "clear", "tail", "produce", "fact", "street", "inch", "multiply", "nothing", "course", "stay", "wheel", "full", "force", "blue", "object", "decide", "surface", "deep", "moon", "island", "foot", "system", "busy", "test", "record", "boat", "common", "gold", "possible", "plane", "stead", "dry", "wonder", "laugh", "thousands", "ago", "ran", "check", "game", "shape", "equate", "hot", "miss", "brought", "heat", "snow", "tire", "bring", "yes", "distant", "fill", "east", "paint", "language", "among"]

TYPING_LESSONS = {
    "home_row": {
        "name": "Home Row",
        "desc": "Master the foundation keys: asdf jkl;.",
        "words": ["asdf", "jkl;", "ask", "lad", "jak", "sad", "fad", "lass", "fall", "salk", "jade", "flask"]
    },
    "top_row": {
        "name": "Top Row",
        "desc": "Practice qwerty uiop keys.",
        "words": ["qwerty", "uiop", "quite", "wiper", "upper", "quote", "power", "tower", "proper", "puppet"]
    },
    "bottom_row": {
        "name": "Bottom Row",
        "desc": "Learn zxcv bnm, keys.",
        "words": ["zxcv", "bnm,", "zone", "cave", "move", "come", "move", "zoom", "name", "came"]
    },
    "numbers": {
        "name": "Number Row",
        "desc": "Practice 1234567890 keys.",
        "words": ["123", "456", "789", "012", "147", "258", "369", "159", "357", "246"]
    },
    "special": {
        "name": "Special Characters",
        "desc": "Practice punctuation and symbols.",
        "words": ["hello!", "world?", "yes,", "no.", "it's", "can't", "won't", "i'm", "you're", "we'll"]
    },
    "speed": {
        "name": "Speed Drills",
        "desc": "Fast common word combinations.",
        "words": ["the quick", "brown fox", "jumps over", "lazy dog", "pack my", "box with", "five dozen", "liquor jugs"]
    }
}

ACHIEVEMENTS = {
    "speed_demon": {"name": "Speed Demon", "desc": "Reach 80+ WPM.", "icon": "🚀"},
    "accuracy_master": {"name": "Accuracy Master", "desc": "Maintain 98%+ accuracy.", "icon": "🎯"},
    "persistent": {"name": "Persistent", "desc": "Complete 10 tests.", "icon": "🔥"},
    "marathon": {"name": "Marathon", "desc": "Type for 5 minutes straight.", "icon": "🏃"},
    "perfectionist": {"name": "Perfectionist", "desc": "Complete a test with 100% accuracy.", "icon": "💎"},
    "consistent": {"name": "Consistent", "desc": "5 tests in a row with >90% accuracy.", "icon": "📈"},
    "speed_machine": {"name": "Speed Machine", "desc": "Reach 100+ WPM.", "icon": "⚡"},
    "improver": {"name": "Improver", "desc": "Improve WPM by 20+ points.", "icon": "📊"},
    "streak_master": {"name": "Streak Master", "desc": "Maintain a 7-day streak.", "icon": "🔥"},
    "early_bird": {"name": "Early Bird", "desc": "Take a test before 8 AM.", "icon": "🌅"},
    "night_owl": {"name": "Night Owl", "desc": "Take a test after 10 PM.", "icon": "🦉"},
    "weekend_warrior": {"name": "Weekend Warrior", "desc": "Practice on weekends.", "icon": "🎮"}
}

class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_path = db_path or get_db_path()
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
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

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
                        correct_characters INTEGER NOT NULL CHECK(correct_characters >= 0),
                        raw_wpm REAL DEFAULT 0,
                        consistency_score REAL DEFAULT 0,
                        test_mode TEXT DEFAULT 'standard'
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
                        finger_mapped TEXT,
                        bigram_context TEXT,
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

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_settings (
                        id INTEGER PRIMARY KEY,
                        setting_key TEXT UNIQUE NOT NULL,
                        setting_value TEXT NOT NULL,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS performance_insights (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        test_id INTEGER NOT NULL,
                        insight_type TEXT NOT NULL,
                        insight_data TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (test_id) REFERENCES test_results (id) ON DELETE CASCADE
                    )
                ''')

                conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            raise

    def save_test_result(self, wpm, accuracy, duration, words_typed, errors, difficulty, chars_typed=0, correct_chars=0, raw_wpm=0, consistency=0, test_mode='standard'):
        """Enhanced test result saving with additional metrics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO test_results
                    (wpm, accuracy, mistakes, test_duration, difficulty, word_count, characters_typed,
                     correct_characters, raw_wpm, consistency_score, test_mode)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (wpm, accuracy, errors, duration, difficulty, words_typed, chars_typed, correct_chars, raw_wpm, consistency, test_mode))

                test_id = cursor.lastrowid

                today = datetime.now().date()
                cursor.execute('''
                    INSERT OR REPLACE INTO daily_streaks (date, tests_completed)
                    VALUES (?, COALESCE((SELECT tests_completed FROM daily_streaks WHERE date = ?) + 1, 1))
                ''', (today, today))

                conn.commit()
                return test_id
        except sqlite3.Error as e:
            print(f"Error saving test result: {e}")
            return None

    def save_error_patterns(self, test_id, error_patterns):
        """Save detailed error patterns for analysis"""
        if not test_id or not error_patterns:
            return

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                for error in error_patterns:
                    if isinstance(error, dict):
                        cursor.execute('''
                            INSERT INTO error_patterns
                            (test_id, character_intended, character_typed, position, word_context, finger_mapped, bigram_context)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (test_id, error.get('intended', ''), error.get('typed', ''),
                              error.get('position', 0), error.get('context', ''),
                              error.get('finger', ''), error.get('bigram', '')))
                    else:
                        if '->' in str(error):
                            intended, typed = str(error).split('->', 1)
                            cursor.execute('''
                                INSERT INTO error_patterns
                                (test_id, character_intended, character_typed, position, word_context, finger_mapped, bigram_context)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (test_id, intended.strip(), typed.strip(), 0, '', '', ''))
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

    def get_recent_stats(self, limit=10):
        """Get recent statistics with enhanced data"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT wpm, accuracy, test_duration, word_count, mistakes, difficulty, date,
                           consistency_score, test_mode, raw_wpm
                    FROM test_results
                    ORDER BY date DESC
                    LIMIT ?
                ''', (limit,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting recent stats: {e}")
            return []

    def get_best_stats(self):
        """Get comprehensive best statistics"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT
                        MAX(wpm) as best_wpm,
                        MAX(accuracy) as best_accuracy,
                        AVG(wpm) as avg_wpm,
                        AVG(accuracy) as avg_accuracy,
                        COUNT(*) as total_tests,
                        MAX(consistency_score) as best_consistency,
                        AVG(consistency_score) as avg_consistency,
                        SUM(test_duration) as total_time
                    FROM test_results
                ''')
                return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error getting best stats: {e}")
            return None

    def get_statistics(self, days=30):
        """Get statistics with parameterized queries for security"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, date, wpm, accuracy, mistakes, test_duration, difficulty,
                           word_count, characters_typed, correct_characters, consistency_score
                    FROM test_results
                    WHERE date >= datetime('now', '-' || ? || ' days')
                    ORDER BY date DESC
                ''', (days,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting statistics: {e}")
            return []

    def get_error_analysis(self, days=30):
        """Get comprehensive error analysis"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT character_intended, character_typed, COUNT(*) as frequency,
                           finger_mapped, bigram_context
                    FROM error_patterns ep
                    JOIN test_results tr ON ep.test_id = tr.id
                    WHERE tr.date >= datetime('now', '-' || ? || ' days')
                    GROUP BY character_intended, character_typed, finger_mapped
                    ORDER BY frequency DESC
                    LIMIT 20
                ''', (days,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting error analysis: {e}")
            return []

    def get_streak_count(self):
        """Get current streak count"""
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

    def get_user_setting(self, key, default=None):
        """Get user setting value"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT setting_value FROM user_settings WHERE setting_key = ?', (key,))
                result = cursor.fetchone()
                return result[0] if result else default
        except sqlite3.Error as e:
            print(f"Error getting user setting: {e}")
            return default

    def set_user_setting(self, key, value):
        """Set user setting value"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_settings (setting_key, setting_value)
                    VALUES (?, ?)
                ''', (key, str(value)))
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error setting user setting: {e}")
            return False

    def get_performance_trends(self, days=30):
        """Get performance trends for analysis"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT DATE(date) as test_date, AVG(wpm) as avg_wpm, AVG(accuracy) as avg_accuracy,
                           COUNT(*) as test_count, AVG(consistency_score) as avg_consistency
                    FROM test_results
                    WHERE date >= datetime('now', '-' || ? || ' days')
                    GROUP BY DATE(date)
                    ORDER BY test_date DESC
                ''', (days,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting performance trends: {e}")
            return []

# Database instance - initialize lazily
db = None

def get_db():
    """Get database instance, initializing if needed"""
    global db
    if db is None:
        try:
            db = DatabaseManager()
        except Exception as e:
            print(f"Database initialization error: {e}")
            # Return a mock database for error cases
            return MockDatabase()
    return db

class MockDatabase:
    """Mock database for error cases"""
    def get_best_stats(self):
        return None
    def get_recent_stats(self, limit):
        return []
    def get_achievements(self):
        return []
    def get_streak_count(self):
        return 0
    def save_test_result(self, *args, **kwargs):
        return None
    def get_statistics(self, days=30):
        return []
    def get_error_analysis(self, days=30):
        return []
    def get_performance_trends(self, days=30):
        return []
    def unlock_achievement(self, achievement_id):
        return False
    def save_error_patterns(self, test_id, patterns):
        return None
    def get_user_setting(self, key, default=None):
        return default
    def set_user_setting(self, key, value):
        return None

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'SnakeType API is running',
        'vercel': bool(os.getenv('VERCEL'))
    })

# Explicit static file serving for Vercel
@app.route('/static/<path:filename>')
def serve_static(filename):
    from flask import send_from_directory
    import mimetypes
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    response = send_from_directory(static_dir, filename)

    # Ensure proper MIME types
    if filename.endswith('.css'):
        response.headers['Content-Type'] = 'text/css'
    elif filename.endswith('.js'):
        response.headers['Content-Type'] = 'application/javascript'

    return response

# Favicon route
@app.route('/favicon.ico')
def favicon():
    from flask import send_from_directory
    return send_from_directory(os.path.dirname(__file__), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    try:
        database = get_db()
        best_stats = database.get_best_stats()
        recent_stats = database.get_recent_stats(5)
        achievements = database.get_achievements()
        streak = database.get_streak_count()

        return render_template('index.html',
                             best_stats=best_stats,
                             recent_stats=recent_stats,
                             achievements=achievements,
                             streak=streak)
    except Exception as e:
        print(f"Error in index route: {e}")
        return render_template('index.html',
                             best_stats=None,
                             recent_stats=[],
                             achievements=[],
                             streak=0)

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/lessons')
def lessons():
        return render_template('lessons.html', lessons=TYPING_LESSONS)

@app.route('/achievements')
def achievements():
    database = get_db()
    user_achievements = database.get_achievements()
    unlocked_ids = {ach[0] for ach in user_achievements}

    stats = database.get_statistics(days=30)
    progress = {}

    if stats:
        best_wpm = max(stat[2] for stat in stats)
        best_acc = max(stat[3] for stat in stats)
        test_count = len(stats)

        progress = {
            'speed_demon': min(100, (best_wpm / 80) * 100),
            'speed_machine': min(100, (best_wpm / 100) * 100),
            'accuracy_master': min(100, (best_acc / 98) * 100),
            'persistent': min(100, (test_count / 10) * 100)
        }

    return render_template('achievements.html',
                         achievements=ACHIEVEMENTS,
                         unlocked=unlocked_ids,
                         progress=progress)

@app.route('/stats')
def stats():
    try:
        database = get_db()
        recent_stats = database.get_recent_stats(20)
        best_stats = database.get_best_stats()
        error_analysis = database.get_error_analysis(30)
        trends = database.get_performance_trends(30)

        return render_template('stats.html',
                             recent_stats=recent_stats,
                             best_stats=best_stats,
                             error_analysis=error_analysis,
                             trends=trends)
    except Exception as e:
        print(f"Error in stats route: {e}")
        return render_template('stats.html',
                             recent_stats=[],
                             best_stats={},
                             error_analysis={},
                             trends={})

@app.route('/api/get_words')
def get_words():
    difficulty = request.args.get('difficulty', 'medium')
    count = int(request.args.get('count', 200))  # Increased default count
    lesson_type = request.args.get('lesson_type', None)

    if lesson_type and lesson_type in TYPING_LESSONS:
        lesson = TYPING_LESSONS[lesson_type]
        words = lesson['words'] * (count // len(lesson['words']) + 1)
        words = words[:count]
        return jsonify({'words': words, 'lesson_name': lesson['name']})

    if difficulty == 'adaptive':
        recent_stats = db.get_recent_stats(5)
        if recent_stats:
            avg_wpm = sum(stat[0] for stat in recent_stats) / len(recent_stats)
            avg_acc = sum(stat[1] for stat in recent_stats) / len(recent_stats)

            if avg_wpm > 60 and avg_acc > 95:
                difficulty = 'hard'
            elif avg_wpm > 40 and avg_acc > 90:
                difficulty = 'medium'
            else:
                difficulty = 'easy'

    if difficulty == 'easy':
        available_words = EASY_WORDS.copy()
    elif difficulty == 'hard':
        available_words = HARD_WORDS.copy()
    elif difficulty == 'common':
        available_words = COMMON_WORDS.copy()
    else:  # medium
        available_words = MEDIUM_WORDS.copy()

    if count > len(available_words):
        words = []
        while len(words) < count:
            random.shuffle(available_words)
            remaining_needed = count - len(words)
            words.extend(available_words[:remaining_needed])
    else:
        words = random.sample(available_words, count)
        random.shuffle(words)  # Shuffle the final selection

    return jsonify({'words': words})

@app.route('/api/save_result', methods=['POST'])
def save_result():
    data = request.json

    wpm = data.get('wpm', 0)
    accuracy = data.get('accuracy', 0)
    duration = data.get('duration', 0)
    words_typed = data.get('words_typed', 0)
    errors = data.get('errors', 0)
    difficulty = data.get('difficulty', 'medium')
    chars_typed = data.get('characters_typed', 0)
    correct_chars = data.get('correct_characters', 0)
    raw_wpm = data.get('raw_wpm', wpm)
    consistency = data.get('consistency_score', 0)
    test_mode = data.get('test_mode', 'standard')
    error_patterns = data.get('error_patterns', [])

    database = get_db()
    test_id = database.save_test_result(wpm, accuracy, duration, words_typed, errors,
                                difficulty, chars_typed, correct_chars, raw_wpm,
                                consistency, test_mode)

    if test_id and error_patterns:
        database.save_error_patterns(test_id, error_patterns)

    achievements_unlocked = []
    stats = database.get_statistics(days=30)

    if wpm >= 80 and database.unlock_achievement('speed_demon'):
        achievements_unlocked.append('speed_demon')
    if wpm >= 100 and database.unlock_achievement('speed_machine'):
        achievements_unlocked.append('speed_machine')

    if accuracy >= 98 and database.unlock_achievement('accuracy_master'):
        achievements_unlocked.append('accuracy_master')
    if accuracy == 100 and database.unlock_achievement('perfectionist'):
        achievements_unlocked.append('perfectionist')

    if duration >= 300 and database.unlock_achievement('marathon'):  # 5 minutes
        achievements_unlocked.append('marathon')

    if len(stats) >= 10 and database.unlock_achievement('persistent'):
        achievements_unlocked.append('persistent')

    from datetime import datetime
    current_hour = datetime.now().hour
    if current_hour < 8 and database.unlock_achievement('early_bird'):
        achievements_unlocked.append('early_bird')
    if current_hour >= 22 and database.unlock_achievement('night_owl'):
        achievements_unlocked.append('night_owl')

    if datetime.now().weekday() >= 5 and database.unlock_achievement('weekend_warrior'):
        achievements_unlocked.append('weekend_warrior')

    streak = database.get_streak_count()
    if streak >= 7 and database.unlock_achievement('streak_master'):
        achievements_unlocked.append('streak_master')

    if len(stats) >= 5:
        recent_accuracy = [stat[3] for stat in stats[:5]]
        if all(acc > 90 for acc in recent_accuracy) and database.unlock_achievement('consistent'):
            achievements_unlocked.append('consistent')

    if len(stats) >= 10:
        recent_wpm = [stat[2] for stat in stats[:5]]
        older_wpm = [stat[2] for stat in stats[5:10]]
        if sum(recent_wpm)/5 - sum(older_wpm)/5 >= 20 and database.unlock_achievement('improver'):
            achievements_unlocked.append('improver')

    return jsonify({
        'success': True,
        'test_id': test_id,
        'achievements': achievements_unlocked
    })

@app.route('/api/stats')
def get_stats():
    database = get_db()
    recent_stats = database.get_recent_stats(20)
    best_stats = database.get_best_stats()
    error_analysis = database.get_error_analysis(30)
    trends = database.get_performance_trends(30)

    return jsonify({
        'recent_stats': recent_stats,
        'best_stats': best_stats,
        'error_analysis': error_analysis,
        'trends': trends
    })

@app.route('/api/achievements')
def get_achievements():
    database = get_db()
    user_achievements = database.get_achievements()
    return jsonify({
        'achievements': user_achievements,
        'all_achievements': ACHIEVEMENTS
    })

@app.route('/api/lessons')
def get_lessons():
    return jsonify({'lessons': TYPING_LESSONS})

@app.route('/api/export_data')
def export_data():
    """Export user data as JSON"""
    stats = db.get_statistics(days=365)  # Get full year of data
    achievements = db.get_achievements()
    error_analysis = db.get_error_analysis(days=365)

    export_data = {
        'stats': stats,
        'achievements': achievements,
        'error_analysis': error_analysis,
        'export_date': datetime.now().isoformat()
    }

    return jsonify(export_data)

@app.route('/api/upload_text', methods=['POST'])
def upload_text():
    """Handle custom text upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        content = file.read().decode('utf-8')
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

        words = words[:200]

        return jsonify({
            'success': True,
            'words': words,
            'word_count': len(words)
        })

    except Exception as e:
        return jsonify({'error': f'Failed to process file: {str(e)}'}), 400

@app.route('/api/performance_insights')
def get_performance_insights():
    """Get advanced performance insights"""
    database = get_db()
    stats = database.get_statistics(days=30)
    if not stats:
        return jsonify({'insights': [], 'recommendations': []})

    insights = []
    recommendations = []

    wpm_scores = [stat[2] for stat in stats]
    accuracy_scores = [stat[3] for stat in stats]

    avg_wpm = sum(wpm_scores) / len(wpm_scores)
    avg_accuracy = sum(accuracy_scores) / len(accuracy_scores)

    if avg_wpm < 40:
        insights.append({
            'type': 'speed',
            'message': f'Your average speed is {avg_wpm:.1f} WPM - focus on building muscle memory',
            'icon': '🏃'
        })
        recommendations.append('Practice finger positioning and maintain steady rhythm')
    elif avg_wpm < 60:
        insights.append({
            'type': 'speed',
            'message': f'Good progress at {avg_wpm:.1f} WPM - work on consistency',
            'icon': '📈'
        })
        recommendations.append('Try typing without looking at keyboard')

    if avg_accuracy < 95:
        insights.append({
            'type': 'accuracy',
            'message': f'Accuracy at {avg_accuracy:.1f}% - slow down for better precision',
            'icon': '🎯'
        })
        recommendations.append('Focus on accuracy over speed')

    if len(stats) >= 10:
        recent_wpm = sum(wpm_scores[:5]) / 5
        older_wpm = sum(wpm_scores[5:10]) / 5

        if recent_wpm > older_wpm + 2:
            insights.append({
                'type': 'trend',
                'message': 'Great improvement! Your speed is increasing',
                'icon': '🚀'
            })

    return jsonify({
        'insights': insights,
        'recommendations': recommendations
    })

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('typing_update')
def handle_typing_update(data):
    emit('typing_feedback', {
        'wpm': data.get('wpm', 0),
        'accuracy': data.get('accuracy', 0),
        'progress': data.get('progress', 0)
    })

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
