from models.asm_parser import ASMParser
from models.instruction_loader import InstructionLoader
from models.assembler import Assembler
from models.cpu import CPU

def main():
    print("\n1. Se încarcă instrucțiunile din Excel...")
    loader = InstructionLoader()
    # Încarcă primul sheet
    loader.load("Template_tema1.xlsx", sheet_name=0)


    print("2. Se parsează fișierul test.asm...")
    parsed_asm = ASMParser.parse("test.asm")

    print("\n3. === ASAMBLARE (Generare Cod Mașină) ===")
    assembler = Assembler(loader)
    hex_output = assembler.assemble(parsed_asm)

    for original_tokens, hex_code in zip(parsed_asm, hex_output):
        original_line = " ".join(original_tokens)
        print(f"{original_line:<15} -> {hex_code}")

    print("\n4. Încărcare în Procesor (RAM)...")
    cpu = CPU()
    cpu.load_program(hex_output)
    cpu.print_status()

if __name__ == "__main__":
    main()