import customtkinter as ctk
from tkinter import filedialog, messagebox
import os

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class CPUViewerApp(ctk.CTk):
    def __init__(self, cpu_instance=None, assembler_instance=None):
        super().__init__()

        self.cpu = cpu_instance
        self.assembler = assembler_instance
        self.ui_fields = {}

        self.title("CPU Emulator")
        self.geometry("1100x720")

        self.top_frame = ctk.CTkFrame(self, height=40, corner_radius=0)
        self.top_frame.pack(side="top", fill="x")

        self.btn_open = ctk.CTkButton(self.top_frame, text="File -> Open .asm", width=130, command=self.open_file)
        self.btn_open.pack(side="left", padx=10, pady=5)

        self.btn_assemble = ctk.CTkButton(self.top_frame, text="Assemble", width=100, command=self.assemble_code)
        self.btn_assemble.pack(side="left", padx=10, pady=5)

        self.btn_step = ctk.CTkButton(self.top_frame, text="Step (Clock Cycle)", width=130, command=self.step_execution)
        self.btn_step.pack(side="left", padx=10, pady=5)

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(2, weight=1)

        self.left_panel = ctk.CTkFrame(self.main_frame)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        ctk.CTkLabel(self.left_panel, text="Cod ASM", font=("Arial", 14, "bold")).pack(pady=10)
        self.asm_textbox = ctk.CTkTextbox(self.left_panel, width=300, height=500)
        self.asm_textbox.pack(padx=10, pady=5, fill="both", expand=True)

        #ctk.CTkLabel(self.left_panel, text="Instructiunea Curenta", font=("Arial", 14, "bold")).pack(pady=(10, 0))
        #self.current_inst_entry = ctk.CTkEntry(self.left_panel, width=250, justify="center")
        #self.current_inst_entry.pack(padx=10, pady=10)

        self.center_panel = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.center_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.create_group(self.center_panel, "Registre Speciale",
                          ["PC", "IR", "SP", "MAR", "ADR", "MDR", "T", "IVR"])

        self.create_group(self.center_panel, "Flags (N Z V C)",
                          ["FLAG", "N", "Z", "V", "C"])

        self.create_group(self.center_panel, "Magistrale (Buses)",
                          ["SBUS", "DBUS", "RBUS"])

        self.create_group(self.center_panel, "Unitatea Aritmetico-Logica",
                          ["Input S", "Input D", "Operatie", "Output R"])

        self.right_panel = ctk.CTkFrame(self.main_frame)
        self.right_panel.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        ctk.CTkLabel(self.right_panel, text="Registre Generale", font=("Arial", 14, "bold")).pack(pady=10)
        self.gen_regs_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.gen_regs_frame.pack(fill="x", padx=10)

        for i in range(16):
            reg_name = f"R{i}"
            ctk.CTkLabel(self.gen_regs_frame, text=reg_name).grid(row=i, column=0, padx=10, pady=4, sticky="e")
            entry = ctk.CTkEntry(self.gen_regs_frame, width=120, justify="center")
            entry.grid(row=i, column=1, padx=5, pady=4)
            entry.insert(0, "0000")
            entry.configure(state="readonly")
            self.ui_fields[reg_name] = entry

    def create_group(self, parent, title, labels):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=(0, 10))

        ctk.CTkLabel(frame, text=title, font=("Arial", 13, "bold")).grid(
            row=0, column=0, columnspan=2, pady=5)

        for i, label in enumerate(labels):
            ctk.CTkLabel(frame, text=label).grid(row=i + 1, column=0, padx=10, pady=3, sticky="e")
            entry = ctk.CTkEntry(frame, width=120, justify="center")
            entry.grid(row=i + 1, column=1, padx=10, pady=3)
            default = "0000" if label not in ("Operatie",) else "NONE"
            entry.insert(0, default)
            entry.configure(state="readonly")
            self.ui_fields[label] = entry

    def open_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("ASM Files", "*.asm"), ("All Files", "*.*")])
        if filepath:
            filename = os.path.basename(filepath)
            self.asm_textbox.delete("0.0", "end")
            with open(filepath, 'r') as f:
                self.asm_textbox.insert("0.0", f.read())

    def assemble_code(self):
        cod_asm_text = self.asm_textbox.get("0.0", "end")

        with open("test.asm", "w") as f:
            f.write(cod_asm_text)

        from models.asm_parser import ASMParser
        parsed_lines = ASMParser.parse("test.asm")

        if not parsed_lines:
            messagebox.showerror("Eroare", "Fisierul ASM este gol sau are erori de sintaxa!")
            return

        machine_codes = self.assembler.assemble(parsed_lines)

        self.cpu.load_program(machine_codes, start_address=0)
        self.cpu.PC = 0
        self.cpu.MAR = 0

        self.update_ui()
        messagebox.showinfo("Asamblare Reusita",
                            f"Codul a fost compilat si incarcat in RAM!\n"
                            f"Dimensiune: {len(machine_codes)} cuvinte.\n"
                            f"Primele valori: {[hex(v) for v in machine_codes[:6]]}")

    def step_execution(self):
        if self.cpu and hasattr(self.cpu, 'opcodes_map'):
            ok = self.cpu.execute_clock_cycle(self.cpu.opcodes_map)
            self.update_ui()
            if not ok:
                messagebox.showinfo("Halt", "Procesorul s-a oprit (HALT sau adresa invalida).")
        else:
            messagebox.showerror("Eroare", "CPU-ul nu a fost initializat corect.")

    def _set_val(self, key: str, value_str: str):
        """Write a value into a readonly Entry widget."""
        if key in self.ui_fields:
            self.ui_fields[key].configure(state="normal")
            self.ui_fields[key].delete(0, "end")
            self.ui_fields[key].insert(0, value_str)
            self.ui_fields[key].configure(state="readonly")

    def update_ui(self):
        if not self.cpu:
            return

        self._set_val("PC",  f"{self.cpu.PC:04X}")
        self._set_val("IR",  f"{self.cpu.IR:04X}")
        self._set_val("SP",  f"{self.cpu.SP:04X}")
        self._set_val("T",   f"{self.cpu.T:04X}")
        self._set_val("ADR", f"{self.cpu.ADR:04X}")
        self._set_val("MDR", f"{self.cpu.MDR:04X}")
        self._set_val("IVR", f"{self.cpu.IVR:04X}")
        self._set_val("MAR", str(self.cpu.MAR))   # decimal is clearer for debug

        flags_int = (self.cpu.flags['N'] << 3) | (self.cpu.flags['Z'] << 2) | \
                    (self.cpu.flags['V'] << 1) | self.cpu.flags['C']
        self._set_val("FLAG", f"{flags_int:04b}")   # binary e.g. "0110"
        self._set_val("N", str(self.cpu.flags['N']))
        self._set_val("Z", str(self.cpu.flags['Z']))
        self._set_val("V", str(self.cpu.flags['V']))
        self._set_val("C", str(self.cpu.flags['C']))

        self._set_val("SBUS", f"{self.cpu.SBUS:04X}")
        self._set_val("DBUS", f"{self.cpu.DBUS:04X}")
        self._set_val("RBUS", f"{self.cpu.RBUS:04X}")

        self._set_val("Input S",  f"{self.cpu.SBUS:04X}")
        self._set_val("Input D",  f"{self.cpu.DBUS:04X}")
        self._set_val("Output R", f"{self.cpu.RBUS:04X}")

        for i in range(16):
            reg_name = f"R{i}"
            self._set_val(reg_name, f"{self.cpu.registers[reg_name]:04X}")


if __name__ == "__main__":
    app = CPUViewerApp()
    app.mainloop()
