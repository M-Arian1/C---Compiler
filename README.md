# C--- Compiler

A modular compiler implementation for C---, a simplified version of the C programming language, developed as an educational project.

## Project Overview

This compiler is built with multiple phases that correspond to the standard compiler pipeline:

1. **Lexical Analysis (Phase 1)** - Tokenizes the input source code
2. **Syntax Analysis** - Parses tokens and builds a parse tree 
3. **Semantic Analysis** - Checks for semantic correctness
4. **Code Generation** - Generates intermediate or target code

The current implementation includes Phase 1, which performs lexical analysis on the input code.

## Phase 1: Lexical Analysis

The lexical analyzer (scanner) reads input characters and groups them into tokens. It uses a deterministic finite automaton (DFA) to recognize patterns in the input and categorizes them into:

- Keywords (`if`, `else`, `int`, `while`, etc.)
- Identifiers
- Numbers
- Symbols (`+`, `-`, `*`, etc.)
- Comments (both single-line and multi-line)

The scanner also handles errors such as:
- Invalid numbers
- Invalid inputs
- Unclosed comments
- Unmatched comments

### Output Files

Phase 1 produces the following output files:
- `tokens.txt` - List of recognized tokens
- `symbol_table.txt` - Table of identifiers and keywords
- `lexical_errors.txt` - List of lexical errors encountered during scanning

## Project Structure

```
C---Compiler/
├── Phase1/
│   ├── main.py                     # Main entry point for the compiler
│   ├── src/
│   │   ├── Automata.py             # DFA implementation
│   │   ├── AutomataBuilder.py      # Builder for the lexical analyzer's DFA
│   │   ├── InputReader.py          # Handles reading from input files
│   │   ├── Tokens.py               # Token type definitions
│   │   ├── inputfiles/             # Contains input source files
│   │   └── outputfiles/            # Contains generated output files
│   └── tables/
│       └── Tables.py               # Symbol, error, and token table implementations
```

## Getting Started

### Prerequisites

- Python 3.x

### Running the Compiler

1. Clone the repository
2. Navigate to the project root directory
3. Place your C--- source code in `Phase1/src/inputfiles/input.txt`
4. Run the compiler:

```bash
python Phase1/main.py
```

5. Check the output files in `Phase1/src/outputfiles/`

## Language Syntax

C--- supports a subset of C syntax, including:

- Variable declarations (e.g., `int x;`)
- Array declarations (e.g., `int arr[10];`)
- Function declarations and definitions
- Control structures (if statements, while loops)
- Expressions and assignments
- Comments (both single-line `//` and multi-line `/* */`)

## Future Development

Upcoming phases will include:
- Phase 2: Syntax Analysis (Parser)
- Phase 3: Semantic Analysis
- Phase 4: Code Generation

## License

This project is open-source and available for educational purposes.

## Acknowledgements

This project draws inspiration from compiler design principles and techniques taught in computer science courses.
