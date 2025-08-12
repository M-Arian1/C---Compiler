from SemanticStack import SemanticStack


class CodeGenerator:
    
    def __init__(self, parser) -> None:
        memory = MemoryError(0, 512, 1000)
        self.parser = parser
        self.semantic_errors = {}
        self.memory = memory
        self.semantic_stack = SemanticStack()
        self.program_block = memory.PB
        self.data_block = memory.DB
        self.temp_block = memory.TB
        pass
    
    
    #TODO
    #Phase3