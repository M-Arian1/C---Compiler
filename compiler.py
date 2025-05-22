from Grammar import Grammar                # Your Grammar class
from GrammarBuilder import GrammarBuilder
from Phase1.scanner import Scanner         # Corrected import for Scanner in Phase1 package
from TransitionDiagram import DiagramBuilder  # Your builder for diagrams
from TopDownParser import DiagramParser           # The parser you implemented

def main():
    # Step 1: Initialize Scanner
    input_code = open('input.txt').read()  # Adjust path if needed
    scanner = Scanner(input_code)
    grammar = GrammarBuilder.get_grammar()
    # Step 2: Build Grammar
    

    # Step 3: Build Transition Diagrams
    diagram_builder = DiagramBuilder(grammar)
    diagrams = diagram_builder.build_all()

    # Step 4: Parse using DiagramParser
    parser = DiagramParser(grammar, diagrams, scanner)
    try:
        parse_tree = parser.parse("Program")  # Replace with your actual start symbol
        print("Parse Tree:")
        for step in parse_tree:
            print(step)
        print("\nParsing completed successfully.")
    except Exception as e:
        print("Parsing failed with error:")
        print(e)

if __name__ == "__main__":
    main()
