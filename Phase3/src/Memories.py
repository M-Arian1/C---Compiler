from enum import Enum

WORD_SIZE = 4
MEMORY_BLOCK_SIZE = 4
MAX_MEMORY_ADDRESS = 1000


# ===== Memory Layer =====

class Memory:
    """Abstract base for all memory segments."""
    def __init__(self, base_address, bound_address):
        self.base_address = base_address
        self.bound_address = bound_address
        self.current_address = base_address

    def _check_bounds(self, address):
        if not (self.base_address <= address <= self.bound_address):
            raise MemoryError(f"Address {address} out of bounds [{self.base_address}, {self.bound_address}].")


class AddressableSegment(Memory):
    """A memory segment where each cell stores a value."""
    def __init__(self, base_address, bound_address):
        super().__init__(base_address, bound_address)
        self.cells = []

    def allocate_cell(self):
        if self.current_address + MEMORY_BLOCK_SIZE > self.bound_address:
            raise MemoryError("Segment overflow.")
        self.cells.append(None)
        allocated_address = self.current_address
        self.current_address += MEMORY_BLOCK_SIZE
        return allocated_address

    def _address_to_index(self, address):
        if address % MEMORY_BLOCK_SIZE != 0:
            raise MemoryError(f"Unaligned memory access at {address}.")
        return (address - self.base_address) // MEMORY_BLOCK_SIZE

    def get(self, address):
        idx = self._address_to_index(address)
        try:
            return self.cells[idx]
        except IndexError:
            raise MemoryError("Invalid memory access.")

    def set(self, address, value):
        idx = self._address_to_index(address)
        try:
            self.cells[idx] = value
        except IndexError:
            raise MemoryError("Invalid memory access.")


class CodeSegment(Memory):
    """Stores compiled instructions."""
    def __init__(self, base_address, bound_address):
        super().__init__(base_address, bound_address)
        self.instructions = {}

    def add_instruction(self, instruction, address=None):
        if address is None:
            address = self.current_address
            self.current_address += 1
        self._check_bounds(address)
        self.instructions[address] = instruction

    def set_program_counter(self, address):
        self._check_bounds(address)
        self.current_address = address

    def __str__(self):
        return "\n".join(
            f"{addr}\t{self.instructions[addr]}" for addr in sorted(self.instructions)
        )


class DataSegment(AddressableSegment):
    """Holds program variables."""
    pass


class TemporarySegment(AddressableSegment):
    """Holds temporary variables for computation."""
    def allocate_temp(self):
        return self.allocate_cell()


class Memory:
    """Encapsulates the entire memory space."""
    def __init__(self, code_start, data_start, temp_start):
        self.program_block = CodeSegment(code_start, data_start - 1)
        self.data_block = DataSegment(data_start, temp_start - 1)
        self.temp_segment = TemporarySegment(temp_start, MAX_MEMORY_ADDRESS - 1)

    def code(self):
        return self.program_block

    def data(self):
        return self.data_block

    def temporaries(self):
        return self.temp_segment


# ===== Instruction Layer =====

class Instruction:
    """Abstract base class for all instruction types."""
    def __str__(self):
        raise NotImplementedError("Subclasses must implement __str__.")


class TACOperation(Enum):
    ADD = "ADD"
    MULTIPLY = "MULT"
    SUBTRACT = "SUB"
    EQUAL = "EQ"
    LESS_THAN = "LT"
    ASSIGN = "ASSIGN"
    JUMP_IF_FALSE = "JPF"
    JUMP = "JP"
    PRINT = "PRINT"


class ThreeAddressInstruction(Instruction):
    """Represents a 3-address code instruction."""
    def __init__(self, operation: TACOperation, operand1=None, operand2=None, operand3=None):
        self.operation = operation
        self.operands = [operand1, operand2, operand3]

    def __str__(self):
        operand_strings = [str(op) if op is not None else "" for op in self.operands]
        return f"({self.operation.value},{','.join(operand_strings)})"
