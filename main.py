from models.asm_parser import ASMParser
from models.instruction_loader import InstructionLoader
from models.assembler import Assembler

#interfata temporara

def main():
    print("\n--- Testare Instruction Loader ---")
    loader = InstructionLoader()
    opcodes = loader.load("Template_tema1.xlsx")

    print("--- Testare ASM Parser ---")
    parsed_asm = ASMParser.parse("test.asm")

    print("\n3. Generare Cod Masina (Asamblare):")
    assembler = Assembler(opcodes)
    hex_output = assembler.assemble(parsed_asm)


    for original_tokens, hex_code in zip(parsed_asm, hex_output):
        original_line = " ".join(original_tokens)
        print(f"{original_line:<15} -> {hex_code}")
if __name__ == "__main__":
    main()