"""
Mehrazin Malekghasemi 401100539
Mohammad Arian Iravani 401110397
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))


from tables.Tables import SymbolTable, ErrorTable, TokenTable
from src.AutomataBuilder import AutomataBuilder
from src.Automata import Automaton, State, Alphabet, Error
from src.InputReader import InputReader
from src.Automata import StateType
from src.Tokens import Token


def get_next_token():
    global C_minus_scanner
    global input_reader
    
    state = C_minus_scanner.getStartState()
    counter = 0
    token = ""
    # print(state.get_name())
    
    while state.type[0] == StateType.INTER:
        char = input_reader.get_next_char()
        if not char :  # Check for EOF
            break
        # if char == chr(26) :
        #     stripped_tok = token.strip()
        #     if (stripped_tok.startswith("/*")):
                
        #         final_state = State((StateType.ERROR, Error.UNCLOSED_COMMENT))
                
        #         return final_state, token, input_reader.get_line_no()
        #     else:
        #         break
      
       
            
            
        
        new_state = C_minus_scanner.next_state(state, char)
        # print(new_state.get_name(), token)
        if not new_state:
            input_reader.push_back(char)
            break
            
        state = new_state
        token += char
        counter += 1

    
    if not state :
        
        input_reader.push_back(token[-1])
        token = token[:-1]
        return C_minus_scanner.default_panic_state, token, input_reader.get_line_no()
        
    final_state = state
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
        # print("new token " + token+"\n")
        # print("\n"+'"""')
        # print(token)
        # print(state.get_name())
        # print('"""' + '\n')
        if not token:
            continue
            
        # Check for comments
        if token.startswith("/*"):
            in_comment = True
            comment_buffer = token
            
            
        if in_comment:
            comment_buffer += token
            if token.endswith("*/"):
                in_comment = False
                # token_table.add_token(state_type=(StateType.ACCEPT, Token.COMMENT), token=comment_buffer, line_no=line_no)
                comment_buffer = ""
            else:
                if state.type[0] == StateType.ERROR and state.type[1] == Error.UNCLOSED_COMMENT:
                    error_table.add_record(token, state, line_no)
            continue        
                
            
                
                
       
        # Process token based on its content rather than relying solely on state
        token_stripped = token.strip()
        # print("type",state.type)
        if state.type[0] == StateType.ERROR:
            # print(state.get_name())
            if(state.type [1] == Error.UNCLOSED_COMMENT):
                if "\n" in token:
                    token = token.split()[0]
                    first_word = token.strip()[:7]
                    error_table.add_record(f"{first_word}...", state, line_no)
                else:
                    error_table.add_record(token, state, line_no)
            else:
                error_table.add_record(token, state, line_no)
        
            
       
        else:
            # Classic token classification approach
            
            if state.type[0] == StateType.END:
                continue
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