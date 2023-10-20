from intbase import InterpreterBase
from intbase import ErrorType
from element import Element
from brewparse import parse_program
import copy

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        self.trace_output = trace_output
        super().__init__(console_output, inp)   # call InterpreterBase's constructor

    # Students must implement this in their derived class
    def run(self, program):
        ast = parse_program(program)
        self.variables_values = {}
        main_func_node = self.get_main_func_node(ast)
        if self.trace_output:
            print(main_func_node)
        if main_func_node is not None:
            self.run_main_func(main_func_node)
        else:
            super().error(
                ErrorType.NAME_ERROR,
                "No main() function was found",
            )

    def get_main_func_node(self, ast):
        if ast.elem_type == InterpreterBase.PROGRAM_DEF:
            for func_node in ast.dict['functions']:
                if func_node.dict['name'] == 'main':
                    return func_node
        return None
    
    def run_main_func(self, func_node):
        if func_node.elem_type == InterpreterBase.FUNC_DEF:
            statements = func_node.dict['statements']
            for statement in statements:
                self.run_statement(statement)

    def run_statement(self, statement_node):
        if statement_node.elem_type == '=':
            key = statement_node.dict['name']
            right_node = statement_node.dict['expression']
            self.variables_values[key] = self.evaluate_exp_var_or_val(right_node)
        elif statement_node.elem_type == InterpreterBase.FCALL_DEF:
            func_name = statement_node.dict['name']
            args = statement_node.dict['args']
            self.run_func(func_name, args)
    
    def evaluate_exp_var_or_val(self, node):
        if node.elem_type == InterpreterBase.INT_DEF or node.elem_type == InterpreterBase.STRING_DEF:
            return node
        elif node.elem_type == InterpreterBase.VAR_DEF:
            return self.evaluate_var(node)
        else:
            return self.evaluate_expression(node)
    
    def evaluate_var(self, var_node):
        var_name = var_node.dict['name']
        if var_name in self.variables_values:
            return copy.copy(self.variables_values[var_name])
        else:
            super().error(
                ErrorType.NAME_ERROR,
                f"Variable {var_name} has not been defined",
            )
    
    def evaluate_expression(self, expression_node):
        if expression_node.elem_type == '+':
            op1 = self.evaluate_exp_var_or_val(expression_node.dict['op1'])
            op2 = self.evaluate_exp_var_or_val(expression_node.dict['op2'])
            return self.evaluate_add(op1, op2)
        elif expression_node.elem_type == '-':
            op1 = self.evaluate_exp_var_or_val(expression_node.dict['op1'])
            op2 = self.evaluate_exp_var_or_val(expression_node.dict['op2'])
            return self.evaluate_subtract(op1, op2)
        elif expression_node.elem_type == InterpreterBase.FCALL_DEF:
            func_name = expression_node.dict['name']
            args = expression_node.dict['args']
            return self.run_func(func_name, args)
    
    def evaluate_add(self, op1, op2):
        if op1.elem_type == InterpreterBase.STRING_DEF or op2.elem_type == InterpreterBase.STRING_DEF:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for add operation",
            )
        else:
            result = copy.copy(op1)
            result.dict['val'] = op1.dict['val'] + op2.dict['val']
            return result
        
    def evaluate_subtract(self, op1, op2):
        if op1.elem_type == InterpreterBase.STRING_DEF or op2.elem_type == InterpreterBase.STRING_DEF:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for subtract operation",
            )
        else:
            result = copy.copy(op1)
            result.dict['val'] = op1.dict['val'] - op2.dict['val']
            return result
    
    def run_func(self, func_name, args):
        if func_name == 'inputi':
            return self.handle_inputi(args)
        elif func_name == 'print':
            self.handle_print(args)
        else:
            super().error(ErrorType.NAME_ERROR,
                      f"Unknown function {func_name}")

    def handle_inputi(self, args):
        if len(args) == 1:
            value = self.evaluate_exp_var_or_val(args[0])
            prompt = value.dict['val']
            super().output(prompt)
        elif len(args) > 1:
            super().error(
                ErrorType.NAME_ERROR,
                f"No inputi() function found that takes > 1 parameter",
            )
        user_input = super().get_input()
        int_value = int(user_input)
        input_element = Element(InterpreterBase.INT_DEF, val=int_value)
        return input_element
    
    def handle_print(self, args):
        if self.trace_output:
            print('handle_print', args)
        string_to_output = ''
        for arg in args:
            value = self.evaluate_exp_var_or_val(arg)
            output_piece = value.dict['val']
            string_to_output += str(output_piece)
        if self.trace_output:
            print(string_to_output)
        super().output(string_to_output)