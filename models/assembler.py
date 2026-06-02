class Assembler:
    def __init__(self, loader):
        self.opcodes = loader.opcodes_map
        self.registers = loader.registers_map
        self.ad_modes = loader.addressing_modes

    def parse_operand(self, operation_string):
        """Transforma un operand text in valoarea sa binara"""
        if operation_string.startswith('+') or operation_string.startswith('-') or operation_string.lstrip('-').isdigit():
            offset = int(operation_string)
            if offset < 0:
                offset = (1 << 8) + offset
            return offset & 0xFF


        clean_register_name = operation_string.replace('(', '').replace(')+', '').replace('@', '')

        current_mode = self.ad_modes["AD"]
        register_value = 0

        if clean_register_name in self.registers:
            register_value = self.registers[clean_register_name]

        return (current_mode << 4) | register_value

    def assemble(self, parsed_lines):
        machine_code_list = []

        for tokens in parsed_lines:
            if not tokens: continue
            mnemonic = tokens[0]

            if mnemonic not in self.opcodes:
                machine_code_list.append("ERROR")
                continue

            instruction_info = self.opcodes[mnemonic]
            base_machine_code = instruction_info['base']
            avalable_empty_bits = instruction_info['empty_bits']

            if avalable_empty_bits == 12 and len(tokens) >= 3: #CONTINUA DE ACI
                src_op = self.parse_operand(tokens[1])  # Primul operand
                dest_op = self.parse_operand(tokens[2])  # Al doilea operand
                base_machine_code |= (dest_op << 6) | src_op

            elif avalable_empty_bits == 6 and len(tokens) >= 2:
                dest_op = self.parse_operand(tokens[1])
                base_machine_code |= dest_op

            elif avalable_empty_bits == 8 and len(tokens) >= 2:
                offset = self.parse_operand(tokens[1])
                base_machine_code |= offset

            machine_code_list.append(base_machine_code)

        return machine_code_list