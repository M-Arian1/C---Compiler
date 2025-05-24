import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Phase2.src.Grammar import Grammar                # Your Grammar class
from Phase2.src.GrammarBuilder import GrammarBuilder
from Phase1.scanner import Scanner         # Scanner from Phase1
from Phase2.src.TransitionDiagram import DiagramBuilder  # Builder for diagrams
from Phase2.src.TopDownParser import DiagramParser           # Parser implementation

def main():
    print("Starting compiler...")
    # Step 1: Initialize Scanner
    input_code = open('Phase1/src/inputfiles/input.txt').read()  # Adjust path if needed
    print("Input code loaded...")
    scanner = Scanner(input_code)
    print("Scanner initialized...")
    
    # Step 2: Build Grammar
    grammar = GrammarBuilder.get_grammar()
    print("Grammar built...")

    # Step 3: Build Transition Diagrams
    print("Building transition diagrams...")
    diagram_builder = DiagramBuilder(grammar)
    diagrams = diagram_builder.build_all()
    print("Transition diagrams built...")

    # Step 4: Parse using DiagramParser
    print("Starting parsing...")
    parser = DiagramParser(grammar, diagrams, scanner)
    try:
        parse_tree = parser.parse("Program")  # Replace with your actual start symbol
        print("\nParse Tree:")
        for step in parse_tree:
            print(step)
        print("\nParsing completed successfully.")
    except Exception as e:
        print("Parsing failed with error:")
        print(str(e))
        print("Stack trace:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
