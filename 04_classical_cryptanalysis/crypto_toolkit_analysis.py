import collections
import re
import math

class CryptoAnalyzer:
    """
    A toolkit for performing classical cryptanalysis on a given ciphertext.
    It includes frequency analysis, n-gram analysis, Index of Coincidence,
    Kasiski Examination, and word pattern analysis.
    """
    def __init__(self, ciphertext):
        # Sanitize the text: uppercase letters only
        self.raw_text = ciphertext
        self.ciphertext = ''.join(filter(str.isalpha, ciphertext)).upper()
        self.length = len(self.ciphertext)
        self.frequencies = collections.Counter(self.ciphertext)
        # Standard English letter frequencies for comparison
        self.english_ioc = 0.067

    def analyze_letter_frequency(self):
        """Calculates and prints the frequency of each letter."""
        print("--- 1. Letter Frequency Analysis ---")
        print(f"Total letters: {self.length}")
        sorted_freqs = self.frequencies.most_common()
        for letter, count in sorted_freqs:
            percentage = (count / self.length) * 100
            print(f"  {letter}: {count:<4} ({percentage:.2f}%)")
        print("-" * 35)

    def analyze_ngrams(self, n=2):
        """Calculates and prints the frequency of n-grams (digrams, trigrams, etc.)."""
        print(f"--- 2. Top 10 {n}-gram Analysis ---")
        ngrams = [self.ciphertext[i:i+n] for i in range(self.length - n + 1)]
        ngram_counts = collections.Counter(ngrams).most_common(10)
        for ngram, count in ngram_counts:
            print(f"  {ngram}: {count}")
        print("-" * 35)

    def calculate_ioc(self):
        """Calculates and prints the Index of Coincidence (IoC)."""
        print("--- 3. Index of Coincidence (IoC) ---")
        numerator = sum(count * (count - 1) for count in self.frequencies.values())
        denominator = self.length * (self.length - 1)
        ioc = numerator / denominator if denominator > 0 else 0
        
        print(f"  Calculated IoC: {ioc:.4f}")
        print(f"  Standard English IoC: {self.english_ioc:.4f}")
        
        if abs(ioc - self.english_ioc) < 0.01:
            print("  Analysis: IoC is high. Suggests a monoalphabetic substitution cipher.")
        else:
            print("  Analysis: IoC is low. Suggests a polyalphabetic cipher (e.g., Vigenère).")
        print("-" * 35)

    def _get_factors(self, number):
        """Helper function to get all factors of a number."""
        factors = set()
        for i in range(2, int(math.sqrt(number)) + 1):
            if number % i == 0:
                factors.add(i)
                factors.add(number // i)
        return factors

    def perform_kasiski_examination(self, min_len=3, max_len=5):
        """Performs Kasiski examination to guess key length for polyalphabetic ciphers."""
        print("--- 4. Kasiski Examination (Key Length Guess) ---")
        
        repeated_sequences = {}
        for length in range(min_len, max_len + 1):
            for i in range(self.length - length):
                seq = self.ciphertext[i:i+length]
                if seq in repeated_sequences:
                    continue
                
                indices = [m.start() for m in re.finditer(re.escape(seq), self.ciphertext)]
                if len(indices) > 1:
                    repeated_sequences[seq] = indices

        if not repeated_sequences:
            print("  No significant repeated sequences found.")
            print("-" * 35)
            return

        possible_factors = collections.Counter()
        for seq, indices in repeated_sequences.items():
            distances = [indices[j] - indices[j-1] for j in range(1, len(indices))]
            for dist in distances:
                factors = self._get_factors(dist)
                possible_factors.update(factors)

        print("  Top 5 most likely key lengths:")
        for length, count in possible_factors.most_common(5):
            print(f"  - Length {length} (found {count} times)")
        print("-" * 35)

    def _get_word_pattern(self, word):
        """Helper function to create a word pattern like 'ABBC'."""
        pattern = ""
        mapping = {}
        next_char_code = ord('A')
        for char in word:
            if char not in mapping:
                mapping[char] = chr(next_char_code)
                next_char_code += 1
            pattern += mapping[char]
        return pattern

    def analyze_word_patterns(self):
        """Analyzes and prints word patterns from the text."""
        print("--- 5. Word Pattern Analysis ---")
        words = re.findall(r'[a-zA-Z]+', self.raw_text.upper())
        pattern_counts = collections.Counter()
        
        for word in words:
            if len(word) > 2:
                pattern = self._get_word_pattern(word)
                pattern_counts[pattern] += 1
        
        print("  Top 5 most common word patterns found:")
        for pattern, count in pattern_counts.most_common(5):
            example_word = next((w for w in words if self._get_word_pattern(w) == pattern), "")
            print(f"  - Pattern '{pattern}' (e.g., '{example_word}') appeared {count} times.")
        print("-" * 35)

def run_analysis(text_to_analyze):
    """Initializes the analyzer and runs all analysis methods."""
    analyzer = CryptoAnalyzer(text_to_analyze)
    analyzer.analyze_letter_frequency()
    analyzer.analyze_ngrams(n=2)
    analyzer.analyze_ngrams(n=3)
    analyzer.calculate_ioc()
    analyzer.perform_kasiski_examination()
    analyzer.analyze_word_patterns()

if __name__ == "__main__":
    print("=" * 20 + " Interactive Cryptanalysis Toolkit " + "=" * 20)
    
    # Get ciphertext directly from user input
    print("➡️ Enter your ciphertext below (press Enter twice when finished):")
    
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    
    ciphertext = "\n".join(lines)
    
    if ciphertext.strip():
        print("\n" + "=" * 20 + " ANALYSIS OF YOUR CIPHERTEXT " + "=" * 20)
        run_analysis(ciphertext)
    else:
        print("\n[!] Error: No ciphertext was entered.")
