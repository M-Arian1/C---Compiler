# C-minus compiler

A one-pass compiler written in Python for **C-minus**, a small subset of C. It goes from source code to three-address code: a DFA-based scanner, a predictive (LL(1)) parser driven by transition diagrams, and syntax-directed code generation with a semantic stack.

Compiler Design course project, Sharif University of Technology (2025), by **Arian Tehrani** and **Mehrazin Malekghasemi**.

## Pipeline
1. **Lexical analysis** (`Phase1/`): a hand-built DFA recognises keywords, identifiers, numbers, symbols and both comment styles. It fills the symbol table and reports lexical errors (invalid numbers, invalid input, unclosed or unmatched comments) with line numbers, then keeps going.
2. **Syntax analysis** (`Phase2/`): the grammar (`Phase2/data/grammar.txt`) is left-factored and free of left recursion. Its FIRST, FOLLOW and predict sets are computed and saved (`firsts.txt`, `follows.txt`, `predict_sets.txt`), and each non-terminal becomes a transition diagram. The parser walks these diagrams, builds the parse tree and recovers from syntax errors using FOLLOW sets.
3. **Semantic analysis and code generation** (`Phase3/`): action symbols in `actioned_grammar.txt` fire during parsing. A semantic stack, scoped symbol tables and a memory layout (code, data and temporaries) generate three-address instructions (`ASSIGN, ADD, SUB, MULT, EQ, LT, JPF, JP, PRINT`) for expressions, assignments, `if`/`else`, `while` with `break`, arrays, functions and `return`, and the built-in `output()`.

## Run
```bash
python compiler.py          # reads input.txt from the project root
```
Outputs: `output.txt` (three-address code, one numbered instruction per line), `parse_tree.txt` and `syntax_errors.txt`.

## Example
```c
void main(void) {
    int i;
    i = 0;
    while (i < 3) {
        output(i);
        i = i + 1;
    }
}
```

## Layout
```
compiler.py               entry point: scanner -> grammar -> diagrams -> parser + code generator
Phase1/                   DFA scanner, token types, symbol/error tables
Phase2/                   grammar, FIRST/FOLLOW/predict sets, transition-diagram parser, parse tree
Phase3/                   semantic stack, memory model, three-address code generator
```

## License
MIT, see [LICENSE](LICENSE).
