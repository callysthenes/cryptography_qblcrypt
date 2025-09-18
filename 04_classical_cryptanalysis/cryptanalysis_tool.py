#!/usr/bin/env python3
"""
Classical Cryptanalysis Tool
Analyzes frequency distributions and patterns in classical cryptographic schemes
"""

import string
import collections
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple
import re

class CryptAnalyzer:
    def __init__(self):
        # English letter frequencies (approximate percentages)
        self.english_freq = {
            'A': 8.12, 'B': 1.49, 'C': 2.78, 'D': 4.25, 'E': 12.02, 'F': 2.23,
            'G': 2.02, 'H': 6.09, 'I': 6.97, 'J': 0.15, 'K': 0.77, 'L': 4.03,
            'M': 2.41, 'N': 6.75, 'O': 7.51, 'P': 1.93, 'Q': 0.10, 'R': 5.99,
            'S': 6.33, 'T': 9.06, 'U': 2.76, 'V': 0.98, 'W': 2.36, 'X': 0.15,
            'Y': 1.97, 'Z': 0.07
        }
        
        # Common English bigrams and trigrams
        self.common_bigrams = ['TH', 'HE', 'IN', 'ER', 'AN', 'RE', 'ED', 'ND', 'ON', 'EN']
        self.common_trigrams = ['THE', 'AND', 'ING', 'HER', 'HAT', 'HIS', 'THA', 'ERE', 'FOR', 'ENT']
    
    def clean_text(self, text: str) -> str:
        """Remove non-alphabetic characters and convert to uppercase"""
        return ''.join(char.upper() for char in text if char.isalpha())
    
    def frequency_analysis(self, text: str) -> Dict[str, float]:
        """Perform frequency analysis on the given text"""
        clean_text = self.clean_text(text)
        total_chars = len(clean_text)
        
        if total_chars == 0:
            return {}
        
        freq_count = collections.Counter(clean_text)
        freq_percent = {char: (count / total_chars) * 100 
                       for char, count in freq_count.items()}
        
        return dict(sorted(freq_percent.items()))
    
    def bigram_analysis(self, text: str) -> Dict[str, int]:
        """Analyze bigram (two-letter) patterns"""
        clean_text = self.clean_text(text)
        bigrams = [clean_text[i:i+2] for i in range(len(clean_text)-1)]
        return dict(collections.Counter(bigrams).most_common(20))
    
    def trigram_analysis(self, text: str) -> Dict[str, int]:
        """Analyze trigram (three-letter) patterns"""
        clean_text = self.clean_text(text)
        trigrams = [clean_text[i:i+3] for i in range(len(clean_text)-2)]
        return dict(collections.Counter(trigrams).most_common(15))
    
    def index_of_coincidence(self, text: str) -> float:
        """Calculate Index of Coincidence (IC) - useful for determining key length"""
        clean_text = self.clean_text(text)
        n = len(clean_text)
        
        if n <= 1:
            return 0.0
        
        freq_count = collections.Counter(clean_text)
        ic = sum(count * (count - 1) for count in freq_count.values()) / (n * (n - 1))
        
        return ic
    
    def chi_squared_test(self, text: str) -> float:
        """Calculate chi-squared statistic compared to English"""
        observed_freq = self.frequency_analysis(text)
        chi_squared = 0.0
        text_length = len(self.clean_text(text))
        
        for letter in string.ascii_uppercase:
            observed = observed_freq.get(letter, 0) * text_length / 100
            expected = self.english_freq[letter] * text_length / 100
            if expected > 0:
                chi_squared += ((observed - expected) ** 2) / expected
        
        return chi_squared
    
    def kasiski_examination(self, text: str, min_length: int = 3) -> Dict[str, List[int]]:
        """Find repeated sequences and their distances (Kasiski examination)"""
        clean_text = self.clean_text(text)
        sequences = {}
        
        for length in range(min_length, min(10, len(clean_text) // 2)):
            for i in range(len(clean_text) - length + 1):
                seq = clean_text[i:i+length]
                if seq in sequences:
                    sequences[seq].append(i)
                else:
                    sequences[seq] = [i]
        
        # Filter out sequences that appear only once
        repeated_sequences = {seq: positions for seq, positions in sequences.items() 
                            if len(positions) > 1}
        
        # Calculate distances between occurrences
        sequence_distances = {}
        for seq, positions in repeated_sequences.items():
            distances = []
            for i in range(len(positions) - 1):
                distances.append(positions[i+1] - positions[i])
            sequence_distances[seq] = distances
        
        return sequence_distances
    
    def plot_frequency_analysis(self, text: str, title: str = "Frequency Analysis"):
        """Create a bar chart comparing text frequencies to English frequencies"""
        text_freq = self.frequency_analysis(text)
        
        letters = list(string.ascii_uppercase)
        text_freqs = [text_freq.get(letter, 0) for letter in letters]
        english_freqs = [self.english_freq[letter] for letter in letters]
        
        x = np.arange(len(letters))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(15, 8))
        bars1 = ax.bar(x - width/2, text_freqs, width, label='Ciphertext', alpha=0.8)
        bars2 = ax.bar(x + width/2, english_freqs, width, label='English', alpha=0.8)
        
        ax.set_xlabel('Letters')
        ax.set_ylabel('Frequency (%)')
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(letters)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def analyze_caesar_cipher(self, ciphertext: str) -> Dict[int, float]:
        """Try all possible Caesar cipher shifts and rank by chi-squared"""
        results = {}
        
        for shift in range(26):
            decrypted = self.caesar_decrypt(ciphertext, shift)
            chi_sq = self.chi_squared_test(decrypted)
            results[shift] = chi_sq
        
        # Sort by chi-squared (lower is better)
        return dict(sorted(results.items(), key=lambda x: x[1]))
    
    def caesar_decrypt(self, text: str, shift: int) -> str:
        """Decrypt text using Caesar cipher with given shift"""
        clean_text = self.clean_text(text)
        decrypted = ""
        
        for char in clean_text:
            shifted = (ord(char) - ord('A') - shift) % 26
            decrypted += chr(shifted + ord('A'))
        
        return decrypted
    
    def analyze_vigenere_key_length(self, text: str, max_key_length: int = 20) -> Dict[int, float]:
        """Estimate Vigenère key length using Index of Coincidence"""
        clean_text = self.clean_text(text)
        key_length_scores = {}
        
        for key_length in range(1, min(max_key_length + 1, len(clean_text) // 2)):
            # Split text into columns based on key length
            columns = [''] * key_length
            for i, char in enumerate(clean_text):
                columns[i % key_length] += char
            
            # Calculate average IC for all columns
            avg_ic = sum(self.index_of_coincidence(col) for col in columns) / key_length
            key_length_scores[key_length] = avg_ic
        
        return dict(sorted(key_length_scores.items(), key=lambda x: x[1], reverse=True))
    
    def print_analysis_report(self, text: str, title: str = "Cryptanalysis Report"):
        """Generate comprehensive analysis report"""
        print(f"\n{'='*60}")
        print(f"{title}")
        print(f"{'='*60}")
        
        clean_text = self.clean_text(text)
        print(f"Text length: {len(clean_text)} characters")
        print(f"Index of Coincidence: {self.index_of_coincidence(text):.4f}")
        print(f"Chi-squared vs English: {self.chi_squared_test(text):.2f}")
        
        print(f"\n{'-'*40}")
        print("FREQUENCY ANALYSIS")
        print(f"{'-'*40}")
        freq = self.frequency_analysis(text)
        for i, (char, pct) in enumerate(freq.items()):
            if i % 4 == 0:
                print()
            print(f"{char}: {pct:5.2f}%", end="  ")
        print()
        
        print(f"\n{'-'*40}")
        print("TOP BIGRAMS")
        print(f"{'-'*40}")
        bigrams = self.bigram_analysis(text)
        for i, (bg, count) in enumerate(list(bigrams.items())[:10]):
            if i % 5 == 0:
                print()
            print(f"{bg}: {count:3d}", end="  ")
        print()
        
        print(f"\n{'-'*40}")
        print("TOP TRIGRAMS")
        print(f"{'-'*40}")
        trigrams = self.trigram_analysis(text)
        for i, (tg, count) in enumerate(list(trigrams.items())[:10]):
            if i % 5 == 0:
                print()
            print(f"{tg}: {count:2d}", end="  ")
        print()
        
        print(f"\n{'-'*40}")
        print("KASISKI EXAMINATION")
        print(f"{'-'*40}")
        kasiski = self.kasiski_examination(text)
        for seq, distances in list(kasiski.items())[:5]:
            print(f"'{seq}': distances {distances}")
        
        print(f"\n{'-'*40}")
        print("CAESAR CIPHER ANALYSIS (Top 5 shifts)")
        print(f"{'-'*40}")
        caesar_results = self.analyze_caesar_cipher(text)
        for i, (shift, chi_sq) in enumerate(list(caesar_results.items())[:5]):
            decrypted_sample = self.caesar_decrypt(text, shift)[:50]
            print(f"Shift {shift:2d} (χ²={chi_sq:6.2f}): {decrypted_sample}...")
        
        print(f"\n{'-'*40}")
        print("VIGENÈRE KEY LENGTH ANALYSIS (Top 5)")
        print(f"{'-'*40}")
        vigenere_results = self.analyze_vigenere_key_length(text)
        for key_len, ic in list(vigenere_results.items())[:5]:
            print(f"Key length {key_len:2d}: IC = {ic:.4f}")


def main():
    """Main function with example usage"""
    analyzer = CryptAnalyzer()
    
    # Example ciphertext (you can replace this with your own)
    sample_ciphertext = """
    WKLV LV D VDPSOH PHVVDJH HQFUBSWHG ZLWK D VLPSOH FDHVDU FLSKHU
    WKH TXLFN EURZQ IRA MXPSV RYHU WKH ODCB GRJ
    """
    
    print("Classical Cryptanalysis Tool")
    print("=" * 60)
    
    # Option 1: Use sample text
    print("\nOption 1: Analyze sample Caesar cipher")
    print("Sample text:", sample_ciphertext.strip())
    analyzer.print_analysis_report(sample_ciphertext, "Sample Caesar Cipher Analysis")
    
    # Create frequency plot
    try:
        analyzer.plot_frequency_analysis(sample_ciphertext, "Sample Caesar Cipher Frequency Analysis")
    except Exception as e:
        print(f"Note: Plotting requires matplotlib. Error: {e}")
    
    print("\n" + "="*60)
    print("INTERACTIVE MODE")
    print("="*60)
    
    # Interactive mode
    while True:
        print("\nChoose an option:")
        print("1. Analyze your own ciphertext")
        print("2. Generate sample substitution cipher")
        print("3. Analyze Vigenère cipher")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            ciphertext = input("\nEnter your ciphertext: ").strip()
            if ciphertext:
                analyzer.print_analysis_report(ciphertext, "Custom Ciphertext Analysis")
                
                plot_choice = input("\nGenerate frequency plot? (y/n): ").strip().lower()
                if plot_choice == 'y':
                    try:
                        analyzer.plot_frequency_analysis(ciphertext, "Custom Ciphertext Frequency Analysis")
                    except Exception as e:
                        print(f"Plotting error: {e}")
        
        elif choice == '2':
            # Generate a simple substitution cipher example
            plaintext = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
            # Simple substitution: A->Z, B->Y, C->X, etc.
            substitution = str.maketrans(
                'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                'ZYXWVUTSRQPONMLKJIHGFEDCBA'
            )
            ciphertext = plaintext.translate(substitution)
            
            print(f"\nGenerated substitution cipher:")
            print(f"Plaintext:  {plaintext}")
            print(f"Ciphertext: {ciphertext}")
            
            analyzer.print_analysis_report(ciphertext, "Generated Substitution Cipher Analysis")
        
        elif choice == '3':
            # Vigenère analysis example
            vigenere_example = """
            LXFOPVEFRNHR MPRFAQZLDX LWEKKIFMHQ ZFGPIWK RTGITIK FZGPDL ZFWQYXIK
            RXQYTXM ZFGQMWXLHYKRXWFLHGLV ZFGMVGADFCV ZFGNLKDYDGMFHQ WDGTIK
            """
            
            print(f"\nAnalyzing sample Vigenère cipher:")
            print(f"Ciphertext: {vigenere_example.strip()}")
            analyzer.print_analysis_report(vigenere_example, "Vigenère Cipher Analysis")
        
        elif choice == '4':
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please enter 1-4.")


# Additional utility functions
def calculate_mutual_index_of_coincidence(text1: str, text2: str) -> float:
    """Calculate mutual index of coincidence between two texts"""
    clean_text1 = ''.join(char.upper() for char in text1 if char.isalpha())
    clean_text2 = ''.join(char.upper() for char in text2 if char.isalpha())
    
    n1, n2 = len(clean_text1), len(clean_text2)
    if n1 == 0 or n2 == 0:
        return 0.0
    
    freq1 = collections.Counter(clean_text1)
    freq2 = collections.Counter(clean_text2)
    
    mic = sum(freq1[char] * freq2[char] for char in string.ascii_uppercase) / (n1 * n2)
    return mic


def friedman_test(text: str) -> float:
    """Estimate key length using Friedman's method"""
    clean_text = ''.join(char.upper() for char in text if char.isalpha())
    n = len(clean_text)
    
    if n <= 1:
        return 1.0
    
    ic = CryptAnalyzer().index_of_coincidence(text)
    
    # Friedman's formula: L ≈ 0.027n / ((n-1) * IC - 0.038n + 0.065)
    if (n-1) * ic - 0.038 * n + 0.065 != 0:
        estimated_length = (0.027 * n) / ((n-1) * ic - 0.038 * n + 0.065)
        return max(1.0, estimated_length)
    else:
        return 1.0


def detect_cipher_type(text: str) -> str:
    """Attempt to identify the cipher type based on statistical analysis"""
    analyzer = CryptAnalyzer()
    ic = analyzer.index_of_coincidence(text)
    chi_sq = analyzer.chi_squared_test(text)
    
    if ic > 0.06:
        if chi_sq < 100:
            return "Likely plaintext or simple substitution"
        else:
            return "Likely monoalphabetic substitution cipher"
    elif ic > 0.04:
        return "Likely polyalphabetic cipher (Vigenère, etc.)"
    else:
        return "Likely complex polyalphabetic or random text"


if __name__ == "__main__":
    # Example usage
    print("Testing cipher type detection:")
    
    # Test different cipher types
    test_texts = {
        "Caesar": "WKH TXLFN EURZQ IRA MXPSV RYHU WKH ODCB GRJ",
        "Substitution": "WKH TXLFN EURZQ IRA MXPSV RYHU WKH ODCB GRJ".translate(
            str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'QWERTYUIOPASDFGHJKLZXCVBNM')
        ),
        "Plaintext": "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
    }
    
    for cipher_type, text in test_texts.items():
        detected = detect_cipher_type(text)
        print(f"{cipher_type}: {detected}")
    
    print("\n" + "="*60)
    print("Starting interactive analysis tool...")
    main()
