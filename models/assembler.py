class Assembler:
    def __init__(self, loader):
        # Preluăm dicționarele pregătite de loader
        self.opcodes = loader.opcodes_map
        self.registers = loader.registers_map
        self.ad_modes = loader.addressing_modes

    def parse_operand(self, op_str):
        """Transformă un operand text în valoarea sa binară."""
        # 1. Tratare offset pentru Branch (ex: +5, -2)
        if op_str.startswith('+') or op_str.startswith('-') or op_str.lstrip('-').isdigit():
            offset = int(op_str)
            if offset < 0:
                offset = (1 << 8) + offset  # Complement față de 2
            return offset & 0xFF


        # 2. Tratare Registre. Curățăm simbolurile speciale pt flexibilitate
        clean_op = op_str.replace('(', '').replace(')+', '').replace('@', '')

        mode = self.ad_modes["AD"]  # Presupunem Adresare Directă (01) ca standard pentru "R1"
        reg_val = 0

        if clean_op in self.registers:
            reg_val = self.registers[clean_op]
            # (Pe viitor: dacă op_str are paranteze rotunde, mode = self.ad_modes["AI"], etc.)

        # Pachetul pentru un operand este: [AM - 2 biți] [REG - 4 biți]
        return (mode << 4) | reg_val

    def assemble(self, parsed_lines):
        machine_code = []

        for tokens in parsed_lines:
            if not tokens: continue
            mnemonic = tokens[0]

            if mnemonic not in self.opcodes:
                machine_code.append("ERROR")
                continue

            inst = self.opcodes[mnemonic]
            code = inst['base']
            empty = inst['empty_bits']

            # Instrucțiuni cu 2 operanzi (12 biți liberi pt 2 pachete a câte 6 biți)
            if empty == 12 and len(tokens) >= 3:
                src_op = self.parse_operand(tokens[1])  # Primul operand
                dest_op = self.parse_operand(tokens[2])  # Al doilea operand
                # [DEST] se shiftează cu 6 biți ca să lase loc pt [SRC] la final
                code |= (dest_op << 6) | src_op

            # Instrucțiuni cu 1 operand (6 biți liberi la final)
            elif empty == 6 and len(tokens) >= 2:
                dest_op = self.parse_operand(tokens[1])
                code |= dest_op

            # Instrucțiuni Branch (8 biți liberi pt offset la final)
            elif empty == 8 and len(tokens) >= 2:
                offset = self.parse_operand(tokens[1])
                code |= offset

            machine_code.append(code)

        return machine_code