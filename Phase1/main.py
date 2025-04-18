import sys
import os
sys.path.append(os.path.dirname(__file__))


from tables.Tables import SymbolTable, ErrorTable, TokenTable
from src.AutomataBuilder import AutomataBuilder
from src.InputReader import InputReader


def get_next_token():
    
    global C_minus_scanner
    global input_reader
    
    states = [C_minus_scanner.getStartState()]
    counter = 0
    token = ""
    while states:
        char = input_reader.get_next_char()
        if not char:
            break
        new_states = C_minus_scanner.next_states(states,char)
        if not new_states:
            input_reader.back()
            break
        states = new_states
        token += char
        counter += 1
        
    final_state = states[0]
    if(final_state.is_push_back_needed):
        input_reader.push_back()
    return final_state, token, input_reader.get_line_no
    


def main():
    global C_minus_scanner
    global input_reader
    C_minus_scanner = AutomataBuilder()
    input_reader = InputReader('input.txt')
    #TODO: complete and generate files, then run tests
    sym_table = SymbolTable(['break', 'else', 'if', 'int', 'while', 'return', 'void', 'main'])
    error_table = ErrorTable()
    token_table = TokenTable()
    
    
    while input_reader.get_next_char != '':
        input_reader.push_back()
        state, token, line_no = get_next_token()
        if (state.type[0] == StateType.Error):
            error_table.add_record(token, state)
        else:
            token_table.add_token(state, token, line_no)
            if (state.type[1] == Token.SYMBOL or state.type[1] == Token.ID):
                sym_table.add_symbol({"name" : token})
            
    token_table.write_to_file(token_table.generate_text,"tokens.txt")
    sym_table.write_to_file(sym_table.sym_to_text, "symbol_table.txt")
    error_table.write_to_file(error_table.generate_error_text, "lexical_errors.txt")        
    
    if __name__=="__main__":
        main()