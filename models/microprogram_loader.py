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

        # Column indices (0-based)
        COL_LABEL      = 0   # A: Eticheta
        COL_ADDR       = 1   # B: Microadresa MPM (decimal)
        COL_SBUS       = 4   # E: Sursa SBUS
        COL_DBUS       = 5   # F: Sursa DBUS
        COL_ALU        = 6   # G: Operatie ALU
        COL_RBUS       = 7   # H: Destinatie RBUS
        COL_MEM        = 8   # I: Operatii cu Memoria
        COL_OTHER      = 9   # J: Alte Operatii
        COL_SUCCESSOR  = 10  # K: Succesor
        COL_INDEX_SEL  = 11  # L: Selectie INDEX
        COL_INVERSION  = 12  # M: True negat/False
        COL_JUMP_ADDR  = 13  # N: Microadresa de salt

        for index_linie, current_row in excel_table.iterrows():
            # --- Label ---
            label_raw = current_row.iloc[COL_LABEL]
            label = str(label_raw).strip() if not pd.isna(label_raw) else ""

            # --- Micro address (skip header / non-numeric rows) ---
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

            # Strip empty / nan strings back to NONE
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
