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
        messagebox.showinfo("Asamblare Reușită", "Codul ASM a fost parsat și convertit în cod mașină cu succes!")
        # Aici folosești self.assembler.assemble(parsed_lines)
        # self.cpu.load_program(machine_codes)

    def step_execution(self):
        # Aici vei apela logica: self.cpu.execute_clock_cycle() sau echivalentul
        # Apoi actualizezi UI-ul folosind update_ui()
        self.update_ui()
        pass

    def update_ui(self):
        # Model pentru a face update valorilor dintr-un Entry blocat (readonly)
        def set_val(key, value):
            self.ui_fields[key].configure(state="normal")
            self.ui_fields[key].delete(0, "end")
            self.ui_fields[key].insert(0, value)
            self.ui_fields[key].configure(state="readonly")

        # Aici iei valorile din self.cpu și le pui pe ecran. Exemplu:
        # set_val("PC", f"0x{self.cpu.PC:04X}")
        # set_val("R0", f"0x{self.cpu.registers['R0']:04X}")


if __name__ == "__main__":
    app = CPUViewerApp()
    app.mainloop()