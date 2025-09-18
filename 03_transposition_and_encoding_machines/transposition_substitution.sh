#!/bin/bash

echo "Enter text:"
read plaintext

# Caesar substitution: shift by 3 (simple monoalphabetic substitute)
ciphertext=$(echo "$plaintext" | tr 'A-Za-z' 'D-ZA-Cd-za-c')
echo "Substitution (Caesar Shift 3): $ciphertext"

# Basic transposition: reverse the text
transposed=$(echo "$ciphertext" | rev)
echo "Transposed: $transposed"
