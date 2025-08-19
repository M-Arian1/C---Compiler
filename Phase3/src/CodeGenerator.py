from Phase3.src.SemanticStack import SemanticStack
from Phase3.src.Memories import *

CHECK_ERRORS = False
class CodeGenerator:
    
    def __init__(self, parser) -> None:
        memory = Memory(0, 500, 700)
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
        self.while_scope_number = 0
        self.functions_list = []
        self.in_func = []
        self.action = None
        self.prev_act = None
        self.has_error = False
        self.current_function_name = None
        self.main_back = -1
        
        
    def add_function(self, func):
        
        self.functions_list.append(func)
        self.in_func.append(func.name)
        
    def get_function_by_name(self, name):
        my_func = None
        
        for f in self.functions_list:

            if str(f.name) == name:
                my_func = f
                break
        return my_func

    
    
    #TODO
    def get_pb(self):
        block = self.program_block.get_cells()
        
        #tof
        my_range = []
        for i in range(sorted(block.keys())[-1] + 1):
            my_range.append(0)
        for address in block.keys():
            my_range[address] = 1
        result = []
        for address in range(len(my_range)):
            if my_range[address] == 1:
                instruction = block[address]
                # Format: "line_number (OPERATION, operand1, operand2, operand3)"
                result.append(f"{address}\t{instruction.to_string()}")
            else:
                instruction = ThreeAddressInstruction(TACOperation.JUMP, str(address + 1))
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
    
    # ADD this enhanced get_op_type() method to CodeGenerator class:
    def get_op_type(self, addr):
        """Enhanced operand type checking with better error handling"""
        try:
            # Handle immediate values
            if isinstance(addr, str):
                if addr.startswith('#'):
                    return 'int'  # Immediate values are integers
                elif addr.startswith('@'):
                    # Indirect address - try to get the base type
                    base_addr_str = addr[1:]
                    try:
                        base_addr = int(base_addr_str)
                        data = self.data_block.get_data_by_address(base_addr)
                        return data.type if data else 'int'
                    except (ValueError, KeyError, AttributeError):
                        return 'int'  # Default to int for unknown indirect addresses
            
            # Handle direct addresses
            if isinstance(addr, int):
                data = self.data_block.get_data_by_address(addr)
                return data.type if data else 'int'
            
            # Handle string addresses (should be converted to int)
            if isinstance(addr, str) and addr.isdigit():
                data = self.data_block.get_data_by_address(int(addr))
                return data.type if data else 'int'
            
            # For any other case, default to int
            return 'int'
            
        except (AttributeError, KeyError, ValueError) as e:
            
            return 'int'
        
       
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
        for scope in reversed(self.scope_stack):

            if name in scope:
                symbol = scope[name]
                return symbol.address, is_implicit_print, symbol.is_func  # variable or function starting address

        # If not found
        #TODO: handle the semantic error with line number and etc
        # self.semantic_errors.append()
        raise KeyError(f"Undeclared identifier: {name}")
    
    def find_by_addr(self, addr):
        for scope in reversed(self.scope_stack):
            for name in scope:
                if scope[name].address == int(addr):
                    return scope[name]
        
        
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

            pass
        else:
            #TODO:check for list and dict type later
            self.data_block.create_data(var_name, 'int', self.scope_stack[-1])
        return
        

# REPLACE the push_id() method with this corrected version:
    def push_id(self, token):
        """Handle identifier pushing - treat 'output' as a regular function identifier"""
        try:
            addr, is_implicit_print, is_func = self.findaddr(token)
            
            
            if is_implicit_print:  # This is the 'output' function
                self.semantic_stack.push('output')
            elif is_func:
                self.semantic_stack.push(str(token).strip())
            else:
                self.semantic_stack.push(addr)
                
        except KeyError:
            # Handle undeclared variable error
            
            # Add semantic error
            self.semantic_errors.append(f"#{self.parser.get_line()}: Semantic Error! '{token}' is not defined")
            # For now, push the token itself to prevent crashes
            self.semantic_stack.push(token)
        return
    
    #######################################
    ###                                 ###
    ###          ARITHMETIC OPS         ###
    ###                                 ###
    ####################################### 
    
    def relative_op(self, token):
        self.program_block.add_instruction(ThreeAddressInstruction(TACOperation.ASSIGN,'#0',f"{self.temp_block.current_address}"))
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
        self.program_block.add_instruction(ThreeAddressInstruction(TACOperation.ASSIGN,'#0',f"{self.temp_block.current_address}"))
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
        self.program_block.add_instruction(ThreeAddressInstruction(TACOperation.ASSIGN,'#0',f"{self.temp_block.current_address}"))
        tmp = self.temp_block.allocate_temp()

        
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
            instr = ThreeAddressInstruction(TACOperation.PRINT, operand, '', '')
            self.program_block.add_instruction(instr)
        pass
    
    #######################################
    ###                                 ###
    ###           ASSIGNMENTS           ###
    ###                                 ###
    ####################################### 
    
    def assignment(self, token):
        
        

        rvalue = self.semantic_stack.pop()
        lvalue = self.semantic_stack.pop() 
        
        instr = ThreeAddressInstruction(TACOperation.ASSIGN, rvalue, lvalue)
        self.program_block.add_instruction(instr)
        self.semantic_stack.push(lvalue)
        
        return
        
        return
    def finish_assing_seq(self, token):
        
        if not self.semantic_stack.is_empty() and self.prev_act == "#assign":
            self.semantic_stack.pop()
        if not self.semantic_stack.is_empty() and self.semantic_stack.top(1) == 'output':
            operand = self.semantic_stack.pop()
            instr = ThreeAddressInstruction(self.semantic_stack.pop(), operand, '', '')
            self.program_block.add_instruction(instr)
        
        pass

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
        
        jpf_address = self.semantic_stack.pop()      
        
        condition_result = self.semantic_stack.pop() 
        
        
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
        """Save the address where while condition evaluation starts"""
        # This should be called BEFORE evaluating the while condition
        while_start_addr = self.program_block.current_address
        self.semantic_stack.push(while_start_addr)
        
        # Initialize breaks for current scope
        if self.while_scope_number not in self.breaks:
            self.breaks[self.while_scope_number] = []
        
      
        return

    def while_cond_jump(self, token):
        """Reserve space for conditional jump and open scope for while body"""
        # This should be called AFTER condition evaluation but BEFORE while body
        # At this point, condition result should be on top of semantic stack
        
        # Reserve space for JPF instruction
        jpf_addr = self.program_block.current_address
        self.program_block.increment_addr()  # Reserve the space
        self.semantic_stack.push(jpf_addr)   # Save where JPF will go
        
        # Open new scope for while body
        self.while_scope_number += 1
        self.open_new_scope()
        self.breaks[self.while_scope_number] = []
        
        
        return

    def fill_while(self, token):
        """Fill in the JPF instruction and add jump back to condition"""
        # Stack should contain (from top): jpf_address, condition_result, while_start_address
        
        
        
        # Get addresses from semantic stack
        jpf_addr = self.semantic_stack.pop()          # Where to put JPF
        condition_result = self.semantic_stack.pop()  # Condition evaluation result  
        while_start_addr = self.semantic_stack.pop()  # Where condition evaluation starts
        
        # Current address is where we'll continue after the while loop
        after_while_addr = self.program_block.current_address + 1  # +1 for the JP instruction we're about to add
        
        # Create and backpatch JPF instruction
        # If condition is false, jump to after the while loop
        jpf_instr = ThreeAddressInstruction(TACOperation.JUMP_IF_FALSE, condition_result, after_while_addr, '')
        self.program_block.add_instruction(jpf_instr, jpf_addr)
        
        # Add unconditional jump back to condition evaluation
        jp_back_instr = ThreeAddressInstruction(TACOperation.JUMP, while_start_addr, '', '')
        self.program_block.add_instruction(jp_back_instr)
        
        # Now backpatch all break statements to jump to current address (after the loop)
        current_scope = self.while_scope_number
        if current_scope in self.breaks:
            for break_addr in self.breaks[current_scope]:
                break_instr = ThreeAddressInstruction(TACOperation.JUMP, self.program_block.current_address, '', '')
                self.program_block.add_instruction(break_instr, break_addr)
            # Clear breaks for this scope
            del self.breaks[current_scope]
        
        # Close the while body scope
        self.end_scope()
        self.while_scope_number -= 1
        return
    
    
    def remove_expression_result(self, token):
        
        if self.semantic_stack.sp == 0:
            return
        self.semantic_stack.pop()
        return
    def break_save(self, token):
        break_addr = self.program_block.current_address
        self.program_block.increment_addr()
        
        # FIX: Use while_scope_number instead of scope_number
        current_scope = self.while_scope_number
        
        if current_scope not in self.breaks:
            self.breaks[current_scope] = []
        self.breaks[current_scope].append(break_addr)
        
        
        return
    
    

    #######################################
    ###                                 ###
    ###               ARRAY             ###
    ###                                 ###
    #######################################    
    

    def array_declaration(self, token):
        array_size = int(self.semantic_stack.pop())
        array_name = self.semantic_stack.pop()
        array_type = self.semantic_stack.pop()
        dummy_symbol_table = {}
        array_addr = self.data_block.create_data(array_name, 'array', dummy_symbol_table, int(array_size),
                                    {'array_size': int(array_size)})
        pointer_addr = self.data_block.create_data(array_name,'array',self.scope_stack[-1])
        self.program_block.add_instruction(ThreeAddressInstruction(TACOperation.ASSIGN,f'#{array_addr}', f'{pointer_addr}'))

        return
    

       
    def calculate_array_addr(self, token):
        self.program_block.add_instruction(ThreeAddressInstruction(TACOperation.ASSIGN,'#0',f"{self.temp_block.current_address}"))
        tmp1 = self.temp_block.allocate_temp()
        self.program_block.add_instruction(ThreeAddressInstruction(TACOperation.ASSIGN,'#0',f"{self.temp_block.current_address}"))
        tmp2 = self.temp_block.allocate_temp()
        offset = self.semantic_stack.pop()
        base = self.semantic_stack.pop()
        mult_instruction = ThreeAddressInstruction(TACOperation.MULTIPLY, '#4', offset, tmp1)
        self.program_block.add_instruction(mult_instruction)
        if self.find_by_addr(base).type == 'array' or str(base).startswith('@'):
            self.program_block.add_instruction(ThreeAddressInstruction(TACOperation.ASSIGN,'#0',f"{self.temp_block.current_address}"))
            tmp_array_base = self.temp_block.allocate_temp()
            self.program_block.add_instruction(ThreeAddressInstruction(TACOperation.ASSIGN, base, tmp_array_base, ''))
            add_instruction = ThreeAddressInstruction(TACOperation.ADD, tmp_array_base, tmp1, tmp2)
        else:
            add_instruction = ThreeAddressInstruction(TACOperation.ADD, str(base), tmp1, tmp2)
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
        
        if self.main_back == -1:
            self.main_back = self.program_block.current_address
            self.program_block.increment_addr()
        if str(func_name) == 'main':
        
            main_start_addr = self.program_block.current_address
            # We'll backpatch address 0 with JP to main_start_addr later
            main_jump = ThreeAddressInstruction(TACOperation.JUMP, main_start_addr, '', '')
            self.program_block.add_instruction(main_jump, self.main_back)  # Backpatch at address 0
            self.program_block.add_instruction(ThreeAddressInstruction(TACOperation.ASSIGN,'#0', f'{self.data_block.get_res()}'))
            
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
        
        
    def param_declaration(self, token):
        var_name = self.semantic_stack.pop()
        var_type = self.semantic_stack.pop()
        if var_type == 'void':

            pass
        else:
            #TODO:check for list and dict type later
            self.data_block.create_data(var_name, 'int', self.scope_stack[-1])
            self.semantic_stack.push(var_type)
            self.semantic_stack.push(var_name)
        return
    
        pass
    def push_param_in_ss(self, token):
        self.semantic_stack.push(token)
        pass
    
    def function_arguments(self, token):  # Fix: correct spelling
        # Collect all arguments
        args = []
        
        i = 1
        while (str(self.semantic_stack.top()) != "#arguments"):
            
            i+= 1
            arg_name = self.semantic_stack.pop()
            arg_type = self.semantic_stack.pop()
            
            arg_addr,_,_ = self.findaddr(arg_name)
            
            arg = FunctionArg(arg_name, arg_addr, arg_type)
            args.append(arg)
            # Add argument to current scope (function scope)
        
        self.semantic_stack.pop()  # Remove "#arguments"
        func_name = self.semantic_stack.pop()   
        
        
        
        if func_name != 'main':
            func_obj = self.get_function_by_name(func_name)
            if func_obj:
                # Add all arguments to function
                for arg in reversed(args):  # Reverse to maintain correct order
                    func_obj.add_args(arg)
        return
    
    def return_value(self, token):

        return_val = self.semantic_stack.pop()
        rt_inst = ThreeAddressInstruction(TACOperation.ASSIGN, f'{return_val}', f'{self.data_block.get_res()}')
        self.program_block.add_instruction(rt_inst)
        

        return
    
    def function_end(self, token):
        
        if self.current_function_name == 'main':
            return
        ret_addr = self.get_function_by_name(self.current_function_name).return_addr
        ret_jmp_inst = ThreeAddressInstruction(TACOperation.JUMP,f'@{ret_addr}')
        self.program_block.add_instruction(ret_jmp_inst)
        
        self.current_function_name = None
        self.end_scope()
        return
    
    def jump_return(self, token):
        # return
        
        ret_addr = self.get_function_by_name(self.current_function_name).return_addr
        ret_jmp_inst = ThreeAddressInstruction(TACOperation.JUMP,f'@{ret_addr}')
        self.program_block.add_instruction(ret_jmp_inst)
        return
    
    

        

    
    def pointer_declaration(self, token):
        arg_name = self.semantic_stack.pop()
        data_type = self.semantic_stack.pop()
        if data_type == 'void':
            pass
        else:
            self.data_block.create_data(arg_name, 'array', self.scope_stack[-1])
            self.semantic_stack.push(data_type)
            self.semantic_stack.push(arg_name)
            
        return
   
    

   
        
# REPLACE the args_in_func_call_begin() method with this corrected version:
    def args_in_func_call_begin(self, token):
        """Handle beginning of function call arguments"""

            
        func_name = self.semantic_stack.top()
       
        
        if func_name == 'output':
            # No special handling needed here, just mark argument collection start

            self.semantic_stack.push("#call_args")
            return
        else:
            # Check if the function is defined
            func_obj = self.get_function_by_name(func_name)
            if func_obj is None:
                # Function not found - add semantic error with correct format
                self.semantic_errors.append(f"#{self.parser.get_line()}: Semantic Error! '{func_name}' is not defined")
                # Still push marker to prevent parsing issues
                self.semantic_stack.push("#call_args")
                return
            
            # Function exists, proceed normally
            self.semantic_stack.push("#call_args")
            return
            
    
        
    # REPLACE the args_in_func_call_end() method with this completely rewritten version:
    def args_in_func_call_end(self, token):
        """Handle end of function call arguments - generate appropriate instructions"""
        # Collect all arguments from the stack
        args = []
        while str(self.semantic_stack.top()) != "#call_args":

            arg_addr = self.semantic_stack.pop()
            args.append(arg_addr)
        
        # Remove the "#call_args" marker
        self.semantic_stack.pop()
        
        # Get the function name
        func_name = self.semantic_stack.pop()

        
        # Reverse args to get correct order (last pushed = first argument)
        args = list(reversed(args))
        
        # Handle 'output' function specially (implicitly defined)
        if func_name == 'output':
            # Validate argument count for output function
            if len(args) != 1:
                self.semantic_errors.append(f"#{self.parser.get_line()}: Semantic error! Mismatch in numbers of arguments of 'output'")
                return
            
            # Validate argument type (should be int)
            arg = args[0]
            try:
                arg_type = self.get_op_type(arg) if not str(arg).startswith('#') else 'int'
                if arg_type != 'int' and CHECK_ERRORS:
                    self.semantic_errors.append(f"#{self.parser.get_line()}: Semantic Error! Mismatch in type of argument 1 for 'output'. Expected 'int' but got '{arg_type}' instead")
                    return
            except (AttributeError, KeyError):
                # If we can't determine type, assume it's correct
                pass
            
            # Generate PRINT instruction with correct format
            print_instr = ThreeAddressInstruction(TACOperation.PRINT, arg, '', '')
            self.program_block.add_instruction(print_instr)
            

            self.semantic_stack.push(arg)
            # output function doesn't return a value that can be used in expressions
            # So we don't push anything back on the semantic stack
            return
        
        # Handle user-defined functions
        func_obj = self.get_function_by_name(func_name)
        if func_obj is None:
            # Error already reported in args_in_func_call_begin, just return

            return
        
        # Validate argument count
        expected_args = func_obj.get_args()

        if len(args) != len(expected_args):
            self.semantic_errors.append(f"#{self.parser.get_line()}: Semantic error! Mismatch in numbers of arguments of '{func_name}'")
            
            return
        
        # Validate argument types and generate assignment instructions
        for i in range(len(args)):
            arg = args[i]
            expected_arg = expected_args[i]
            assign_instr = ThreeAddressInstruction(TACOperation.ASSIGN, arg, expected_arg.get_addr(), '')
            self.program_block.add_instruction(assign_instr)
        
        # Set up return address
        return_addr_temp = func_obj.get_return_addr()
        return_addr_instr = ThreeAddressInstruction(TACOperation.ASSIGN, f'#{self.program_block.current_address + 2}', f"{return_addr_temp}", '')
        self.program_block.add_instruction(return_addr_instr)
        func_obj.set_return_addr(return_addr_temp)
        
        # Generate jump to function
        jump_instr = ThreeAddressInstruction(TACOperation.JUMP, func_obj.get_addr(), '', '')
        self.program_block.add_instruction(jump_instr)
        
        # Prepare to receive return value
        self.program_block.add_instruction(ThreeAddressInstruction(TACOperation.ASSIGN,'#0',f"{self.temp_block.current_address}"))
        result_temp = self.temp_block.allocate_temp()
        self.semantic_stack.push(result_temp)
        
        # Generate instruction to copy return value
        return_val_instr = ThreeAddressInstruction(TACOperation.ASSIGN, self.data_block.get_res(), result_temp, '')
        self.program_block.add_instruction(return_val_instr)
        



    def exec_semantic_action(self, action_symbol, token):
        self.prev_act = self.action
        self.action = action_symbol
        
        action_str = str(action_symbol)
        if action_str == "#push_in_semantic_stack":
            self.push_token_in_semantic_stack(token)
        elif action_str == "#var_declare":
            self.variable_declaration(token)
        elif action_str == "#arr_declare":
            self.array_declaration(token)
        elif action_str == "#func_declare":
            self.function_declaration(token)
        elif action_str == "#args_info":
            self.function_arguments(token)
        elif action_str == "#fun_end":
            self.function_end(token)
        elif action_str == "#ptr_declare":
            self.pointer_declaration(token)
        elif action_str == "#br_save":
            self.break_save(token)
        elif action_str == "#save_cond":
            self.save_index_before_cond_jump(token)
        elif action_str == "#save_jpf":
            self.save_jpf(token)
        elif action_str == "#jp":
            self.jump(token)
        elif action_str == "#save_while_uncond":
            self.while_save(token)
        elif action_str == "#save_while_cond_jpf":
            self.while_cond_jump(token)
        elif action_str == "#fill_while_body":
            self.fill_while(token)
        elif action_str == "#remove_exp_result":
            self.remove_expression_result(token)
        elif action_str == "#return_jp":
            self.jump_return(token)
        elif action_str == "#save_return_value":
            self.return_value(token)
        elif action_str == "#pid":
            self.push_id(token)
        elif action_str == "#print":
            self.print_value(token)
        elif action_str == "#assign":
            self.assignment(token)
        elif action_str == "#array_addr":
            self.calculate_array_addr(token)
        elif action_str == "#relation":
            self.relative_op(token)
        elif action_str == "#arithm_op":
            self.arithmetic_operation(token)
        elif action_str == "#mult":
            self.multiply(token)
        elif action_str == "#push_imm_in_semantic_stack":
            self.push_immediate(token)
        elif action_str == "#args_begin":
            self.args_in_func_call_begin(token)
        elif action_str == "#args_end":
            self.args_in_func_call_end(token)
        elif action_str == "#push_param_in_semantic_stack":
            self.push_param_in_ss(token)
        elif action_str == "#param_declare":
            self.param_declaration(token)
        elif action_str == "#finish_assign_seq":
            self.finish_assing_seq(token)
        else:
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
    def get_args_len(self):
        cnt = 0
        for a in self.args:
            cnt += 1
        return cnt
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
    
    def get_addr(self):
        return self.addr
    
    