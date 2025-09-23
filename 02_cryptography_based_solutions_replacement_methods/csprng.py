# =============================================================================
#
#   A Student's Guide to Cracking Python's `random` Module
#
#   This script provides a detailed, step-by-step visualization of the
#   bitwise operations used to reverse the generator's disguise and
#   predict its output.
#
# =============================================================================

import random
import time

# --- These are the official "magic numbers" for the Mersenne Twister algorithm ---
(W, N, M, R) = (32, 624, 397, 31)
A = 0x9908B0DF
U, D = 11, 0xFFFFFFFF
S, B = 7, 0x9D2C5680
T, C = 15, 0xEFC60000
L = 18
F = 1812433253
LOWER_MASK = (1 << R) - 1
UPPER_MASK = (~LOWER_MASK) & D

# --- Helper function to make binary numbers easy to read ---
def to_binary(n):
    """Formats a number as a readable 32-bit binary string."""
    b = bin(n)[2:].zfill(32)
    return ' '.join(b[i:i+8] for i in range(0, 32, 8))

# --- Mathematically Correct Reversal Functions ---
def reverse_right_shift_xor(y, shift):
    res = y
    for _ in range(32 // shift + 1):
        res = y ^ (res >> shift)
    return res

def reverse_left_shift_xor(y, shift, mask):
    res = y
    for _ in range(32 // shift + 1):
        res = y ^ ((res << shift) & mask)
    return res

# --- Main Demonstration Script ---

# A simple wrapper for the main logic
def run_demonstration():
    print("="*80)
    print("PART 1: OBSERVING THE 'RANDOM' SEQUENCE")
    print("="*80)
    while True:
        try:
            seed_value = int(input("Enter any whole number to use as a seed (e.g., 42): "))
            break
        except ValueError:
            print("That wasn't a valid number. Please try again.")

    random.seed(seed_value)
    history = []
    for _ in range(903):
        history.append(random.getrandbits(32))

    print(f"\nSeeding the generator with '{seed_value}'. We have stored the first 903 numbers.")
    input("\nPress Enter to begin the attack...")
    
    # --- Step-by-step Untempering Visualization ---
    def untemper_verbose(y):
        """Reverses the disguise, showing each step."""
        print("\n" + "-"*80)
        print("STEP B: Reversing the Disguise (Untempering)")
        print(f"Let's dissect the first observed number: {y}")
        print(f"Binary: {to_binary(y)}")
        print("-" * 80)
        input("Press Enter to begin the 4-step reversal...")

        y_step = y
        
        print("\n[1/4] Reversing: y ^= (y >> 18)")
        y_step = reverse_right_shift_xor(y_step, L)
        print(f"      Before: {to_binary(y)}")
        print(f"      After:  {to_binary(y_step)}")
        input("Press Enter...")

        y = y_step
        print("\n[2/4] Reversing: y ^= (y << 15) & 0xEFC60000")
        y_step = reverse_left_shift_xor(y_step, T, C)
        print(f"      Before: {to_binary(y)}")
        print(f"      After:  {to_binary(y_step)}")
        input("Press Enter...")
        
        y = y_step
        print("\n[3/4] Reversing: y ^= (y << 7) & 0x9D2C5680")
        y_step = reverse_left_shift_xor(y_step, S, B)
        print(f"      Before: {to_binary(y)}")
        print(f"      After:  {to_binary(y_step)}")
        input("Press Enter...")
        
        y = y_step
        print("\n[4/4] Reversing: y ^= (y >> 11)")
        y_step = reverse_right_shift_xor(y_step, U)
        print(f"      Before: {to_binary(y)}")
        print(f"      After:  {to_binary(y_step)}")
        print("\nReversal complete! This is the true, undisguised internal number.")
        
        return y_step

    # Silent version for processing the rest of the numbers
    def untemper_silent(y):
        y = reverse_right_shift_xor(y, L)
        y = reverse_left_shift_xor(y, T, C)
        y = reverse_left_shift_xor(y, S, B)
        y = reverse_right_shift_xor(y, U)
        return y
    
    # --- Get observed numbers and reconstruct the state ---
    observed_numbers = history[900-N : 900]
    reconstructed_state = []

    # Process the first number verbosely
    first_true_number = untemper_verbose(observed_numbers[0])
    reconstructed_state.append(first_true_number)
    
    print("\nNow, reversing the remaining 623 numbers silently to build the full state...")
    time.sleep(2)
    for i in range(1, N):
        reconstructed_state.append(untemper_silent(observed_numbers[i]))
    print("...done.")
    print("We now have a perfect clone of the generator's internal state!")
    input("\nPress Enter to use this state to predict number 901...")
    
    # --- Step-by-step Prediction and Tempering Visualization ---
    print("\n" + "-"*80)
    print("STEP C: Predicting Number 901")
    print("-" * 80)
    
    print("1. Following the generator's recipe on our cloned state:")
    state = reconstructed_state
    val1, val2, val3 = state[0], state[1], state[M]
    print(f"   - Takes state[0]:   {to_binary(val1)}")
    print(f"   - Takes state[1]:   {to_binary(val2)}")
    print(f"   - Takes state[397]: {to_binary(val3)}")
    input("Press Enter...")

    y = (val1 & UPPER_MASK) | (val2 & LOWER_MASK)
    print(f"\n   - Mixes top of first and bottom of second:\n     {to_binary(y)}")
    input("Press Enter...")

    next_internal_val = val3 ^ (y >> 1) ^ A if (y & 1) else val3 ^ (y >> 1)
    print(f"\n   - Shifts, mixes with state[397] and a magic number to get the new internal state value:\n     {to_binary(next_internal_val)}")
    print("\nThis is the PREDICTED true number. Now we must apply the disguise to match the generator's output.")
    input("Press Enter to apply the 4-step disguise (Tempering)...")
    
    print("\n2. Applying the Disguise (Tempering):")
    y_tempered_step = next_internal_val
    print(f"      Start:  {to_binary(y_tempered_step)}")
    
    print("\n   [1/4] Applying: y ^= y >> 11")
    y_tempered_step ^= (y_tempered_step >> U)
    print(f"      Result: {to_binary(y_tempered_step)}")
    input("Press Enter...")

    print("\n   [2/4] Applying: y ^= (y << 7) & 0x9D2C5680")
    y_tempered_step ^= (y_tempered_step << S) & B
    print(f"      Result: {to_binary(y_tempered_step)}")
    input("Press Enter...")

    print("\n   [3/4] Applying: y ^= (y << 15) & 0xEFC60000")
    y_tempered_step ^= (y_tempered_step << T) & C
    print(f"      Result: {to_binary(y_tempered_step)}")
    input("Press Enter...")

    print("\n   [4/4] Applying: y ^= y >> 18")
    y_tempered_step ^= (y_tempered_step >> L)
    print(f"      Result: {to_binary(y_tempered_step)}")
    
    predicted_number = y_tempered_step
    actual_number = history[900]
    
    print("\n3. Comparing our final prediction to the real number:")
    print(f"   Our Prediction: {predicted_number}")
    print(f"   Actual Number:  {actual_number}")
    if predicted_number == actual_number:
        print("\n   RESULT: ✅ PERFECT MATCH!")
    else:
        print("\n   RESULT: ❌ MISMATCH!")
    
    print("\n\n" + "="*80)
    print("DEMONSTRATION COMPLETE!")
    print("We have successfully visualized every step of the attack.")
    print("="*80)

# Run the main demonstration
if __name__ == "__main__":
    run_demonstration()
