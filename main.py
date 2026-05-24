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
    numeric_output = assembler.assemble(parsed_asm)

    for original_tokens, code_int in zip(parsed_asm, numeric_output):
        original_line = " ".join(original_tokens)
        print(f"{original_line:<15} -> {code_int:04X}")
    print("\n4. Export în fișier binar real (output.bin)...")
    try:
        # Deschidem fișierul în modul 'wb' (Write Binary)
        with open("output.bin", "wb") as file:
            for code_int in numeric_output:
                # Fiecare instrucțiune are 16 biți (2 octeți).
                # byteorder='big' înseamnă că octetul cel mai semnificativ (MSB) se scrie primul,
                # exact în ordinea în care citim biții din Excel de la stânga la dreapta.
                file.write(code_int.to_bytes(2, byteorder='big'))
        print("   [Succes] Fișierul 'output.bin' a fost generat!")
    except Exception as e:
        print(f"   [Eroare] Nu s-a putut salva fișierul binar: {e}")


    print("\n4. Încărcare în Procesor (RAM)...")
    cpu = CPU()
    cpu.load_program(numeric_output)
    cpu.print_status()

if __name__ == "__main__":
    main()