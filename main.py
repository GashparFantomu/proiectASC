from models.asm_parser import ASMParser
from models.instruction_loader import InstructionLoader

#interfata temporara
print("--- Testare ASM Parser ---")
parsed_asm = ASMParser.parse("test.asm")
for line in parsed_asm:
    print(line)

print("\n--- Testare Instruction Loader ---")
loader = InstructionLoader()
opcodes = loader.load("Template_tema1.xlsx")

for mnemonic, opcode_int in opcodes.items():
    binary_str = format(opcode_int, '04b')
    print(f"Instructiune: {mnemonic:<5} | Opcode (int): {opcode_int:<2} | Binar: {binary_str}")
