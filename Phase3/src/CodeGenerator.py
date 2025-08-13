from Phase3.src.SemanticStack import SemanticStack
from Phase3.src.Memories import Memory

class CodeGenerator:
    
    def __init__(self, parser) -> None:
        memory = Memory(0, 512, 1000)
        self.parser = parser
        self.semantic_errors = {}
        self.memory = memory
        self.semantic_stack = ss = SemanticStack()
        self.program_block = memory.program_block
        self.data_block = memory.data_block
        self.temp_block = memory.temp_segment
        pass
    
    
    #TODO
    #Phase3
    def push_token_in_semantic_stack(self,token):
        
        pass
    
    def variable_declaration(self,token):
        pass
    
    def array_declaration(self, token):
        pass
    
    def function_declaration(self, token):
        pass
    
    def function_arguements(self,token):
        pass
    
    def function_end(self, token):
        pass
    
    def pointer_declaration(self, token):
        pass
    
    def break_save(self, token):
        pass
    
    def save_index_before_cond_jump(self, token):
        pass
    
    def save_jpf(self, token):
        pass
    
    def uncond_jump(self, token):
        pass
    
    def jump(self, token):
        pass
    
    def while_unconditional_jump(self, token):
        pass
    
    def while_cond_jump(self, token):
        pass
    
    def fill_while(self, token):
        pass
    
    def jump_return(self, token):
        pass
    
    def return_value(self, token):
        pass
    
    def push_id(self, token):
        pass
    
    def print_value(self, token):
        pass
    
    def assignment(self, token):
        pass
    
    def calculate_array_addr(self, token):
        pass
    
    def relative_op(self, token):
        pass
    
    def arithmetic_operation(self, token):
        pass
    
    def multiply(self, token):
        pass
    
    def push_immediate(self, token):
        pass
    
    def args_in_func_call_begin(self, token):
        pass
    
    def args_in_func_call_end(self, token):
        pass
    
    