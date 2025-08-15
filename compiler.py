
"""
Mehrazin Malekghasemi 401100539
Mohammad Arian Iravani 401110397
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase2.src.Grammar import Grammar                # Grammar class with predict/follow
from Phase2.src.GrammarBuilder import GrammarBuilder
from Phase1.scanner import Scanner                    # Your scanner class
from Phase2.src.TransitionDiagram import DiagramBuilder  # Diagram builder
from Phase2.src.TopDownParser import DiagramParser       # Diagram-based parser
from Phase3.src.SemanticStack import SemanticStack

def main():
    # Step 2: Initialize scanner
    scanner = Scanner()

    # Step 3: Build grammar
    grammar = GrammarBuilder.get_grammar()

    # Step 4: Build diagrams
    diagram_builder = DiagramBuilder(grammar)
    diagrams = diagram_builder.build_all()
    diagram_builder.print_diagrams()

    # Step 5: Parse
    parser = DiagramParser(grammar, diagrams, scanner)

    try:
        parse_tree = parser.parse("Program")  # Entry point for parsing
        with open('parse_tree.txt', 'w') as f:
            f.write(str(parse_tree))
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
