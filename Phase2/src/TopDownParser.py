from enum import Enum
from Phase1.src.Tokens import Token
from Phase3.src.CodeGenerator import CodeGenerator
from Phase3.src.SemanticStack import SemanticStack

class EdgeType(Enum):
    TERMINAL = 'TERMINAL'
    NON_TERMINAL = 'NON_TERMINAL'
    EPSILON = 'EPSILON'
    ACTION_SYMBOL = 'ACTION_SYMBOL'


class ParserEdge:
    def __init__(self, source, target, symbol, edge_type):
        self.source = source
        self.target = target
        self.symbol = symbol
        self.edge_type = edge_type


class ParserState:
    def __init__(self, id, is_final=False):
        self.id = id
        self.is_final = is_final
        self.edges = []

    def add_edge(self, symbol, target, edge_type):
        self.edges.append(ParserEdge(self, target, symbol, edge_type))


class ParserDiagram:
    def __init__(self, name):
        self.name = name
        self.states = []
        self.start_state = None
        self.final_states = []

    def add_state(self, state):
        if self.start_state is None:
            self.start_state = state
        self.states.append(state)
        if state.is_final:
            self.final_states.append(state)


class DiagramParser:

    def __init__(self, grammar, diagrams, scanner):
        self.grammar = grammar
        self.diagrams = diagrams
        self.scanner = scanner
        self.current_state, self.current_token, self.current_line_number = self.scanner.get_next_token()
        self.return_stack = []
        self.parse_tree = None
        self.current_node = None
        self.error_log = open('syntax_errors.txt', 'w')
        self.error_messages = []
        self.type = None
        self.unexpected_eof_flag = False
        self.missing_end_detected = False
        self.code_generator = code_generator = CodeGenerator(self)
        self.semantic_actions={
            "#push_in_semantic_stack" :         code_generator.push_token_in_semantic_stack,
            "#var_declare":                     code_generator.variable_declaration,
            "#arr_declare":                     code_generator.array_declaration,
            "#func_declare":                    code_generator.function_declaration,
            "#args_info":                       code_generator.function_arguements,
            "fun_end":                          code_generator.function_end,
            "#ptr_declare":                     code_generator.pointer_declaration,
            "#br_save":                         code_generator.break_save,
            "#save_cond":                       code_generator.save_index_before_cond_jump,
            "#save_jpf":                        code_generator.save_jpf,
            "#jp":                              code_generator.jump,
            "#save_while_uncond":               code_generator.while_unconditional_jump,
            "#save_while_cond_jpf":             code_generator.while_cond_jump,
            "#fill_while_body":                 code_generator.fill_while,
            "#return_jp":                       code_generator.jump_return,
            "#save_return_value":               code_generator.return_value,
            "#pid":                             code_generator.push_id,
            "#print":                           code_generator.print_value,
            "#assign":                          code_generator.assignment,
            "#array_addr":                      code_generator.calculate_array_addr,
            "#relation":                        code_generator.relative_op,
            "#arithm_op":                       code_generator.arithmetic_operation,
            "#mult":                            code_generator.multiply,
            "##push_imm_in_semantic_stack":     code_generator.push_immediate,
            "#args_begin":                      code_generator.args_in_func_call_begin,
            "#args_end":                        code_generator.args_in_func_call_end
        }

    def log_error(self, message):
        error_msg = f"#{self.current_line_number} : syntax error, {message}\n"
        print(f"\n[DEBUG] Logging error: {error_msg}")
        self.error_messages.append(error_msg)

    def match_token_to_symbol(self, symbol):
        print(f"\n[DEBUG] Matching token: '{self.current_token}' against symbol: '{symbol}'")
        if str(symbol) == "KEYWORD":
            result = self.current_state.type[1].value == Token.KEYWORD.value
            print(f"[DEBUG] KEYWORD match result: {result}")
            return result
        if str(symbol) == "ID":
            result = self.current_state.type[1].value == Token.ID.value
            print(f"[DEBUG] ID match result: {result}")
            return result
        if str(symbol) == "NUM":
            result = self.current_state.type[1].value == Token.NUM.value
            print(f"[DEBUG] NUM match result: {result}")
            return result
        result = str(self.current_token) == str(symbol)
        print(f"[DEBUG] Direct symbol match result: {result}")
        return result

    def check_in_set(self, set):
        print(f"\n[DEBUG] === Checking Token in Set ===")
        print(f"[DEBUG] Current token: '{self.current_token}'")
        print(f"[DEBUG] Checking against set: {set}")
        
        for p in set:
            print(f"[DEBUG] Checking against element: '{p}'")
            if self.match_token_to_symbol(p):
                print(f"[DEBUG] ✓ Found match with '{p}'")
                return True
                
        print(f"[DEBUG] ✗ No matches found in set")
        return False

    def match(self, terminal):
        print(f"\n[DEBUG] === Match Operation ===")
        print(f"[DEBUG] Attempting to match terminal: '{terminal}'")
        print(f"[DEBUG] Current token: '{self.current_token}' at line {self.current_line_number}")
        print(f"[DEBUG] Current state type: {self.current_state.type if hasattr(self.current_state, 'type') else 'N/A'}")
        
        if self.match_token_to_symbol(terminal):
            matched = self.current_token
            print(f"[DEBUG] ✓ Match successful! Token: '{matched}'")
            self.current_state, self.current_token, self.current_line_number = self.scanner.get_next_token()
            print(f"[DEBUG] Next token: '{self.current_token}' at line {self.current_line_number}")
            return matched
        else:
            print(f"[DEBUG] ✗ Match failed! Expected: '{terminal}'")
            self.log_error(f"missing {terminal}")
            return None

    def parse(self, start_symbol):
        from Phase2.src.TreeHandler import ParseNode
        print(f"\n[DEBUG] ========================================")
        print(f"[DEBUG] Starting Parse Process")
        print(f"[DEBUG] Start Symbol: '{start_symbol}'")
        print(f"[DEBUG] Available Diagrams: {list(self.diagrams.keys())}")
        print(f"[DEBUG] ========================================")
        
        start_diagram = self.diagrams[start_symbol]
        print(f"[DEBUG] Creating parse tree with root: '{start_symbol}'")
        self.parse_tree = ParseNode(start_symbol)
        self.current_node = self.parse_tree
        
        print(f"[DEBUG] Beginning diagram execution for '{start_symbol}'")
        self.execute_diagram(start_symbol, start_diagram)

        if self.current_token != '$':
            print(f"[DEBUG] Adding end marker '$' to parse tree")
            terminal_node = ParseNode('$', '$')
            self.current_node.add_child(terminal_node)
        else:
            print(f"[DEBUG] Parse completed successfully with proper end marker")

        print(f"\n[DEBUG] Writing error log...")
        with self.error_log as f:
            if self.error_messages:
                print(f"[DEBUG] Found {len(self.error_messages)} syntax errors")
                f.write("".join(self.error_messages))
            else:
                print(f"[DEBUG] No syntax errors found")
                f.write("There is no syntax error.\n")

        self.error_log.close()
        print(f"[DEBUG] Parse process complete")
        print(f"[DEBUG] ========================================\n")
        return self.parse_tree

    def execute_semantic_action(self, action_symbol):
        """Execute the semantic action associated with the action symbol"""
        action_name = str(action_symbol)
        print(f"[DEBUG] Executing semantic action: {action_name}")
        
        if action_name in self.semantic_actions:
            try:
                # Call the semantic action with the current token
                self.semantic_actions[action_name](self.current_token)
                print(f"[DEBUG] Successfully executed semantic action: {action_name}")
            except Exception as e:
                print(f"[DEBUG] Error executing semantic action {action_name}: {e}")
        else:
            print(f"[DEBUG] Warning: Semantic action {action_name} not found in semantic_actions")

    def execute_diagram(self, diagram_name, diagram):
        from Phase2.src.TreeHandler import ParseNode
        print(f"\n[DEBUG] ============================================")
        print(f"[DEBUG] Executing Diagram: '{diagram_name}'")
        print(f"[DEBUG] Number of states in diagram: {len(diagram.states)}")
        print(f"[DEBUG] Number of final states: {len(diagram.final_states)}")
        state = diagram.start_state
        print(f"[DEBUG] Initial state ID: {state.id}")
        print(f"[DEBUG] Current token: '{self.current_token}' at line {self.current_line_number}")
        print(f"[DEBUG] Current parse tree node: '{self.current_node}'")
        print(f"[DEBUG] ============================================")

        loop_counter = 0
        max_loops = 1000  # Prevent infinite loops during debugging
        state_history = []
        while (self.scanner.input_reader_has_next() or self.current_token == '$') and not self.unexpected_eof_flag and not self.missing_end_detected:
            print(f"\n[DEBUG] === LOOP {loop_counter} ===")
            print(f"[DEBUG] Current state: {state.id}, is_final: {state.is_final}")
            print(f"[DEBUG] Current token: '{self.current_token}'")
            print(f"[DEBUG] Scanner has next: {self.scanner.input_reader_has_next()}")
            
            transitioned = False
            epsilon_edge = None
            terminal_transitions = []
            non_terminal_transitions = []
            action_symbol_transitions = []

            print(f"\n[DEBUG] Analyzing edges from state {state.id}")
            for edge in state.edges:
                print(f"[DEBUG] Examining edge: {edge.symbol} ({edge.edge_type.value}) -> State {edge.target.id}")
                if edge.edge_type.value == EdgeType.TERMINAL.value:
                    terminal_transitions.append(edge)
                    print(f"[DEBUG] Added terminal transition: {edge.symbol}")
                elif edge.edge_type.value == EdgeType.NON_TERMINAL.value:
                    non_terminal_transitions.append(edge)
                    print(f"[DEBUG] Added non-terminal transition: {edge.symbol}")
                elif edge.edge_type.value == EdgeType.ACTION_SYMBOL.value:
                    action_symbol_transitions.append(edge)
                    print(f"[DEBUG] Added action symbol transition: {edge.symbol}")
                elif edge.edge_type.value == EdgeType.EPSILON.value:
                    epsilon_edge = edge
                    print(f"[DEBUG] Found epsilon edge")

            # Handle action symbols first
            for action_edge in action_symbol_transitions:
                print(f"[DEBUG] *** PROCESSING ACTION SYMBOL: {action_edge.symbol} ***")
                print(f"[DEBUG] Moving from state {state.id} to state {action_edge.target.id}")
                
                # Execute the semantic action
                self.execute_semantic_action(action_edge.symbol)
                
                # Move to the target state
                old_state_id = state.id
                state = action_edge.target
                transitioned = True
                print(f"[DEBUG] *** ACTION COMPLETED: Moved from state {old_state_id} to state {state.id} ***")
                print(f"[DEBUG] New state is_final: {state.is_final}")
                break

            if transitioned:
                print(f"[DEBUG] Transitioned via action symbol, continuing loop")
                continue

            # Handle terminal transitions
            for edge in terminal_transitions:
                if self.match_token_to_symbol(edge.symbol):
                    print(f"[DEBUG] Matched terminal: {edge.symbol}")
                    terminal_node = ParseNode(edge.symbol, self.current_token)
                    self.current_node.add_child(terminal_node)
                    self.match(edge.symbol)
                    state = edge.target
                    transitioned = True
                    break

            if transitioned:
                continue

            # Handle non-terminal transitions
            for edge in non_terminal_transitions:
                predict = self.grammar.get_predict(str(edge.symbol))
                if self.check_in_set(predict):
                    print(f"[DEBUG] Matched non-terminal: {edge.symbol}")
                    non_terminal_node = ParseNode(edge.symbol)
                    self.current_node.add_child(non_terminal_node)

                    parent_node = self.current_node
                    self.current_node = non_terminal_node

                    self.return_stack.append(edge.target)
                    self.execute_diagram(str(edge.symbol), self.diagrams[str(edge.symbol)])

                    self.current_node = parent_node
                    state = self.return_stack.pop()
                    transitioned = True
                    break

            if transitioned:
                continue

            # Handle epsilon transitions
            if epsilon_edge is not None:
                print(f"[DEBUG] Taking epsilon transition")
                epsilon_node = ParseNode('epsilon')
                self.current_node.add_child(epsilon_node)
                state = epsilon_edge.target
                transitioned = True
                continue

            # Error handling
            if not transitioned:
                if state.is_final:
                    print(f"[DEBUG] Reached final state {state.id}, returning")
                    return

                if self.current_token == "$":
                    self.log_error(f"Unexpected EOF")
                    self.unexpected_eof_flag = True
                    return

                # Error recovery
                if state.edges:
                    error_edge = state.edges[0]
                    if error_edge.edge_type.value == EdgeType.TERMINAL.value:
                        if str(error_edge.symbol) == "$":
                            self.missing_end_detected = True
                            return
                        else:
                            self.log_error(f"missing {error_edge.symbol}")
                            state = error_edge.target
                            continue
                    elif error_edge.edge_type.value == EdgeType.NON_TERMINAL.value:
                        follow = self.grammar.get_follow(str(error_edge.symbol))
                        if self.check_in_set(follow):
                            self.log_error(f"missing {error_edge.symbol}")
                            state = error_edge.target
                            continue
                        else:
                            if hasattr(self.current_state, 'type') and self.current_state.type[1].value in [Token.ID.value, Token.NUM.value]:
                                syntax_error_txt = self.current_state.type[1].value
                            else:
                                syntax_error_txt = self.current_token
                            self.log_error(f"illegal {syntax_error_txt}")
                            self.current_state, self.current_token, self.current_line_number = self.scanner.get_next_token()
                            continue
                else:
                    # No edges from current state - this shouldn't happen
                    print(f"[DEBUG] Error: No edges from state {state.id}")
                    return
            loop_counter += 1
            state_history.append((state.id, str(self.current_token)))
            
            # Check for immediate loops (same state with same token)
            if len(state_history) > 10:
                recent_states = state_history[-10:]
                if len(set(recent_states)) <= 2:  # Only 1-2 unique state-token combinations
                    print(f"[DEBUG] *** POTENTIAL INFINITE LOOP DETECTED ***")
                    print(f"[DEBUG] Recent state-token history: {recent_states}")
                    print(f"[DEBUG] Current state: {state.id}, token: {self.current_token}")
                    
            if loop_counter > max_loops:
                print(f"[DEBUG] *** INFINITE LOOP DETECTED in {diagram_name} at state {state.id} ***")
                print(f"[DEBUG] Current token: {self.current_token}")
                print(f"[DEBUG] State edges:")
                for i, edge in enumerate(state.edges):
                    print(f"[DEBUG]   Edge {i}: {edge.symbol} ({edge.edge_type.value}) -> State {edge.target.id}")
                print(f"[DEBUG] Last 20 state transitions: {state_history[-20:]}")
                break
            transitioned = False
            epsilon_edge = None
            terminal_transitions = []
            non_terminal_transitions = []
            action_symbol_transitions = []

            print(f"\n[DEBUG] Analyzing edges from state {state.id}")
            for edge in state.edges:
                print(f"[DEBUG] Examining edge: {edge.symbol} ({edge.edge_type.value}) -> State {edge.target.id}")
                if edge.edge_type.value == EdgeType.TERMINAL.value:
                    terminal_transitions.append(edge)
                    print(f"[DEBUG] Added terminal transition: {edge.symbol}")
                elif edge.edge_type.value == EdgeType.NON_TERMINAL.value:
                    non_terminal_transitions.append(edge)
                    print(f"[DEBUG] Added non-terminal transition: {edge.symbol}")
                elif edge.edge_type.value == EdgeType.ACTION_SYMBOL.value:
                    action_symbol_transitions.append(edge)
                    print(f"[DEBUG] Added action symbol transition: {edge.symbol}")
                elif edge.edge_type.value == EdgeType.EPSILON.value:
                    epsilon_edge = edge
                    print(f"[DEBUG] Found epsilon edge")

            # Handle action symbols first
            for action_edge in action_symbol_transitions:
                print(f"[DEBUG] Processing action symbol: {action_edge.symbol}")
                
                # Execute the semantic action
                self.execute_semantic_action(action_edge.symbol)
                
                # Move to the target state
                state = action_edge.target
                transitioned = True
                print(f"[DEBUG] Moved to state {state.id} after action symbol")
                break

            if transitioned:
                continue

            # Handle terminal transitions
            for edge in terminal_transitions:
                if self.match_token_to_symbol(edge.symbol):
                    print(f"[DEBUG] Matched terminal: {edge.symbol}")
                    terminal_node = ParseNode(edge.symbol, self.current_token)
                    self.current_node.add_child(terminal_node)
                    self.match(edge.symbol)
                    state = edge.target
                    transitioned = True
                    break

            if transitioned:
                continue

            # Handle non-terminal transitions
            for edge in non_terminal_transitions:
                predict = self.grammar.get_predict(str(edge.symbol))
                if self.check_in_set(predict):
                    print(f"[DEBUG] Matched non-terminal: {edge.symbol}")
                    non_terminal_node = ParseNode(edge.symbol)
                    self.current_node.add_child(non_terminal_node)

                    parent_node = self.current_node
                    self.current_node = non_terminal_node

                    self.return_stack.append(edge.target)
                    self.execute_diagram(str(edge.symbol), self.diagrams[str(edge.symbol)])

                    self.current_node = parent_node
                    state = self.return_stack.pop()
                    transitioned = True
                    break

            if transitioned:
                continue

            # Handle epsilon transitions
            if epsilon_edge is not None:
                print(f"[DEBUG] Taking epsilon transition")
                epsilon_node = ParseNode('epsilon')
                self.current_node.add_child(epsilon_node)
                state = epsilon_edge.target
                transitioned = True
                continue

            # Error handling
            if not transitioned:
                if state.is_final:
                    print(f"[DEBUG] Reached final state {state.id}, returning")
                    return

                if self.current_token == "$":
                    self.log_error(f"Unexpected EOF")
                    self.unexpected_eof_flag = True
                    return

                # Error recovery
                if state.edges:
                    error_edge = state.edges[0]
                    if error_edge.edge_type.value == EdgeType.TERMINAL.value:
                        if str(error_edge.symbol) == "$":
                            self.missing_end_detected = True
                            return
                        else:
                            self.log_error(f"missing {error_edge.symbol}")
                            state = error_edge.target
                            continue
                    elif error_edge.edge_type.value == EdgeType.NON_TERMINAL.value:
                        follow = self.grammar.get_follow(str(error_edge.symbol))
                        if self.check_in_set(follow):
                            self.log_error(f"missing {error_edge.symbol}")
                            state = error_edge.target
                            continue
                        else:
                            if hasattr(self.current_state, 'type') and self.current_state.type[1].value in [Token.ID.value, Token.NUM.value]:
                                syntax_error_txt = self.current_state.type[1].value
                            else:
                                syntax_error_txt = self.current_token
                            self.log_error(f"illegal {syntax_error_txt}")
                            self.current_state, self.current_token, self.current_line_number = self.scanner.get_next_token()
                            continue
                else:
                    # No edges from current state - this shouldn't happen
                    print(f"[DEBUG] Error: No edges from state {state.id}")
                    return