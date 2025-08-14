from enum import Enum

# === Constants ===
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
    def get_name(self):
        return str(self.symbol)
    def edge_info(self):
        print("from :", self.source.get_id(), "with", self.symbol, "to", self.target.get_id(), "Type:", self.edge_type)


class ParserState:
    def __init__(self, id, is_final=False, has_semantic_action = False):
        self.id = id
        self.is_final = is_final
        self.edges = []
        self.has_semantic_action = has_semantic_action

    def add_edge(self, symbol, target, edge_type):
        self.edges.append(ParserEdge(self, target, symbol, edge_type))
    
    def get_id(self):
        return str(self.id)
    
    def has_action(self):
        return self.has_semantic_action
    
    def get_edges_from_state(self):
        return self.edges


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

    def new_state(self, is_final=False, has_semantic_action = False):
        state = ParserState(self.state_counter, is_final, has_semantic_action)
        self.state_counter += 1
        return state

    def determine_edge_type(self, symbol):
        print(f"[DEBUG] Determining edge type for symbol: {symbol} (type: {type(symbol)})")
        if isinstance(symbol, self.grammar.Terminal):
            print(f"[DEBUG] → TERMINAL")
            return EdgeType.TERMINAL
        elif isinstance(symbol, self.grammar.NonTerminal):
            print(f"[DEBUG] → NON_TERMINAL")
            return EdgeType.NON_TERMINAL
        elif isinstance(symbol, self.grammar.ActionSymbol):
            print(f"[DEBUG] → ACTION_SYMBOL")
            return EdgeType.ACTION_SYMBOL
        elif symbol == 'epsilon' or symbol == 'ε':
            print(f"[DEBUG] → EPSILON")
            return EdgeType.EPSILON
        else:
            print(f"[DEBUG] → ERROR: Unknown symbol type!")
            raise ValueError(f"Unknown symbol type: {symbol}")

    def build_all(self):
        for nt_name, rules in self.grammar.rule_map.items():
            print(f"\n[DEBUG] Building diagram for: {nt_name}")
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
            print(f"[DEBUG] Processing rule: {rule.lhs} → {[str(s) for s in production]}")
            
            if len(production) == 0:  # ε-production
                print(f"[DEBUG] Adding epsilon edge from {start.id} to {final.id}")
                start.add_edge('epsilon', final, EdgeType.EPSILON)
                continue

            current = start
            for i, symbol in enumerate(production):
                is_last = (i == len(production) - 1)
                edge_type = self.determine_edge_type(symbol)
                has_semantic_action = (edge_type.value == EdgeType.ACTION_SYMBOL.value)
                
                next_state = final if is_last else self.new_state(has_semantic_action = has_semantic_action)
                if not is_last:
                    diagram.add_state(next_state)
                
                print(f"[DEBUG] Adding edge: State {current.id} --[{symbol} ({edge_type.value})]-> State {next_state.id}")
                current.add_edge(symbol, next_state, edge_type)
                current = next_state

    def print_diagrams(self):
        for nt_name, diagram in self.diagrams.items():
            print(f"\n=== Diagram for Non-Terminal: {nt_name} ===")
            for state in diagram.states:
                final_str = " (final)" if state.is_final else ""
                print(f"  State {state.id}{final_str}")
                for edge in state.edges:
                    print(f"    --[{edge.symbol} ({edge.edge_type.name})]--> State {edge.target.id}")