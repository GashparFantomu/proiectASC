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

        COL_LABEL      = 0
        COL_ADDR       = 1
        COL_SBUS       = 4
        COL_DBUS       = 5
        COL_ALU        = 6
        COL_RBUS       = 7
        COL_MEM        = 8
        COL_OTHER      = 9
        COL_SUCCESSOR  = 10
        COL_INDEX_SEL  = 11
        COL_INVERSION  = 12
        COL_JUMP_ADDR  = 13

        for index_linie, current_row in excel_table.iterrows():
            label_raw = current_row.iloc[COL_LABEL]
            label = str(label_raw).strip() if not pd.isna(label_raw) else ""

            try:
                address_value = current_row.iloc[COL_ADDR]
                if pd.isna(address_value) or "Microadresa" in str(address_value):
                    continue
                micro_address = int(float(address_value))
            except (ValueError, TypeError):
                continue

            def cell(col):
                v = current_row.iloc[col]
                return str(v).strip() if not pd.isna(v) else "NONE"

            sbus      = cell(COL_SBUS)
            dbus      = cell(COL_DBUS)
            alu       = cell(COL_ALU)
            rbus      = cell(COL_RBUS)
            memory_op = cell(COL_MEM)
            other_ops = cell(COL_OTHER)
            successor = cell(COL_SUCCESSOR)
            index_sel = cell(COL_INDEX_SEL)   # e.g. "INDEX0: 000", "INDEX3: 011"
            inversion = cell(COL_INVERSION)   # "T: 0" or "F: 1"
            jump_addr = cell(COL_JUMP_ADDR)   # e.g. "PWFAIL: 0000011" or "B1: 0001010"

            for field in [sbus, dbus, alu, rbus, memory_op, other_ops]:
                if field in ("nan", "", "NaN"):
                    field = "NONE"

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
                index_sel=index_sel,
                inversion=inversion,
                jump_address=jump_addr,
            )
            self.microinstructions.append(micro_inst)

        print(f"[MicroprogramLoader] Incarcat {len(self.microinstructions)} microinstructiuni.")
        return self.microinstructions
