from enum import Enum
from Phase1.src.Tokens import Token
class EdgeType(Enum):
    TERMINAL = 'TERMINAL'
    NON_TERMINAL = 'NON_TERMINAL'
    EPSILON = 'EPSILON'
    


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
        self.current_state ,self.current_token, self.current_line_number = self.scanner.get_next_token()
        self.return_stack = []
        self.parse_tree = None
        self.current_node = None
        self.error_log = open('syntax_errors.txt', 'w')
        self.type = None

    def log_error(self, message):
        self.error_log.write(f"#{self.current_line_number} : syntax error, {message}\n")
    
    def match_token_to_symbol(self, symbol):
        if symbol == "ID":
            return self.current_state.type[1] == Token.ID
        if symbol == "NUM":
            return self.current_state.type[1] == Token.NUM
        return self.current_token == symbol
    
    
    def check_in_predict(self, edge):
        predict = self.grammar.get_predict(edge.get_name())
        for p in predict:
            if self.match_token_to_symbol(p):
                return True
            
        return False
        

    def match(self, terminal):
        if self.match_token_to_symbol(terminal):
            matched = self.current_token
            self.current_state, self.current_token, self.current_line_number = self.scanner.get_next_token()
            # print(self.current_token)
            return matched
        else:
            self.log_error(f"missing {terminal}")
            return None

    def parse(self, start_symbol):
        from Phase2.src.TreeHandler import ParseNode
        start_diagram = self.diagrams[start_symbol]
        print(self.current_token)
        self.parse_tree = ParseNode(start_symbol)
        self.current_node = self.parse_tree
        self.execute_diagram(start_symbol, start_diagram)
        if self.current_token != '$':
            self.log_error(f"illegal {self.current_state.type[1].value}")
        self.error_log.close()
        return self.parse_tree
    

            
    def execute_diagram(self, diagram_name, diagram):
        from Phase2.src.TreeHandler import ParseNode
        print("We now are in :", diagram_name)
        state = diagram.start_state
        
        while self.scanner.input_reader_has_next():
            transitioned = False
            epsilon_edge = None
            terminal_transitions = []
            non_terminal_transitions = []
            terminal_matched = False
            non_terminal_matched = False
            
            for edge in state.edges:
                if edge.edge_type.value == EdgeType.TERMINAL.value:
                    terminal_transitions.append(edge)
                elif edge.edge_type.value == EdgeType.NON_TERMINAL.value:
                    non_terminal_transitions.append(edge)
                elif edge.edge_type == EdgeType.EPSILON:
                    epsilon_edge = edge
                    
            for edge in terminal_transitions:
                if self.match_token_to_symbol(edge.symbol):
                    # Create terminal node and add it to current node
                    terminal_node = ParseNode(edge.symbol, self.current_token)
                    self.current_node.add_child(terminal_node)
                    edge.edge_info()
                    print("token", self.current_token)
                    self.match(edge.symbol)
                    state = edge.target
                    transitioned = True
                    terminal_matched = True
                    break
                    
            if terminal_matched:
                continue
              # No match in terminals
            for edge in non_terminal_transitions:
                predict = self.grammar.get_predict(edge.get_name())
                if self.check_in_predict(edge):
                    print("token", self.current_token, "in", predict)
                    # Create non-terminal node
                    non_terminal_node = ParseNode(edge.symbol)
                    self.current_node.add_child(non_terminal_node)
                    
                    # Save current node and update it for recursive call
                    parent_node = self.current_node
                    self.current_node = non_terminal_node
                    
                    self.return_stack.append(edge.target)
                    edge.edge_info()
                    print("token", self.current_token)
                    
                    self.execute_diagram(edge.symbol, self.diagrams[str(edge.symbol)])
                    
                    # Restore the current node after recursion
                    self.current_node = parent_node
                    state = self.return_stack.pop()
                    transitioned = True
                    non_terminal_matched = True
                    continue
            
            # if non_terminal_matched and epsilon_edge is None:
            #     continue            #if reaches here: no match
            
            #check for epsilon
            if not transitioned and epsilon_edge is not None:
                # Create epsilon node and add it to current node
                epsilon_node = ParseNode('epsilon')
                self.current_node.add_child(epsilon_node)
                state = epsilon_edge.target
                continue
              #if Reaches here : syntax error
            if not state.is_final:
                error_edge = state.edges[0]
                edge = error_edge
                if edge.edge_type.value == EdgeType.TERMINAL.value:
                    self.log_error(f"missing {edge.symbol}")
                    # Create error node for missing terminal
                    error_node = ParseNode('error', f"missing {edge.symbol}")
                    self.current_node.add_child(error_node)
                    state = error_edge.target
                    transitioned = True
                    continue
                elif edge.edge_type.value == EdgeType.NON_TERMINAL.value:
                    follow = self.grammar.get_follow(edge.get_name())
                    if self.current_token in follow:
                        self.log_error(f"missing {edge.symbol}")
                        # Create error node for missing non-terminal
                        error_node = ParseNode('error', f"missing {edge.symbol}")
                        self.current_node.add_child(error_node)
                        state = edge.target
                        transitioned = True
                        continue
                    else: #TODO: Handle with synch
                        self.log_error(f"illegal {self.current_token}")
                        # Create error node for illegal token
                        error_node = ParseNode('error', f"illegal {self.current_token}")
                        self.current_node.add_child(error_node)
                        self.current_state, self.current_token, self.current_line_number = self.scanner.get_next_token()
                        continue  # Resynchronize by returning from current diagram
            
            if not transitioned:
                if state.is_final:
                    return
                else:
                    self.log_error(f"illegal {self.current_token}")
                    self.current_state, self.current_token, self.current_line_number = self.scanner.get_next_token()
                    state = diagram.start_state

                
                
                
                                
            # for edge in state.edges:
            #     print( diagram_name, edge.edge_type.value ==  EdgeType.NON_TERMINAL.value)
            #     edge.edge_info()
            #     if edge.edge_type.value == EdgeType.TERMINAL.value:
                    
            #         if self.current_token == edge.symbol:
            #             self.parse_tree.append(('match', edge.symbol))
            #             edge.edge_info()
            #             print("token",self.current_token)
            #             self.match(edge.symbol)
            #             state = edge.target
            #             transitioned = True
            #             break
            #         else:
            #             self.log_error(f"missing {edge.symbol}")
            #             state = edge.target
            #             transitioned = True
            #             break

            #     elif edge.edge_type.value == EdgeType.NON_TERMINAL.value:
            #         print(edge.symbol)
            #         predict = self.grammar.get_predict(edge.get_name())
            #         follow = self.grammar.get_follow(edge.get_name())
                   
            #         if self.current_token in predict:
            #             self.parse_tree.append(('enter', edge.symbol))
            #             self.return_stack.append(edge.target)
            #             edge.edge_info()
            #             print("token",self.current_token)

            #             self.execute_diagram(edge.symbol, self.diagrams[str(edge.symbol)])
            #             state = self.return_stack.pop()
            #             transitioned = True
            #             break
            #         elif self.current_token in follow:
            #             self.log_error(f"missing {edge.symbol}")
            #             state = edge.target
            #             transitioned = True
            #             break
            #         else: #TODO: Handle with synch
            #             self.log_error(f"illegal {self.current_token}")
            #             self.current_token = self.scanner.get_next_token()
            #             return  # Resynchronize by returning from current diagram

            #     elif edge.edge_type == EdgeType.EPSILON:
            #         epsilon_edge = edge
            #         continue

                # elif edge.edge_type.value == EdgeType.ACTION.value:
                    
                #     self.parse_tree.append(('action', edge.symbol))
                #     state = edge.target
                #     transitioned = True
                #     break
                
            # if not transitioned and epsilon_edge is not None:
            # # Only now take the epsilon transition
            #     self.parse_tree.append(('epsilon',))
            #     state = epsilon_edge.target
            #     continue

            # if not transitioned:
            #     if state.is_final:
            #         return
            #     else:
            #         self.log_error(f"illegal {self.current_token}")
            #         self.current_state, self.current_token, self.current_line_number = self.scanner.get_next_token()
            #         state = diagram.start_state
