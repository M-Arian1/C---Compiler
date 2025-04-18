from src.Automata import *
from src.Tokens import *

class AutomataBuilder:
    def __init__(self):
        self.automaton = self.buildAutomaton()
        
    def getStartState(self):
        return self.automaton.get_start_state()
        
    def next_state(self, state, char):
        return self.automaton.next_state(state, char)

        
    @staticmethod

    def buildAutomaton():
        start_state = State(name="start_state")
        panic_alphabet = Alphabet().include_all_chars().exclude(('a', 'z')) \
                                    .exclude(('A', 'Z')) \
                                    .exclude(('0', '9')) \
                                    .exclude((',', ',')).exclude((':', ':')).exclude((';', ';')) \
                                    .exclude(('[', '[')).exclude((']', ']')).exclude(('(', '(')) \
                                    .exclude((')', ')')).exclude(('{', '{')).exclude(('}', '}')) \
                                    .exclude(('+', '+')).exclude(('-', '-')).exclude(('*', '*')) \
                                    .exclude(('/', '/')).exclude(('=', '=')) \
                                    .exclude(('<', '<')).exclude((' ', ' ')) \
                                    .exclude(('\t', '\t')).exclude(('\n', '\n')).exclude(('\r', '\r')) \
                                    .exclude(('\f', '\f')).exclude(('\v', '\v'))\
                                    .exclude(('/', '/'))\
                                    .exclude((chr(26), chr(26)))
        
        automaton = Automaton(start_state, panic_alphabet)
        
        # STATES DEFINITION WITH NAMES
        end_state = State(name="end_state",type = (StateType.END, ))
        state_no_1 = State(name="state_no_1")
        state_num = State((StateType.ACCEPT, Token.NUM), push_back_needed=True, name="state_num")
        err_state_inv_num = State((StateType.ERROR, Error.INVALID_NUM), name="err_state_inv_num")
        
        state_symbol = State((StateType.ACCEPT, Token.SYMBOL), name="state_symbol")
        state_assign = State(name="state_assign")
        state_equal = State((StateType.ACCEPT, Token.SYMBOL), name="state_equal")  # For == symbol
        
        state_no_2 = State(name="state_no_2")
        err_state_unmatched_comm = State((StateType.ERROR, Error.UNMATCHED_COMMENT), name="err_state_unmatched_comm")
        state_symb_type_2 = State((StateType.ACCEPT, Token.SYMBOL), push_back_needed=True, name="state_symb_type_2")
        
        state_comm_slash = State(name="state_comm_slash")
        state_comm_star = State(name="state_comm_star")
        state_no_3 = State(name="state_no_3")
        state_unclosed_comm = State((StateType.ERROR, Error.UNCLOSED_COMMENT), name="state_unclosed_comm", push_back_needed= True)
        state_comment = State((StateType.ACCEPT, Token.COMMENT), name="state_comment")
        
        state_no_4 = State(name="state_no_4")
        state_txt_id = State((StateType.ACCEPT, Token.ID), push_back_needed=True, name="state_txt_id")
        
        # Add states to automaton
        automaton.add_state(state_no_1)
        automaton.add_state(state_num)
        automaton.add_state(err_state_inv_num)
        
        automaton.add_state(state_symbol)
        automaton.add_state(state_assign)
        automaton.add_state(state_equal)
        
        automaton.add_state(state_no_2)
        automaton.add_state(err_state_unmatched_comm)
        automaton.add_state(state_symb_type_2)
        
        automaton.add_state(state_comm_slash)
        automaton.add_state(state_comm_star, False)
        # automaton.add_transition(state_comm_star, end_state, panic_alphabet)
        automaton.add_state(state_no_3)
        automaton.add_state(state_unclosed_comm)
        automaton.add_state(state_comment)
        
        automaton.add_state(state_no_4)
        automaton.add_state(state_txt_id)
        
        # State Transitions (example for a few transitions)
        alph_eof = Alphabet()
        # EOF = chr(26)
        automaton.add_transition(start_state, end_state, alph_eof)
        
        alph_ws = Alphabet()
        for ws in [' ', '\t', '\n', '\r', '\f', '\v']:
            alph_ws.include((ws, ws))
        automaton.add_transition(start_state, start_state, alph_ws)
        
        alph_dig = Alphabet()
        alph_dig.include(('0', '9'))
        automaton.add_transition(start_state, state_no_1, alph_dig)
        automaton.add_transition(state_no_1, state_no_1, alph_dig)
        
        #State Transitions
        alph_eof = Alphabet()
        alph_eof.include((chr(26), chr(26)))
        #EOF = chr(26)
        
        automaton.add_transition(start_state, end_state, alph_eof)
        
        alph_ws = Alphabet()
        for ws in [' ', '\t', '\n', '\r', '\f', '\v']:
            alph_ws.include((ws, ws))
        automaton.add_transition(start_state, start_state, alph_ws)
        
        alph_dig = Alphabet()
        alph_dig.include(('0','9'))
        automaton.add_transition(start_state, state_no_1, alph_dig)
        automaton.add_transition(state_no_1, state_no_1, alph_dig)
        
        alph_ws_s_eof = Alphabet()
        for ws in [' ', '\t', '\n', '\r', '\f', '\v']:
            alph_ws_s_eof.include((ws, ws))
        for sym in [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '/', '=', '<']:
            alph_ws_s_eof.include((sym, sym))
            
        alph_ws_s_eof.include((chr(26), chr(26)))  
        automaton.add_transition(state_no_1, state_num, alph_ws_s_eof)
        
        alph_letter = Alphabet()
        alph_letter.include(('A','Z'))
        alph_letter.include(('a','z'))
        automaton.add_transition(state_no_1, err_state_inv_num, alph_letter)
        
        
        
        alph_syms = Alphabet()
        for sym in [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '<']:
            alph_syms.include((sym, sym))
        automaton.add_transition(start_state, state_symbol, alph_syms)
        
        alph_eq_sign = Alphabet()
        alph_eq_sign.include(('=','='))
        automaton.add_transition(start_state, state_assign, alph_eq_sign)
        
        alph_slash = Alphabet()
        alph_slash.include(('/', '/'))
        # Handle == comparison operator
        automaton.add_transition(state_assign, state_equal, alph_eq_sign)
        automaton.add_transition(state_assign, state_comm_slash, alph_slash)
        
        alph_ws_dig_let = Alphabet()
        for ws in [' ', '\t', '\n', '\r', '\f', '\v']:
            alph_ws_dig_let.include((ws, ws))
        alph_ws_dig_let.include(('A','Z'))
        alph_ws_dig_let.include(('a','z'))
        alph_ws_dig_let.include(('0','9'))
        automaton.add_transition(state_assign, state_symb_type_2, alph_ws_dig_let)
        
        alph_star = Alphabet()
        alph_star.include(('*','*'))
        automaton.add_transition(start_state, state_no_2, alph_star)
        
        automaton.add_transition(state_no_2, err_state_unmatched_comm, alph_slash)
        automaton.add_transition(state_no_2, state_symb_type_2, alph_ws_dig_let)
        
        # Handle comments
        automaton.add_transition(start_state, state_comm_slash, alph_slash)
        automaton.add_transition(state_comm_slash, state_symb_type_2, alph_ws_dig_let)
        automaton.add_transition(state_comm_slash, state_comm_star, alph_star)
        
        alph_any_but_star_eof = Alphabet().include_all_chars()
        alph_any_but_star_eof.exclude(('*','*')).exclude((chr(26), chr(26)))
        automaton.add_transition(state_comm_star, state_comm_star, alph_any_but_star_eof)
        automaton.add_transition(state_comm_star, state_unclosed_comm, alph_eof)
        automaton.add_transition(state_comm_star, state_no_3, alph_star)
        
        alph_any_but_slsh_eof = Alphabet().include_all_chars()
        alph_any_but_slsh_eof.exclude((chr(26), chr(26))).exclude(('/', '/'))
        automaton.add_transition(state_no_3, state_comm_star, alph_any_but_slsh_eof)
        automaton.add_transition(state_no_3, state_unclosed_comm, alph_eof)
        automaton.add_transition(state_no_3, state_comment, alph_slash)
        
        automaton.add_transition(start_state, state_no_4, alph_letter)
        alph_let_dig = Alphabet()
        alph_let_dig.include(('A', 'Z'))
        alph_let_dig.include(('a', 'z'))
        alph_let_dig.include(('0', '9'))
        automaton.add_transition(state_no_4, state_no_4, alph_let_dig)
        automaton.add_transition(state_no_4, state_txt_id, alph_ws_s_eof)
        
        # Handle symbols that directly follow other characters
        alph_sym_chars = Alphabet()
        for sym in [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '/', '=', '<']:
            alph_sym_chars.include((sym, sym))
        automaton.add_transition(state_no_4, state_symb_type_2, alph_sym_chars)
        automaton.add_transition(state_no_1, state_symb_type_2, alph_sym_chars)
        
        alph = Alphabet().include_all_chars()
        
        # print(panic_alphabet.is_in_alphabet('/'))  # True (ASCII 47)
        
        return automaton
