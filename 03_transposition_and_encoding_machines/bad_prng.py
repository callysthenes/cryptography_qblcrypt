#!/usr/bin/env python3

# A simple, flawed PRNG for demonstration purposes.

FILENAME = "bad_prng_data.bin"
NUM_BYTES = 1024 * 1024  # 1 MB

def generate_bad_prng_data(seed: int):
    """
    Generates data using a simple Linear Congruential Generator (LCG).
    Formula: X_{n+1} = (a * X_n + c) mod m
    """
    print(f"Generating {NUM_BYTES // 1024} KB of BAD PRNG data...")
    print(f"Using seed: {seed}")

    # Poor LCG parameters to show predictable patterns
    a = 1
    c = 7
    m = 256

    current_val = seed
    bad_random_data = bytearray()

    for _ in range(NUM_BYTES):
        current_val = (a * current_val + c) % m
        bad_random_data.append(current_val)

    try:
        with open(FILENAME, "wb") as f:
            f.write(bad_random_data)
        print(f"Successfully created '{FILENAME}'.")
    except IOError as e:
        print(f"Error writing to file: {e}")

def main():
    try:
        user_input = input("Enter a seed (integer, default 42): ")
        seed = int(user_input) if user_input.strip() != "" else 42
    except (ValueError, EOFError, KeyboardInterrupt):
        print("\nInvalid input or cancelled. Using default seed 42.")
        seed = 42

    generate_bad_prng_data(seed)

if __name__ == "__main__":
    main()
