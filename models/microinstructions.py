from dataclasses import dataclass

@dataclass
class InstructionDef:
    mnemonic: str
    opcode: str

@dataclass
class MicroInstruction:
    label: str
    micro_address: int
    sbus: str
    dbus: str
    alu: str
    rbus: str
    memory_op: str
    other_ops: str
    successor: str
    jump_address: str