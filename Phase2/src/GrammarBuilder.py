from Grammar import Grammar

def read_grammar_file(filename='grammar.txt'):
    g = Grammar()
    with open(filename) as f:
        for line in f:
            if '→' not in line:
                continue
            lhs, rhs = line.strip().split('→')
            lhs = lhs.strip()
            rhs_symbols = rhs.strip().split()
            g.add_production(lhs, rhs_symbols)
    g.finalize()
    return g

def get_grammar():
    g = read_grammar_file()
    g.load_firsts('firsts.txt')
    g.load_follows('follow.txt')
    g.load_predicts('predict_sets.txt')
    # g.print_grammar()
    return g


