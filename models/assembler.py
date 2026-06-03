class Assembler:
    def __init__(self, loader):
        self.opcodes = loader.opcodes_map
        self.registers = loader.registers_map
        self.ad_modes = loader.addressing_modes

    # ---- Addressing mode constants (matches instruction format spec) ----
    # 00 = imediat (immediate)
    # 01 = registru direct (register direct)
    # 10 = registru indirect (register indirect)
    # 11 = indexat (indexed)

    TWO_OPERAND  = {"MOV", "ADD", "SUB", "CMP", "AND", "OR", "XOR"}
    ONE_OPERAND  = {"CLR", "NEG", "INC", "DEC", "ASL", "ASR", "LSR",
                    "ROL", "ROR", "RLC", "RRC", "JMP", "CALL", "PUSH", "POP"}
    BRANCH       = {"BR", "BEQ", "BNE", "BPL", "BMI", "BCS", "BCC", "BVS", "BVC"}
    NO_OPERAND   = {"NOP", "HALT", "RET", "RETI", "WAIT", "CLC", "SEC",
                    "CLZ", "SEZ", "CLV", "SEV", "CLS", "SES", "CCC", "SCC"}

    class ParsedOperand:
        def __init__(self, mode, register, extra=None):
            self.mode = mode
            self.register = register
            self.extra = extra  # immediate value or index offset

    def _parse_operand(self, token: str) -> "Assembler.ParsedOperand":
        """
        Parse a single operand token into (mode, register, extra).

        Formats:
          R3         -> mode=01 (register direct), reg=3
          (R3)       -> mode=10 (register indirect), reg=3
          5(R3)      -> mode=11 (indexed), reg=3, extra=5
          1248H      -> mode=00 (immediate), reg=0, extra=0x1248
          42         -> mode=00 (immediate), reg=0, extra=42
        """
        t = token.strip()

        # Register direct: R0 .. R15
        if t.upper().startswith('R') and t[1:].isdigit():
            reg = int(t[1:])
            return self.ParsedOperand(mode=0b01, register=reg)

        # Register indirect: (R0) .. (R15)
        if t.startswith('(R') and t.endswith(')'):
            reg = int(t[2:-1])
            return self.ParsedOperand(mode=0b10, register=reg)

        # Indexed: offset(Rn)
        if '(R' in t and t.endswith(')'):
            paren = t.index('(R')
            offset_str = t[:paren]
            reg_str = t[paren+2:-1]
            offset = int(offset_str, 0) if offset_str else 0
            reg = int(reg_str)
            return self.ParsedOperand(mode=0b11, register=reg, extra=offset)

        # Immediate: hex (e.g. 1248H) or decimal
        if t.upper().endswith('H'):
            value = int(t[:-1], 16)
        else:
            value = int(t, 0)
        return self.ParsedOperand(mode=0b00, register=0, extra=value)

    def assemble(self, parsed_lines: list) -> list:
        """
        Assemble parsed token lines into machine-code words.

        Instruction formats (from spec):
          2-operand:  [opcode:4][MAS:2][RS:4][MAD:2][RD:4]   (bit 15..0)
          1-operand:  [opcode:10][MAD:2][RD:4]
          branch:     [opcode:8][OFFSET:8]
          no-operand: [opcode:16]
        """
        machine_code_list = []
        idx = 0
        flat_tokens = []

        # Flatten the list-of-lists (each inner list is one source line)
        for line_tokens in parsed_lines:
            flat_tokens.extend(line_tokens)

        while idx < len(flat_tokens):
            mnemonic = flat_tokens[idx].upper()
            idx += 1

            if mnemonic not in self.opcodes:
                print(f"[Assembler] Mnemonic necunoscut: '{mnemonic}'")
                machine_code_list.append(0)
                continue

            inst_info = self.opcodes[mnemonic]
            base_opcode = inst_info['base']   # already the opcode bits, pre-shifted

            if mnemonic in self.NO_OPERAND:
                machine_code_list.append(base_opcode)

            elif mnemonic in self.TWO_OPERAND:
                # Assembly syntax: MNEMONIC dest, src
                dest = self._parse_operand(flat_tokens[idx]);   idx += 1
                src  = self._parse_operand(flat_tokens[idx]);   idx += 1

                # Format: [opcode:4][srcMode:2][srcReg:4][destMode:2][destReg:4]
                word = (base_opcode << 12) | (src.mode << 10) | (src.register << 6) | \
                       (dest.mode << 4)   | dest.register
                machine_code_list.append(word & 0xFFFF)

                # Extra words for indexed addressing (in order: src extra, then dest extra)
                if src.extra is not None:
                    machine_code_list.append(src.extra & 0xFFFF)
                if dest.extra is not None:
                    machine_code_list.append(dest.extra & 0xFFFF)

            elif mnemonic in self.ONE_OPERAND:
                # Assembly syntax: MNEMONIC dest
                dest = self._parse_operand(flat_tokens[idx]);   idx += 1

                # Format: [opcode:10][destMode:2][destReg:4]
                word = (base_opcode << 6) | (dest.mode << 4) | dest.register
                machine_code_list.append(word & 0xFFFF)

                if dest.extra is not None:
                    machine_code_list.append(dest.extra & 0xFFFF)

            elif mnemonic in self.BRANCH:
                # Assembly syntax: MNEMONIC offset  (signed 8-bit offset)
                offset_str = flat_tokens[idx];   idx += 1
                offset = int(offset_str, 0)
                if offset < 0:
                    offset = (1 << 8) + offset
                word = (base_opcode << 8) | (offset & 0xFF)
                machine_code_list.append(word & 0xFFFF)

        return machine_code_list
