import os
from Phase2.src.Grammar import Grammar

class GrammarBuilder:
    @staticmethod
    def get_grammar():
        g = Grammar()
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        grammar_file = os.path.join(base_path, 'data', 'grammar.txt')
        
        # Read grammar file
        with open(grammar_file, encoding='utf-8') as f:
            for line in f:
                if '→' not in line:
                    continue
                lhs, rhs = line.strip().split('→')
                lhs = lhs.strip()
                rhs_symbols = rhs.strip().split()
                g.add_production(lhs, rhs_symbols)
        g.finalize()
        
        # Load additional data
        g.load_firsts(os.path.join(base_path, 'data', 'firsts.txt'))
        g.load_follows(os.path.join(base_path, 'data', 'follows.txt'))
        g.load_predicts(os.path.join(base_path, 'data', 'predict_sets.txt'))
        return g

