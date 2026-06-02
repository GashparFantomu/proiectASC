import re
import os

class ASMParser:
    DELIMITERS = r'[ ,\t\r\n]+'

    @staticmethod
    def parse(filepath: str) -> list:
        if not os.path.exists(filepath):
            print(f"[Eroare] Nu am gasit fisierul ASM: {filepath}")
            return []

        with open(filepath, 'r') as file:
            content = file.read()

        parsed_lines = []
        for line in content.splitlines():
            clean_line = line.split(';')[0].strip()
            if not clean_line:
                continue

            tokens = [token for token in re.split(ASMParser.DELIMITERS, clean_line) if token]
            parsed_lines.append(tokens)

        return parsed_lines