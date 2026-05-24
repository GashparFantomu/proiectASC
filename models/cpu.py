class CPU:
    def __init__(self, memory_size: int = 4096):
        # 1. File-ul de Registre Generale (R0 - R15) - fiecare pe 16 biți
        self.registers = {f"R{i}": 0 for i in range(16)}

        # 2. Registrele speciale ale arhitecturii
        self.PC = 0  # Program Counter (adresa instrucțiunii curente)
        self.SP = 0  # Stack Pointer (pointer-ul de stivă)
        self.IR = 0  # Instruction Register (păstrează codul instrucțiunii curente)
        self.T = 0  # Registru Temporar (invizibil programatorului)

        # 3. Registrele de interfață cu memoria (Memory Interface)
        self.ADR = 0  # Address Register (păstrează adresa pentru RAM)
        self.MDR = 0  # Data Register (păstrează datele citite/scrise în RAM)
        self.IVR = 0  # Interrupt Vector Register

        # 4. Magistralele interne (Buses) - folosite pentru transferul de date în același ciclu
        self.SBUS = 0
        self.DBUS = 0
        self.RBUS = 0

        # 5. Flag-urile de condiție (Registrul CCR / FLAG)
        self.flags = {
            'N': 0,  # Negative
            'Z': 0,  # Zero
            'V': 0,  # Overflow
            'C': 0  # Carry
        }

        # 6. Memoria RAM (vector de numere pe 16 biți)
        self.memory = [0] * memory_size

        # 7. Memoria de Microprogram (MPM) - controlerul intern al CPU-ului
        self.micro_memory = {}  # Va fi încărcată din Microprogram.xlsx
        self.MAR = 0  # Micro Address Register (arată linia curentă din microprogram)

    def load_program(self, machine_codes: list, start_address: int = 0):
        """Încarcă codul mașină (Hex) generat de Asamblor în memoria RAM."""
        self.PC = start_address
        for i, code_val in enumerate(machine_codes):
            # Convertim din Hex (text) în întreg pe 16 biți
            self.memory[start_address + i] = code_val
        print(f"[CPU] Program incarcat in RAM la adresa {start_address}. Dimensiune: {len(code_val)} cuvinte.")

    def print_status(self):
        """Afișează starea curentă a celor mai importanți regiștri (util pentru debug)."""
        print("\n=== STARE CPU ===")
        print(f"PC: {self.PC:04X} | IR: {self.IR:04X} | SP: {self.SP:04X} | MAR: {self.MAR}")
        print(f"ADR: {self.ADR:04X} | MDR: {self.MDR:04X} | T: {self.T:04X}")
        print(f"Buses -> SBUS: {self.SBUS:04X} | DBUS: {self.DBUS:04X} | RBUS: {self.RBUS:04X}")
        print(f"Flags -> N:{self.flags['N']} Z:{self.flags['Z']} V:{self.flags['V']} C:{self.flags['C']}")

        # Afișăm doar regiștrii care nu sunt 0, ca să nu aglomerăm ecranul
        active_regs = {k: v for k, v in self.registers.items() if v != 0}
        print(f"Registre active: {active_regs if active_regs else 'Toate sunt 0'}")
        print("=================\n")