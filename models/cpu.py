class CPU:
    def __init__(self, memory_size: int = 4096):
        self.registers = {f"R{i}": 0 for i in range(16)}

        self.PC = 0
        self.SP = 0
        self.IR = 0
        self.T = 0

        self.ADR = 0
        self.MDR = 0
        self.IVR = 0

        self.SBUS = 0
        self.DBUS = 0
        self.RBUS = 0

        self.flags = {
            'N': 0,
            'Z': 0,
            'V': 0, #overflow
            'C': 0
        }


        self.memory = [0] * memory_size

        self.micro_memory = {}
        self.MAR = 0

    def load_program(self, machine_codes: list, start_address: int = 0):
        """Incarca codul masina (Hex) generat de Asamblor în memoria RAM."""
        self.PC = start_address
        for offset, code_val in enumerate(machine_codes):
            self.memory[start_address + offset] = code_val
        print(f"[CPU] Program incarcat in RAM la adresa {start_address}. Dimensiune: {len(machine_codes)} cuvinte.")

    def print_registers(self):
        """Afiseaza starea curenta la registrii"""
        print("\n=== STARE CPU ===")
        print(f"PC: {self.PC:04X} | IR: {self.IR:04X} | SP: {self.SP:04X} | MAR: {self.MAR}")
        print(f"ADR: {self.ADR:04X} | MDR: {self.MDR:04X} | T: {self.T:04X}")
        print(f"Buses -> SBUS: {self.SBUS:04X} | DBUS: {self.DBUS:04X} | RBUS: {self.RBUS:04X}")
        print(f"Flags -> N:{self.flags['N']} Z:{self.flags['Z']} V:{self.flags['V']} C:{self.flags['C']}")

        active_registers = {}
        for reg_name, reg_value in self.registers.items():
            if reg_value != 0:
                active_registers[reg_name] = reg_value

        if active_registers:
            print(f"Registre active: {active_registers}")
        else:
            print("Registre active: Toate sunt 0")
