import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase2.src.Grammar import Grammar                # Grammar class with predict/follow
from Phase2.src.GrammarBuilder import GrammarBuilder
from Phase1.scanner import Scanner                    # Your scanner class
from Phase2.src.TransitionDiagram import DiagramBuilder  # Diagram builder
from Phase2.src.TopDownParser import DiagramParser       # Diagram-based parser

def main():
    print("Starting compiler...")

    # # Step 1: Load input
    # try:
    #     with open('Phase1/src/inputfiles/input.txt', 'r') as f:
    #         input_code = f.read()
    # except FileNotFoundError:
    #     print("Error: input.txt not found.")
    #     return

    # print("Input code loaded...")

    # Step 2: Initialize scanner
    scanner = Scanner()
    print("Scanner initialized...")

    # Step 3: Build grammar
    grammar = GrammarBuilder.get_grammar()
    print("Grammar built...")

    # Step 4: Build diagrams
    print("Building transition diagrams...")
    diagram_builder = DiagramBuilder(grammar)
    diagrams = diagram_builder.build_all()
    print("Transition diagrams built...")
    
    diagram_builder.print_diagrams()

    # Step 5: Parse
    print("Starting parsing...")
    parser = DiagramParser(grammar, diagrams, scanner)
    # grammar.print_grammar()

    try:
        parse_tree = parser.parse("Program")  # Entry point for parsing
        print("\nParse Tree:")
        print(parse_tree)  # This will use the ParseNode's __str__ method
        # Save parse tree to file
        with open('parse_tree.txt', 'w') as f:
            f.write(str(parse_tree))

        print("\nParsing completed successfully.")
    except Exception as e:
        print("Parsing failed with error:")
        print(str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
