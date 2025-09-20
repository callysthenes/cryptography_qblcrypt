#!/usr/bin/env python3
import random
import hashlib
import argparse

DEFAULT_SEED = 42

def seed_to_int(seed_value: str) -> int:
    """
    Convert a seed string to an integer deterministically.
    If the string is already an integer literal, use it directly.
    Otherwise hash it with sha256 and convert to int.
    """
    seed_value = seed_value.strip()
    if seed_value == "":
        return DEFAULT_SEED
    try:
        return int(seed_value)
    except ValueError:
        h = hashlib.sha256(seed_value.encode("utf-8")).digest()
        return int.from_bytes(h, "big")

def generate_prng_data(seed: int, filename: str, num_bytes: int):
    """
    Generates a file with pseudo-random data from a standard PRNG.
    Seeding makes the output deterministic (not secure for cryptography).
    """
    print(f"Generating {num_bytes // 1024} KB of standard PRNG data...")
    print(f"Using seed (int): {seed}")

    rng = random.Random(seed)

    random_data = bytearray()
    for _ in range(num_bytes):
        random_data.append(rng.getrandbits(8))

    try:
        with open(filename, "wb") as f:
            f.write(random_data)
        print(f"Successfully created '{filename}'.")
    except IOError as e:
        print(f"Error writing to file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Generate deterministic PRNG data file.")
    parser.add_argument("-s", "--seed", type=str,
                        help="Seed value (integer or text). If omitted you'll be prompted. Empty => default 42.")
    parser.add_argument("-o", "--output", type=str, default="prng_data.bin",
                        help="Output filename (default: prng_data.bin)")
    parser.add_argument("-n", "--num-bytes", type=int, default=1024*1024,
                        help="Number of bytes to generate (default: 1 MB)")
    args = parser.parse_args()

    seed_input = args.seed
    if seed_input is None:
        try:
            seed_input = input("Enter seed (integer or text). Leave empty for default 42: ")
        except (KeyboardInterrupt, EOFError):
            print("\nInput cancelled. Using default seed 42.")
            seed_input = ""

    seed_int = seed_to_int(seed_input)
    generate_prng_data(seed_int, args.output, args.num_bytes)

if __name__ == "__main__":
    main()
