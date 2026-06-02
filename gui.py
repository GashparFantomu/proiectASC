import customtkinter as ctk
from tkinter import filedialog, messagebox
import os

ctk.set_appearance_mode("Dark")  # Poate fi "Light", "Dark" sau "System"
ctk.set_default_color_theme("blue")


class CPUViewerApp(ctk.CTk):
    def __init__(self, cpu_instance=None, assembler_instance=None):
        super().__init__()

        # Referințe către backend-ul tău din Python
        self.cpu = cpu_instance
        self.assembler = assembler_instance

        self.title("CPU Emulator - CustomTkinter")
        self.geometry("1050x700")

        # ==================== BARA DE MENIU ====================
        self.top_frame = ctk.CTkFrame(self, height=40, corner_radius=0)
        self.top_frame.pack(side="top", fill="x")

        self.btn_open = ctk.CTkButton(self.top_frame, text="File -> Open .asm", width=120, command=self.open_file)
        self.btn_open.pack(side="left", padx=10, pady=5)

        self.btn_assemble = ctk.CTkButton(self.top_frame, text="Assemble", width=100, command=self.assemble_code)
        self.btn_assemble.pack(side="left", padx=10, pady=5)

        self.btn_step = ctk.CTkButton(self.top_frame, text="Step (Clock Cycle)", width=120, command=self.step_execution)
        self.btn_step.pack(side="left", padx=10, pady=5)

        # ==================== CORPUL PRINCIPAL ====================
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # Împărțim fereastra în 3 coloane egale
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(2, weight=1)

        # --- PANOU STÂNGA (Cod ASM) ---
        self.left_panel = ctk.CTkFrame(self.main_frame)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        ctk.CTkLabel(self.left_panel, text="Cod ASM Parsat", font=("Arial", 14, "bold")).pack(pady=10)
        self.asm_textbox = ctk.CTkTextbox(self.left_panel, width=300, height=500)
        self.asm_textbox.pack(padx=10, pady=5, fill="both", expand=True)

        ctk.CTkLabel(self.left_panel, text="Instrucțiunea Curentă", font=("Arial", 14, "bold")).pack(pady=(10, 0))
        self.current_inst_entry = ctk.CTkEntry(self.left_panel, width=250, justify="center")
        self.current_inst_entry.pack(padx=10, pady=10)

        # --- PANOU CENTRU (Buses, Special Regs, ALU) ---
        self.center_panel = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.center_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Registre Speciale
        self.create_group(self.center_panel, "Registre Speciale", ["PC", "IR", "SP", "FLAG", "MAR", "MDR", "T", "IVR"])

        # Magistrale
        self.create_group(self.center_panel, "Magistrale (Buses)", ["SBUS", "DBUS", "RBUS"])

        # ALU
        self.create_group(self.center_panel, "Unitatea Aritmetico-Logică",
                          ["Input S", "Input D", "Operație", "Output R"])

        # --- PANOU DREAPTA (Registre Generale R0-R15) ---
        self.right_panel = ctk.CTkFrame(self.main_frame)
        self.right_panel.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        ctk.CTkLabel(self.right_panel, text="Registre Generale", font=("Arial", 14, "bold")).pack(pady=10)
        self.gen_regs_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.gen_regs_frame.pack(fill="x", padx=10)

        self.ui_fields = getattr(self, "ui_fields", {})
        for i in range(16):
            reg_name = f"R{i}"
            ctk.CTkLabel(self.gen_regs_frame, text=reg_name).grid(row=i, column=0, padx=10, pady=4, sticky="e")
            entry = ctk.CTkEntry(self.gen_regs_frame, width=120, justify="center")
            entry.grid(row=i, column=1, padx=5, pady=4)
            entry.insert(0, "0x0000")
            entry.configure(state="readonly")
            self.ui_fields[reg_name] = entry

    # === Funcție utilitară pentru grupurile de date din centru ===
    def create_group(self, parent, title, labels):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=5, pady=(0, 15))

        ctk.CTkLabel(frame, text=title, font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
        if not hasattr(self, "ui_fields"):
            self.ui_fields = {}

        for i, label in enumerate(labels):
            ctk.CTkLabel(frame, text=label).grid(row=i + 1, column=0, padx=10, pady=4, sticky="e")
            entry = ctk.CTkEntry(frame, width=120, justify="center")
            entry.grid(row=i + 1, column=1, padx=10, pady=4)
            entry.insert(0, "0x0000" if label != "Operație" else "NONE")
            entry.configure(state="readonly")
            self.ui_fields[label] = entry

    # ==================== EVENIMENTE BUTOANE ====================
    def open_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("ASM Files", "*.asm"), ("All Files", "*.*")])
        if filepath:
            filename = os.path.basename(filepath)

            # Aici apelezi ASMParser din backend-ul tău:
            # parsed_lines = ASMParser.parse(filepath)

            self.asm_textbox.delete("0.0", "end")
            self.asm_textbox.insert("0.0", f"; Fișier încărcat: {filename}\n; Apasă 'Assemble' pentru a compila.\n\n")

            # Exemplu mock-up de afișare (Aici pui string-ul liniilor citite real):
            with open(filepath, 'r') as f:
                self.asm_textbox.insert("end", f.read())

    def assemble_code(self):
        # 1. Preluăm textul complet din caseta ASM din interfață
        cod_asm_text = self.asm_textbox.get("0.0", "end")

        # 2. Îl salvăm temporar într-un fișier sau îl parsam direct.
        # Deocamdată, ca să folosești parserul tău existent, îl scriem în test.asm:
        with open("test.asm", "w") as f:
            f.write(cod_asm_text)

        # 3. Apelăm parserul și asamblorul tău
        from models.asm_parser import ASMParser
        parsed_lines = ASMParser.parse("test.asm")

        if not parsed_lines:
            messagebox.showerror("Eroare", "Fișierul ASM este gol sau are erori de sintaxă!")
            return

        machine_codes = self.assembler.assemble(parsed_lines)

        # 4. Încărcăm codul mașină în CPU
        self.cpu.load_program(machine_codes, start_address=0)

        # 5. Resetăm MAR și PC pentru un nou rulaj
        self.cpu.PC = 0
        self.cpu.MAR = 0

        # 6. Actualizăm interfața grafică cu noile valori (0000 peste tot la început)
        self.update_ui()

        messagebox.showinfo("Asamblare Reușită",
                            f"Codul a fost compilat și încărcat în RAM!\nDimensiune: {len(machine_codes)} cuvinte.")

    def step_execution(self):
        # Verificăm dacă obiectul CPU are opcodes_map salvat
        if self.cpu and hasattr(self.cpu, 'opcodes_map'):
            # Rulăm un singur ciclu de ceas MPM
            self.cpu.execute_clock_cycle(self.cpu.opcodes_map)
            # Actualizăm interfața grafică cu noile valori ale regiștrilor/magistralelor
            self.update_ui()
        else:
            messagebox.showerror("Eroare", "CPU-ul sau configurația de opcoduri nu a fost inițializată corect.")
    def update_ui(self):
        # Funcție ajutătoare pentru a scrie într-un Entry setat pe 'readonly'
        def set_val(key, value_str):
            if key in self.ui_fields:
                self.ui_fields[key].configure(state="normal")
                self.ui_fields[key].delete(0, "end")
                self.ui_fields[key].insert(0, value_str)
                self.ui_fields[key].configure(state="readonly")

        # 1. Actualizăm regiștrii speciali în format Hexazecimal (04X -> ex: 00AF)
        set_val("PC", f"{self.cpu.PC:04X}")
        set_val("IR", f"{self.cpu.IR:04X}")
        set_val("SP", f"{self.cpu.SP:04X}")
        set_val("T", f"{self.cpu.T:04X}")
        set_val("ADR", f"{self.cpu.ADR:04X}")
        set_val("MDR", f"{self.cpu.MDR:04X}")
        set_val("MAR", str(self.cpu.MAR))  # MAR e index de linie, îl lăsăm decimal

        # 2. Actualizăm magistralele
        set_val("SBUS", f"{self.cpu.SBUS:04X}")
        set_val("DBUS", f"{self.cpu.DBUS:04X}")
        set_val("RBUS", f"{self.cpu.RBUS:04X}")

        # 3. Actualizăm flag-urile (0 sau 1)
        set_val("N", str(self.cpu.flags['N']))
        set_val("Z", str(self.cpu.flags['Z']))
        set_val("V", str(self.cpu.flags['V']))
        set_val("C", str(self.cpu.flags['C']))

        # 4. Actualizăm regiștrii generali (R0 - R15)
        for i in range(16):
            reg_name = f"R{i}"
            reg_val = self.cpu.registers[reg_name]
            set_val(reg_name, f"{reg_val:04X}")


if __name__ == "__main__":
    app = CPUViewerApp()
    app.mainloop()