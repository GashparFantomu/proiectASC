class Assembler:
    def __init__(self, loader):
        self.opcodes = loader.opcodes_map
        self.registers = loader.registers_map
        self.ad_modes = loader.addressing_modes

    # 00 = imediat
    # 01 = registru direct
    # 10 = registru indirect
    # 11 = indexat

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
        """
        clean_token = token.strip()

        if clean_token.upper().startswith('R') and clean_token[1:].isdigit():
            register = int(clean_token[1:])
            return self.ParsedOperand(mode=0b01, register=register)

        if clean_token.startswith('(R') and clean_token.endswith(')'):
            register = int(clean_token[2:-1])
            return self.ParsedOperand(mode=0b10, register=register)

        if '(R' in clean_token and clean_token.endswith(')'):
            paren = clean_token.index('(R')
            offset_str = clean_token[:paren]
            reg_str = clean_token[paren+2:-1]
            offset = int(offset_str, 0) if offset_str else 0
            register = int(reg_str)
            return self.ParsedOperand(mode=0b11, register=register, extra=offset)

        if clean_token.upper().endswith('H'):
            value = int(clean_token[:-1], 16)
        else:
            value = int(clean_token, 0)
        return self.ParsedOperand(mode=0b00, register=0, extra=value)

    def assemble(self, parsed_lines: list) -> list:
        """
        Assemble parsed token lines into machine-code words.
        """
        machine_code_list = []
        idx = 0
        flat_tokens = []

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
            base_opcode = inst_info['base']

            if mnemonic in self.NO_OPERAND:
                machine_code_list.append(base_opcode)

            elif mnemonic in self.TWO_OPERAND:
                dest = self._parse_operand(flat_tokens[idx]);   idx += 1
                src  = self._parse_operand(flat_tokens[idx]);   idx += 1

                word = base_opcode | (src.mode << 10) | (src.register << 6) | \
                       (dest.mode << 4)   | dest.register
                machine_code_list.append(word & 0xFFFF)

                if src.extra is not None:
                    machine_code_list.append(src.extra & 0xFFFF)
                if dest.extra is not None:
                    machine_code_list.append(dest.extra & 0xFFFF)

            elif mnemonic in self.ONE_OPERAND:
                dest = self._parse_operand(flat_tokens[idx]);   idx += 1

                word = base_opcode | (dest.mode << 4) | dest.register
                machine_code_list.append(word & 0xFFFF)

                if dest.extra is not None:
                    machine_code_list.append(dest.extra & 0xFFFF)

            elif mnemonic in self.BRANCH:
                offset_str = flat_tokens[idx];   idx += 1
                offset = int(offset_str, 0)
                if offset < 0:
                    offset = (1 << 8) + offset
                offset8bit = offset & 0xFF
                word = base_opcode | offset8bit
                machine_code_list.append(word & 0xFFFF)

        return machine_code_list
