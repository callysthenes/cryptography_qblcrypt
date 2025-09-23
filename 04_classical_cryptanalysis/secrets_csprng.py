import secrets
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Function to calculate Shannon entropy of bytes
def shannon_entropy(hexstr):
    b = bytes.fromhex(hexstr)
    probs = np.bincount(list(b), minlength=256) / len(b)
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs))

# Generate random hex tokens for multiple students
students = ['A', 'B', 'C']
results = []

for s in students:
    hexval = secrets.token_hex(16)  # 128 bits = 32 hex digits
    entropy = shannon_entropy(hexval)
    unique_bytes = len(set(bytes.fromhex(hexval)))
    results.append({
        "Student": f"Student {s}",
        "Hex": hexval,
        "Length_bytes": len(hexval) // 2,
        "Entropy": entropy,
        "Unique_bytes": unique_bytes,
    })

df = pd.DataFrame(results)
print(df)

# Visualize Shannon entropy per token
sns.barplot(x="Student", y="Entropy", data=df)
plt.title("Shannon Entropy per secrets.token_hex(16)")
plt.ylabel("Entropy (bits per byte)")
plt.xlabel("Student")
plt.show()

# Visualize number of unique byte values per token
sns.barplot(x="Student", y="Unique_bytes", data=df)
plt.title("Unique Byte Values per Token")
plt.ylabel("Unique Byte Count")
plt.xlabel("Student")
plt.show()

# Visualizing the byte distribution for each student's token
for idx, row in df.iterrows():
    b = list(bytes.fromhex(row['Hex']))  # Convert bytes to list of ints (0–255)
    sns.histplot(b, bins=256, kde=False)
    plt.title(f"Byte Distribution for {row['Student']}")
    plt.xlabel("Byte Value (0-255)")
    plt.ylabel("Frequency")
    plt.show()

