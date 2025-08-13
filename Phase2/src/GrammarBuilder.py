import os
from Phase2.src.Grammar import Grammar

class GrammarBuilder:
    @staticmethod
    def get_grammar():
        g = Grammar()
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        grammar_file = os.path.join(base_path, 'data', 'actioned_grammar.txt')  #Phase3: we should change the path to be Phase3/grammar.txt
        all_lhs = []

        # First pass: gather all LHS symbols
        with open(grammar_file, encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and '~' in line]
            for line in lines:
                lhs = line.split('~')[0].strip()
                all_lhs.append(lhs)

        # Second pass: parse and add productions
        with open(grammar_file, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '~' not in line:
                    continue

                lhs, rhs_all = line.split('~')
                lhs = lhs.strip()
                rhs_alternatives = rhs_all.strip().split('|')

                for alt in rhs_alternatives:
                    rhs_symbols = alt.strip().split()
                    g.add_production(lhs, rhs_symbols)

        # Finalize to determine terminals/non-terminals
        g.finalize(all_lhs)

        # Load FIRST, FOLLOW, and PREDICT sets
        # g.load_firsts(os.path.join(base_path, 'data', 'firsts.txt'))
        # g.load_follows(os.path.join(base_path, 'data', 'follows.txt'))
        g.load_predicts(os.path.join(base_path, 'data', 'predict_sets.txt'))

        return g
