from Automata import *



# class Token(Enum):
#     NUM = 0
    
class AutomataBuilder:
    def __init__(self) :
        pass
        
    
    def buildAutomaton():
        
        start_state = State()
        automaton = Automaton(start_state)
        
        #STATES DEFINITION
        end_state = State(type= 1)
        
        state_no_1 = State(type= 0)
        state_num = State(type= 0)
        err_state_inv_num = State(type= 2)
        
        state_symbol = State(type= 1)
        state_assign = State(type= 0)
        
        state_no_2 = State(type= 0)
        err_state_unmatched_comm = State(type= 2)
        state_symb_type_2 = State(type= 1)
        
        state_comm_start = State(type= 0)
        state_comm_star = State(type = 0)
        state_no_3 = State(type= 0)
        state_unclosed_comm = State(type= 2)
        state_comment = State(type= 1)
        
        state_no_4 = State(type= 0)
        state_txt_id = State(type= 1)
        
        automaton.add_state(state_no_1)
        automaton.add_state(state_num)
        automaton.add_state(err_state_inv_num)
        
        automaton.add_state(state_symbol)
        automaton.add_state(state_assign)
        
        automaton.add_state(state_no_2)
        automaton.add_state(err_state_unmatched_comm)
        automaton.add_state(state_symb_type_2)
        
        automaton.add_state(state_comm_start)
        automaton.add_transition(state_comm_star)
        automaton.add_state(state_no_3)
        automaton.add_state(state_unclosed_comm)
        automaton.add_state(state_comment)
        
        automaton.add_state(state_no_4)
        automaton.add_state(state_txt_id)
        
        #State Transitions
        alph_eof = Alphabet()
        #EOF = chr(26)
        alph_ws_s_eof.include((chr(26), chr(26)))
        automaton.add_trasition(start_state, end_state, alph_eof)
        
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
        alph_ws_s_eof.include((chr(26), chr(26)))
        automaton.add_transition(state_no_1, state_num, alph_ws_s_eof)
        
        alph_letter = Alphabet()
        alph_letter.include(('A','Z'))
        alph_letter.include(('a','z'))
        automaton.add_transition(state_no_1, err_state_inv_num)
        
        
        
        alph_syms = Alphabet()
        for sym in [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '/', '=', '<']:
            alph_syms.include((sym, sym))
        automaton.add_transition(start_state, state_symbol, alph_syms)
        
        alph_eq_sign = Alphabet
        alph_eq_sign.include(('=','='))
        automaton.add_transition(start_state, state_assign, alph_eq_sign)
        automaton.add_transition(state_assign, state_symbol, alph_eq_sign)
        alph_ws_dig_let = Alphabet()
        for ws in [' ', '\t', '\n', '\r', '\f', '\v']:
            alph_ws_dig_let.include((ws, ws))
        alph_ws_dig_let.include(('A','Z'))
        alph_ws_dig_let.include(('0','9'))
        automaton.add_transition(state_assign, state_symb_type_2, alph_ws_dig_let)
        
        alph_star = Alphabet()
        alph_star.include(('*','*'))
        automaton.add_transition(start_state,state_no_2, alph_star)
        alph_slash = Alphabet()
        alph_slash.include(('/', '/'))
        automaton.add_transition(state_no_2,err_state_unmatched_comm,alph_slash)
        automaton.add_transition(state_no_2,state_symb_type_2, alph_ws_dig_let)
        
        automaton.add_transition(start_state, state_comm_start, alph_slash)
        automaton.add_transition(state_comm_start, state_symb_type_2, alph_ws_dig_let)
        automaton.add_transition(state_comm_start, state_comm_star, alph_star)
        
        alph_any_but_eof = Alphabet()
        alph_any_but_eof.exclude(('*','*'))
        alph_any_but_eof.exclude((chr(26), chr(26)))
        automaton.add_transition(state_comm_star, state_comm_star, alph_any_but_eof)
        automaton.add_transition(state_comm_star, state_unclosed_comm, alph_eof)
        automaton.add_transition(state_comm_star, state_no_3, alph_star)
        
        alph_any_but_slsh = Alphabet()
        alph_any_but_slsh.exclude((chr(26),chr(26)))
        alph_any_but_slsh.exclude(('/','/'))
        automaton.add_transition(state_no_3, state_comm_star, alph_any_but_slsh)
        automaton.add_transition(state_no_3,state_unclosed_comm, alph_eof)
        automaton.add_transition(state_no_3, state_comment, alph_slash)
        
        automaton.add_transition(start_state, state_no_4, alph_letter)
        alph_let_dig = Alphabet()
        alph_let_dig.include(('A', 'Z'))
        alph_let_dig.include(('a', 'z'))
        alph_let_dig.include(('0', '9'))
        automaton.add_transition(state_no_4, state_no_4, alph_let_dig)
        automaton.add_transition(state_no_4, state_txt_id, alph_ws_s_eof)
        pass
