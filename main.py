from gui import CPUViewerApp
from models.asm_parser import ASMParser
from models.instruction_loader import InstructionLoader
from models.assembler import Assembler
from models.cpu import CPU

def main():
    print("loading from Excel...")
    loader = InstructionLoader()
    loader.load("Template_tema1.xlsx", sheet_name=0)


    print("Parsing .asm file...")
    parsed_asm = ASMParser.parse("test.asm")

    print("Asamblare...")
    assembler = Assembler(loader)
    machine_codes = assembler.assemble(parsed_asm)

    for original_tokens, code_int in zip(parsed_asm, machine_codes):
        original_line = " ".join(original_tokens)
        print(f"{original_line:<15} -> {code_int:04X}")
    print("Export în fișier binar real (output.bin)...")
    try:
        with open("output.bin", "wb") as file:
            for code_int in machine_codes:
                file.write(code_int.to_bytes(2, byteorder='big'))
        print("   [Succes] Fisierul 'output.bin' a fost generat!")
    except Exception as e:
        print(f"   [Eroare] Nu s-a putut salva fișierul binar: {e}")


    print("Incarcare in Procesor (RAM)...")
    cpu = CPU()
    cpu.load_program(machine_codes)
    cpu.print_registers()

    app = CPUViewerApp(cpu_instance=cpu, assembler_instance=assembler)
    app.mainloop()

if __name__ == "__main__":
    main()