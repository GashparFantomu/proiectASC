# models/assembler.py

class Assembler:
    def __init__(self, opcodes_map):
        self.opcodes_map = opcodes_map

        self.modes = {
            "AM": "00",  #Imediat aka ala cu valoare imediata
            "AD": "01",  #Direct aka registru - registru
            "AI": "10",  #Indirect aka ala cu paranteze
            "AX": "11"  #Indexat
        }

    def parse_operand(self, operand_str: str):
        """
        Primeste un operand (ex: 'R2', '(R3)') și returneaza
        un tuplu cu (Mod_Adresare_Binar, Registru_Binar).
        """
        operand_str = operand_str.strip()

        #mod adresare indirect
        if operand_str.startswith('(') and operand_str.endswith(')'):
            reg_name = operand_str[1:-1]  # eliminăm parantezele
            reg_num = int(reg_name.replace('R', ''))
            return self.modes["AI"], f"{reg_num:04b}"  # Returnam 10 și codul registrului

        #registru-registru
        elif operand_str.startswith('R') and operand_str[1:].isdigit():
            reg_num = int(operand_str.replace('R', ''))
            return self.modes["AD"], f"{reg_num:04b}"  # Returnam 01 și codul registrului

        #extensii viitoare pentru mod adresare imediat (ex: #5) sau Indexat
        return "00", "0000"

    def assemble(self, parsed_lines: list) -> list:
        machine_code = []

        for tokens in parsed_lines:
            if not tokens:
                continue

            mnemonic = tokens[0].upper()

            #verificam dacă instructiunea e definita în Excel
            if mnemonic not in self.opcodes_map:
                print(f"Eroare: instruciunea asta de aci -> '{mnemonic}' nu a fost găsita... great...")
                continue

            opcode_int = self.opcodes_map[mnemonic]

            #CAZUL A: 2 operanzi (ex: MOV R2, R3)
            #stim că opcode-ul are 4 biti, restul de 12 biti sunt pentru cei 2 operanzi
            if len(tokens) >= 3:
                dest_str = tokens[1]  # Primul este Destinația
                src_str = tokens[2]  # Al doilea este Sursa

                dest_mode, dest_reg = self.parse_operand(dest_str)
                src_mode, src_reg = self.parse_operand(src_str)

                # Format: Opcode(4) | Mod Sursa(2) | Reg Sursa(4) | Mod Dest(2) | Reg Dest(4)
                opcode_bin = f"{opcode_int:04b}"
                binary_str = f"{opcode_bin}{src_mode}{src_reg}{dest_mode}{dest_reg}"

            #CAZUL B: 1 operand (ex: DEC R7)
            #stim din Excel ca opcode-ul are 10 biti, restul de 6 biti sunt pentru operand
            elif len(tokens) == 2:
                dest_str = tokens[1]
                dest_mode, dest_reg = self.parse_operand(dest_str)

                # Format: Opcode(10) | Mod Dest(2) | Reg Dest(4)
                opcode_bin = f"{opcode_int:010b}"
                binary_str = f"{opcode_bin}{dest_mode}{dest_reg}"

            # --- CAZUL C: 0 operanzi (ex: HALT) ---
            # Toti cei 16 biti sunt reprezentati de Opcode
            elif len(tokens) == 1:
                opcode_bin = f"{opcode_int:016b}"
                binary_str = opcode_bin

            #il transformam in hex
            hex_str = f"{int(binary_str, 2):04X}"
            machine_code.append(hex_str)

        return machine_code