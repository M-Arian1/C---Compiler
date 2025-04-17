class SymbolTable:
    
    def __init__(self, keywords_list = []):
        self.all_symbols = []
        self.line_no = 1
        
        for keyword in keywords_list:
            k ={}
            k["name"] = keyword
            k["line"] = ""
            self.all_symbols.append(k)
        
    def get_symbol_by_name(self, symbol):
        for sym in self.all_symbols:
            if symbol["name"] == sym["name"]:
                return sym
        return None
        
    def add_symbol(self, symbol):
        if(self.get_symbol_by_name(symbol["name"]) == None):
            self.all_symbols.append(symbol)
            self.line_no += 1
    
    
    def sym_to_text(self):
        text = ""
        for sym in self.all_symbols:
            text += sym["name"] + ".\t" + sym["line"] +"\n"
            
class ErrorTable:
    pass
        
        