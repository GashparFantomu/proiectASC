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

        excel_table = pd.read_excel(filepath, sheet_name=sheet_name, header=0)
        coloana_mnemonic = 1

        for index, current_row in excel_table.iterrows():
            mnemonic = str(current_row.iloc[coloana_mnemonic]).strip()
            if pd.isna(mnemonic) or mnemonic == 'nan' or not mnemonic:
                continue

            base_opcode = 0
            empty_bits = 0

            for index_coloana_bit in range(2, 18): #16 coloane excel
                base_opcode <<= 1

                if index_coloana_bit < len(current_row):
                    valoare_celula_bit = str(current_row.iloc[index_coloana_bit]).strip()
                    if valoare_celula_bit.endswith('.0'): valoare_celula_bit = valoare_celula_bit[:-2]

                    if valoare_celula_bit in ['0', '1']:
                        base_opcode |= int(valoare_celula_bit)
                    else:
                        empty_bits += 1
                else:
                    empty_bits += 1

            self.opcodes_map[mnemonic] = {
                'base': base_opcode,
                'empty_bits': empty_bits
            }

        return self.opcodes_map