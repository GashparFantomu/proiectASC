class CPU:
    def __init__(self, memory_size: int = 4096):
        self.registers = {f"R{i}": 0 for i in range(16)}

        self.PC  = 0
        self.SP  = 0
        self.IR  = 0
        self.T   = 0
        self.ADR = 0
        self.MDR = 0
        self.IVR = 0

        self.SBUS = 0
        self.DBUS = 0
        self.RBUS = 0

        self.flags = {'N': 0, 'Z': 0, 'V': 0, 'C': 0}

        self.memory = [0] * memory_size
        self.micro_memory = {}   #micro_address -> MicroInstruction
        self.MAR = 0
        self.labels_map = {}     #label_upper -> micro_address
        self.opcodes_map = {}

    def load_program(self, machine_codes: list, start_address: int = 0):
        self.PC = start_address
        for offset, code_val in enumerate(machine_codes):
            self.memory[start_address + offset] = code_val
        print(f"[CPU] Program incarcat la adresa {start_address}. "
              f"Dimensiune: {len(machine_codes)} cuvinte.")
        print(f"[CPU] Primele valori: {[hex(v) for v in machine_codes[:8]]}")

    def load_microprogram(self, microinstructions_list: list):
        self.micro_memory = {m.micro_address: m for m in microinstructions_list}
        self.MAR = 0
        self.labels_map = {}
        for inst in microinstructions_list:
            if inst.label:
                clean = inst.label.replace(":", "").strip().upper()
                self.labels_map[clean] = inst.micro_address
        print(f"[CPU] Microprogram incarcat: {len(self.micro_memory)} microinstr.")

    def execute_clock_cycle(self, opcodes_map):
        if self.MAR == 0 and self.memory[self.PC] == 0:
            print("[CPU] Program terminat.")
            return False

        if self.PC >= len(self.memory):
            print(f"[CPU] Eroare fatala: PC-ul a depasit memoria ({self.PC:04X})") #e mai mult un bandaid fix... *sigh*
            return False

        micro_inst = self.micro_memory.get(self.MAR)
        if not micro_inst:
            print(f"[CPU] Adresa MPM invalida: {self.MAR}. Oprit.")
            return False

        if micro_inst.label == "HALT:":
            print("[CPU] HALT.")
            return False

        self.SBUS = self._compute_sbus(micro_inst.sbus)
        self.DBUS = self._compute_dbus(micro_inst.dbus)

        alu_result = self._compute_alu(micro_inst.alu)

        alu_result = self._handle_other_operations(micro_inst.other_ops, alu_result)

        self.RBUS = alu_result
        self._write_rbus(micro_inst.rbus, alu_result)

        self._handle_memory(micro_inst.memory_op)

        self.MAR = self._compute_next_mar(micro_inst, opcodes_map)
        return True

    @staticmethod
    def _clean(signal: str) -> str:
        if not signal or str(signal).strip() in ("NONE", "NAN", "nan", ""):
            return "NONE"
        clean_signal = str(signal).split(":")[0].strip()
        return clean_signal

    def _compute_sbus(self, semnal_brut: str) -> int:
        semnal_control = self._clean(semnal_brut)

        if semnal_control == "NONE":     return 0
        if semnal_control == "PdPCs":    return self.PC
        if semnal_control == "PdSPs":    return self.SP
        if semnal_control == "PdTs":     return self.T
        if semnal_control == "PdFLAGs":  return self._flags_int()
        if semnal_control == "PdMDRs":   return self.MDR
        if semnal_control == "PdIVRs":   return self.IVR
        if semnal_control == "PdADRs":   return self.ADR
        if semnal_control == "Pd0s":     return 0
        if semnal_control == "Pd-1s":    return 0xFFFF  # Reprezintă -1 în 16 biți
        if semnal_control == "PdTsNEG":  return (-self.T) & 0xFFFF

        # Cazul în care se citește din blocul de registre (R0 - R15)
        if semnal_control == "PdRGs":
            # Extragem bitii pentru registrul sursă din IR
            reg_index = (self.IR >> 6) & 0xF
            return self.registers[f"R{reg_index}"]

        return 0

    def _compute_dbus(self, semnal_brut: str) -> int:
        semnal_control = self._clean(semnal_brut)

        if semnal_control == "NONE":      return 0
        if semnal_control == "PdPCd":     return self.PC
        if semnal_control == "PdMDRd":    return self.MDR
        if semnal_control == "PdMDRdNEG": return (-self.MDR) & 0xFFFF
        if semnal_control == "PdSPd":     return self.SP
        if semnal_control == "PdTd":      return self.T
        if semnal_control == "Pd0d":      return 0
        if semnal_control == "Pd-1d":     return 0xFFFF

        if semnal_control == "PdRGd":
            reg_index = self.IR & 0xF
            return self.registers[f"R{reg_index}"]

        if "PdIR" in semnal_control:
            return self.IR & 0xFF

        return 0

    def _compute_dbus(self, semnal_brut: str) -> int:
        semnal_control = self._clean(semnal_brut)

        if semnal_control == "NONE":      return 0
        if semnal_control == "PdPCd":     return self.PC
        if semnal_control == "PdMDRd":    return self.MDR
        if semnal_control == "PdMDRdNEG": return (-self.MDR) & 0xFFFF
        if semnal_control == "PdSPd":     return self.SP
        if semnal_control == "PdTd":      return self.T
        if semnal_control == "Pd0d":      return 0
        if semnal_control == "Pd-1d":     return 0xFFFF

        if semnal_control == "PdRGd":
            reg_index = self.IR & 0xF
            return self.registers[f"R{reg_index}"]

        if "PdIR" in semnal_control:  # Acopera PdIR[OP] etc.
            return self.IR & 0xFF

        return 0

    def _compute_alu(self, signal: str) -> int:
        control_signal = self._clean(signal)
        if control_signal == "NONE":  return 0
        if control_signal == "SBUS":  return self.SBUS & 0xFFFF
        if control_signal == "DBUS":  return self.DBUS & 0xFFFF
        if control_signal == "SUM":   return (self.SBUS + self.DBUS) & 0xFFFF
        if control_signal == "AND":   return (self.SBUS & self.DBUS) & 0xFFFF
        if control_signal == "OR":    return (self.SBUS | self.DBUS) & 0xFFFF
        if control_signal == "XOR":   return (self.SBUS ^ self.DBUS) & 0xFFFF
        if control_signal == "ASL":   return (self.DBUS << 1) & 0xFFFF
        if control_signal == "ASR":
            return ((self.DBUS >> 1) | (self.DBUS & 0x8000)) & 0xFFFF
        if control_signal == "LSR":   return (self.DBUS >> 1) & 0xFFFF
        if control_signal == "ROL":   return ((self.DBUS << 1) | (self.DBUS >> 15)) & 0xFFFF
        if control_signal == "ROR":   return ((self.DBUS >> 1) | ((self.DBUS & 1) << 15)) & 0xFFFF
        if control_signal == "RLC":   return ((self.DBUS << 1) | self.flags['C']) & 0xFFFF
        if control_signal == "RRC":   return ((self.DBUS >> 1) | (self.flags['C'] << 15)) & 0xFFFF
        return 0

    def _handle_other_operations(self, signal: str, alu_result: int) -> int:
        control_signal = self._clean(signal)
        if control_signal in ("NONE", "NOP"):
            return alu_result
        if control_signal == "+2PC":
            self.PC = (self.PC + 2) & 0xFFFF
        elif control_signal == "-2SP":
            self.SP = (self.SP - 2) & 0xFFFF
        elif control_signal == "+2SP":
            self.SP = (self.SP + 2) & 0xFFFF
        elif control_signal in ("Cin,PdCONDaritm", "Cin,PdCONDari"):
            alu_result = (alu_result + 1) & 0xFFFF
            self._update_arith_flags(alu_result)
        elif control_signal in ("PdCONDaritm", "PdCONDari"):
            self._update_arith_flags(alu_result)
        elif control_signal == "PdCONDlog":
            self._update_logic_flags(alu_result)
        elif control_signal == "INTA,-2SP":
            self.SP = (self.SP - 2) & 0xFFFF
        return alu_result

    def _write_rbus(self, signal: str, value: int):
        control_signal = self._clean(signal)
        filtered_value = value & 0xFFFF
        if control_signal == "NONE":    return
        if control_signal == "PmPC":    self.PC  = filtered_value
        elif control_signal == "PmIR":  self.IR  = filtered_value
        elif control_signal == "PmADR": self.ADR = filtered_value
        elif control_signal == "PmMDR": self.MDR = filtered_value
        elif control_signal == "PmSP":  self.SP  = filtered_value
        elif control_signal == "PmT":   self.T   = filtered_value
        elif control_signal == "PmFLAG":
            self.flags['N'] = (filtered_value >> 3) & 1
            self.flags['Z'] = (filtered_value >> 2) & 1
            self.flags['V'] = (filtered_value >> 1) & 1
            self.flags['C'] = (filtered_value >> 0) & 1
        elif control_signal == "PmRG":
            reg = self.IR & 0xF
            self.registers[f"R{reg}"] = filtered_value

    def _handle_memory(self, signal: str):
        control_signal = self._clean(signal)
        if control_signal in ("READ", "IFCH"):
            address = self.ADR
            self.MDR = self.memory[address] if 0 <= address < len(self.memory) else 0
            if control_signal == "IFCH":
                self.IR = self.MDR          # fetch
        elif control_signal == "WRITE":
            address = self.ADR
            if 0 <= address < len(self.memory):
                self.memory[address] = self.MDR

    def step(self):
        micro_inst = self.micro_memory.get(self.MAR)
        if not micro_inst:
            print(f"[Eroare] Microinstrucțiune invalida la MAR={self.MAR}")
            return

        if micro_inst.label == "HALT":
            print("Program Oprit.")
            return False

        current_sbus_val = self._compute_sbus(micro_inst)
        current_dbus_val = self._compute_dbus(micro_inst)

        alu_result = self._compute_alu(micro_inst, current_sbus_val, current_dbus_val)

        if micro_inst.other_ops == "Cin,PdCONDaritm":
            if micro_inst.label == "INC:":
                alu_result = (alu_result + 1) & 0xFFFF
            self.CurrentAluValue = alu_result

        self._write_rbus(micro_inst, alu_result)

        self._handle_memory(micro_inst)

        self._handle_other_operations(micro_inst, alu_result)

        self.MAR = self._compute_next_microaddress(micro_inst)

        return True
    def _compute_next_mar(self, mi, opcodes_map) -> int:
        successor = self._clean(mi.successor)
        jump_raw  = str(mi.jump_address).strip()
        index_raw = str(mi.index_sel).strip() if hasattr(mi, 'index_sel') else "INDEX0: 000"
        invert    = False
        if hasattr(mi, 'inversion'):
            invert = self._clean(mi.inversion) == "F"

        def resolve(addr_str: str) -> int:
            """Resolve a label like 'B1: 0001010' or 'IFCH: 0000000' to an address."""
            name = addr_str.split(':')[0].strip().upper()
            if name.lstrip('-').isdigit():
                return int(name)
            if name in self.labels_map:
                return self.labels_map[name]
            base = name.rstrip('0123456789')
            if base in self.labels_map:
                return self.labels_map[base]
            print(f"[CPU] WARN: eticheta necunoscuta '{name}' in salt.")
            return self.MAR + 1

        def compute_index(idx_str: str) -> int: #un byte ptr wanna be
            idx_name = self._clean(idx_str)
            if idx_name in ("NONE", "INDEX0"):
                return 0
            if idx_name == "INDEX1":
                return (self.IR >> 13) & 0x7
            if idx_name == "INDEX2":
                return (self.IR >> 8) & 0x3
            if idx_name == "INDEX3":
                return (self.IR >> 4) & 0x3
            if idx_name == "INDEX4":
                return (self.IR >> 12) & 0xF
            if idx_name == "INDEX5":
                return (self.IR >> 12) & 0xF
            if idx_name == "INDEX6":
                return (self.IR >> 1) & 0x3F
            if idx_name == "INDEX7":
                return 0
            return 0

        def verify_jump_condition(succ_str: str, inv: bool) -> bool:
            if "IF Z" in succ_str:
                val = self.flags['Z'] == 1
            elif "IF S" in succ_str:
                val = self.flags['N'] == 1
            elif "IF C" in succ_str:
                val = self.flags['C'] == 1
            elif "IF V" in succ_str:
                val = self.flags['V'] == 1
            elif "IF CIL" in succ_str or "IF ACLOW" in succ_str or "IF IOP" in succ_str:
                val = False   # not simulated → always "no interrupt"
            else:
                val = True    # unconditional
            return (not val) if inv else val

        if successor in ("STEP", "NONE", ""):
            return self.MAR + 1

        if successor == "JUMPI":
            base  = resolve(jump_raw)
            index = compute_index(index_raw)
            return base + index

        if successor == "JUMP":
            return resolve(jump_raw)

        if "JUMPI" in successor:
            if verify_jump_condition(successor, invert):
                base  = resolve(jump_raw)
                index = compute_index(index_raw)
                return base + index
            else:
                return self.MAR + 1

        if "JUMP" in successor:
            if verify_jump_condition(successor, invert):
                return resolve(jump_raw)
            else:
                return self.MAR + 1

        return self.MAR + 1

    def _flags_int(self) -> int:
        return ((self.flags['N'] << 3) | (self.flags['Z'] << 2) |
                (self.flags['V'] << 1) | self.flags['C'])

    def _update_arith_flags(self, result: int):
        r16 = result & 0xFFFF
        self.flags['N'] = 1 if (r16 & 0x8000) else 0
        self.flags['Z'] = 1 if r16 == 0 else 0
        self.flags['C'] = 1 if result > 0xFFFF else 0
        self.flags['V'] = 1 if result > 32767 or result < -32768 else 0

    def _update_logic_flags(self, result: int):
        r16 = result & 0xFFFF
        self.flags['N'] = 1 if (r16 & 0x8000) else 0
        self.flags['Z'] = 1 if r16 == 0 else 0
        self.flags['V'] = 0
        self.flags['C'] = 0

    def print_registers(self):
        print("\n=== STARE CPU ===")
        print(f"PC: {self.PC:04X} | IR: {self.IR:04X} | SP: {self.SP:04X} | MAR: {self.MAR}")
        print(f"ADR: {self.ADR:04X} | MDR: {self.MDR:04X} | T: {self.T:04X}")
        print(f"Buses -> SBUS: {self.SBUS:04X} | DBUS: {self.DBUS:04X} | RBUS: {self.RBUS:04X}")
        print(f"Flags -> N:{self.flags['N']} Z:{self.flags['Z']} "
              f"V:{self.flags['V']} C:{self.flags['C']}")
        active = {k: hex(v) for k, v in self.registers.items() if v != 0}
        print(f"Registre: {active if active else 'toate 0'}")
