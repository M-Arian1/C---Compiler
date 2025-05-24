from enum import Enum
from Phase1.src.Tokens import Token
class EdgeType(Enum):
    TERMINAL = 'TERMINAL'
    NON_TERMINAL = 'NON_TERMINAL'
    EPSILON = 'EPSILON'
    ACTION = 'ACTION'


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
        self.parse_tree = []
        self.error_log = open('syntax_errors.txt', 'w')
        self.type = None

    def log_error(self, message):
        self.error_log.write(f"#{self.current_line_number} : syntax error, {message}\n")

    def match(self, terminal):
        if self.current_token == terminal:
            matched = self.current_token
            self.type, self.current_token, self.current_line_number = self.scanner.get_next_token()
            # print(self.current_token)
            return matched
        else:
            self.log_error(f"missing {terminal}")
            return None

    def parse(self, start_symbol):
        start_diagram = self.diagrams[start_symbol]
        print(self.current_token)
        self.execute_diagram(start_symbol, start_diagram)
        if self.current_token != '$':
            self.log_error(f"illegal {self.current_state.type[1].value}")
        self.error_log.close()
        return self.parse_tree

    def execute_diagram(self, diagram_name, diagram):
        state = diagram.start_state
        while self.scanner.input_reader_has_next():
            transitioned = False
            for edge in state.edges:
                # print( edge.edge_type.value ==  EdgeType.NON_TERMINAL.value)
                if edge.edge_type.value == EdgeType.TERMINAL.value:
                    
                    if self.current_token == edge.symbol:
                        self.parse_tree.append(('match', edge.symbol))
                        self.match(edge.symbol, self.current_line_number )
                        state = edge.target
                        transitioned = True
                        break
                    else:
                        self.log_error(f"missing {edge.symbol}")
                        state = edge.target
                        transitioned = True
                        break

                elif edge.edge_type.value == EdgeType.NON_TERMINAL.value:
                    print(edge.symbol)
                    predict = self.grammar.get_predict(edge.symbol)
                    follow = self.grammar.get_follow(edge.symbol)
                   
                    if self.current_token in predict:
                        self.parse_tree.append(('enter', edge.symbol))
                        self.return_stack.append(edge.target)
                        self.execute_diagram(edge.symbol, self.diagrams[str(edge.symbol)])
                        state = self.return_stack.pop()
                        transitioned = True
                        break
                    elif self.current_token in follow:
                        self.log_error(f"missing {edge.symbol}")
                        state = edge.target
                        transitioned = True
                        break
                    else: #TODO: Handle with synch
                        self.log_error(f"illegal {self.current_token}")
                        self.current_token = self.scanner.get_next_token()
                        return  # Resynchronize by returning from current diagram

                elif edge.edge_type.value == EdgeType.EPSILON.value:
                    self.parse_tree.append(('epsilon', ))
                    state = edge.target
                    transitioned = True
                    break

                elif edge.edge_type.value == EdgeType.ACTION.value:
                    
                    self.parse_tree.append(('action', edge.symbol))
                    state = edge.target
                    transitioned = True
                    break

            if not transitioned:
                if state.is_final:
                    return
                else:
                    self.log_error(f"illegal {self.current_token}")
                    self.current_state,self.current_token ,self.current_line_number = self.scanner.get_next_token()
                    state = diagram.start_state
