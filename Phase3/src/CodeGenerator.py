from Phase3.src.SemanticStack import SemanticStack
from Phase3.src.Memories import *

DEBUG_P3 = True
CHECK_ERRORS = True
class CodeGenerator:
    
    def __init__(self, parser) -> None:
        memory = Memory(0, 512, 1000)
        self.parser = parser
        self.memory = memory
        self.semantic_stack = ss = SemanticStack(self)
        self.program_block = memory.code()
        self.data_block = memory.data()
        self.temp_block = memory.temporaries()
        self.semantic_errors = []
        self.scope_stack=[{}]
        self.breaks = {}
        self.scope_number = 0
        self.functions_list = []
        self.in_func = []
        self.action = None
        self.has_error = False
        self.current_function_name = None
        
    def add_function(self, func):
        self.functions_list.append(func)
        self.in_func.append(func.name)
        
    def get_function_by_name(self, name):
        my_func = None
        if DEBUG_P3:
            print("SELF FUNCS:",self.functions_list)
        for f in self.functions_list:
            if DEBUG_P3:
                print("CHECK Functions, name:", "~~~",f.name,"~~~",type, f.type,"looking for", name)
            if str(f.name) == name:
                my_func = f
                break
        return my_func

    
    
    #TODO
    def get_pb(self):
        block = self.program_block.get_cells()
        # print("PB", self.program_block.cells)
        
        result = []
        for address in sorted(block.keys()):
            instruction = block[address]
            # Format: "line_number (OPERATION, operand1, operand2, operand3)"
            result.append(f"{address}\t{instruction.to_string()}")
        
        return "\n".join(result)
        
            
        
    def check_operand_types(self, first_operand, second_operand):
        first_type, second_type = 'int', 'int'
        try:
            first_type = self.data_block.get_data_by_address(first_operand).type
        except (ValueError, KeyError, AttributeError):
            first_type = 'int'

        try:
            second_type = self.data_block.get_data_by_address(second_operand).type
        except (ValueError, KeyError, AttributeError):
            second_type = 'int'

        return first_type, second_type, second_type == first_type
    
    def get_op_type(self, addr):
        if addr.startswith("#"):
            return 'int'
        return self.data_block.get_data_by_address(addr).type
        
       
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
            
            return None, is_implicit_print, True

        # Search from current scope backwards
        is_func = False
        for scope in reversed(self.scope_stack):
            # print(scope)

            if name in scope:
                symbol = scope[name]
                return symbol.address, is_implicit_print, symbol.is_func  # variable or function starting address

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
            self.semantic_stack.push('int')
            self.semantic_stack.push('output')  # Fix: was self.stack
            return
        
        try:
            addr, _ , is_func = self.findaddr(token)
            if DEBUG_P3:
                print("addr", addr,"token", token)
            if is_func:
                self.semantic_stack.push(str(token).strip())
            else:
                self.semantic_stack.push(addr)  # Fix: was self.stack
        except KeyError:
            # Handle undeclared variable error
            if DEBUG_P3:
                print(f"Error: Undeclared variable {token}")
            # For now, push the token itself to prevent crashes
            self.semantic_stack.push(token)
        return
    
    #######################################
    ###                                 ###
    ###          ARITHMETIC OPS         ###
    ###                                 ###
    ####################################### 
    
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
        if DEBUG_P3:
            print("MULT Begin")
            self.semantic_stack.print_info()
            print("MULT End")
        second_operand = self.semantic_stack.pop()
        # operation = self.semantic_stack.pop()

        first_operand = self.semantic_stack.pop()
        
        _, _, matched = self.check_operand_types(first_operand, second_operand)
        
        if matched:
            instruction = ThreeAddressInstruction(TACOperation.MULTIPLY, first_operand, second_operand, tmp)
            self.semantic_stack.push(tmp)
            self.program_block.add_instruction(instruction)
        else:
            #TODO: handle mismatch error
            pass
        
    #TODO: What is this?
    def print_value(self, token):
        if not self.semantic_stack.is_empty() and self.semantic_stack.top(1) == 'output':
            operand = self.semantic_stack.pop()
            #shouldn't it be TACOperation?
            instr = ThreeAddressInstruction(self.semantic_stack.pop(), operand, '', '')
            self.program_block.add_instruction(instr)
        pass
    
    def assignment(self, token):
        if DEBUG_P3:
            print("ASSIGNMENT")
            self.semantic_stack.print_info()
        
        rvalue = self.semantic_stack.pop()
        lvalue = self.semantic_stack.pop() 
        
        instr = ThreeAddressInstruction(TACOperation.ASSIGN, rvalue, '', lvalue)
        self.program_block.add_instruction(instr)
        
        return


    #######################################
    ###                                 ###
    ###           CONDITIONAL           ###
    ###                                 ###
    ####################################### 
    
    def save_index_before_cond_jump(self, token):
        condition_result = self.semantic_stack.pop()  # Get condition result (1000)

        # Reserve space for JPF instruction
        jpf_address = self.program_block.current_address  # Gets 3
        self.program_block.increment_addr()

        # Push in correct order: jpf_address first, then condition_result
        # This way jpf_address will be on top when save_jpf pops
        self.semantic_stack.push(condition_result)  # Push 1000 first (bottom)
        self.semantic_stack.push(jpf_address)       # Push 3 second (top)

        return
    
    #TODO: Check
    #PRBLEM: shouldn't we save scope or change it?
    def save_jpf(self, token):
        if DEBUG_P3:
            print("SAVE_JPF - Stack before popping:")
            self.semantic_stack.print_info()
            
        jpf_address = self.semantic_stack.pop()      
        if DEBUG_P3:
            print(f"Popped jpf_address: {jpf_address} (should be 3)")
            
        condition_result = self.semantic_stack.pop() 
        if DEBUG_P3:
            print(f"Popped condition_result: {condition_result} (should be 1000)")
        
        else_start_address = self.program_block.current_address + 1
        jp_address = self.program_block.current_address
        self.program_block.increment_addr()  # Reserve space for JP

        jpf_instr = ThreeAddressInstruction(TACOperation.JUMP_IF_FALSE, condition_result, else_start_address, '')
        self.program_block.add_instruction(jpf_instr, jpf_address)
        
        self.semantic_stack.push(jp_address)
        
        return
    
    def jump(self, token):
        jp_address = self.semantic_stack.pop()
        end_address = self.program_block.current_address
        jp_instr = ThreeAddressInstruction(TACOperation.JUMP, end_address, '', '')
        self.program_block.add_instruction(jp_instr, jp_address)
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
        
        # Initialize breaks for current scope
        if self.scope_number not in self.breaks:
            self.breaks[self.scope_number] = []
        
        self.open_new_scope()
        return

    def fill_while(self, token):
        uncond_jmp_index = self.program_block.current_address

        # Create conditional jump instruction
        condition_result = self.semantic_stack.top(1)  # Condition result
        cond_jmp_index = self.semantic_stack.top(0)    # Address for conditional jump
        while_start_addr = self.semantic_stack.top(2)  # While loop start address
        
        # Add conditional jump (JPF)
        cond_jmp = ThreeAddressInstruction(TACOperation.JUMP_IF_FALSE, condition_result, uncond_jmp_index + 1, '')
        self.program_block.add_instruction(cond_jmp, cond_jmp_index)

        # Add unconditional jump back to while condition
        uncond_jmp = ThreeAddressInstruction(TACOperation.JUMP, while_start_addr, '', '')
        self.program_block.add_instruction(uncond_jmp)

        # Clean up semantic stack
        self.semantic_stack.pop()  # Remove condition result
        self.semantic_stack.pop()  # Remove jump address
        self.semantic_stack.pop()  # Remove while start address

        # Fill breaks to current pc
        current_scope = self.scope_number
        if current_scope in self.breaks:
            break_instr = ThreeAddressInstruction(TACOperation.JUMP, self.program_block.current_address, '', '')
            for br in self.breaks[current_scope]:
                self.program_block.add_instruction(break_instr, br)
            # Clear breaks for this scope
            del self.breaks[current_scope]
        
        
        current_scope = self.scope_number
        for ind in self.breaks[current_scope]:
            jmp_instr = ThreeAddressInstruction(TACOperation.JUMP, f'{self.program_block.current_address}', '', '')
            self.program_block.add_instruction(jmp_instr,ind)
            
        self.end_scope()
        
        return
    
    def break_save(self, token):
        # Create a jump instruction that will be backpatched later
        jmp_instr = ThreeAddressInstruction(TACOperation.JUMP, '', '', '')
        jmp_index = self.program_block.add_instruction(jmp_instr)
        
        # Add to breaks list for current scope
        current_scope = self.scope_number
        if current_scope not in self.breaks:
            self.breaks[current_scope] = []
        self.breaks[current_scope].append(jmp_index)
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
        mult_instruction = ThreeAddressInstruction(TACOperation.MULTIPLY, '#4', offset, tmp1)
        self.program_block.add_instruction(mult_instruction)
        if str(base).startswith('@'):
            tmp_array_base = self.temp_block.allocate_temp()
            self.program_block.add_instruction(Instruction('ASSIGN', base, tmp_array_base, ''))
            add_instruction = ThreeAddressInstruction(TACOperation.ADD, tmp_array_base, tmp1, tmp2)
        else:
            add_instruction = ThreeAddressInstruction(TACOperation.ADD, '#' + str(base), tmp1, tmp2)
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
            # For main function, we need to jump to its start
            # Reserve address 0 for initial jump to main
            if self.program_block.current_address == 0:
                # Reserve space for jump to main - we'll fill this later
                self.program_block.increment_addr()
            
            # Store main's starting address for later backpatching
            main_start_addr = self.program_block.current_address
            # We'll backpatch address 0 with JP to main_start_addr later
            main_jump = ThreeAddressInstruction(TACOperation.JUMP, main_start_addr, '', '')
            self.program_block.add_instruction(main_jump, 0)  # Backpatch at address 0
            self.program_block.add_instruction(ThreeAddressInstruction(TACOperation.ASSIGN,'', '#0', f'{self.data_block.get_res()}'))
            
        else:
            # Reserve a jump over this function
            skip_addr = self.program_block.current_address
            self.program_block.increment_addr()   # placeholder JP
            func_start = self.program_block.current_address
            
            return_value_address = self.data_block.allocate_cell()
            func = FunctionObject(func_name, func_type, func_start, self.scope_number, return_value_address)
            self.add_function(func)
            self.scope_stack[-1][str(func_name)] = func

            # backpatch jump to after function later in function_end()
            func._skip_addr = skip_addr

        self.open_new_scope()
        self.current_function_name = func_name
        self.semantic_stack.push(func_name)
        self.semantic_stack.push("#arguments")
        if DEBUG_P3:
            print("printing stack after #arguments:")
            self.semantic_stack.print_info()
        
    def push_param_in_ss(self, token):
        self.semantic_stack.push(token)
        pass
    
    def function_arguments(self, token):  # Fix: correct spelling
        # Collect all arguments
        args = []
        if DEBUG_P3:
            print("printing stack before calling top in arguments:")
            self.semantic_stack.print_info()
        
        while (str(self.semantic_stack.top()) != "#arguments"):
            arg_name = self.semantic_stack.pop()
            arg_type = self.semantic_stack.pop()
            arg_addr = self.data_block.allocate_cell()
            arg = FunctionArg(arg_name, arg_addr, arg_type)
            args.append(arg)
            # Add argument to current scope (function scope)
            self.scope_stack[-1][str(arg_name)] = Data(arg_name, arg_type, arg_addr)
        
        self.semantic_stack.pop()  # Remove "#arguments"
        func_name = self.semantic_stack.pop()   
        
        if DEBUG_P3:
            print("my func_name", func_name)  
            print(self.semantic_stack.print_info())       
        
        if func_name != 'main':
            func_obj = self.get_function_by_name(func_name)
            if func_obj:
                # Add all arguments to function
                for arg in reversed(args):  # Reverse to maintain correct order
                    func_obj.add_args(arg)
        return
    
    def return_value(self, token):
        if DEBUG_P3:
            print("return with value")
        return_val = self.semantic_stack.pop()
        rt_inst = ThreeAddressInstruction(TACOperation.ASSIGN, '', f'{return_val}', f'{self.data_block.get_res()}')
        self.program_block.add_instruction(rt_inst)
        ret_addr = self.get_function_by_name(self.current_function_name).return_addr
        ret_jmp_inst = ThreeAddressInstruction(TACOperation.JUMP,f'@{ret_addr}')
        self.program_block.add_instruction(ret_jmp_inst)

        return
    
    def function_end(self, token):
        self.current_function_name = None
        self.end_scope()
        return
    
    def jump_return(self, token):
        if DEBUG_P3:
            print("return inst")
        ret_addr = self.get_function_by_name(self.current_function_name).return_addr
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
            self.semantic_stack.push('array')
        return
   
    

   
        
    def args_in_func_call_begin(self, token):
        if DEBUG_P3:
            print("Reached begining of function arguments")
        func_name = self.semantic_stack.top()
        if func_name == 'output':
            #TODO: handle output implicitly
            self.semantic_stack.push("#call_args")
            return
        else:
            if (self.get_function_by_name(func_name) == None):
                #TODO: Handle undefined function error
                if DEBUG_P3:
                    print("didn't find func name", func_name)
                self.semantic_errors.append(f"{self.parser.get_line()}:Semantic Error! {func_name} is not defined")
                return
            self.semantic_stack.push("#call_args")

            return
            
    
        
    def args_in_func_call_end(self, token):
        args = []
        while (str(self.semantic_stack.top()) != "#call_args"):
            
            if DEBUG_P3:
                self.semantic_stack.print_info()
                print("in while1")
            arg_addr = self.semantic_stack.pop()

            # arg_addr, _ = self.findaddr(arg_name)
            args.append(arg_addr)
        
        if DEBUG_P3:
            print("hereeeee")
            print(args)
            
        args = list(reversed(args))
        self.semantic_stack.pop()
        func_name = self.semantic_stack.pop()
        if DEBUG_P3:
            print("End of Args",func_name)
        if func_name == 'output':
            for arg in args:
                self.program_block.add_instruction(ThreeAddressInstruction(TACOperation.PRINT, f'{arg}'))

            return
        
        if (len(args) != len(self.get_function_by_name(func_name).get_args())):
            
            self.semantic_errors.append( f"#{self.parser.get_line()}: Semantic error! Mismatch in numbers of arguments of {func_name}")
            return 
        func_args = self.get_function_by_name(func_name).get_args()
        if DEBUG_P3:
            print("ARGS in Calling", args)
        for i in range(len(args)):
            matched = self.get_op_type(args[i]) == func_args[i].get_type()
            if DEBUG_P3:
                print("func arg type", func_args[i].get_type())
                print("passed args", args[i])
            if not matched and CHECK_ERRORS:
                if DEBUG_P3:
                    print("error in arg passing")
                self.semantic_errors.append( f"#{self.parser.get_line()}: Semantic Error! Type mismatch in operands, got {args[i]} instead of {func_args[i].get_type()}")
                return

                
            self.program_block.add_instruction(ThreeAddressInstruction(TACOperation.ASSIGN, '', f'{args[i]}', f'{func_args[i].addr}'))
            
        called_func = self.get_function_by_name(func_name)
        # self.get_function_by_name(func_name).set_return_addr(self.program_block.current_address)
        ret_inst_after_call = ThreeAddressInstruction(TACOperation.ASSIGN, f"{self.program_block.current_address + 2}",f"{called_func.get_return_addr()}", '')
        self.program_block.add_instruction(ret_inst_after_call)
        jmp_to_func = ThreeAddressInstruction(TACOperation.JUMP,self.get_function_by_name(func_name).first_line_addr,'','')
        self.program_block.add_instruction(jmp_to_func)
        
        tmp = self.temp_block.allocate_temp()
        self.semantic_stack.push(tmp)
        #Assuming the return value of function is saved in first address of data block
        self.program_block.add_instruction(ThreeAddressInstruction(TACOperation.ASSIGN,'',f'{self.data_block.get_res()}',f'{tmp}'))
        
    def exec_semantic_action(self, action_symbol, token):
        self.action = action_symbol
        if DEBUG_P3:
            print("MY ACTION CALLED:", action_symbol)
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
                self.function_arguments(token)
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
    def __init__(self, name, type, func_addr, func_scope_number, return_addr=None) -> None:
        self.name = name
        self.scope = func_scope_number
        self.first_line_addr = func_addr
        self.address = func_addr  # Add this for findaddr compatibility
        self.return_addr = return_addr
        self.args = []  # Fix: should be list, not dict
        self.type = type
        self.return_val = None
        self.is_func = True

    def add_args(self, arg):  # Fix: single arg parameter
        self.args.append(arg)
        
    def get_args(self):
        return self.args
        
    def set_return_addr(self, address):
        self.return_addr = address  # Fix: was missing assignment
        
    def get_return_addr(self):
        return self.return_addr
    
    def get_addr(self):
        return self.first_line_addr
    
    def set_return_val(self, value):
        self.return_val = value
        
    def get_return_val(self):
        return self.return_val
    
    def is_func(self):
        return True
    
    
    
    
    
    
class FunctionArg:
    def __init__(self, name, addr, type) -> None:
        self.name = name
        self.addr = addr
        self.type = type
        pass
    def get_name(self):
        return self.name
    
    def get_type(self):
        return self.type
    
    