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
            'N': 0, 'Z': 0, 'V': 0, 'C': 0
        }

        self.memory = [0] * memory_size
        self.micro_memory = {}
        self.MAR = 0
        self.labels_map = {}
        self.opcodes_map = {}

    def load_program(self, machine_codes: list, start_address: int = 0):
        """Incarca codul masina (Hex) generat de Asamblor in memoria RAM."""
        self.PC = start_address
        for offset, code_val in enumerate(machine_codes):
            self.memory[start_address + offset] = code_val
        print(f"[CPU] Program incarcat in RAM la adresa {start_address}. Dimensiune: {len(machine_codes)} cuvinte.")

    def load_microprogram(self, microinstructions_list: list):
        """Incarca lista de microinstructiuni si mapeaza etichetele text (ex: 'MOV' -> adresa)."""
        self.micro_memory = {micro.micro_address: micro for micro in microinstructions_list}
        self.MAR = 0

        self.labels_map = {}
        for inst in microinstructions_list:
            if inst.label:
                clean_label = inst.label.replace(":", "").strip().upper()
                self.labels_map[clean_label] = inst.micro_address

        print(f"[CPU] Microprogram încărcat: {len(self.micro_memory)} microinstrucțiuni.")

    def decode_ir(self, opcodes_map):
        """Determina mnemonicul instructiunii din IR folosind masca de biti."""
        for mnemonic, info in opcodes_map.items():
            empty_bits = info['empty_bits']
            # Masca pentru a izola opcodul de bitii operanzilor
            mask = (0xFFFF << empty_bits) & 0xFFFF
            if (self.IR & mask) == info['base']:
                return mnemonic
        return None

    def execute_clock_cycle(self, opcodes_map):
        """Executa un singur tact de ceas MPM."""
        micro_inst = self.micro_memory.get(self.MAR)
        if not micro_inst:
            print(f"[CPU] Eroare: Nu exista microinstructiune la adresa {self.MAR}. Procesor Oprit.")
            return False

        if micro_inst.label == "HALT:":
            print("[CPU] HALT. Executie oprita.")
            return False

        # 1. Rutare Surse (SBUS si DBUS)
        self.SBUS = self._compute_sbus(micro_inst.sbus)
        self.DBUS = self._compute_dbus(micro_inst.dbus)

        # 2. Unitatea ALU
        rezultat_alu = self._compute_alu(micro_inst.alu)

        # 3. Alte Operatii (ex: +2PC la IFCH sau incrementari/decrementari speciale)
        rezultat_alu = self._handle_other_ops(micro_inst.other_ops, rezultat_alu)

        # 4. Rutare Destinatie (RBUS) -> Salvarea rezultatului in Registru
        self.RBUS = rezultat_alu
        self._write_rbus(micro_inst.rbus, rezultat_alu)

        # 5. Operatii RAM
        self._handle_memory(micro_inst.memory_op)

        # 6. Urmatorul pas (MAR)
        self.MAR = self._compute_next_mar(micro_inst, opcodes_map)

        return True

    # ==================== METODE PRIVATE DE RUTARE =====

    def _curata_semnal(self, semnal: str) -> str:
        """Extrage doar comanda din textul Excel, ignorand bitii (ex: 'PdPCs: 0110' -> 'PDPCS')."""
        if not semnal or semnal == "NONE":
            return "NONE"
        return semnal.split(':')[0].strip().upper()

    def _compute_sbus(self, semnal_sbus: str) -> int:
        semnal = self._curata_semnal(semnal_sbus)
        if semnal == "NONE":    return 0
        if semnal == "PDPCS":   return self.PC
        if semnal == "PDMDRS":  return self.MDR
        if semnal == "PDSPS":   return self.SP
        if semnal == "PDTS":    return self.T
        if semnal == "PDRGS":
            reg_index = self.IR & 0x000F
            return self.registers[f"R{reg_index}"]
        return 0

    def _compute_dbus(self, semnal_dbus: str) -> int:
        semnal = self._curata_semnal(semnal_dbus)
        if semnal == "NONE":    return 0
        if semnal == "PDPCD":   return self.PC
        if semnal == "PDMDRD":  return self.MDR
        if semnal == "PDSPD":   return self.SP
        if semnal == "PDTD":    return self.T
        if semnal == "PDRGD":
            reg_index = (self.IR >> 6) & 0x000F
            return self.registers[f"R{reg_index}"]
        return 0

    def _compute_alu(self, semnal_alu: str) -> int:
        semnal = self._curata_semnal(semnal_alu)
        rezultat = 0
        if semnal == "NONE":
            rezultat = 0
        elif semnal == "SBUS":
            rezultat = self.SBUS
        elif semnal == "DBUS":
            rezultat = self.DBUS
        elif semnal == "SUM":
            rezultat = self.SBUS + self.DBUS
        elif semnal == "AND":
            rezultat = self.SBUS & self.DBUS
        elif semnal == "OR":
            rezultat = self.SBUS | self.DBUS
        elif semnal == "XOR":
            rezultat = self.SBUS ^ self.DBUS
        elif semnal == "NOT":
            rezultat = ~self.SBUS
        return rezultat & 0xFFFF

    def _handle_other_ops(self, semnal_other: str, alu_rezultat: int) -> int:
        semnal = self._curata_semnal(semnal_other)
        if semnal == "+2PC":
            self.PC = (self.PC + 2) & 0xFFFF
        elif semnal == "CIN,PDCONDARITM":  # Operatie pentru instrucțiunea INC
            return (alu_rezultat + 1) & 0xFFFF
        return alu_rezultat

    def _write_rbus(self, semnal_rbus: str, valoare: int):
        semnal = self._curata_semnal(semnal_rbus)
        if semnal == "NONE":   return
        if semnal == "PMPC":   self.PC = valoare
        if semnal == "PMIR":   self.IR = valoare
        if semnal == "PMADR":  self.ADR = valoare
        if semnal == "PMMDR":  self.MDR = valoare
        if semnal == "PMSP":   self.SP = valoare
        if semnal == "PMT":    self.T = valoare
        if semnal == "PMRG":
            reg_index = (self.IR >> 6) & 0x000F
            self.registers[f"R{reg_index}"] = valoare

    def _handle_memory(self, semnal_memorie: str):
        semnal = self._curata_semnal(semnal_memorie)
        if semnal in ["READ", "IFCH"]:
            self.MDR = self.memory[self.ADR]
        elif semnal == "WRITE":
            self.memory[self.ADR] = self.MDR

    def _compute_next_mar(self, micro_inst, opcodes_map) -> int:
        succesor = self._curata_semnal(micro_inst.successor)

        # 1. MAP: Decodifica IR si sari la instructiunea de executat
        if "MAP" in succesor:
            mnemonic = self.decode_ir(opcodes_map)
            if mnemonic and mnemonic in self.labels_map:
                return self.labels_map[mnemonic]
            print(f"[Eroare MAP] Nu s-a gasit rutina MPM pentru IR={self.IR:04X} ({mnemonic})")
            return self.MAR + 1

        # 2. JUMP: Salt la o eticheta sau adresa specifica
        elif "JUMP" in succesor:
            adresa_curata = self._curata_semnal(micro_inst.jump_address)
            # Ignoram saritura catre "PWFAIL" pentru testare normala si trecem la urmatorul pas
            if "PWFAIL" in adresa_curata:
                return self.MAR + 1

            if adresa_curata.isdigit():
                return int(adresa_curata)
            if adresa_curata in self.labels_map:
                return self.labels_map[adresa_curata]

            return self.MAR + 1

        # 3. STEP: Trece la urmatoarea microinstructiune (+1)
        return self.MAR + 1

    def print_registers(self):
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