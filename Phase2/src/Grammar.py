class Grammar:
    class Symbol:
        def __init__(self, name):
            self.name = name.strip()

        def __str__(self):
            return self.name

        def __repr__(self):
            return str(self)

        def __eq__(self, other):
            return isinstance(other, Grammar.Symbol) and self.name == other.name

        def __hash__(self):
            return hash(self.name)

    class Terminal(Symbol):
        pass

    class NonTerminal(Symbol):
        def __init__(self, name):
            super().__init__(name)
            self.goes_to_eps = False

    class Rule:
        def __init__(self, lhs):
            self.lhs = lhs  # NonTerminal
            self.rhs = []   # list of list of Symbols

        def add_rhs(self, symbols):
            self.rhs.append(symbols)

        def __str__(self):
            rhs_str = ' | '.join([' '.join(str(sym) for sym in alt) for alt in self.rhs])
            return f"{self.lhs} → {rhs_str}"

    def __init__(self):
        self.rules = {}              # {NT.name: Rule}
        self.non_terminals = {}      # {name: NonTerminal}
        self.terminals = {}          # {name: Terminal}
        self.first_sets = {}
        self.follow_sets = {}
        self.predict_sets = {}
    
    def load_predicts(self, filename='predict_sets.txt'):
        with open(filename) as f:
            for line in f:
                if ':' in line:
                    key, symbols = line.strip().split(':')
                    self.predict_sets[key.strip()] = set(symbols.strip().split())

    def get_or_create_nt(self, name):
        if name not in self.non_terminals:
            self.non_terminals[name] = Grammar.NonTerminal(name)
        return self.non_terminals[name]

    def get_or_create_terminal(self, name):
        if name not in self.terminals:
            self.terminals[name] = Grammar.Terminal(name)
        return self.terminals[name]

    def add_production(self, lhs_name, rhs_symbols):
        lhs_nt = self.get_or_create_nt(lhs_name)
        if lhs_name not in self.rules:
            self.rules[lhs_name] = Grammar.Rule(lhs_nt)

        if rhs_symbols == ['epsilon']:
            lhs_nt.goes_to_eps = True
            self.rules[lhs_name].add_rhs(['epsilon'])
            return

        rhs = []
        for sym in rhs_symbols:
            if sym in self.non_terminals or sym[0].isupper():
                rhs.append(self.get_or_create_nt(sym))
            else:
                rhs.append(self.get_or_create_terminal(sym))
        self.rules[lhs_name].add_rhs(rhs)

    def finalize(self):
        all_rhs_symbols = {
            str(sym)
            for rule in self.rules.values()
            for alt in rule.rhs
            for sym in alt
            if sym != 'epsilon'
        }

        for sym in all_rhs_symbols:
            if sym not in self.non_terminals:
                self.get_or_create_terminal(sym)

    def load_sets(self, filename):
        sets = {}
        with open(filename) as f:
            for line in f:
                if ':' in line:
                    nt, items = line.strip().split(':')
                    sets[nt.strip()] = set(items.strip().split())
        return sets

    def load_firsts(self, filename='firsts.txt'):
        self.first_sets = self.load_sets(filename)

    def load_follows(self, filename='follow.txt'):
        self.follow_sets = self.load_sets(filename)

    def print_grammar(self):
        print("=== Non-Terminals ===")
        for nt in self.non_terminals.values():
            print(f"{nt.name} (goes_to_eps: {nt.goes_to_eps})")

        print("\n=== Terminals ===")
        for t in self.terminals.values():
            print(t.name)

        print("\n=== Production Rules ===")
        for rule in self.rules.values():
            print(rule)

        print("\n=== FIRST Sets ===")
        for nt, f in self.first_sets.items():
            print(f"{nt}: {sorted(f)}")

        print("\n=== FOLLOW Sets ===")
        for nt, f in self.follow_sets.items():
            print(f"{nt}: {sorted(f)}")
