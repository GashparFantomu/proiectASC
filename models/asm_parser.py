import re
import os

class ASMParser:
    DELIMITERS = r'[ ,\t\r\n]+'

    @staticmethod
    def parse(filepath: str) -> list:
        if not os.path.exists(filepath):
            print("eroare fisier!")
            return []

        with open(filepath, 'r') as file:
            content = file.read()

        raw_lines = content.splitlines()
        parsed_lines = []

        for line in raw_lines:
            line = line.strip()
            if not line:
                continue

            tokens = [t for t in re.split(ASMParser.DELIMITERS, line) if t]
            parsed_lines.append(tokens)

        return parsed_lines