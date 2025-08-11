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
            
    class ActionSymbol(Symbol):
        def __init__(self, name):
            super().__init__(name)
            # self.goes_to_eps = False  -> Not really sure what to do here

    class Rule:
        def __init__(self, lhs, rhs):
            self.lhs = lhs                    # NonTerminal
            self.rhs = rhs                    # list of Symbols (Terminals/NonTerminals)

        def __str__(self):
            rhs_str = ' '.join(str(sym) for sym in self.rhs) if self.rhs else 'EPSILON'
            return f"{self.lhs} → {rhs_str}"

    def __init__(self):
        self.rules = []                      # List of Rule objects
        self.rule_map = {}                   # Optional: maps NT name to list of Rules
        
        self.non_terminals = {}              # {name: NonTerminal}
        self.terminals = {}                  # {name: Terminal}
        self.terminal_names = {
            "+", "-", "*", "(", ")", "[", "]", "{", "}", ";", ",",
            "<", "==", "=", "break", "if", "else", "int", "return",
            "void", "while", "ID", "NUM", "EPSILON", "$"
        }
        self.action_symbols ={}
        # self.action_symbols_names = {
        #     "#push_in_semantic_stack",
        #     "#dec-var",
        #     "#dec-array",
        #     "#pid",
        #     "#mult",
        #     "#add-or-sub",
        #     "#relation",
        #     "#label",
        #     "#until",
        #     "#save",
        #     "#jpf_save",
        #     "#jp",
        #     "#save-num-in-ss",
        #     "#assign",
        #     "#print",
        #     "#calc-arr-addr",
        #     "#begin",
        #     "#end",
        #     "#save-break",
        #     "#dec-func",
        #     "#end-func",
        #     "#dec-pointer",
        #     "#param-info",
        #     "#start-args",
        #     "#check-args",
        #     "#return-value",
        #     "#return-jp"}
        
        
        self.first_sets = {
        "Program": ["int", "void", "EPSILON"],
        "DeclarationList": ["int", "void", "EPSILON"],
        "Declaration": ["int", "void"],
        "DeclarationInitial": ["int", "void"],
        "DeclarationPrime": [";", "[", "(",],
        "VarDeclarationPrime": [";", "["],
        "FunDeclarationPrime": ["("],
        "TypeSpecifier": ["int", "void"],
        "Params": ["int", "void"],
        "ParamList": [",", "EPSILON"],
        "Param": ["int", "void"],
        "ParamPrime": ["[", "EPSILON"],
        "CompoundStmt": ["{"],
        "StatementList": ["ID", ";", "NUM", "(", "{", "break", "if", "while", "return", "+", "-", "EPSILON"],
        "Statement": ["ID", ";", "NUM", "(", "{", "break", "if", "while", "return", "+", "-"],
        "ExpressionStmt": ["ID", ";", "NUM", "(", "break", "+", "-"],
        "SelectionStmt": ["if"],
        "IterationStmt": ["while"],
        "ReturnStmt": ["return"],
        "ReturnStmtPrime": ["ID", ";", "NUM", "(", "+", "-"],
        "Expression": ["ID", "NUM", "(", "+", "-"],
        "B": ["[", "(", "==" ,"=", "+", "-", "<", "*", "EPSILON"],
        "H": ["=", "*", "+", "-", "<", "==", "EPSILON"],
        "SimpleExpressionZegond": ["NUM", "(", "+", "-"],
        "SimpleExpressionPrime": ["(", "+", "-", "<", "==", "EPSILON", "*"],
        "C": ["<", "==", "EPSILON"],
        "Relop": ["<", "=="],
        "AdditiveExpression": ["ID", "NUM", "(", "+", "-"],
        "AdditiveExpressionPrime": ["(", "+", "-", "*", "EPSILON"],
        "AdditiveExpressionZegond": ["NUM", "(", "+", "-"],
        "D": ["+", "-", "EPSILON"],
        "Addop": ["+", "-"],
        "Term": ["ID", "NUM", "(", "+", "-"],
        "TermPrime": ["(", "*", "EPSILON"],
        "TermZegond": ["NUM", "(", "+", "-"],
        "G": ["*", "EPSILON"],
        "SignedFactor": ["ID", "NUM", "(", "+", "-"],
        "SignedFactorPrime": ["(", "EPSILON"],
        "SignedFactorZegond": ["NUM", "(", "+", "-"],
        "Factor": ["ID", "NUM", "("],
        "VarCallPrime": ["(", "[", "EPSILON"],
        "VarPrime": ["[", "EPSILON"],
        "FactorPrime": ["(", "EPSILON"],
        "FactorZegond": ["NUM", "("],
        "Args": ["ID", "NUM", "(", "+", "-", "EPSILON"],
        "ArgList": ["ID", "NUM", "(", "+", "-"],
        "ArgListPrime": [",", "EPSILON"]
        }
        
        self.follow_sets = {
            "Program": ["$"],
            "DeclarationList": ["ID", ";", "NUM", "(", "}", "{", "break", "if", "while", "return", "+", "-", "$"],
            "Declaration": ["ID", ";", "NUM", "(", "}", "{", "break", "if", "while", "return", "+", "-", "int", "void","$"],
            "DeclarationInitial": ["[", "(", ")" , ",", ";"],
            "DeclarationPrime": ["ID", ";", "NUM", "(", "}", "{", "break", "if", "while", "return", "+", "-", "int", "void", "$"],
            "VarDeclarationPrime": ["ID", ";", "NUM", "(", "}", "{", "break", "if", "while", "return", "+", "-", "int", "void", "$"],
            "FunDeclarationPrime": ["ID", ";", "NUM", "(", "}", "{", "break", "if", "while", "return", "+", "-", "int", "void", "$"],
            "TypeSpecifier": ["ID"],
            "Params": [")"],
            "ParamList": [")"],
            "Param": [")", ","],
            "ParamPrime": [")", ","],
            "CompoundStmt": ["ID", ";", "NUM", "(", "}", "{", "int", "void", "break", "if", "else", "while", "return", "+", "-", "$"],
            "StatementList": ["}"],
            "Statement": ["ID", ";", "NUM", "(", "}", "{", "break", "if", "else", "while", "return", "+", "-", "$"],
            "ExpressionStmt": ["ID", ";", "NUM", "(", "}", "{", "break", "if", "else", "while", "return", "+", "-", "$"],
            "SelectionStmt": ["ID", ";", "NUM", "(", "}", "{", "break", "if", "else", "while", "return", "+", "-", "$"],
            "IterationStmt": ["ID", ";", "NUM", "(", "}", "{", "break", "if", "else", "while", "return", "+", "-", "$"],
            "ReturnStmt": ["ID", ";", "NUM", "(", "}", "{", "break", "if", "else", "while", "return", "+", "-", "$"],
            "ReturnStmtPrime": ["ID", ";", "NUM", "(", "}", "{", "break", "if", "else", "while", "return", "+", "-", "$"],
            "Expression": [";", "]", ")", ","],
            "B": [";", "]", ")", ","],
            "H": [";", "]", ")", ","],
            "SimpleExpressionZegond": [";", "]", ")", ","],
            "SimpleExpressionPrime": [";", "]", ")", ","],
            "C": [";", "]", ")", ","],
            "Relop": ["ID", "+", "-", "NUM", "("],
            "AdditiveExpression": [";", "]", ")", ","],
            "AdditiveExpressionPrime": [";", "]", ")", ",", "<", "=="],
            "AdditiveExpressionZegond": [";", "]", ")", ",", "<", "=="],
            "D": [";", "]", ")", ",", "<", "=="],
            "Addop": ["ID", "NUM", "(" "+", "-"],
            "Term": [";", "]", ")", ",", "<", "==", "+", "-"],
            "TermPrime": [";", "]", ")", ",", "<", "==", "+", "-"],
            "TermZegond": [";", "]", ")", ",", "<", "==", "+", "-"],
            "G": [";", "]", ")", ",", "<", "==", "+", "-"],
            "SignedFactor": [";", "]", ")", ",", "<", "==", "+", "-", "*"],
            "SignedFactorPrime":  [";", "]", ")", ",", "<", "==", "+", "-", "*"],
            "SignedFactorZegond": [";", "]", ")", ",", "<", "==", "+", "-", "*"],
            "Factor":             [";", "]", ")", ",", "<", "==", "+", "-", "*"],
            "VarCallPrime": [";", "]", ")", ",", "<", "==", "+", "-", "*"],
            "VarPrime": [";", "]", ")", ",", "<", "==", "+", "-", "*"],
            "FactorPrime": [";", "]", ")", ",", "<", "==", "+", "-", "*"],
            "FactorZegond": [";", "]", ")", ",", "<", "==", "+", "-", "*"],
            "Args": [")"],
            "ArgList": [")"],
            "ArgListPrime": [")"]
        }
        
        self.predict_sets = {
        "Program": {"int", "void", "$"},
        "DeclarationList": {"int", "void", "ID", ";", "NUM", "(", "}", "{", "break", "if", "while", "return", "+", "-", "$"},
        "Declaration": {"int", "void"},
        "DeclarationInitial": {"int", "void"},
        "DeclarationPrime": {";", "[", "("},
        "VarDeclarationPrime": {";", "["},
        "FunDeclarationPrime": {"("},
        "TypeSpecifier": {"int", "void"},
        "Params": {"int", "void"},
        "ParamList": {",", ")"},
        "Param": {"int", "void"},
        "ParamPrime": {"[", ")",","},
        "CompoundStmt": {"{"},
        "StatementList": {"ID", ";", "NUM", "(", "{", "break", "if", "while", "return", "+", "-", "}"},
        "Statement": {"ID", ";", "NUM", "(", "{", "break", "if", "while", "return", "+", "-"},
        "ExpressionStmt": {"ID", ";", "NUM", "(", "break", "+", "-"},
        "SelectionStmt": {"if"},
        "IterationStmt": {"while"},
        "ReturnStmt": {"return"},
        "ReturnStmtPrime": {"ID", ";", "NUM", "(", "+", "-"},
        "Expression": {"ID", "NUM", "(", "+", "-"},
        "B": {"=", "[", "(", "==", "+", "-", "<", "*", ";", "]", ")", ","},
        "H": {"=", "*", "+", "-", "<", "==", ";", "]", ")", ","},
        "SimpleExpressionZegond": {"NUM", "(", "+", "-"},
        "SimpleExpressionPrime": {"(", "+", "-", "<", "==", "*", ";", "]", ")", ","},
        "C": {"<", "==", ";", "]", ")", ","},
        "Relop": {"<", "=="},
        "AdditiveExpression": {"ID", "NUM", "(", "+", "-"},
        "AdditiveExpressionPrime": {"(", "+", "-", "*", ";", "]", ")", ",", "<", "=="},
        "AdditiveExpressionZegond": {"NUM", "(", "+", "-"},
        "D": {"+", "-", ";", "]", ")", ",", "<", "=="},
        "Addop": {"+", "-"},
        "Term": {"ID", "NUM", "(", "+", "-"},
        "TermPrime": {"(", "*", ";", "]", ")", ",", "<", "==", "+", "-"},
        "TermZegond": {"NUM", "(", "+", "-"},
        "G": {"*", ";", "]", ")", ",", "<", "==", "+", "-"},
        "SignedFactor": {"ID", "NUM", "(", "+", "-"},
        "SignedFactorPrime": {"(", ";", "]", ")", ",", "<", "==", "+", "-", "*"},
        "SignedFactorZegond": {"NUM", "(", "+", "-"},
        "Factor": {"ID", "NUM", "("},
        "VarCallPrime": {"(", "[", ";", "]", ")", ",", "<", "==", "+", "-", "*"},
        "VarPrime": {"[", ";", "]", ")", ",", "<", "==", "+", "-", "*"},
        "FactorPrime": {"(", ";", "]", ")", ",", "<", "==", "+", "-", "*"},
        "FactorZegond": {"NUM", "("},
        "Args": {"ID", "NUM", "(", "+", "-", ")"},
        "ArgList": {"ID", "NUM", "(", "+", "-"},
        "ArgListPrime": {",", ")"}
    }
        for term in self.terminal_names:
            self.get_or_create_terminal(term)

    def get_or_create_nt(self, name):
        if (name not in self.non_terminals):
            self.non_terminals[name] = Grammar.NonTerminal(name)
        return self.non_terminals[name]

    def get_or_create_terminal(self, name):
        if (name not in self.terminals):
            self.terminals[name] = Grammar.Terminal(name)
        return self.terminals[name]
    
    def get_or_create_action_symbol(self, name):
        #TODO
        if (str(name).startswith("#")):
            self.action_symbols[name] = Grammar.ActionSymbol(name)
        return self.action_symbols[name]
        

    def add_production(self, lhs_name, rhs_symbols):
        lhs = self.get_or_create_nt(lhs_name)

        if rhs_symbols == ['EPSILON']:
            lhs.goes_to_eps = True
            rule = Grammar.Rule(lhs, [])
        else:
            rhs = []
            for sym in rhs_symbols:
                if sym in self.terminal_names:
                    rhs.append(self.get_or_create_terminal(sym))
                elif str(sym).startswith("#"):
                    rhs.append(self.get_or_create_action_symbol(sym))
                else:
                    rhs.append(self.get_or_create_nt(sym))
            rule = Grammar.Rule(lhs, rhs)

        self.rules.append(rule)
        if lhs.name not in self.rule_map:
            self.rule_map[lhs.name] = []
        self.rule_map[lhs.name].append(rule)

    def load_predicts(self, filename='predict_sets.txt'):
        with open(filename) as f:
            for line in f:
                if ':' in line:
                    key, symbols = line.strip().split(':')
                    self.predict_sets[key.strip()] = set(symbols.strip().split())

    def load_sets(self, filename):
        sets = {}
        with open(filename) as f:
            for line in f:
                if ':' in line:
                    nt, items = line.strip().split(':')
                    sets[nt.strip()] = set(items.strip().split())
        return sets
    def get_predict(self, symbol):
        # Return an empty set if the symbol is not found in predict_sets
        return self.predict_sets.get(symbol, set())
    
    def get_follow(self, symbol):
        # Return an empty set if the symbol is not found in follow_sets
        return self.follow_sets.get(symbol, set())
    # def load_firsts(self, filename='firsts.txt'):
    #     self.first_sets = self.load_sets(filename)

    # def load_follows(self, filename='follow.txt'):
    #     self.follow_sets = self.load_sets(filename)
        
    def finalize(self, all_lhs):
    # Ensure all RHS symbols are registered as either terminals or non-terminals
        for rule in self.rules:
            new_rhs = []
            for sym in rule.rhs:
                if isinstance(sym, str):
                    if sym in all_lhs:
                        sym_obj = self.get_or_create_nt(sym)
                    elif str(sym).startswith("#"): #Phase 3: hard-coded
                        sym_obj = self.get_or_create_action_symbol(sym)
                    else:
                        sym_obj = self.get_or_create_terminal(sym)
                    new_rhs.append(sym_obj)
                else:
                    new_rhs.append(sym)  # Already a Terminal or NonTerminal object
            rule.rhs = new_rhs
            
            
    def print_grammar(self):
        print("=== Non-Terminals ===")
        for nt in self.non_terminals.values():
            print(f"{nt.name} (goes_to_eps: {nt.goes_to_eps})")

        print("\n=== Terminals ===")
        for t in self.terminals.values():
            print(t.name)

        print("\n=== Production Rules ===")
        for rule in self.rules:
            print(rule)

        print("\n=== FIRST Sets ===")
        for nt, f in self.first_sets.items():
            print(f"{nt}: {sorted(f)}")

        print("\n=== FOLLOW Sets ===")
        for nt, f in self.follow_sets.items():
            print(f"{nt}: {sorted(f)}")
