import os

# Define the output filename and the number of bytes to generate
FILENAME = "csprng_data.bin"
NUM_BYTES = 1024 * 1024  # 1 MB

def generate_csprng_data():
    """
    Generates a file with cryptographically secure pseudo-random data.
    os.urandom() pulls from the operating system's entropy sources.
    """
    print(f"Generating {NUM_BYTES // 1024} KB of CSPRNG data...")

    # os.urandom() is the recommended function for generating
    # cryptographically secure random bytes. It does not require manual seeding.
    # remember python does also have another module called secrets
    try:
        random_data = os.urandom(NUM_BYTES)

        # Write the data to a binary file
        with open(FILENAME, "wb") as f:
            f.write(random_data)
        print(f"Successfully created '{FILENAME}'.")
    except IOError as e:
        print(f"Error writing to file: {e}")
    except Exception as e:
        print(f"An error occurred during generation: {e}")


if __name__ == "__main__":
    generate_csprng_data()
