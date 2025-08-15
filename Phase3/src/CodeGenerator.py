from Phase3.src.SemanticStack import SemanticStack
from Phase3.src.Memories import *
class CodeGenerator:
    
    def __init__(self, parser) -> None:
        memory = Memory(0, 512, 1000)
        self.parser = parser
        self.memory = memory
        self.semantic_stack = ss = SemanticStack()
        self.program_block = memory.program_block
        self.data_block = memory.data_block
        self.temp_block = memory.temp_segment
        self.semantic_errors = {}
        self.scope_stack=[{}]
        self.breaks = {}
    
    
    #TODO
    def check_operand_types(self, first_operand, second_operand):
        first_type,second_type = 'int', 'int'
        try:
            first_type = self.data_block.get_data_by_address(first_operand).type
        except (ValueError, KeyError, AttributeError):
            first_type = 'int'

        try:
            second_type = self.data_block.get_data_by_address(second_operand).type
        except (ValueError, KeyError, AttributeError):
            second_type = 'int'

        return first_type, second_type, True
        
        
        
    def findaddr(self, name):
        """
        Look for 'name' starting from current scope backwards.
        Works for variables, arrays, pointers, and functions.
        Special-case: 'output' returns PRINT keyword.
        """
        is_implicit_print = False
        # Special built-in
        if name == "output":
            is_implicit_print = True
            
            return None, is_implicit_print

        # Search from current scope backwards
        for scope in reversed(self.scope_stack):
            # print(scope)
            if name in scope:
                symbol = scope[name]
                return symbol.address, is_implicit_print  # variable or function starting address

        # If not found
        #TODO: handle the semantic error with line number and etc
        # self.semantic_errors.append()
        raise KeyError(f"Undeclared identifier: {name}")
        
    
    
    #Phase3
    def push_token_in_semantic_stack(self,token):
        self.semantic_stack.push(token)
        return
    
    def push_immediate(self, token):
        self.semantic_stack.push(f'#{token}')
        return
    
    def variable_declaration(self,token):
        var_name = self.semantic_stack.pop()
        var_type = self.semantic_stack.pop()
        if var_type == 'void':
            # self.semantic_errors[int(self.parser.scanner.get_line_number()) - 1] = \
            #     "Semantic Error! Illegal type of void for '" + var_name + "'"
            # self.memory.PB.has_error = True
            pass
        else:
            #TODO:check for list and dict type later
            # print(self.scope_stack[-1].__class__)
            self.data_block.create_data(var_name, 'int', self.scope_stack[-1])
        return
        
    def push_id(self, token):
        if self.token == 'output':
            self.stack.push('PRINT')
            return
        #TODO: handle the semantic error differently
        
        addr = self.findaddr(token)
        self.semantic_stack.push(addr)
        return
    
    def array_declaration(self, token):
        array_size = self.semantic_stack.pop()
        array_name = self.semantic_stack.pop()
        self.data_block.create_data(array_name, 'array', self.scope_stack[-1], int(array_size),
                                    {'array_size': int(array_size)})
        return
    
    #when one of function arguemnts is an array
    def pointer_declaration(self, token):
        arg_name = self.semantic_stack.pop()
        data_type = self.semantic_stack.pop()
        if data_type == 'void':
            #TODO: Handle error
            # self.semantic_errors[int(self.parser.scanner.get_line_number()) - 1] = \
            #     "Semantic Error! Illegal type of void for '" + name + "'"
            # self.memory.PB.has_error = True
            pass
        else:
            self.data_block.create_data(arg_name, 'array', self.scope_stack[-1])
        return
    
    def relative_op(self, token):
        tmp = self.temp_block.allocate_temp()
        second_operand, operation, first_operand = self.semantic_stack.pop(3)
        if str(operation) == '==':
            op = TACOperation.EQUAL
        elif str(operation) == '<':
            op = TACOperation.LESS_THAN
        else:
            #TODO: if the operation was none of the above
            pass
        first_op_type, second_op_type, matched = self.check_operand_types(first_operand, second_operand)
        
        if matched:
            instruction = ThreeAddressInstruction(op, first_operand, second_operand, tmp)
            self.semantic_stack.push(tmp)
            self.program_block.add_instruction(instruction)
        else:
            #TODO: handle mismatch error
            pass
        
        
    
    def arithmetic_operation(self, token):
        
        tmp = self.temp_block.allocate_temp()
        second_operand, operation, first_operand = self.semantic_stack.pop(3)
        if str(operation) == '+':
            op = TACOperation.ADD
        elif str(operation) == '-':
            op = TACOperation.SUBTRACT
        else:
            #TODO: if the operation was none of the above
            pass
        first_op_type, second_op_type, matched = self.check_operand_types(first_operand, second_operand)
        
        if matched:
            instruction = ThreeAddressInstruction(op, first_operand, second_operand, tmp)
            self.semantic_stack.push(tmp)
            self.program_block.add_instruction(instruction)
        else:
            #TODO: handle mismatch error
            pass
        
    
    def multiply(self, token):
        
        tmp = self.temp_block.allocate_temp()
        second_operand, operation, first_operand = self.semantic_stack.pop(3)
        _, _, matched = self.check_operand_types(first_operand, second_operand)
        
        if matched:
            instruction = ThreeAddressInstruction(TACOperation.MULTIPLY, first_operand, second_operand, tmp)
            self.semantic_stack.push(tmp)
            self.program_block.add_instruction(instruction)
        else:
            #TODO: handle mismatch error
            pass
    
    
    def print_value(self, token):
        if not self.semantic_stack.is_empty() and self.semantic_stack.top(1) == 'PRINT':
            operand = self.semantic_stack.pop()
            #shouldn't it be TACOperation?
            instr = Instruction(self.semantic_stack.pop(), operand, '', '')
            self.program_block.add_instruction(instr)
        pass
    
    def assignment(self, token):
        instr = Instruction(TACOperation.ASSIGN, self.semantic_stack.pop(), self.semantic_stack.top(), '')
        self.program_block.add_instruction(instr)
        return

    #######################################
    ###                                 ###
    ###           CONDITIONAL           ###
    ###                                 ###
    ####################################### 
    
    def save_index_before_cond_jump(self, token):
        index = self.program_block.current_address
        self.semantic_stack.push(index)
        self.program_block.increment_addr()
        return
    
    #TODO: Check
    #PRBLEM: shouldn't we save scope or change it?
    def save_jpf(self, token):
        jpf_index = self.semantic_stack.pop()
        condition_result = self.semantic_stack.pop()

        # Backpatch JPF at the reserved spot
        instr = Instruction(TACOperation.JUMP_IF_FALSE, condition_result, '', self.program_block.current_address + 1)
        self.program_block.add_instruction(instr, jpf_index)

        # Reserve spot for unconditional JP to skip the else
        jp_index = self.program_block.current_address
        self.program_block.increment_addr()
        
        # Push JP index for later backpatching
        self.semantic_stack.push(jp_index)
        return
    
    def jump(self, token):
        jp_index = self.semantic_stack.pop()
        instr = Instruction(TACOperation.JUMP, '', '', self.program_block.current_address)
        self.program_block.add_instruction(instr, jp_index)
        return
    
    
    
    #######################################
    ###                                 ###
    ###         WHILE     ACTIONS       ###
    ###                                 ###
    #######################################
    def while_unconditional_jump(self, token):
        pass
    
    def while_cond_jump(self, token):
        pass
    
    def fill_while(self, token):
        pass
    
    def break_save(self, token):
        
        pass
    
    

    #######################################
    ###                                 ###
    ###               ARRAY             ###
    ###                                 ###
    #######################################    
    
    
    def calculate_array_addr(self, token):
        
        pass


    #######################################
    ###                                 ###
    ###     FUNCTION RELATED ACTIONS    ###
    ###                                 ###
    #######################################
    def args_in_func_call_begin(self, token):
        pass
    
    def args_in_func_call_end(self, token):
        pass
    
    def function_declaration(self, token):
        
        pass
    
    def function_arguements(self,token):
        pass
    
    def function_end(self, token):
        pass
    
    def jump_return(self, token):
        pass
    
    def return_value(self, token):
        pass
    