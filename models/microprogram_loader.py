import pandas as pd
import os
from models.microinstructions import MicroInstruction


class MicroprogramLoader:
    def __init__(self):
        self.microinstructions = []

    def load(self, filepath: str, sheet_name: str = "Microprogram") -> list:
        if not os.path.exists(filepath):
            print(f"[Eroare] Nu am găsit fișierul de microprogram: {filepath}")
            return []

        # Citim Excel-ul
        df = pd.read_excel(filepath, sheet_name=sheet_name, header=0)
        self.microinstructions = []

        for index, row in df.iterrows():
            # Eticheta (ex: IFCH:)
            label = str(row.iloc[0]).strip() if not pd.isna(row.iloc[0]) else ""

            # Adresa de microprogram (ignorăm rândurile fără adresă validă)
            try:
                addr_val = row.iloc[1]
                if pd.isna(addr_val) or "Microadresa" in str(addr_val):
                    continue
                micro_address = int(float(addr_val))
            except (ValueError, TypeError):
                continue

            # Extragem textul semnalelor (din coloanele aferente din Excelul tau)
            sbus = str(row.iloc[4]).strip() if not pd.isna(row.iloc[4]) else "NONE"
            dbus = str(row.iloc[5]).strip() if not pd.isna(row.iloc[5]) else "NONE"
            alu = str(row.iloc[6]).strip() if not pd.isna(row.iloc[6]) else "NONE"
            rbus = str(row.iloc[7]).strip() if not pd.isna(row.iloc[7]) else "NONE"
            memory_op = str(row.iloc[8]).strip() if not pd.isna(row.iloc[8]) else "NONE"
            other_ops = str(row.iloc[9]).strip() if not pd.isna(row.iloc[9]) else "NONE"
            successor = str(row.iloc[10]).strip() if not pd.isna(row.iloc[10]) else "STEP"
            jump_address = str(row.iloc[13]).strip() if not pd.isna(row.iloc[13]) else "0"

            micro_inst = MicroInstruction(
                label=label,
                micro_address=micro_address,
                sbus=sbus,
                dbus=dbus,
                alu=alu,
                rbus=rbus,
                memory_op=memory_op,
                other_ops=other_ops,
                successor=successor,
                jump_address=jump_address
            )
            self.microinstructions.append(micro_inst)

        return self.microinstructions