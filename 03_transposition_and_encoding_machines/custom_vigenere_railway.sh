#!/bin/bash

# --- Helper functions ---

# Convert letter to 0-25 index (A=0, Z=25)
ord() {
    LC_CTYPE=C printf '%d' "'$1"
}

chr() {
    printf "\\$(printf '%03o' "$1")"
}

# Normalize input (uppercase, remove spaces)
normalize() {
    echo "$1" | tr '[:lower:]' '[:upper:]' | tr -d ' '
}

# Vigenere Encrypt
vigenere_encrypt() {
    local text=$(normalize "$1")
    local key=$(normalize "$2")
    local result=""
    local keylen=${#key}
    local i=0

    for ((j=0; j<${#text}; j++)); do
        c=${text:j:1}
        if [[ "$c" =~ [A-Z] ]]; then
            cval=$(( $(ord "$c") - 65 ))
            kval=$(( $(ord "${key:i%keylen:1}") - 65 ))
            new=$(( (cval + kval) % 26 ))
            result+=$(chr $((new + 65)))
            ((i++))
        fi
    done
    echo "$result"
}

# Vigenere Decrypt
vigenere_decrypt() {
    local text=$(normalize "$1")
    local key=$(normalize "$2")
    local result=""
    local keylen=${#key}
    local i=0

    for ((j=0; j<${#text}; j++)); do
        c=${text:j:1}
        if [[ "$c" =~ [A-Z] ]]; then
            cval=$(( $(ord "$c") - 65 ))
            kval=$(( $(ord "${key:i%keylen:1}") - 65 ))
            new=$(( (cval - kval + 26) % 26 ))
            result+=$(chr $((new + 65)))
            ((i++))
        fi
    done
    echo "$result"
}

# Compute Rail Fence depth from password using "fractal math"
rail_depth() {
    local key=$(normalize "$1")
    local sum=0
    for ((j=0; j<${#key}; j++)); do
        c=${key:j:1}
        val=$(( $(ord "$c") - 64 )) # A=1
        sum=$((sum + val))
    done
    # reduce to single digit
    while [ $sum -gt 9 ]; do
        newsum=0
        for ((i=0; i<${#sum}; i++)); do
            newsum=$((newsum + ${sum:i:1}))
        done
        sum=$newsum
    done
    if [ $sum -lt 2 ]; then
        sum=2
    fi
    echo $sum
}

# Rail Fence Encrypt
rail_fence_encrypt() {
    local text="$1"
    local rails=$2
    local len=${#text}
    local result=""

    for ((r=0; r<rails; r++)); do
        pos=$r
        dir=1
        while [ $pos -lt $len ]; do
            result+=${text:pos:1}
            if [ $r -eq 0 ] || [ $r -eq $((rails-1)) ]; then
                pos=$((pos + 2*(rails-1)))
            else
                if [ $dir -eq 1 ]; then
                    pos=$((pos + 2*(rails-r-1)))
                    dir=0
                else
                    pos=$((pos + 2*r))
                    dir=1
                fi
            fi
        done
    done
    echo "$result"
}

# Rail Fence Decrypt
rail_fence_decrypt() {
    local text="$1"
    local rails=$2
    local len=${#text}
    local rail=()
    local mark=()
    for ((i=0; i<len; i++)); do
        mark+=("_")
    done

    # mark zigzag pattern
    idx=0
    dir=1
    for ((i=0; i<len; i++)); do
        mark[$i]=$idx
        if [ $idx -eq 0 ]; then dir=1; fi
        if [ $idx -eq $((rails-1)) ]; then dir=-1; fi
        idx=$((idx + dir))
    done

    # assign ciphertext to rails
    pos=0
    for ((r=0; r<rails; r++)); do
        for ((i=0; i<len; i++)); do
            if [ ${mark[$i]} -eq $r ]; then
                rail[$i]=${text:pos:1}
                ((pos++))
            fi
        done
    done

    echo "${rail[*]}" | tr -d ' '
}

# --- Main Program ---
read -p "Mode (encrypt/decrypt): " mode
read -p "Enter password: " password
read -p "Enter message: " message

depth=$(rail_depth "$password")

if [ "$mode" == "encrypt" ]; then
    step1=$(vigenere_encrypt "$message" "$password")
    final=$(rail_fence_encrypt "$step1" $depth)
    echo "Encrypted message: $final"
elif [ "$mode" == "decrypt" ]; then
    step1=$(rail_fence_decrypt "$message" $depth)
    final=$(vigenere_decrypt "$step1" "$password")
    echo "Decrypted message: $final"
else
    echo "Invalid mode."
fi
