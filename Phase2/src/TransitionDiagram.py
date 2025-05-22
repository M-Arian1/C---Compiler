from enum import Enum

# === Constants ===
class EdgeType(Enum):
    TERMINAL = 1
    NON_TERMINAL = 2
    ACTION = 3
    EPSILON = 4


class ParseTreeNode:
    def __init__(self, label, parent=None):
        self.label = label
        self.children = []
        self.parent = parent

    def add_child(self, child_node):
        self.children.append(child_node)

    def __repr__(self):
        return f"{self.label} -> {[str(c) for c in self.children]}"


class ParserEdge:
    def __init__(self, source, destination, edge_type, label, return_state=None):
        self.source = source
        self.destination = destination
        self.edge_type = edge_type
        self.label = label
        self.return_state = return_state


class ParserState:
    def __init__(self, ID, production_name, is_begin=False, is_final=False):
        self.ID = ID
        self.edges = []
        self.production_name = production_name
        self.is_begin = is_begin
        self.is_final = is_final

    def add_edge(self, destination, edge_type, label, return_state=None):
        edge = ParserEdge(self, destination, edge_type, label, return_state)
        self.edges.append(edge)


class ParserDiagram:
    def __init__(self, name):
        self.name = name
        self.states = []
        self.start_state = None
        self.final_states = []

    def add_state(self, state):
        if not self.states:
            self.start_state = state
        self.states.append(state)
        if state.is_final:
            self.final_states.append(state)


class DiagramBuilder:
    def __init__(self, grammar):
        self.grammar = grammar
        self.diagrams = {}
        self.state_counter = 0

    def new_state(self, prod_name, is_begin=False, is_final=False):
        state = ParserState(self.state_counter, prod_name, is_begin, is_final)
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
            start = self.new_state(rule.lhs.name, is_begin=True)
            current = start
            diagram.add_state(start)

            if production == ['epsilon']:
                final = self.new_state(rule.lhs.name, is_final=True)
                diagram.add_state(final)
                current.add_edge(final, EdgeType.EPSILON, 'epsilon')
                continue

            for i, symbol in enumerate(production):
                is_last = (i == len(production) - 1)
                edge_type = self.determine_edge_type(symbol)
                final = self.new_state(rule.lhs.name, is_final=True) if is_last else self.new_state(rule.lhs.name)
                diagram.add_state(final)

                if edge_type == EdgeType.NON_TERMINAL:
                    # No immediate move; transition with return point
                    current.add_edge(None, edge_type, symbol, return_state=final)
                else:
                    current.add_edge(final, edge_type, symbol)

                if edge_type != EdgeType.NON_TERMINAL:
                    current = final

        return diagram
