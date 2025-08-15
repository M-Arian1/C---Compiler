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
        self.error_messages.append(f"#{self.current_line_number} : syntax error, {message}\n")

    def match_token_to_symbol(self, symbol):
        if str(symbol) == "KEYWORD":
            return self.current_state.type[1].value == Token.KEYWORD.value
        if str(symbol) == "ID":
            return self.current_state.type[1].value == Token.ID.value
        if str(symbol) == "NUM":
            return self.current_state.type[1].value == Token.NUM.value
        return str(self.current_token) == str(symbol)

    def check_in_set(self, set):
        for p in set:
            if self.match_token_to_symbol(p):
                return True
        return False

    def match(self, terminal):
        if self.match_token_to_symbol(terminal):
            matched = self.current_token
            self.current_state, self.current_token, self.current_line_number = self.scanner.get_next_token()
            return matched
        else:
            self.log_error(f"missing {terminal}")
            return None

    def parse(self, start_symbol):
        from Phase2.src.TreeHandler import ParseNode
        start_diagram = self.diagrams[start_symbol]
        self.parse_tree = ParseNode(start_symbol)
        self.current_node = self.parse_tree
        self.execute_diagram(start_symbol, start_diagram)

        if self.current_token != '$':
            terminal_node = ParseNode('$', '$')
            self.current_node.add_child(terminal_node)

        with self.error_log as f:
            if self.error_messages:
                f.write("".join(self.error_messages))
            else:
                f.write("There is no syntax error.\n")

        self.error_log.close()
        return self.parse_tree

    #Phase3: Needs massive changes
    def execute_diagram(self, diagram_name, diagram):
        from Phase2.src.TreeHandler import ParseNode
        state = diagram.start_state

        while (self.scanner.input_reader_has_next() or self.current_token == '$') and not self.unexpected_eof_flag and not self.missing_end_detected:
            transitioned = False
            epsilon_edge = None
            terminal_transitions = []
            non_terminal_transitions = []
            transition_with_action_symbol = []
            state_or_transition_has_action = False
            terminal_matched = False
            non_terminal_matched = False

            for edge in state.edges:
                if edge.edge_type.value == EdgeType.TERMINAL.value:
                    terminal_transitions.append(edge)
                elif edge.edge_type.value == EdgeType.NON_TERMINAL.value:
                    non_terminal_transitions.append(edge)
                elif edge.edge_type.value == EdgeType.ACTION_SYMBOL.value:
                    transition_with_action_symbol.append(edge)
                    state_or_transition_has_action = True
                elif edge.edge_type.value == EdgeType.EPSILON.value:
                    epsilon_edge = edge
            
            if state_or_transition_has_action:
                print("on action")
                #TODO
                #Phase3
                '''We should do the destined semantic routine IF the token matches with the next transition after this
                if there's no transition after this we should only do the routine and probably continue?'''
                
                
                for edge in transition_with_action_symbol:
                    target_state = edge.target
                    act_sym = edge.symbol

                    #Case 1: action symbol transitions into a final state
                    if target_state.is_final:
                        #TODO: perform the semantic action and then return without using the token
                        self.code_generator[act_sym](self.current_token)
                        pass 
                    
                    #Case 2: action symbol is a transition to an intermediate state
                    else:
                        #TODO: first we should add the transition from this state into the next one and add it to the possible "edges" so it matches with that instead of an action symbol!
                        
                        #get the next edge after this
                        next_edge = target_state.get_edges_from_state()[0]
                        if next_edge.edge_type.value == EdgeType.TERMINAL.value:
                            # edge = next_edge
                            if self.match_token_to_symbol(next_edge.symbol):
                                terminal_node = ParseNode(next_edge.symbol, self.current_token)
                                self.current_node.add_child(terminal_node)
                                self.match(next_edge.symbol)
                                state = next_edge.target
                                transitioned = True
                                terminal_matched = True
                                #TODO: perform action and advance token
                                self.code_generator[act_sym](self.current_token)

                                
                        if terminal_matched:
                            break   
                        if next_edge.edge_type.value == EdgeType.NON_TERMINAL.value:
                            predict = self.grammar.get_predict(next_edge.get_name())
                            if self.check_in_set(predict):
                                non_terminal_node = ParseNode(next_edge.symbol)
                                self.current_node.add_child(non_terminal_node)

                                parent_node = self.current_node
                                self.current_node = non_terminal_node

                                self.return_stack.append(next_edge.target)
                                self.code_generator[act_sym](self.current_token)
                                self.execute_diagram(next_edge.symbol, self.diagrams[str(edge.symbol)])
                                self.current_node = parent_node
                                state = self.return_stack.pop()
                                transitioned = True
                                non_terminal_matched = True
                               
                                
                        if non_terminal_matched:
                            break
                        if not transitioned and  next_edge.edge_type.value == EdgeType.EPSILON.value:
                            epsilon_edge = next_edge
                            epsilon_node = ParseNode('epsilon')
                            self.current_node.add_child(epsilon_node)
                            state = epsilon_edge.target
                            transitioned = True
                            self.code_generator[act_sym](self.current_token)
                            continue
                        
            if transitioned: 
                continue
            
            
            for edge in terminal_transitions:
                if self.match_token_to_symbol(edge.symbol):
                    terminal_node = ParseNode(edge.symbol, self.current_token)
                    self.current_node.add_child(terminal_node)
                    self.match(edge.symbol)
                    state = edge.target
                    transitioned = True
                    terminal_matched = True
                    break

            if terminal_matched:
                continue

            for edge in non_terminal_transitions:
                predict = self.grammar.get_predict(edge.get_name())
                if self.check_in_set(predict):
                    non_terminal_node = ParseNode(edge.symbol)
                    self.current_node.add_child(non_terminal_node)

                    parent_node = self.current_node
                    self.current_node = non_terminal_node

                    self.return_stack.append(edge.target)
                    self.execute_diagram(edge.symbol, self.diagrams[str(edge.symbol)])

                    self.current_node = parent_node
                    state = self.return_stack.pop()
                    transitioned = True
                    non_terminal_matched = True
                    break

            if non_terminal_matched:
                continue

            if not transitioned and epsilon_edge is not None:
                epsilon_node = ParseNode('epsilon')
                self.current_node.add_child(epsilon_node)
                state = epsilon_edge.target
                continue

            if not state.is_final:
                if self.current_token == "$":
                    self.log_error(f"Unexpected EOF")
                    self.unexpected_eof_flag = True
                    return

                error_edge = state.edges[0]
                edge = error_edge
                if edge.edge_type.value == EdgeType.TERMINAL.value:
                    if str(edge.symbol) == "$":
                        self.missing_end_detected = True
                        transitioned = True
                        return
                    else:
                        self.log_error(f"missing {edge.symbol}")
                        state = error_edge.target
                        transitioned = True
                        continue
                elif edge.edge_type.value == EdgeType.NON_TERMINAL.value:
                    follow = self.grammar.get_follow(edge.get_name())
                    if self.check_in_set(follow):
                        self.log_error(f"missing {edge.symbol}")
                        state = edge.target
                        transitioned = True
                        continue
                    else:
                        if self.current_state.type[1].value == Token.ID.value or self.current_state.type[1].value == Token.NUM.value:
                            syntax_error_txt = self.current_state.type[1].value
                        else:
                            syntax_error_txt = self.current_token
                        self.log_error(f"illegal {syntax_error_txt}")
                        self.current_state, self.current_token, self.current_line_number = self.scanner.get_next_token()
                        continue

            if not transitioned:
                if state.is_final:
                    return