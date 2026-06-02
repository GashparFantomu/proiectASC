import pandas as pd
import os
from models.microinstructions import MicroInstruction


class MicroprogramLoader:
    def __init__(self):
        self.microinstructions = []

    def load(self, filepath: str, sheet_name: str = "Microprogram") -> list:
        if not os.path.exists(filepath):
            print(f"[Eroare] Nu am gasit fisierul de microprogram: {filepath}")
            return []

        excel_table = pd.read_excel(filepath, sheet_name=sheet_name, header=0)
        self.microinstructions = []


        coloana_eticheta = 0  # Coloana A din Excel
        coloana_microadresa = 1  # Coloana B din Excel
        coloana_SBUS = 4  # Coloana E din Excel
        coloana_DBUS = 5  # Coloana F din Excel
        coloana_ALU = 6  # Coloana G din Excel
        coloana_RBUS = 7  # Coloana H din Excel
        coloana_memorie = 8  # Coloana I din Excel
        coloana_alte_operatii = 9  # Coloana J din Excel
        coloana_succesor = 10  # Coloana K din Excel
        coloana_adresa_salt = 13  # Coloana N din Excel


        for index_linie, current_row in excel_table.iterrows():
            label = str(current_row.iloc[coloana_eticheta]).strip() if not pd.isna(current_row.iloc[coloana_eticheta]) else ""

            try:
                address_value = current_row.iloc[coloana_microadresa]
                if pd.isna(address_value) or "Microadresa" in str(address_value):
                    continue
                micro_address_numeric = int(float(address_value))
            except (ValueError, TypeError):
                continue

            sbus = str(current_row.iloc[coloana_SBUS]).strip() if not pd.isna(current_row.iloc[coloana_SBUS]) else "NONE"
            dbus = str(current_row.iloc[coloana_DBUS]).strip() if not pd.isna(current_row.iloc[coloana_DBUS]) else "NONE"
            alu = str(current_row.iloc[coloana_ALU]).strip() if not pd.isna(current_row.iloc[coloana_ALU]) else "NONE"
            rbus = str(current_row.iloc[coloana_RBUS]).strip() if not pd.isna(current_row.iloc[coloana_RBUS]) else "NONE"
            memory_op = str(current_row.iloc[coloana_memorie]).strip() if not pd.isna(current_row.iloc(coloana_memorie)) else "NONE"
            other_ops = str(current_row.iloc[coloana_alte_operatii]).strip() if not pd.isna(current_row.iloc[coloana_alte_operatii]) else "NONE"
            successor = str(current_row.iloc[coloana_succesor]).strip() if not pd.isna(current_row.iloc[coloana_succesor]) else "STEP"
            jump_address = str(current_row.iloc[coloana_adresa_salt]).strip() if not pd.isna(current_row.iloc[coloana_adresa_salt]) else "0"

            micro_inst = MicroInstruction(
                label=label,
                micro_address=micro_address_numeric,
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