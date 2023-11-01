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
        self.functions = ast.dict['functions']
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
            context = {}
            for statement in statements:
                run_result = self.run_statement(statement, context)
                if run_result is not None:
                    return run_result
                
    def run_statement(self, statement_node, context):
        if statement_node.elem_type == '=':
            key = statement_node.dict['name']
            right_node = statement_node.dict['expression']
            if key in context:
                value = self.evaluate_exp_var_or_val(right_node, context)
                context[key].elem_type = value.elem_type
                context[key].dict['val'] = value.dict['val']
            else:
                context[key] = self.evaluate_exp_var_or_val(right_node, context)
            return None
        elif statement_node.elem_type == InterpreterBase.IF_DEF:
            condition_value = self.evaluate_exp_var_or_val(statement_node.dict['condition'], context)
            if condition_value.elem_type != InterpreterBase.BOOL_DEF:
                super().error(
                    ErrorType.TYPE_ERROR,
                    f"Incompatible type for if condition",
                )
            condition = condition_value.dict['val']
            if_context = copy.copy(context)
            if condition:
                for if_statement_node in statement_node.dict['statements']:
                    run_result = self.run_statement(if_statement_node, if_context)
                    if run_result is not None:
                        return run_result
            else:
                if statement_node.dict['else_statements'] is None:
                    return None
                for else_statement_node in statement_node.dict['else_statements']:
                    run_result = self.run_statement(else_statement_node, if_context)
                    if run_result is not None:
                        return run_result
            return None
        elif statement_node.elem_type == InterpreterBase.WHILE_DEF:
            condition_value = self.evaluate_exp_var_or_val(statement_node.dict['condition'], context)
            if condition_value.elem_type != InterpreterBase.BOOL_DEF:
                super().error(
                    ErrorType.TYPE_ERROR,
                    f"Incompatible type for while condition",
                )
            condition = condition_value.dict['val']
            while condition:
                while_context = copy.copy(context)
                for while_statement_node in statement_node.dict['statements']:
                    run_result = self.run_statement(while_statement_node, while_context)
                    if run_result is not None:
                        return run_result
                
                condition_value = self.evaluate_exp_var_or_val(statement_node.dict['condition'], context)
                if condition_value.elem_type != InterpreterBase.BOOL_DEF:
                    super().error(
                        ErrorType.TYPE_ERROR,
                        f"Incompatible type for while condition",
                    )
                condition = condition_value.dict['val']
            return None
        elif statement_node.elem_type == InterpreterBase.RETURN_DEF:
            if statement_node.dict['expression'] is None:
                return Element(InterpreterBase.NIL_DEF)
            return self.evaluate_exp_var_or_val(statement_node.dict['expression'], context)
        elif statement_node.elem_type == InterpreterBase.FCALL_DEF:
            func_name = statement_node.dict['name']
            args = statement_node.dict['args']
            return self.run_func(func_name, args, context)
        return None
    
    def evaluate_exp_var_or_val(self, node, context):
        if node.elem_type == InterpreterBase.INT_DEF or node.elem_type == InterpreterBase.STRING_DEF:
            return copy.deepcopy(node)
        elif node.elem_type == InterpreterBase.BOOL_DEF or node.elem_type == InterpreterBase.NIL_DEF:
            return copy.deepcopy(node)
        elif node.elem_type == InterpreterBase.VAR_DEF:
            return self.evaluate_var(node, context)
        else:
            return self.evaluate_expression(node, context)
    
    def evaluate_var(self, var_node, context):
        var_name = var_node.get('name')
        if var_name in context:
            return copy.deepcopy(context[var_name])
        else:
            super().error(
                ErrorType.NAME_ERROR,
                f"Variable {var_name} has not been defined",
            )
    
    def evaluate_expression(self, expression_node, context):
        if expression_node.elem_type == '+':
            op1 = self.evaluate_exp_var_or_val(expression_node.dict['op1'], context)
            op2 = self.evaluate_exp_var_or_val(expression_node.dict['op2'], context)
            return self.evaluate_add(op1, op2)
        elif expression_node.elem_type == '-':
            op1 = self.evaluate_exp_var_or_val(expression_node.dict['op1'], context)
            op2 = self.evaluate_exp_var_or_val(expression_node.dict['op2'], context)
            return self.evaluate_subtract(op1, op2)
        elif expression_node.elem_type == '*':
            op1 = self.evaluate_exp_var_or_val(expression_node.dict['op1'], context)
            op2 = self.evaluate_exp_var_or_val(expression_node.dict['op2'], context)
            return self.evaluate_multiply(op1, op2)
        elif expression_node.elem_type == '/':
            op1 = self.evaluate_exp_var_or_val(expression_node.dict['op1'], context)
            op2 = self.evaluate_exp_var_or_val(expression_node.dict['op2'], context)
            return self.evaluate_divide(op1, op2)
        elif expression_node.elem_type == '==':
            op1 = self.evaluate_exp_var_or_val(expression_node.dict['op1'], context)
            op2 = self.evaluate_exp_var_or_val(expression_node.dict['op2'], context)
            return self.evaluate_equality(op1, op2)
        elif expression_node.elem_type == '!=':
            op1 = self.evaluate_exp_var_or_val(expression_node.dict['op1'], context)
            op2 = self.evaluate_exp_var_or_val(expression_node.dict['op2'], context)
            return self.evaluate_inequality(op1, op2)
        elif expression_node.elem_type == '<':
            op1 = self.evaluate_exp_var_or_val(expression_node.dict['op1'], context)
            op2 = self.evaluate_exp_var_or_val(expression_node.dict['op2'], context)
            return self.evaluate_less(op1, op2)
        elif expression_node.elem_type == '<=':
            op1 = self.evaluate_exp_var_or_val(expression_node.dict['op1'], context)
            op2 = self.evaluate_exp_var_or_val(expression_node.dict['op2'], context)
            return self.evaluate_less_equal(op1, op2)
        elif expression_node.elem_type == '>':
            op1 = self.evaluate_exp_var_or_val(expression_node.dict['op1'], context)
            op2 = self.evaluate_exp_var_or_val(expression_node.dict['op2'], context)
            return self.evaluate_greater(op1, op2)
        elif expression_node.elem_type == '>=':
            op1 = self.evaluate_exp_var_or_val(expression_node.dict['op1'], context)
            op2 = self.evaluate_exp_var_or_val(expression_node.dict['op2'], context)
            return self.evaluate_greater_equal(op1, op2)
        elif expression_node.elem_type == '&&':
            op1 = self.evaluate_exp_var_or_val(expression_node.dict['op1'], context)
            op2 = self.evaluate_exp_var_or_val(expression_node.dict['op2'], context)
            return self.evaluate_and_and(op1, op2)
        elif expression_node.elem_type == '||':
            op1 = self.evaluate_exp_var_or_val(expression_node.dict['op1'], context)
            op2 = self.evaluate_exp_var_or_val(expression_node.dict['op2'], context)
            return self.evaluate_or_or(op1, op2)
        elif expression_node.elem_type == InterpreterBase.NEG_DEF:
            op1 = self.evaluate_exp_var_or_val(expression_node.dict['op1'], context)
            return self.evaluate_neg(op1)
        elif expression_node.elem_type == '!':
            op1 = self.evaluate_exp_var_or_val(expression_node.dict['op1'], context)
            return self.evaluate_not(op1)
        elif expression_node.elem_type == InterpreterBase.FCALL_DEF:
            func_name = expression_node.dict['name']
            args = expression_node.dict['args']
            run_result = self.run_func(func_name, args, context)
            if run_result is None:
                return Element(InterpreterBase.NIL_DEF)
            else:
                return run_result
        else:
            super().error(ErrorType.NAME_ERROR,
                      f"Unknown expression {expression_node}")
    
    def evaluate_add(self, op1, op2):
        if op1.elem_type == InterpreterBase.STRING_DEF and op2.elem_type == InterpreterBase.STRING_DEF:
            result = copy.deepcopy(op1)
            result.dict['val'] = op1.dict['val'] + op2.dict['val']
            return result
        if op1.elem_type != InterpreterBase.INT_DEF or op2.elem_type != InterpreterBase.INT_DEF:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for add operation",
            )
        else:
            result = copy.deepcopy(op1)
            result.dict['val'] = op1.dict['val'] + op2.dict['val']
            return result
        
    def evaluate_subtract(self, op1, op2):
        if op1.elem_type != InterpreterBase.INT_DEF or op2.elem_type != InterpreterBase.INT_DEF:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for subtract operation",
            )
        else:
            result = copy.deepcopy(op1)
            result.dict['val'] = op1.dict['val'] - op2.dict['val']
            return result
        
    def evaluate_multiply(self, op1, op2):
        if op1.elem_type != InterpreterBase.INT_DEF or op2.elem_type != InterpreterBase.INT_DEF:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for multiply operation",
            )
        else:
            result = copy.deepcopy(op1)
            result.dict['val'] = op1.dict['val'] * op2.dict['val']
            return result
    
    def evaluate_divide(self, op1, op2):
        if op1.elem_type != InterpreterBase.INT_DEF or op2.elem_type != InterpreterBase.INT_DEF:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for divide operation",
            )
        else:
            result = copy.deepcopy(op1)
            result.dict['val'] = op1.dict['val'] // op2.dict['val']
            return result
        
    def evaluate_equality(self, op1, op2):
        if op1.elem_type == InterpreterBase.NIL_DEF and op2.elem_type == InterpreterBase.NIL_DEF:
            return Element(InterpreterBase.BOOL_DEF, val=True)
        elif op1.elem_type == InterpreterBase.NIL_DEF:
            return Element(InterpreterBase.BOOL_DEF, val=False)
        elif op1.elem_type == InterpreterBase.NIL_DEF:
            return Element(InterpreterBase.BOOL_DEF, val=False)
        elif op1.elem_type != op2.elem_type:
            return Element(InterpreterBase.BOOL_DEF, val=False)
        return Element(InterpreterBase.BOOL_DEF, val=op1.dict['val'] == op2.dict['val'])
    
    def evaluate_inequality(self, op1, op2):
        if op1.elem_type == InterpreterBase.NIL_DEF and op2.elem_type == InterpreterBase.NIL_DEF:
            return Element(InterpreterBase.BOOL_DEF, val=False)
        elif op1.elem_type == InterpreterBase.NIL_DEF:
            return Element(InterpreterBase.BOOL_DEF, val=True)
        elif op1.elem_type == InterpreterBase.NIL_DEF:
            return Element(InterpreterBase.BOOL_DEF, val=True)
        elif op1.elem_type != op2.elem_type:
            return Element(InterpreterBase.BOOL_DEF, val=True)
        return Element(InterpreterBase.BOOL_DEF, val=op1.dict['val'] != op2.dict['val'])
    
    def evaluate_less(self, op1, op2):
        if op1.elem_type != InterpreterBase.INT_DEF or op2.elem_type != InterpreterBase.INT_DEF:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for < operation",
            )
        return Element(InterpreterBase.BOOL_DEF, val=op1.dict['val'] < op2.dict['val'])
    
    def evaluate_less_equal(self, op1, op2):
        if op1.elem_type != InterpreterBase.INT_DEF or op2.elem_type != InterpreterBase.INT_DEF:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for <= operation",
            )
        return Element(InterpreterBase.BOOL_DEF, val=op1.dict['val'] <= op2.dict['val'])

    def evaluate_greater(self, op1, op2):
        if op1.elem_type != InterpreterBase.INT_DEF or op2.elem_type != InterpreterBase.INT_DEF:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for > operation",
            )
        return Element(InterpreterBase.BOOL_DEF, val=op1.dict['val'] > op2.dict['val'])

    def evaluate_greater_equal(self, op1, op2):
        if op1.elem_type != InterpreterBase.INT_DEF or op2.elem_type != InterpreterBase.INT_DEF:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for >= operation",
            )
        return Element(InterpreterBase.BOOL_DEF, val=op1.dict['val'] >= op2.dict['val'])
    
    def evaluate_and_and(self, op1, op2):
        if op1.elem_type != InterpreterBase.BOOL_DEF or op2.elem_type != InterpreterBase.BOOL_DEF:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for && operation",
            )
        return Element(InterpreterBase.BOOL_DEF, val=op1.dict['val'] and op2.dict['val'])
    
    def evaluate_or_or(self, op1, op2):
        if op1.elem_type != InterpreterBase.BOOL_DEF or op2.elem_type != InterpreterBase.BOOL_DEF:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for || operation",
            )
        return Element(InterpreterBase.BOOL_DEF, val=op1.dict['val'] or op2.dict['val'])
    
    def evaluate_neg(self, op1):
        if op1.elem_type != InterpreterBase.INT_DEF:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for neg operation",
            )
        return Element(InterpreterBase.INT_DEF, val=-op1.dict['val'])
    
    def evaluate_not(self, op1):
        if op1.elem_type != InterpreterBase.BOOL_DEF:
            super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for ! operation",
            )
        return Element(InterpreterBase.BOOL_DEF, val=(not op1.dict['val']))
    
    def evaluate_arg_values(self, args, context):
        arg_value_list = []
        for arg in args:
            arg_value_list.append(self.evaluate_exp_var_or_val(arg, context))
        return arg_value_list
    
    def run_func(self, func_name, args, context):
        if func_name == 'inputi':
            return self.handle_inputi(args, context)
        elif func_name == 'print':
            return self.handle_print(args, context)
        elif func_name == 'inputs':
            return self.handle_inputs(args, context)
        
        arg_values = self.evaluate_arg_values(args, context)
        for func_node in self.functions:
            if func_node.dict['name'] == func_name and len(arg_values) == len(func_node.dict['args']):
                func_context = copy.copy(context)
                for index in range(len(func_node.dict['args'])):
                    arg_node = func_node.dict['args'][index]
                    func_context[arg_node.dict['name']] = arg_values[index]
                statements = func_node.dict['statements']
                for statement in statements:
                    run_result = self.run_statement(statement, func_context)
                    if self.trace_output:
                        print(func_context)
                        print("{")
                        for key in func_context:
                            print(key + ":" + str(func_context[key].dict['val']))
                        print("}")
                        print("{")
                        for key in context:
                            print(key + ":" + str(context[key].dict['val']))
                        print("}")
                        print(">>")
                    if run_result is not None:
                        return run_result
                return None
        
        super().error(
            ErrorType.NAME_ERROR,
            f"No {func_name} function found that takes {len(arg_values)} parameters",
        )

    def handle_inputi(self, args, context):
        if len(args) == 1:
            value = self.evaluate_exp_var_or_val(args[0], context)
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
    
    def handle_inputs(self, args, context):
        if len(args) == 1:
            value = self.evaluate_exp_var_or_val(args[0], context)
            prompt = value.dict['val']
            super().output(prompt)
        elif len(args) > 1:
            super().error(
                ErrorType.NAME_ERROR,
                f"No inputs() function found that takes > 1 parameter",
            )
        user_input = super().get_input()
        str_value = str(user_input)
        input_element = Element(InterpreterBase.STRING_DEF, val=str_value)
        return input_element
    
    def handle_print(self, args, context):
        if self.trace_output:
            print('handle_print', args, context)
        string_to_output = ''
        for arg in args:
            value = self.evaluate_exp_var_or_val(arg, context)
            if value is None:
                super().error(
                    ErrorType.NAME_ERROR,
                    f"Missing some var",
                )
            output_piece = str(value.dict['val'])
            if value.elem_type == InterpreterBase.BOOL_DEF:
                output_piece = output_piece.lower()
            string_to_output += output_piece
        if self.trace_output:
            print(string_to_output)
        super().output(string_to_output)
        return None