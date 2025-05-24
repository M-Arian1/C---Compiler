from enum import Enum

# === Constants ===
class EdgeType(Enum):
    TERMINAL = 'TERMINAL'
    NON_TERMINAL = 'NON_TERMINAL'
    ACTION = 'ACTION'
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


class DiagramBuilder:
    def __init__(self, grammar):
        self.grammar = grammar
        self.diagrams = {}
        self.state_counter = 0

    def new_state(self, is_final=False):
        state = ParserState(self.state_counter, is_final)
        self.state_counter += 1
        return state

    def determine_edge_type(self, symbol):
        if isinstance(symbol, self.grammar.Terminal):
            return EdgeType.TERMINAL
        elif isinstance(symbol, self.grammar.NonTerminal):
            return EdgeType.NON_TERMINAL
        elif symbol == 'epsilon':
            return EdgeType.EPSILON
        elif isinstance(symbol, str) and symbol.startswith("#"):
            return EdgeType.ACTION
        else:
            raise ValueError(f"Unknown symbol type: {symbol}")

    def build_all(self):
        for nt_name, rule in self.grammar.rules.items():
            self.diagrams[nt_name] = self.build_diagram(rule)
        return self.diagrams

    def build_diagram(self, rule):
        diagram = ParserDiagram(rule.lhs.name)
        for production in rule.rhs:
            start = self.new_state()
            current = start
            diagram.add_state(start)

            if production == ['epsilon']:
                final = self.new_state(is_final=True)
                diagram.add_state(final)
                current.add_edge('epsilon', final, EdgeType.EPSILON)
                continue

            for i, symbol in enumerate(production):
                is_last = (i == len(production) - 1)
                edge_type = self.determine_edge_type(symbol)
                final = self.new_state(is_final=is_last)
                diagram.add_state(final)
                current.add_edge(symbol, final, edge_type)
                current = final
        return diagram
