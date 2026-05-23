import pandas as pd
import os

print("--instruction loader--")
class InstructionLoader:
    def __init__(self):
        self.opcodes_map = {}

    def load(self, filepath: str, sheet_name: str = "Sheet1") -> dict:
        if not os.path.exists(filepath):
            print("eroare fisier", filepath)
            return self.opcodes_map

        df = pd.read_excel(filepath, sheet_name=sheet_name, header=0)

        for index, row in df.iterrows():
            mnemonic = str(row.iloc[1]).strip()

            if pd.isna(mnemonic) or mnemonic == 'nan' or not mnemonic:
                continue

            opcode = 0

            for col_idx in range(2, 18):
                if col_idx < len(row):
                    val = str(row.iloc[col_idx]).strip()

                    if val.endswith('.0'):
                        val = val[:-2]

                    if val in ['0', '1']:
                        bit = int(val)
                        opcode = (opcode << 1) | bit
                    else:
                        break

            self.opcodes_map[mnemonic] = opcode

        return self.opcodes_map