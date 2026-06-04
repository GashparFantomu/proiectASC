from gui import CPUViewerApp
from models.asm_parser import ASMParser
from models.instruction_loader import InstructionLoader
from models.assembler import Assembler
from models.cpu import CPU
from models.microprogram_loader import MicroprogramLoader


def main():
    print("loading from Excel... Template_tema1.xlsx")
    loader = InstructionLoader()
    loader.load("Template_tema1.xlsx", sheet_name=0)

    print("Parsing .asm file...")
    parsed_asm = ASMParser.parse("test.asm")

    print("Asamblare...")
    assembler = Assembler(loader)
    machine_codes = assembler.assemble(parsed_asm)

    print("Incarcare microprogram din Microprogram.xlsx...")
    micro_loader = MicroprogramLoader()
    micro_lista = micro_loader.load("Microprogram.xlsx")

    print("Incarcare in Procesor (RAM)...")
    cpu = CPU()
    cpu.load_program(machine_codes)
    cpu.load_microprogram(micro_lista)
    cpu.opcodes_map = loader.opcodes_map
    cpu.print_registers()
    app = CPUViewerApp(cpu_instance=cpu, assembler_instance=assembler)
    app.mainloop()

if __name__ == "__main__":
    main()