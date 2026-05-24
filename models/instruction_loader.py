import pandas as pd
import os

print("--instruction loader--")
class InstructionLoader:
    def __init__(self):
        self.opcodes_map = {}
        self.registers_map = {f"R{i}": i for i in range(16)}
        self.addressing_modes = {"AM": 0b00, "AD": 0b01, "AI": 0b10, "AX": 0b11}

    def load(self, filepath: str, sheet_name: int = 0) -> dict:
        if not os.path.exists(filepath):
            print(f"[Eroare] Fisierul nu exista: {filepath}")
            return self.opcodes_map

        df = pd.read_excel(filepath, sheet_name=sheet_name, header=0)

        for index, row in df.iterrows():
            mnemonic = str(row.iloc[1]).strip()
            if pd.isna(mnemonic) or mnemonic == 'nan' or not mnemonic:
                continue

            base_opcode = 0
            empty_bits = 0

            # Iterăm prin cele 16 coloane de biți (index 2 la 17 în Excel)
            for col_idx in range(2, 18):
                base_opcode <<= 1  # Shiftăm la stânga la fiecare pas

                if col_idx < len(row):
                    val = str(row.iloc[col_idx]).strip()
                    if val.endswith('.0'): val = val[:-2]

                    if val in ['0', '1']:
                        base_opcode |= int(val)
                    else:
                        empty_bits += 1  # Am dat de o "gaură" (ex: operand)
                else:
                    empty_bits += 1

            self.opcodes_map[mnemonic] = {
                'base': base_opcode,
                'empty_bits': empty_bits
            }

        return self.opcodes_map