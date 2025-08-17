from enum import Enum

WORD_SIZE = 4
MEMORY_BLOCK_SIZE = 4
MAX_MEMORY_ADDRESS = 1000


# ===== Memory Layer =====

class Data():
    def __init__(self, lexeme, type, loc, is_func=False, attrs={}):
        self.lexeme = lexeme
        self.address = loc
        self.type = type
        self.is_func = is_func
        self.attrs = attrs
        if type == 'int' or type == 'array':
            self.type_size = WORD_SIZE
    
    def is_func(self):
        return self.is_func
        
class MemorySegment:
    """Abstract base for all memory segments."""
    def __init__(self, base_address, bound_address):
        self.base_address = base_address
        self.bound_address = bound_address
        self.current_address = base_address
        # self.cells = {}

    def _check_bounds(self, address):
        if not (self.base_address <= address <= self.bound_address):
            raise MemoryError(f"Address {address} out of bounds [{self.base_address}, {self.bound_address}].")
        
    def increment_addr(self, val = 1):
        self.current_address += val
        
    def decrement_addr(self, val = 1):
        self.current_address -= val
        #TODO: handle memory error
        
    def allocate_cell(self):
        if self.current_address + MEMORY_BLOCK_SIZE > self.bound_address:
            raise MemoryError("Segment overflow.")
        allocated_address = self.current_address
        self.cells[allocated_address] = None  # Fix: use address as key, not append
        self.current_address += MEMORY_BLOCK_SIZE
        return allocated_address


# class AddressableSegment(MemorySegment):
#     """A memory segment where each cell stores a value."""
#     def __init__(self, base_address, bound_address):
#         super().__init__(base_address, bound_address)
#         self.cells = []

#     def allocate_cell(self):
#         if self.current_address + MEMORY_BLOCK_SIZE > self.bound_address:
#             raise MemoryError("Segment overflow.")
#         allocated_address = self.current_address
#         self.cells.append(None)
#         self.current_address += MEMORY_BLOCK_SIZE
#         return allocated_address

#     def _address_to_index(self, address):
#         if address % MEMORY_BLOCK_SIZE != 0:
#             raise MemoryError(f"Unaligned memory access at {address}.")
#         return (address - self.base_address) // MEMORY_BLOCK_SIZE

#     def get(self, address):
#         idx = self._address_to_index(address)
#         try:
#             return self.cells[idx]
#         except IndexError:
#             raise MemoryError("Invalid memory access.")

#     def set(self, address, value):
#         idx = self._address_to_index(address)
#         try:
#             self.cells[idx] = value
#         except IndexError:
#             raise MemoryError("Invalid memory access.")


class CodeSegment(MemorySegment):
    """Stores compiled instructions."""
    def __init__(self, base_address, bound_address):
        super().__init__(base_address, bound_address)
        # self.instructions = {}
        self.scope = 0
        self.error = False
        self.cells = {}

    def add_instruction(self, instruction, address=None):
        if address is None:
            address = self.current_address
            self.current_address += 1
        self._check_bounds(address)
        self.cells[address] = instruction
        return address  # Return where the instruction was stored

    def set_program_counter(self, address):
        self._check_bounds(address)
        self.current_address = address

    def __str__(self):
        return "\n".join(
            f"{addr}\t{self.cells[addr]}" for addr in sorted(self.cells)
        )
        
    def decrement_scope(self, value = 1):
        if self.scope > 1:
            self.scope -= value
    
    def increment_scope(self, value=1):
        self.scope += value
        
    def get_cells(self):
        return self.cells


class DataSegment(MemorySegment):
    """Holds program variables."""
    def __init__(self, base_address, bound_address):
        super().__init__(base_address, bound_address)
        self.cells = {}
        self.reserved_addr_for_return = base_address
        self.current_address += WORD_SIZE
    def create_data(self, data_name, data_type, symbol_table, array_size=1, attrs={}):
        # self.cells.append[self.current_address]
        for i in range(array_size):
            data = Data(data_name, data_type, self.current_address, attrs=attrs)
            if i == 0:
                symbol_table[str(data_name)]= data
            self.cells[self.current_address] = data
            self.current_address += data.type_size
    pass


    def create_function(self, func_name, func_type, func_first_line, symbol_table):
        data = Data(func_name, func_type, func_first_line, attrs=None)
        symbol_table[str(func_name)] = data
        return

    def get_data_by_address(self, address):
        return self.cells[address]
    
    def write_at(self, address, data):
        self.cells[address] = data
        return
    
    def get_res(self):
        return self.reserved_addr_for_return
    

class TemporarySegment(MemorySegment):
    def __init__(self, base_address, bound_address):
        super().__init__(base_address, bound_address)
        self.cells = []
    """Holds temporary variables for computation."""
    def allocate_temp(self):
        if self.current_address + MEMORY_BLOCK_SIZE > self.bound_address:
            raise MemoryError("Segment overflow.")
        allocated_address = self.current_address
        self.cells.append(None)
        self.current_address += MEMORY_BLOCK_SIZE
        return allocated_address


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

    def to_string(self):
        op1 = str(self.operands[0]) if self.operands[0] is not None else ""
        op2 = str(self.operands[1]) if self.operands[1] is not None else ""
        op3 = str(self.operands[2]) if self.operands[2] is not None else ""
        
        return f"({self.operation.value}, {op1}, {op2}, {op3})"
