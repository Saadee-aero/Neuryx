import re

class RomanTransliterator:
    """
    A deterministic, rule-based transliteration engine for converting Urdu script
    to natural, readable Roman Urdu (phonetic English).
    Preserves English words, formulas, and mathematical symbols.
    """
    def __init__(self):
        # Phase 2: Word-Level Overrides (High Priority)
        # Includes common grammar, academic terms, and high-frequency words
        self.word_overrides = {
            # Grammar / Common Words
            "ہے": "hai", "ہیں": "hain", "ہوں": "hoon", "ہو": "ho",
            "کا": "ka", "کی": "ki", "کے": "ke", "کو": "ko",
            "میں": "mein", "اور": "aur", "سے": "se", "پر": "par",
            "یہ": "yeh", "وہ": "woh", "اس": "is", "us": "us", # 'us' is tricky without diacritics
            "تھا": "tha", "تھی": "thi", "تھے": "the",
            "رہا": "raha", "رہی": "rahi", "رہے": "rahe",
            "گیا": "gaya", "گئی": "gayi", "گئے": "gaye",
            "کر": "kar", "کیا": "kya", "کیوں": "kyun",
            "پہلے": "pehle", "بعد": "baad",
            "جب": "jab", "تب": "tab", "اب": "ab",
            "اگر": "agar", "مگر": "magar", "لیکن": "lekin",
            "تو": "to", "بھی": "bhi",
            "ہم": "hum", "تم": "tum", "آپ": "aap",
            "میرا": "mera", "میری": "meri", "میرے": "mere",
            "اپنا": "apna", "اپنی": "apni", "اپنے": "apne",
            "کیسے": "kaise", "کیسی": "kaisi", "کیسا": "kaisa",
            "کتنا": "kitna", "کتنی": "kitni", "کتنے": "kitne",
            "کیونکہ": "kyunke", "تاکہ": "taake",
            "سب": "sab", "کچھ": "kuch", "ہر": "har",
            "والا": "wala", "والی": "wali", "والے": "wale",
            "چاہیے": "chahiye", "نہیں": "nahi", "ہوتا": "hota", "ہوتی": "hoti", "ہوتے": "hote",
            "دیکھیں": "dekhen", "سنیں": "sunen", "پڑھیں": "parhen", "لکھیں": "likhen",
            
            # Academic / Heavy Words
            "ضروری": "zaroori", "اہم": "ahm", "تعلیم": "taleem",
            "مسئلہ": "masla", "قانون": "qanoon", "امتحان": "imtihan",
            "سوال": "sawal", "جواب": "jawab", "مثال": "misal",
            "نظریہ": "nazriya", "نتیجہ": "natija", "تحقیق": "tehqeeq",
            "سائنس": "science", "ریاضی": "math", # Optional natural mapping? Strict phonetic: riyazi
            "بہت": "bohat",
            
            # Synonyms / Variations
            "ہاں": "han",
            "جائے": "jaye", "لڑکے": "larke", "لڑکیاں": "larkiyan", "لڑکوں": "larkon"
        }

        # Phase 3: Character Map
        self.char_map = {
            'ا': 'a', 'آ': 'aa',
            'ب': 'b', 'پ': 'p', 'ت': 't', 'ٹ': 't', 'ث': 's',
            'ج': 'j', 'چ': 'ch', 'ح': 'h', 'خ': 'kh',
            'د': 'd', 'ڈ': 'd', 'ذ': 'z',
            'ر': 'r', 'ڑ': 'r', 'ز': 'z', 'ژ': 'zh',
            'س': 's', 'ش': 'sh', 'ص': 's', 'ض': 'z',
            'ط': 't', 'ظ': 'z', 'ع': 'a', 'غ': 'gh',
            'ف': 'f', 'ق': 'q', 'ک': 'k', 'گ': 'g',
            'ل': 'l', 'م': 'm', 'ن': 'n', 'ں': 'n',
            'و': 'o', 'ہ': 'h', 'ھ': 'h',
            'ی': 'i', 'ے': 'e', 'ئے': 'e', 'ئ': 'e',
            'ۃ': 'h', 'ة': 'h',
            # Punctuation
            '۔': '.', '،': ',', '؟': '?'
        }
        
        # Add Urdu Digits (0-9) programmatically
        urdu_zero = 0x06f0 
        # Also add extended Arabic-Indic digits just in case (0660-0669)
        arabic_zero = 0x0660
        
        for i in range(10):
            self.char_map[chr(urdu_zero + i)] = str(i)
            self.char_map[chr(arabic_zero + i)] = str(i)

    def is_urdu_char(self, char: str) -> bool:
        return '\u0600' <= char <= '\u06FF'

    def apply_suffix_rules(self, word: str) -> tuple[str, str]:
        """
        Checks for common suffixes and returns (stem, distinct_roman_suffix)
        If matched, caller should transliterate stem and append suffix.
        Returns (word, "") if no suffix match.
        """
        # Phase 2: Suffix Rules
        # Order matters: longer suffixes first
        suffixes = [
            ("یوں", "iyon"), # larkiyon
            ("وں", "on"),    # larkon
            ("یاں", "iyan"), # larkiyan
            ("یں", "ein"),   # kitabein
            ("ات", "at"),    # maloomat
            ("گا", "ga"),    # jaye ga - strictly usually separate word, but if attached: jayega
            ("گی", "gi"),
            ("گے", "ge"),
            ("کر", "kar"),   # aa kar -> aakar if attached
        ]
        
        for suffix, roman_suffix in suffixes:
            if word.endswith(suffix):
                # stem matches?
                # Use positive indexing to avoid linter issues with negative slices
                stem = word[:len(word) - len(suffix)]
                # Ensure stem isn't empty (e.g. if word IS the suffix)
                if stem:
                    return stem, roman_suffix
                
        return word, ""

    def transliterate_word(self, word: str) -> str:
        """
        Transliterates a single word using overrides, suffix logic, smart vowels, and char mapping.
        """
        # 0. Check for exact overrides
        if word in self.word_overrides:
            return self.word_overrides[word]

        # 1. Preservation Checks (English/Math/Symbols)
        if not any(self.is_urdu_char(c) for c in word):
            return word

        # 2. Suffix Handling
        stem, suffix_roman = self.apply_suffix_rules(word)
        # If suffix matched, we map the stem and add the known suffix
        # BUT stem might need standard mapping.
        
        target_word = stem if suffix_roman else word
        
        # 3. Validation - if stem is empty or too short, maybe strict map was better? 
        # But suffix logic expects stems.
        
        roman = ""
        length = len(target_word)
        
        for i, char in enumerate(target_word):
            if not self.is_urdu_char(char):
                roman += char
                continue
            
            # Smart Vowel handling (Phase 5)
            # "ا" rules
            if char == 'ا':
                # If start and next is consonant -> 'a' (already 'a' in map)
                # If middle -> 'a' matches. 
                # Refinement: double vowels?
                mapped_char = 'a'
            elif char == 'و':
                # Start -> w, else o.
                # "او" -> "oo" handled by combination or just o+o?
                # current map 'o'.
                if i == 0:
                    mapped_char = 'w'
                else: 
                     # Check previous char. If prev is Alif "ا", then "او" might be "ao" or "oo".
                     # "جاؤ" -> jao. "بول" -> bol. "لوگ" -> log.
                     # Let's stick to 'w' start, 'o' otherwise.
                     mapped_char = 'o'
                     
            elif char == 'ی':
                # "ای" -> "ai" or "ee"?
                # "بھائی" -> bhai. (Alif + HamzaYe)
                # "کیا" -> kya. (Kaf + Ye + Alif) -> here 'Ye' is consonant 'y'.
                # Heuristic: If followed by Alif, often 'y'. (kya, pyara)
                if i < length - 1 and target_word[i+1] == 'ا':
                    mapped_char = 'y'
                else:
                    mapped_char = 'i'

            elif char == 'ے':
                 mapped_char = 'e'
                 
            else:
                 mapped_char = self.char_map.get(char, "")
            
            roman += mapped_char
            
        final_roman = roman + suffix_roman
        
        # Post-processing cleanups (Rule 5)
        # "aa a" -> "aaa" ? No, user said avoid duplication.
        # "aa" is okay. "aaa" is bad.
        # "iy" + "on" -> "iyon" (correct).
        
        # Specific fix for "ai" mapping if needed, e.g. "hay" -> "hai" is in override.
        
        return final_roman

    def transliterate_text(self, text: str) -> str:
        """
        Transliterates full text while preserving structure.
        """
        if not text:
            return ""

        # Split by whitespace to preserve word boundaries
        tokens = re.split(r'(\s+)', text)
        output = []

        for token in tokens:
            # Check for math/formulas protection
            if any(c in token for c in "=+-*/^"):
                output.append(token)
                continue
            
            # Check for capital single letters variables
            if token.strip() in ['L', 'M', 'F', 'X', 'Y', 'Z', 'A', 'B', 'C']:
                 output.append(token)
                 continue

            output.append(self.transliterate_word(token))
            
        result = "".join(output)
        
        # Phase 6: Clean Output Normalization
        # Remove duplicate spaces
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result

# Singleton instance
transliterator = RomanTransliterator()

def urdu_to_roman(text: str) -> str:
    """Wrapper"""
    return transliterator.transliterate_text(text)
