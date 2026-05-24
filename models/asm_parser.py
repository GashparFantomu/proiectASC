import re
import os

class ASMParser:
    DELIMITERS = r'[ ,\t\r\n]+'

    @staticmethod
    def parse(filepath: str) -> list:
        if not os.path.exists(filepath):
            print(f"[Eroare] Nu am găsit fișierul ASM: {filepath}")
            return []

        with open(filepath, 'r') as file:
            content = file.read()

        parsed_lines = []
        for line in content.splitlines():
            # Eliminăm comentariile inline și spațiile inutile
            line = line.split(';')[0].strip()
            if not line:
                continue

            tokens = [t for t in re.split(ASMParser.DELIMITERS, line) if t]
            parsed_lines.append(tokens)

        return parsed_lines