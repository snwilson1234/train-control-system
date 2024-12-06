#terminal thing for code
from interpreter import *

class Compiler:
    def __init__(self):
        self.interpreter = Interpreter()

    def prog_run(fn, text):
        # Generate tokens
        lexer = Lexer(fn, text)
        tokens, error = lexer.make_tokens()
        if error: return None, error
  
        # Generate AST
        parser = Parser(tokens)
        ast = parser.parse()
        if ast.error: return None, ast.error

        # Run program
        interpreter = Interpreter()
        context = Context('<program>')
        context.symbol_table = global_symbol_table
        result = interpreter.visit(ast.node, context)

        return result.value, result.error

    def run(self):
        while True:
            text = input('swplc > ')
            if text.strip() == "":
                continue

            result, error = prog_run('<stdin>', text)

            if error:
                print(error.as_string())
            elif result:
                if len(result.elements) == 1:
                    print(repr(result.elements[0]))
                else:
                    print(repr(result))

# Create an instance of the Shell class
shell = Compiler()

# Run the program
shell.run()
