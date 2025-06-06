from enum import Enum

# === Constants ===
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
    def get_name(self):
        return str(self.symbol)
    def edge_info(self):
        print("from :", self.source.get_id(), "with", self.symbol, "to", self.target.get_id(), "Type:", self.edge_type)


class ParserState:
    def __init__(self, id, is_final=False):
        self.id = id
        self.is_final = is_final
        self.edges = []

    def add_edge(self, symbol, target, edge_type):
        self.edges.append(ParserEdge(self, target, symbol, edge_type))
    
    def get_id(self):
        return str(self.id)


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
        elif symbol == 'epsilon' or symbol == 'ε':
            return EdgeType.EPSILON
        else:
            raise ValueError(f"Unknown symbol type: {symbol}")

    def build_all(self):
        for nt_name, rules in self.grammar.rule_map.items():
            diagram = ParserDiagram(nt_name)
            self.build_diagram(diagram, rules)
            self.diagrams[nt_name] = diagram
        return self.diagrams

    def build_diagram(self, diagram, rules):
        # Create shared start and final states
        start = self.new_state()
        final = self.new_state(is_final=True)
        diagram.start_state = start
        diagram.add_state(start)
        diagram.add_state(final)
        diagram.final_states.append(final)

        for rule in rules:
            production = rule.rhs
            # print("PRODUCTION", production, "len", (len(production)),)
            if len(production) == 1 and str(production[0]) == 'ε':  # ε-production
                start.add_edge('epsilon', final, EdgeType.EPSILON)
                continue

            current = start
            for i, symbol in enumerate(production):
                is_last = (i == len(production) - 1)
                edge_type = self.determine_edge_type(symbol)
                next_state = final if is_last else self.new_state()
                if not is_last:
                    diagram.add_state(next_state)
                current.add_edge(symbol, next_state, edge_type)
                current = next_state

    def print_diagrams(self):
        for nt_name, diagram in self.diagrams.items():
            print(f"\nDiagram for Non-Terminal: {nt_name}")
            for state in diagram.states:
                final_str = " (final)" if state.is_final else ""
                print(f"  State {state.id}{final_str}")
                for edge in state.edges:
                    print(f"    --[{edge.symbol} ({edge.edge_type.name})]--> State {edge.target.id}")

