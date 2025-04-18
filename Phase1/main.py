import sys
import os
sys.path.append(os.path.dirname(__file__))


from tables.Tables import SymbolTable, ErrorTable, TokenTable
from src.AutomataBuilder import AutomataBuilder
from src.InputReader import InputReader
from src.Automata import StateType
from src.Tokens import Token


def get_next_token():
    global C_minus_scanner
    global input_reader
    
    states = [C_minus_scanner.getStartState()]
    counter = 0
    token = ""
    
    while states:
        char = input_reader.get_next_char()
        if not char or char == chr(26):  # Check for EOF
            break
        
        new_states = C_minus_scanner.next_states(states, char)
        if not new_states:
            input_reader.push_back(char)
            break
            
        states = new_states
        token += char
        counter += 1
    
    if not states:
        return C_minus_scanner.default_panic_state, token, input_reader.get_line_no()
        
    final_state = states[0]
    if final_state.push_back_needed:
        input_reader.push_back(token[-1])
        token = token[:-1]
    
    return final_state, token, input_reader.get_line_no()

def is_comment_token(token):
    return token.strip().startswith('/*') and token.strip().endswith('*/')

def main():
    global C_minus_scanner
    global input_reader
    C_minus_scanner = AutomataBuilder()
    input_reader = InputReader('Phase1/src/inputfiles/input.txt')
    
    # Define keywords list
    keywords = ['break', 'else', 'if', 'int', 'while', 'return', 'void']
    
    sym_table = SymbolTable(keywords)
    error_table = ErrorTable()
    token_table = TokenTable()
    
    in_comment = False
    comment_buffer = ""
    
    while input_reader.has_next():
        state, token, line_no = get_next_token()
        if not token:
            continue
            
        # Check for comments
        if token.strip() == "/*":
            in_comment = True
            comment_buffer = token
            continue
            
        if in_comment:
            comment_buffer += token
            if token.strip() == "*/":
                in_comment = False
                token_table.add_token(state_type=(StateType.ACCEPT, Token.COMMENT), token=comment_buffer, line_no=line_no)
                comment_buffer = ""
            continue
            
        # Process token based on its content rather than relying solely on state
        token_stripped = token.strip()
        
        if state.type[0] == StateType.ERROR:
            error_table.add_record(token, state, line_no)
        else:
            # Classic token classification approach
            if token_stripped in keywords:
                token_table.add_token(state_type=(StateType.ACCEPT, Token.KEYWORD), token=token, line_no=line_no)
                sym_table.add_symbol({"name": token_stripped})
            elif token_stripped.isdigit():
                # Handle numbers
                token_table.add_token(state_type=(StateType.ACCEPT, Token.NUM), token=token, line_no=line_no)
            elif token_stripped.isalnum() and token_stripped and not token_stripped[0].isdigit():
                # Handle identifiers
                token_table.add_token(state_type=(StateType.ACCEPT, Token.ID), token=token, line_no=line_no)
                sym_table.add_symbol({"name": token_stripped})
            elif token_stripped in ['+', '-', '*', '/', '<', '=', '==', ';', ':', ',', '[', ']', '(', ')', '{', '}']:
                # Handle symbols
                token_table.add_token(state_type=(StateType.ACCEPT, Token.SYMBOL), token=token, line_no=line_no)
            elif isinstance(state.type, tuple) and len(state.type) > 1:
                # State-based classification as fallback
                if state.type[1] == Token.COMMENT:
                    continue  # Skip comments in token table output
                token_table.add_token(state, token, line_no)
            else:
                # Last resort using the token's content to classify
                if '==' in token_stripped:
                    token_table.add_token(state_type=(StateType.ACCEPT, Token.SYMBOL), token=token, line_no=line_no)
                else:
                    token_table.add_token(state, token, line_no)
    
    token_table.write_to_file(token_table.generate_text(), "Phase1/src/outputfiles/tokens.txt")
    sym_table.write_to_file(sym_table.sym_to_text(), "Phase1/src/outputfiles/symbol_table.txt")
    error_table.write_to_file(error_table.generate_error_text(), "Phase1/src/outputfiles/lexical_errors.txt")

if __name__=="__main__":
    main()