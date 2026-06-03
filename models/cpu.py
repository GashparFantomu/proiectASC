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
        self.micro_memory = {}   # micro_address -> MicroInstruction
        self.MAR = 0
        self.labels_map = {}     # label_upper -> micro_address
        self.opcodes_map = {}

    # ================================================================
    # Load / Init
    # ================================================================

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

    # ================================================================
    # Main execution step
    # ================================================================

    def execute_clock_cycle(self, opcodes_map):
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

        # Other ops (flags, PC+2, SP±2, Cin+1)
        alu_result = self._handle_other_ops(micro_inst.other_ops, alu_result)

        self.RBUS = alu_result
        self._write_rbus(micro_inst.rbus, alu_result)

        self._handle_memory(micro_inst.memory_op)

        self.MAR = self._compute_next_mar(micro_inst, opcodes_map)
        return True

    # ================================================================
    # Private helpers
    # ================================================================

    @staticmethod
    def _clean(signal: str) -> str:
        """'PdPCs: 0110' -> 'PDPCS'   |  'INDEX3: 011' -> 'INDEX3'"""
        if not signal or str(signal).strip().upper() in ("NONE", "NAN", ""):
            return "NONE"
        return str(signal).split(':')[0].strip().upper()

    # ---- SBUS ----
    # Source register  = IR[9:6]  (RS field in 2-operand instructions)
    # For 1-operand instructions the single register is IR[3:0] but
    # the microprogram always routes it through MDR/T, never PdRGs directly
    # for 1-operand.  The C# code: PdRGs -> GeneralRegisters[(IR>>6)&0xF]
    def _compute_sbus(self, sig: str) -> int:
        s = self._clean(sig)
        if s == "NONE":     return 0
        if s == "PDPCS":    return self.PC
        if s == "PDSPS":    return self.SP
        if s == "PDTS":     return self.T
        if s == "PDFLAGS":  return self._flags_int()
        if s == "PDMDRS":   return self.MDR
        if s == "PDIVRS":   return self.IVR
        if s == "PDADRS":   return self.ADR
        if s == "PD0S":     return 0
        if s == "PD-1S":    return 0xFFFF          # -1 in 16-bit
        if s == "PDTSNEG":  return (-self.T) & 0xFFFF
        if s == "PDRGS":
            reg = (self.IR >> 6) & 0xF             # RS = bits [9:6]
            return self.registers[f"R{reg}"]
        return 0

    # ---- DBUS ----
    # Destination register = IR[3:0]  (RD field)
    def _compute_dbus(self, sig: str) -> int:
        s = self._clean(sig)
        if s == "NONE":      return 0
        if s == "PDPCD":     return self.PC
        if s == "PDMDRD":    return self.MDR
        if s == "PDMDRDNEG": return (-self.MDR) & 0xFFFF
        if s == "PDSPD":     return self.SP
        if s == "PDTD":      return self.T
        if s == "PD0D":      return 0
        if s == "PD-1D":     return 0xFFFF
        if s == "PDRGD":
            reg = self.IR & 0xF                    # RD = bits [3:0]
            return self.registers[f"R{reg}"]
        # "PdIR [7…0]d"  used by CLC/SEC/etc.
        if "PDIR" in s:
            return self.IR & 0xFF
        return 0

    # ---- ALU ----
    def _compute_alu(self, sig: str) -> int:
        s = self._clean(sig)
        if s == "NONE":  return 0
        if s == "SBUS":  return self.SBUS & 0xFFFF
        if s == "DBUS":  return self.DBUS & 0xFFFF
        if s == "SUM":   return (self.SBUS + self.DBUS) & 0xFFFF
        if s == "AND":   return (self.SBUS & self.DBUS) & 0xFFFF
        if s == "OR":    return (self.SBUS | self.DBUS) & 0xFFFF
        if s == "XOR":   return (self.SBUS ^ self.DBUS) & 0xFFFF
        if s == "ASL":   return (self.DBUS << 1) & 0xFFFF
        if s == "ASR":
            return ((self.DBUS >> 1) | (self.DBUS & 0x8000)) & 0xFFFF
        if s == "LSR":   return (self.DBUS >> 1) & 0xFFFF
        if s == "ROL":   return ((self.DBUS << 1) | (self.DBUS >> 15)) & 0xFFFF
        if s == "ROR":   return ((self.DBUS >> 1) | ((self.DBUS & 1) << 15)) & 0xFFFF
        if s == "RLC":   return ((self.DBUS << 1) | self.flags['C']) & 0xFFFF
        if s == "RRC":   return ((self.DBUS >> 1) | (self.flags['C'] << 15)) & 0xFFFF
        return 0

    # ---- Other Operations ----
    def _handle_other_ops(self, sig: str, result: int) -> int:
        s = self._clean(sig)
        if s in ("NONE", "NOP"):
            return result
        if s == "+2PC":
            self.PC = (self.PC + 2) & 0xFFFF
        elif s == "-2SP":
            self.SP = (self.SP - 2) & 0xFFFF
        elif s == "+2SP":
            self.SP = (self.SP + 2) & 0xFFFF
        elif s in ("CIN,PDCONDARITM", "CIN,PDCONDARI", "CIN,PDCONDARI"):
            result = (result + 1) & 0xFFFF
            self._update_arith_flags(result)
        elif s in ("PDCONDARITM", "PDCONDARI"):
            self._update_arith_flags(result)
        elif s == "PDCONDLOG":
            self._update_logic_flags(result)
        elif s == "INTA,-2SP":
            self.SP = (self.SP - 2) & 0xFFFF
        # Hardware-only signals (A(1)BE1, A(0)BVI, etc.) — no-op in simulation
        return result

    # ---- Write RBUS ----
    # Destination register for PmRG = IR[3:0]  (RD field)
    def _write_rbus(self, sig: str, value: int):
        s = self._clean(sig)
        v = value & 0xFFFF
        if s == "NONE":    return
        if s == "PMPC":    self.PC  = v
        elif s == "PMIR":  self.IR  = v
        elif s == "PMADR": self.ADR = v
        elif s == "PMMDR": self.MDR = v
        elif s == "PMSP":  self.SP  = v
        elif s == "PMT":   self.T   = v
        elif s == "PMFLAG":
            self.flags['N'] = (v >> 3) & 1
            self.flags['Z'] = (v >> 2) & 1
            self.flags['V'] = (v >> 1) & 1
            self.flags['C'] = (v >> 0) & 1
        elif s == "PMRG":
            reg = self.IR & 0xF                    # RD = bits [3:0]
            self.registers[f"R{reg}"] = v

    # ---- Memory ----
    def _handle_memory(self, sig: str):
        s = self._clean(sig)
        if s in ("READ", "IFCH"):
            addr = self.ADR
            self.MDR = self.memory[addr] if 0 <= addr < len(self.memory) else 0
            if s == "IFCH":
                self.IR = self.MDR          # fetch: also loads IR
        elif s == "WRITE":
            addr = self.ADR
            if 0 <= addr < len(self.memory):
                self.memory[addr] = self.MDR

    # ---- Compute Next MAR ----
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
            # Try stripping trailing _z or numeric suffix
            base = name.rstrip('0123456789')
            if base in self.labels_map:
                return self.labels_map[base]
            print(f"[CPU] WARN: eticheta necunoscuta '{name}' in salt.")
            return self.MAR + 1

        def compute_index(idx_str: str) -> int:
            """Compute the INDEX value based on INDEX0..INDEX7 and current IR."""
            idx_name = self._clean(idx_str)
            if idx_name in ("NONE", "INDEX0"):
                return 0
            if idx_name == "INDEX1":
                # IR[15:14] = bits that select which instruction class (B1 dispatch)
                # From the C# reference, INDEX1 is used for the CIL/class check at IFCH_1
                return (self.IR >> 13) & 0x7  # simplified
            if idx_name == "INDEX2":
                # Source addressing mode = IR[9:8]
                return (self.IR >> 8) & 0x3
            if idx_name == "INDEX3":
                # Destination addressing mode = IR[3:2]  (MAD field bits [5:4] of instruction)
                # Actually MAD = IR[5:4] for 2-operand, IR[5:4] for 1-operand
                return (self.IR >> 4) & 0x3
            if idx_name == "INDEX4":
                # Jump to specific 2-operand instruction routine:
                # IR[15:12] = opcode of 2-op instr (MOV=0, ADD=1, SUB=2, ...)
                return (self.IR >> 12) & 0xF
            if idx_name == "INDEX5":
                # Jump to 1-operand or branch instruction routine
                # For 1-op: IR[11:6] contains the sub-opcode
                # C# uses (IR>>12)&0xF for B3/B4 dispatch
                return (self.IR >> 12) & 0xF
            if idx_name == "INDEX6":
                return (self.IR >> 1) & 0x3F
            if idx_name == "INDEX7":
                return 0
            return 0

        def cond_met(succ_str: str, inv: bool) -> bool:
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

        # STEP
        if successor in ("STEP", "NONE", ""):
            return self.MAR + 1

        # Unconditional JUMPI (indexed)
        if successor == "JUMPI":
            base  = resolve(jump_raw)
            index = compute_index(index_raw)
            return base + index

        # Unconditional JUMP (non-indexed)
        if successor == "JUMP":
            return resolve(jump_raw)

        # Conditional JUMPI variants: "IF Z JUMPI", "IF C JUMPI", etc.
        if "JUMPI" in successor:
            if cond_met(successor, invert):
                base  = resolve(jump_raw)
                index = compute_index(index_raw)
                return base + index
            else:
                return self.MAR + 1

        # Conditional JUMP variants (non-indexed)
        if "JUMP" in successor:
            if cond_met(successor, invert):
                return resolve(jump_raw)
            else:
                return self.MAR + 1

        return self.MAR + 1

    # ---- Flag helpers ----
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
