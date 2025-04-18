from Phase1.src.AutomataBuilder import AutomataBuilder
from Phase1.src.InputReader import InputReader

from src import *
from tables import *

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
    
    