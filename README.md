# 🔐 Applied Cryptography & Secure Systems

![Cryptography Banner](https://placehold.co/1200x300/4338ca/ffffff?text=Applied+Cryptography+%26+Secure+Systems)

Welcome to the official GitHub repository for the **Applied Cryptography** course. This repository contains all the hands-on lab exercises for the semester.

> 📌 **Our philosophy:** *You learn by doing.*

Forget endless static slides—here, you’ll **write code**, **break ciphers**, **analyze network traffic**, and build a **practical portfolio** of cryptographic skills.

We explore modern cryptographic systems through Python, real-world tools, and secure development practices.

---

## 🚀 Getting Started

To ensure everyone has a uniform environment, **all labs are conducted inside a Kali Linux Virtual Machine (VM)**.

### 1️⃣ Install Kali Linux

- Download the latest **Kali Linux VirtualBox** from here.
- Import the VM into VirtualBox using your platform’s import wizard.

### 2️⃣ Configure Your Tools

Open a terminal inside your Kali VM and install the essential tools for this course:

```bash
sudo apt update && sudo apt install -y git python3 python3-pip xclip openssl
🔧 Set Up Git & GitHub
3️⃣ Create and Configure Your GitHub Account
Go to GitHub.com and create a free account if you don’t already have one.

Configure Git with your name and email (used for commits):

bash
Copy
Edit
git config --global user.name "Your Name"
git config --global user.email "your.student_email@example.com"
4️⃣ Fork and Clone the Repository
Visit the course repository:
👉 https://github.com/callysthenes/cryptography_qblcrypt

Click Fork in the upper-right to create your own copy.

Clone your fork to your Kali VM:

bash
Copy
Edit
git clone git@github.com:your_username/cryptography_qblcrypt.git
cd cryptography_qblcrypt
💡 Replace your_username with your actual GitHub username.

5️⃣ Set Up SSH Access (One-Time Only)
To enable pushing code securely via SSH:

bash
Copy
Edit
# Generate SSH key
ssh-keygen -t ed25519 -C "your.student_email@example.com"
# Press Enter three times to accept the defaults

# Start SSH agent and add your key
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key to clipboard
cat ~/.ssh/id_ed25519.pub | xclip -sel clip
Then:

Go to GitHub → Settings → SSH and GPG keys → New SSH key

Paste the copied key and save.

6️⃣ Submit Your Work
Each time you complete lab work:

bash
Copy
Edit
git add .
git commit -m "Lab submission by $(git config user.name)"
git push origin main
Then open your browser:

Navigate to your forked repo

Click Contribute → Open Pull Request

Title it:
Submission – YOUR_FULL_NAME

Click Create Pull Request 🎉

📚 Course Structure & Labs
Lab #	Topic	Directory Path	Key Skills
01	Classical Cryptanalysis	01_Classical_Ciphers/	Frequency Analysis, Python
02	Symmetric Encryption	02_Symmetric_Encryption/	AES-GCM, Cryptography Library
03	Password Hashing & Security	03_Hashing_Passwords/	bcrypt, argon2, Secure Storage
04	Asymmetric Crypto & Signatures	04_Asymmetric_Crypto/	RSA, OpenSSL, Digital Signatures
05	Public Key Infrastructure (PKI)	05_PKI_Validation/	OpenSSL CLI, Certificate Chain Validation
06	Network Traffic Analysis	06_Network_Forensics/	Wireshark, TLS, Traffic Forensics

⚖️ Ethics & Responsibility
The tools and techniques taught—especially those involving Kali Linux—are powerful and must be used responsibly.

❗ Use your knowledge only on systems you own or are authorized to test.
Unauthorized use is unethical, illegal, and strictly forbidden.

🤖 Use LLMs for Mastery
LLMs like ChatGPT or Gemini can help you go deeper into any topic. Use them for clarity, exploration, or guided practice.

🧠 Example Prompt
Act as a cybersecurity protocol designer. Explain the concept of Forward Secrecy in TLS.
Why does an ephemeral Diffie-Hellman handshake (DHE/ECDHE) provide this property, while a classic RSA key exchange does not?
Describe a scenario where the lack of forward secrecy could be catastrophic.

Happy hacking — ethically.
