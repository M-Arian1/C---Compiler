import os
from Phase2.src.Grammar import Grammar

class GrammarBuilder:
    @staticmethod
    def get_grammar():
        g = Grammar()
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        grammar_file = os.path.join(base_path, 'data', 'grammar.txt')

        # Read grammar file and add productions
        with open(grammar_file, encoding='utf-8') as f:
            
            for line in f:
                
                line = line.strip()
                print(line)
                if not line or '~' not in line:
                    # print("nl")
                    continue

                lhs, rhs_all = line.split('~')
                lhs = lhs.strip()
                # print("lhs", lhs)
                rhs_alternatives = rhs_all.strip().split('|')
                
                for alt in rhs_alternatives:
                    rhs_symbols = alt.strip().split()
                    g.add_production(lhs, rhs_symbols)

        g.finalize()

        # Load FIRST, FOLLOW, and PREDICT sets
        # g.load_firsts(os.path.join(base_path, 'data', 'firsts.txt'))
        # g.load_follows(os.path.join(base_path, 'data', 'follows.txt'))
        g.load_predicts(os.path.join(base_path, 'data', 'predict_sets.txt'))

        return g
