from Phase3.src.SemanticStack import SemanticStack
from Phase3.src.Memories import *

DEBUG_P3 = True
class CodeGenerator:
    
    def __init__(self, parser) -> None:
        memory = Memory(0, 512, 1000)
        self.parser = parser
        self.memory = memory
        self.semantic_stack = ss = SemanticStack(self)
        self.program_block = memory.code()
        self.data_block = memory.data()
        self.temp_block = memory.temporaries()
        self.semantic_errors = {}
        self.scope_stack=[{}]
        self.breaks = {}
        self.scope_number = 0
        self.functions_list = []
        self.in_func = []
        self.action = None
        
    def add_function(self, func):
        self.functions_list.append(func)
        self.in_func.append(func.name)
        
    def get_function_by_name(self, name):
        my_func = None
        for f in self.functions_list:
            if str(f.name) == name:
                my_func = f
        return my_func

    
    
    #TODO
    def get_pb(self):
        block = self.program_block.get_cells()
        print("PB", self.program_block.cells)
        
        result = []
        for address in sorted(block.keys()):
            instruction = block[address]
            # Format: "line_number (OPERATION, operand1, operand2, operand3)"
            result.append(f"{address}\t{instruction.to_string()}")
        
        return "\n".join(result)
        
            
        
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
        
        
    def open_new_scope(self):
        # Push a new, empty dictionary onto the scope stack
        self.scope_stack.append({})
        self.scope_number += 1
 
        
    def end_scope(self):
        # Pop the current scope
        self.scope_stack.pop()
        self.scope_number -= 1

    
    
    #PHASE 3
    def push_token_in_semantic_stack(self, token):
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
        if token == 'output':
            self.stack.push('PRINT')
            return
        #TODO: handle the semantic error differently
        
        addr, _ = self.findaddr(token)
        if DEBUG_P3:
            print("addr", addr)
        self.semantic_stack.push(addr)
        return
     
    def relative_op(self, token):
        tmp = self.temp_block.allocate_temp()
        second_operand = self.semantic_stack.pop()
        operation       = self.semantic_stack.pop()
        first_operand = self.semantic_stack.pop()
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
        second_operand = self.semantic_stack.pop()
        operation = self.semantic_stack.pop()
        first_operand = self.semantic_stack.pop()
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
        second_operand = self.semantic_stack.pop()
        operation = self.semantic_stack.pop()
        first_operand = self.semantic_stack.pop()
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
            instr = ThreeAddressInstruction(self.semantic_stack.pop(), operand, '', '')
            self.program_block.add_instruction(instr)
        pass
    
    def assignment(self, token):
        instr = ThreeAddressInstruction(TACOperation.ASSIGN, self.semantic_stack.pop(), self.semantic_stack.top(), '')
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
    def while_save(self, token):
        addr = self.program_block.current_address
        self.semantic_stack.push(addr)
        return
    
    def while_cond_jump(self, token):
        addr = self.program_block.current_address
        self.semantic_stack.push(addr)
        self.program_block.increment_addr()

        self.open_new_scope()
        return
    
    def fill_while(self, token):
        uncond_jmp_index = self.program_block.current_address


        cond_jmp = Instruction(TACOperation.JUMP_IF_FALSE, self.semantic_stack.top(1), uncond_jmp_index + 1)
        cond_jmp_index = self.stack.top(0)
        self.program_block.add_instruction(cond_jmp, cond_jmp_index)

        uncond_jmp = Instruction(TACOperation.JUMP, self.semantic_stack.top(2))
        self.program_block.add_instruction(uncond_jmp)

        self.semantic_stack.pop(3)

        # fill breaks to current pc (no valid breaks except in while => #fill_break moved here and combined with #fill_while)
        break_instr = Instruction(TACOperation.JUMP, self.program_block.current_address)
        for br in self.breaks[self.scope]:
            self.program_block.add_instruction(break_instr, br)
        self.end_scope()
        return
    
    def break_save(self, token):
        jmp_index = self.program_block.add_instruction(Instruction(TACOperation.JUMP, "", "", ""))
        self.breaks[self.scope].append(jmp_index)
        return
    
    

    #######################################
    ###                                 ###
    ###               ARRAY             ###
    ###                                 ###
    #######################################    
    

    def array_declaration(self, token):
        array_size = self.semantic_stack.pop()
        array_name = self.semantic_stack.pop()
        self.data_block.create_data(array_name, 'array', self.scope_stack[-1], int(array_size),
                                    {'array_size': int(array_size)})
        return
    
        #when one of function arguemnts is an array

       
    def calculate_array_addr(self, token):
        tmp1 = self.temp_block.allocate_temp()
        tmp2 = self.temp_block.allocate_temp()
        offset = self.semantic_stack.pop()
        base = self.semantic_stack.pop()
        mult_instruction = Instruction(TACOperation.MULTIPLY, '#4', offset, tmp1)
        self.program_block.add_instruction(mult_instruction)
        if str(base).startswith('@'):
            tmp_array_base = self.temp_block.allocate_temp()
            self.program_block.add_instruction(Instruction('ASSIGN', base, tmp_array_base, ''))
            add_instruction = Instruction(TACOperation.ADD, tmp_array_base, tmp1, tmp2)
        else:
            add_instruction = Instruction(TACOperation.ADD, '#' + str(base), tmp1, tmp2)
        self.program_block.add_instruction(add_instruction)
        self.semantic_stack.push('@' + str(tmp2))
        pass
    
    
    
    


    #######################################
    ###                                 ###
    ###     FUNCTION RELATED ACTIONS    ###
    ###                                 ###
    #######################################
    def function_declaration(self, token):
        func_name = self.semantic_stack.pop()
        func_type = self.semantic_stack.pop()
        if DEBUG_P3:
            print("func name in func declaration:", func_name)
        if str(func_name) == 'main':
            #reserve some memory for main using push immediate and whatever, 
            # but before that, check the base address of data or program block
            instr = ThreeAddressInstruction(TACOperation.ASSIGN,'','#0', '0')
            self.program_block.add_instruction(instr)
            main_instr = ThreeAddressInstruction(TACOperation.JUMP, self.program_block.current_address)
            self.program_block.add_instruction(main_instr)
            
        
        else:
            first_line_addr = self.program_block.current_address
            # func_data = Data("",)
            
            return_value_address = self.data_block.allocate_cell
            func = FunctionObject(func_name,func_type, first_line_addr, self.scope_number, return_value_address )
            self.add_function(func)
            pass

        self.open_new_scope()
        self.semantic_stack.push(func_name)
        self.semantic_stack.push("#arguments")
        if DEBUG_P3:
            print("printing stack after #arguments:")
            self.semantic_stack.print_info()
        pass
        
    def push_param_in_ss(self, token):
        self.semantic_stack.push(token)
        pass
    
    def function_arguements(self,token):
        #for args_info
        args = []
        if DEBUG_P3:
            print("printing stack before calling top in arguments:")
            self.semantic_stack.print_info()
        while (str(self.semantic_stack.top()) != "#arguments"):
            arg_name = self.semantic_stack.pop()
            arg_type = self.semantic_stack.pop()
            arg_addr = self.data_block.allocate_cell
            arg = FunctionArg(arg_name, arg_addr, arg_type)
            args.append(arg)
        self.semantic_stack.pop()
        func_name = self.semantic_stack.pop()   
        if DEBUG_P3:
            print("my func_name",func_name)  
            print(self.semantic_stack.print_info())       
        if func_name != 'main':
            self.get_function_by_name(func_name).add_args(arg)

        pass
    
    def return_value(self, token):
        return_val = self.semantic_stack.pop()
        rt_inst = ThreeAddressInstruction(TACOperation.ASSIGN, '','0', return_val)
        self.program_block.add_instruction(rt_inst)
        return
    
    def function_end(self, token):
        self.current_function_name = None
        self.end_scope()
        return
    
    def jump_return(self, token):
        ret_addr = self.get_function_by_name(self.current_function_name).re
        ret_jmp_inst = ThreeAddressInstruction(TACOperation.JUMP,f'@{ret_addr}')
        self.program_block.add_instruction(ret_jmp_inst)
        return
    
    

        

    
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
            self.semantic_stack.push(arg_name)
            self.semantic_stack.push(data_type)
        return
   
    

   
        
    def args_in_func_call_begin(self, token):
        func_name = self.semantic_stack.top()
        if func_name == 'PRINT':
            #TODO: handle output implicitly
            
            return
        else:
            if (self.get_function_by_name(func_name) == None):
                #TODO: Handle undefined function error
                return
            self.semantic_stack.push("#call_args")

            return
            
    
        
    def args_in_func_call_end(self, token):
        args = []
        while (str(self.semantic_stack.top()) != "#call_args"):
            arg_name = self.semantic_stack.pop()
            self.semantic_stack.pop()
            arg_addr, _ = self.findaddr(arg_name)
            args.append(arg_addr)
            
        args = reversed(args)
        self.semantic_stack.pop()
        func_name = self.semantic_stack.pop()
        if func_name == 'PRINT':
            for arg in args:
                self.program_block.add_instruction(ThreeAddressInstruction(TACOperation.PRINT, f'{arg}'))

            return
        if (len(args) != len(self.get_function_by_name(func_name).get_args())):
            raise "semantic error! Mismatch in numbers of arguments of ID"
        func_args = self.get_function_by_name(func_name).get_args()
        for i in len(args):
            self.program_block.add_instruction(ThreeAddressInstruction(TACOperation.ASSIGN, '', f'@{args[i]}', f'{func_args[i]}'))
            
        self.get_function_by_name(func_name).set_return_addr(self.program_block.current_address)
        
    def exec_semantic_action(self, action_symbol, token):
        self.action = action_symbol
        match str(action_symbol):
            case "#push_in_semantic_stack":
                self.push_token_in_semantic_stack(token)
            case "#var_declare":
                self.variable_declaration(token)
            case "#arr_declare":
                self.array_declaration(token)
            case "#func_declare":
                self.function_declaration(token)
            case "#args_info":
                self.function_arguements(token)
            case "#fun_end":
                self.function_end(token)
            case "#ptr_declare":
                self.pointer_declaration(token)
            case "#br_save":
                self.break_save(token)
            case "#save_cond":
                self.save_index_before_cond_jump(token)
            case "#save_jpf":
                self.save_jpf(token)
            case "#jp":
                self.jump(token)
            case "#save_while_uncond":
                self.while_save(token)
            case "#save_while_cond_jpf":
                self.while_cond_jump(token)
            case "#fill_while_body":
                self.fill_while(token)
            case "#return_jp":
                self.jump_return(token)
            case "#save_return_value":
                self.return_value(token)
            case "#pid":
                self.push_id(token)
            case "#print":
                self.print_value(token)
            case "#assign":
                self.assignment(token)
            case "#array_addr":
                self.calculate_array_addr(token)
            case "#relation":
                self.relative_op(token)
            case "#arithm_op":
                self.arithmetic_operation(token)
            case "#mult":
                self.multiply(token)
            case "#push_imm_in_semantic_stack":
                self.push_immediate(token)
            case "#args_begin":
                self.args_in_func_call_begin(token)
            case "#args_end":
                self.args_in_func_call_end(token)
            case "#push_param_in_semantic_stack":
                self.push_param_in_ss(token)
            case _:
                raise ValueError(f"Unknown semantic action: {action_symbol}")
        
    

class FunctionObject:
    def __init__(self, name, type, func_addr, func_scope_number, return_addr= None) -> None:
        self.name = name
        self.scope = func_scope_number
        self.first_line_addr = func_addr
        #return addr is where we write where we should jump at the end of the function
        self.return_addr = return_addr
        self.args = {}
        self.type = type
        self.return_val = None

        pass
    def add_args(self, args):
        for arg in args:    
            self.args.append(arg)
        
    def get_args(self):
        return self.args
    
        
    def set_return_addr(self, address):
        self.return_addr
        
    def get_return_addr(self):
        return self.return_addr
    
    def get_addr(self):
        return self.first_line_addr
    
    def set_return_val(self, value):
        self.return_val = value
        
    def get_return_val(self):
        return self.return_val
    
    
    
    
    
    
class FunctionArg:
    def __init__(self, name, addr, type) -> None:
        self.name = name
        self.addr = addr
        self.type = type
        pass
    
    