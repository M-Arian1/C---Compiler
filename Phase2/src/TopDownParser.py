from enum import Enum

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
        self.current_token = self.scanner.get_next_token()
        self.return_stack = []
        self.parse_tree = []

    def match(self, terminal):
        if self.current_token == terminal:
            matched = self.current_token
            self.current_token = self.scanner.get_next_token()
            return matched
        else:
            self.error(f"Expected token '{terminal}' but found '{self.current_token}'")

    def error(self, msg):
        raise Exception(f"Syntax Error: {msg}")

    def parse(self, start_symbol):
        start_diagram = self.diagrams[start_symbol]
        self.execute_diagram(start_diagram)
        if self.current_token != '$':
            self.error("Extra input after parsing completed")
        return self.parse_tree

    def execute_diagram(self, diagram):
        state = diagram.start_state
        while True:
            transitioned = False
            for edge in state.edges:
                if edge.edge_type == EdgeType.TERMINAL and self.current_token == edge.symbol:
                    self.parse_tree.append(('match', edge.symbol))
                    self.match(edge.symbol)
                    state = edge.target
                    transitioned = True
                    break
                elif edge.edge_type == EdgeType.NON_TERMINAL:
                    self.return_stack.append(edge.target)
                    self.parse_tree.append(('enter', edge.symbol))
                    self.execute_diagram(self.diagrams[str(edge.symbol)])
                    state = self.return_stack.pop()
                    transitioned = True
                    break
                elif edge.edge_type == EdgeType.EPSILON:
                    self.parse_tree.append(('epsilon', ))
                    state = edge.target
                    transitioned = True
                    break
                elif edge.edge_type == EdgeType.ACTION:
                    self.parse_tree.append(('action', edge.symbol))
                    state = edge.target
                    transitioned = True
                    break
            if not transitioned:
                if state.is_final:
                    return
                else:
                    self.error("No valid transition from state {} with token '{}'".format(state.id, self.current_token))
