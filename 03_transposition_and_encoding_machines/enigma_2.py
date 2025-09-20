#!/usr/bin/env python3
"""
Enigma I (3-rotor) interactive emulator with step-by-step pedagogical tracing.

Author: Pedro V
Senior Programmer Enhancement: Added a clear Encrypt/Decrypt menu.
The core logic remains unchanged due to the Enigma's reciprocal nature.
"""

from typing import Dict, List, Tuple

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
A2I = {c: i for i, c in enumerate(ALPHABET)}
I2A = {i: c for c, i in A2I.items()}


# Historical rotor wirings (Enigma I rotors I-V), and turnover notch positions
ROTOR_SPECS = {
    "I":  {"wiring": "EKMFLGDQVZNTOWYHXUSPAIBRCJ", "notch": "Q"},
    "II": {"wiring": "AJDKSIRUXBLHWTMCQGZNPYFVOE", "notch": "E"},
    "III":{"wiring": "BDFHJLCPRTXVZNYEIWGAKMUSQO", "notch": "V"},
    "IV": {"wiring": "ESOVPZJAYQUIRHXLNFTGKDCMWB", "notch": "J"},
    "V":  {"wiring": "VZBRGITYUPSDNHLXAWMJQOFECK", "notch": "Z"},
}

# Reflectors (B and C commonly used in period)
REFLECTOR_SPECS = {
    "B": "YRUHQSLDPXNGOKMIEBFZCWVJAT",
    "C": "FVPJIAOYEDRZXWGCTKUQSBNMHL",
}


def sanitize_plugboard_input(s: str) -> List[Tuple[str, str]]:
    """Parse a plugboard specification like 'AB CD EF' into [('A','B'), ('C','D'), ...]"""
    parts = s.strip().upper().split()
    pairs = []
    used = set()
    for token in parts:
        token = token.strip()
        if len(token) == 2 and token[0] in ALPHABET and token[1] in ALPHABET:
            a, b = token[0], token[1]
            if a == b:
                continue
            if a in used or b in used:
                raise ValueError(f"Plugboard letter repeated: {a} or {b} already used.")
            pairs.append((a, b))
            used.add(a); used.add(b)
        else:
            raise ValueError(f"Invalid plugboard token: '{token}'. Use pairs like 'AB CD EF'.")
    if len(pairs) > 10:
        raise ValueError("At most 10 plugboard pairs are allowed.")
    return pairs


class Rotor:
    def __init__(self, name: str, wiring: str, notch: str, ring_setting: int = 1, position: str = "A"):
        """
        - name: 'I', 'II', etc.
        - wiring: 26-char string, mapping from A-Z on rotor's forward side.
        - notch: letter at which rotor causes next rotor to step on turnover (e.g., 'Q' for rotor I).
        - ring_setting: 1..26 (Ringstellung). This shifts wiring relative to rotor position.
        - position: 'A'..'Z' (Grundstellung) current rotor window letter shown to operator.
        """
        self.name = name
        self.wiring = wiring.upper()
        self.notch = notch.upper()
        # Convert ring_setting and position to numeric indices (0..25)
        if not (1 <= ring_setting <= 26):
            raise ValueError("ring_setting must be in 1..26")
        self.ring = (ring_setting - 1)  # internal numeric 0..25
        if position not in ALPHABET:
            raise ValueError("position must be A-Z")
        self.pos = A2I[position]  # current rotor position 0..25

        # Precompute forward and backward mapping arrays (0..25)
        self.forward_map = [A2I[c] for c in self.wiring]
        # Build reverse mapping
        self.backward_map = [0] * 26
        for i, v in enumerate(self.forward_map):
            self.backward_map[v] = i

    def at_notch(self) -> bool:
        """Return True if rotor's current window letter is at its notch position."""
        return I2A[self.pos] == self.notch

    def step(self):
        """Advance rotor position by 1 (like rotating the rotor)."""
        self.pos = (self.pos + 1) % 26

    def encode_forward(self, c_idx: int) -> Tuple[int, str]:
        """
        Encode letter index traveling *from keyboard towards reflector* through this rotor.
        Returns (output_index, trace string).
        Formula (taking ring setting & rotor position into account):
        - convert c into rotor coordinate: (c + pos - ring) mod 26
        - apply wiring: wiring[rotor_coord] -> gives mapped letter index m
        - convert back to machine coordinate: (m - pos + ring) mod 26
        """
        rotor_coord = (c_idx + self.pos - self.ring) % 26
        mapped = self.forward_map[rotor_coord]
        out_idx = (mapped - self.pos + self.ring) % 26
        trace = (f"Rotor {self.name} forward: in={I2A[c_idx]}(idx{c_idx}) "
                 f"-> rotor_coord={I2A[rotor_coord]} -> wiring->{I2A[mapped]} "
                 f"-> out={I2A[out_idx]}(idx{out_idx}); pos={I2A[self.pos]}, ring={self.ring+1}")
        return out_idx, trace

    def encode_backward(self, c_idx: int) -> Tuple[int, str]:
        """
        Encode letter index traveling *from reflector back to keyboard* through rotor.
        Use backward_map with same coordinate transformation reversed.
        """
        rotor_coord = (c_idx + self.pos - self.ring) % 26
        mapped = self.backward_map[rotor_coord]
        out_idx = (mapped - self.pos + self.ring) % 26
        trace = (f"Rotor {self.name} backward: in={I2A[c_idx]}(idx{c_idx}) "
                 f"-> rotor_coord={I2A[rotor_coord]} -> wiring_inv->{I2A[mapped]} "
                 f"-> out={I2A[out_idx]}(idx{out_idx}); pos={I2A[self.pos]}, ring={self.ring+1}")
        return out_idx, trace


class EnigmaMachine:
    # --- Class content is unchanged ---
    def __init__(self,
                 rotor_names: List[str],
                 ring_settings: List[int],
                 initial_positions: List[str],
                 reflector_name: str,
                 plug_pairs: List[Tuple[str, str]]):
        if len(rotor_names) != 3 or len(ring_settings) != 3 or len(initial_positions) != 3:
            raise ValueError("Provide exactly three rotors, three ring settings, three initial positions.")
        self.left = Rotor(rotor_names[0], ROTOR_SPECS[rotor_names[0]]["wiring"],
                          ROTOR_SPECS[rotor_names[0]]["notch"],
                          ring_settings[0], initial_positions[0])
        self.middle = Rotor(rotor_names[1], ROTOR_SPECS[rotor_names[1]]["wiring"],
                            ROTOR_SPECS[rotor_names[1]]["notch"],
                            ring_settings[1], initial_positions[1])
        self.right = Rotor(rotor_names[2], ROTOR_SPECS[rotor_names[2]]["wiring"],
                           ROTOR_SPECS[rotor_names[2]]["notch"],
                           ring_settings[2], initial_positions[2])
        if reflector_name not in REFLECTOR_SPECS:
            raise ValueError("Unsupported reflector. Choose 'B' or 'C'.")
        self.reflector_name = reflector_name
        self.reflector_wiring = [A2I[c] for c in REFLECTOR_SPECS[reflector_name]]
        self.plugboard = {c: c for c in ALPHABET}
        for a, b in plug_pairs:
            self.plugboard[a] = b
            self.plugboard[b] = a
        self.initial_positions = [initial_positions[0], initial_positions[1], initial_positions[2]]

    def reset(self):
        self.left.pos = A2I[self.initial_positions[0]]
        self.middle.pos = A2I[self.initial_positions[1]]
        self.right.pos = A2I[self.initial_positions[2]]

    def plugboard_swap(self, letter: str) -> Tuple[str, str]:
        swapped = self.plugboard.get(letter, letter)
        return swapped, f"Plugboard: {letter} -> {swapped}"

    def reflector_map(self, idx: int) -> Tuple[int, str]:
        mapped = self.reflector_wiring[idx]
        trace = f"Reflector {self.reflector_name}: {I2A[idx]} -> {I2A[mapped]}"
        return mapped, trace

    def step_rotors(self) -> str:
        trace_msgs = []
        middle_notch = self.middle.at_notch()
        right_notch = self.right.at_notch()
        if middle_notch:
            trace_msgs.append(f"Middle rotor at notch ({self.middle.notch}) -> Middle and Left will step.")
            self.middle.step()
            self.left.step()
        elif right_notch: # Use elif to prevent middle stepping twice from one keypress
            trace_msgs.append(f"Right rotor at notch ({self.right.notch}) -> Middle will step.")
            self.middle.step()
        self.right.step()
        trace_msgs.append("Right rotor always steps.")
        pos_trace = f"Positions after stepping: Left={I2A[self.left.pos]} Middle={I2A[self.middle.pos]} Right={I2A[self.right.pos]}"
        trace_msgs.append(pos_trace)
        return "\n".join(trace_msgs)

    def process_character(self, ch: str) -> Tuple[str, List[str]]:
        ch = ch.upper()
        if ch not in ALPHABET:
            raise ValueError("Only A-Z letters allowed for process_character.")
        traces = []
        step_trace = self.step_rotors()
        traces.append("=== Stepping ===")
        traces.append(step_trace)
        swapped_in, t = self.plugboard_swap(ch)
        traces.append("=== Plugboard In ===")
        traces.append(t)
        idx = A2I[swapped_in]
        traces.append("=== Through Rotors (forward) ===")
        idx, t = self.right.encode_forward(idx)
        traces.append(t)
        idx, t = self.middle.encode_forward(idx)
        traces.append(t)
        idx, t = self.left.encode_forward(idx)
        traces.append(t)
        traces.append("=== Reflector ===")
        idx, t = self.reflector_map(idx)
        traces.append(t)
        traces.append("=== Through Rotors (backward) ===")
        idx, t = self.left.encode_backward(idx)
        traces.append(t)
        idx, t = self.middle.encode_backward(idx)
        traces.append(t)
        idx, t = self.right.encode_backward(idx)
        traces.append(t)
        out_letter = I2A[idx]
        swapped_out, t = self.plugboard_swap(out_letter)
        traces.append("=== Plugboard Out ===")
        traces.append(t)
        traces.append(f"Output letter: {swapped_out}")
        return swapped_out, traces

    def status(self) -> List[str]:
        lines = [
            f"Rotors (left->right): {self.left.name} {self.middle.name} {self.right.name}",
            f"Positions: Left={I2A[self.left.pos]} Middle={I2A[self.middle.pos]} Right={I2A[self.right.pos]}",
            f"Ring settings: Left={self.left.ring+1} Middle={self.middle.ring+1} Right={self.right.ring+1}",
            f"Reflector: {self.reflector_name}",
            f"Plugboard pairs: {', '.join([f'{a}{b}' for a,b in self._plug_pairs_list()])}"
        ]
        return lines

    def _plug_pairs_list(self):
        seen = set()
        pairs = []
        for c in ALPHABET:
            mapped = self.plugboard[c]
            if mapped != c and c not in seen:
                pairs.append((c, mapped))
                seen.add(c); seen.add(mapped)
        return pairs


def configure_machine() -> EnigmaMachine:
    """Interactive setup: prompts the user for all machine settings."""
    print("\n--- Enigma Machine Configuration ---")
    print("Choose three rotors (left, middle, right) from: I II III IV V")
    while True:
        try:
            user = input("Enter rotor names separated by spaces (e.g. II I III): ").strip().upper().split()
            if len(user) != 3:
                print("Please enter exactly three rotor names.")
                continue
            for r in user:
                if r not in ROTOR_SPECS:
                    raise ValueError(f"Unknown rotor: {r}")
            rotor_names = user
            break
        except Exception as e:
            print("Error:", e)
    
    ring_settings = []
    print("Ring settings (Ringstellung) - numbers 1..26; default 1")
    for pos in ["left", "middle", "right"]:
        while True:
            try:
                rs = input(f"Ring for {pos} rotor (1-26) [default 1]: ").strip()
                if rs == "": rs = "1"
                rsn = int(rs)
                if not (1 <= rsn <= 26): raise ValueError("Must be 1..26")
                ring_settings.append(rsn)
                break
            except Exception as e: print("Error:", e)

    initial_positions = []
    print("Initial rotor positions (Grundstellung) - letters A..Z.")
    for pos in ["left", "middle", "right"]:
        while True:
            try:
                p = input(f"Initial position for {pos} rotor (A-Z) [default A]: ").strip().upper()
                if p == "": p = "A"
                if p not in ALPHABET: raise ValueError("Must be A-Z")
                initial_positions.append(p)
                break
            except Exception as e: print("Error:", e)
    
    while True:
        try:
            ref = input("Choose reflector (B or C) [default B]: ").strip().upper()
            if ref == "": ref = "B"
            if ref not in REFLECTOR_SPECS: raise ValueError("Choose B or C")
            reflector_name = ref
            break
        except Exception as e: print("Error:", e)

    while True:
        try:
            pb = input("Enter plugboard pairs (e.g. 'AB CD EF'), or blank for none: ").strip().upper()
            plug_pairs = sanitize_plugboard_input(pb) if pb else []
            break
        except Exception as e: print("Error:", e)

    return EnigmaMachine(rotor_names, ring_settings, initial_positions, reflector_name, plug_pairs)


def interactive_processing_loop(machine: EnigmaMachine, mode: str):
    """Main interactive loop for processing messages with verbose trace."""
    print("\nMachine configured and ready.")
    for line in machine.status():
        print("  " + line)
    
    prompt_text = "plaintext to encrypt" if mode == "encrypt" else "ciphertext to decrypt"
    print(f"\nType a message to begin {mode}ing.")
    print("Special commands: status, reset, quit/exit.")

    while True:
        user_input = input(f"\nEnter {prompt_text} (or command): ").strip()
        if not user_input:
            continue
        
        cmd = user_input.lower()
        if cmd in ("exit", "quit"):
            print("Returning to main menu.")
            break
        if cmd == "status":
            print("\n".join(machine.status()))
            continue
        if cmd == "reset":
            machine.reset()
            print("Rotor positions reset to initial state:", machine.initial_positions)
            continue

        message = user_input.upper()
        output_chars = []
        for ch in message:
            if ch not in ALPHABET:
                # Skip non-alphabetic characters
                continue
            
            out, traces = machine.process_character(ch)
            print("\n" + "="*60)
            print(f"Input character: {ch}")
            print("-"*60)
            for line in traces:
                print(line)
            print("-"*60)
            print(f"Output character: {out}")
            print("="*60)
            output_chars.append(out)
        
        if output_chars:
            result_label = "Ciphertext" if mode == "encrypt" else "Plaintext"
            print(f"\nProcessed message ({result_label}):", "".join(output_chars))

def main():
    """Main function to run the Enigma emulator menu."""
    print("Welcome to the Enigma I interactive emulator (teaching edition).")
    while True:
        print("\n--- Main Menu ---")
        print("1. Encrypt a message")
        print("2. Decrypt a message")
        print("3. Exit")
        choice = input("Select an option (1, 2, or 3): ").strip()

        if choice == '1':
            print("\n>> Starting Encryption Mode <<")
            machine = configure_machine()
            interactive_processing_loop(machine, "encrypt")
        elif choice == '2':
            print("\n>> Starting Decryption Mode <<")
            print("NOTE: To decrypt, you must use the EXACT same settings as encryption.")
            machine = configure_machine()
            interactive_processing_loop(machine, "decrypt")
        elif choice == '3':
            print("Exiting. Goodbye.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

# If executed directly, run the main menu
if __name__ == "__main__":
    main()