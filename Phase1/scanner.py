import sys
import os
sys.path.append(os.path.dirname(__file__))


from tables.Tables import SymbolTable, ErrorTable, TokenTable
from src.AutomataBuilder import AutomataBuilder
from src.Automata import Automaton, State, Alphabet, Error
from src.InputReader import InputReader
from src.Automata import StateType
from src.Tokens import Token


class Scanner:
    def __init__(self):
        self.C_minus_scanner = AutomataBuilder()
        self.input_reader = InputReader('input.txt')
    
    def input_reader_has_next(self):
        return self.input_reader.has_next()

    def get_next_token_from_source(self):
    
        state = self.C_minus_scanner.getStartState()
        counter = 0
        token = ""
        
        while state.type[0] == StateType.INTER:
            if InputReader.has_next:
                char = self.input_reader.get_next_char()
            else:
                return State((StateType.END, Token.EOF)), '$', counter
            
            if not char :  # Check for EOF
                break

            new_state = self.C_minus_scanner.next_state(state, char)
            if not new_state:
                self.input_reader.push_back(char)
                break
                
            state = new_state
            token += char
            counter += 1

        
        if not state :
            
            self.input_reader.push_back(token[-1])
            token = token[:-1]
            return self.C_minus_scanner.default_panic_state, token, self.input_reader.get_line_no()
            
        final_state = state
        if final_state.push_back_needed:
            self.input_reader.push_back(token[-1])
            token = token[:-1]
        return final_state, token, self.input_reader.get_line_no()

    def get_next_token(self):
        state, token, line_no = self.get_next_token_from_source()
        keywords = ['break', 'else', 'if', 'int', 'while', 'return', 'void']
        if   state.type[1].value  == Token.SYMBOL.value or  state.type[1].value  == Token.NUM.value:
            token_stripped = token.strip()
            
            return state, token_stripped, line_no
        
        elif state.type[1].value == Token.ID.value or  state.type[1].value == Token.KEYWORD.value :
            token_stripped = token.strip()
            if token_stripped in keywords:
                state = (State((StateType.ACCEPT, Token.KEYWORD), push_back_needed=True, name="state_txt_id"))
            return state, token_stripped, line_no
        
                
        elif token.strip() == chr(26):
            return state, '$', line_no
        else: #error or ws or comment
            return self.get_next_token()