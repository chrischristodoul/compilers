import sys

# made in Python 3.13.2
# Χριστοδούλου Χρήστος 5392, Μπάμπαλης Στυλιανός 5292

# Σύστημα για πίνακα συμβόλων
class Entity:
    def __init__(self, name, entity_type, offset=None, mode=None):
        self.name = name
        self.entity_type = entity_type  # "variable", "parameter", "function", "procedure", "temporary", "return"
        self.offset = offset
        self.mode = mode  # "by value"/"by reference"(μόνο parameters)
        self.value = None

    def __str__(self):
        info = ""
        if self.entity_type == "parameter":
            info = f"Parameter ({self.mode}): {self.name} (offset {self.offset})"
        elif self.entity_type == "return":
            info = f"Return Value: (offset {self.offset})"
        elif self.entity_type == "temporary":
            info = f"Μεταβλητή (temp): {self.name} (offset {self.offset})"

        else:
            info = f"{self.entity_type.capitalize()}: {self.name} (offset {self.offset})"

        if self.value is not None:
            info += f", value={self.value}"
        return info

# για κάθε scope κάνει άλλο(main,if,for,while,do,function,procedure)
class Scope:
    def __init__(self, name, nesting_level):
        self.name = name
        self.nesting_level = nesting_level
        self.entities = []
        self.offset = 0  # επόμενο offset

    def add_entity(self, entity):
        entity.offset = self.offset
        self.entities.append(entity)
        self.offset += 4

    def lookup(self, name):
        for entity in self.entities:
            if entity.name == name:
                return entity
        return None

    def __str__(self):
        output = f"Scope: {self.name}\n"
        for entity in self.entities:
            output += "  " + str(entity) + "\n"
        return output

# Πίνακας συμβόλων
class SymbolTable:
    def __init__(self):
        self.scopes = []
        self.all_scopes = []
        self.if_counter = 0
        self.while_counter = 0
        self.for_counter = 0
        self.do_counter = 0
        self.open_scope("main")

    def open_scope(self, name):
        nesting_level = len(self.scopes)
        scope = Scope(name, nesting_level)
        self.scopes.append(scope)
        self.all_scopes.append(scope)

    def close_scope(self):
        self.scopes.pop()

    def current_scope(self):
        return self.scopes[-1] if self.scopes else None

    def add_variable(self, name):
        var = Entity(name, "variable")
        self.current_scope().add_entity(var)

    def add_parameter(self, name, mode):
        param = Entity(name, "parameter", mode=mode)
        self.current_scope().add_entity(param)

    def add_function(self, name):
        func = Entity(name, "function")
        self.current_scope().add_entity(func)

    def add_procedure(self, name):
        proc = Entity(name, "procedure")
        self.current_scope().add_entity(proc)

    def add_temporary(self, name):
        temp = Entity(name, "temporary")
        self.current_scope().add_entity(temp)

    def add_return(self):
        ret = Entity("return", "return")
        self.current_scope().add_entity(ret)

    def lookup(self, name):
        for scope in reversed(self.scopes):
            entity = scope.lookup(name)
            if entity:
                return entity
        return None

    def open_if_scope(self):
        name = f"if_{self.if_counter}"
        self.if_counter += 1
        self.open_scope(name)

    def open_while_scope(self):
        name = f"while_{self.while_counter}"
        self.while_counter += 1
        self.open_scope(name)

    def open_for_scope(self):
        name = f"for_{self.for_counter}"
        self.for_counter += 1
        self.open_scope(name)

    def open_do_scope(self):
        name = f"do_{self.do_counter}"
        self.do_counter += 1
        self.open_scope(name)

    def write_to_file(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            for scope in self.all_scopes:
                f.write(str(scope))
                f.write("\n")

# Tokens
KEYWORDS = {
    "πρόγραμμα", "δήλωση", "εάν", "τότε", "αλλιώς", "εάν_τέλος", "επανάλαβε", "μέχρι", "όσο", "όσο_τέλος",
    "για", "έως", "με_βήμα", "για_τέλος", "διάβασε", "γράψε", "συνάρτηση", "διαδικασία", "διαπροσωπεία",
    "είσοδος", "έξοδος", "αρχή_συνάρτησης", "τέλος_συνάρτησης", "αρχή_διαδικασίας", "τέλος_διαδικασίας",
    "αρχή_προγράμματος", "τέλος_προγράμματος", "ή", "και", "εκτέλεσε"
}
OPERATORS = {"+", "-", "*", "/", "<", ">", "=", "<=", ">=", "<>", ":="}
DELIMITERS = {";", ",", ":"}
GROUPING = {"(", ")", "[", "]", "”"}
COMMENTS = {"{", "}"}
REFERENCE = {"%"}
DIGITS = "0123456789"
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρστυφχψωςΆΈΎΊΌΉΏάέύίόήώ"

# λεκτικός αναλυτής greek++
def lexer(code):
    tokens = []
    i = 0
    line = 1
    while i < len(code):
        char = code[i]  # στοιχείο κώδικα

        # κενά, tabs, newlines αγνούνται
        if char in " \t":
            i += 1
            continue
        if char == "\n":
            line += 1
            i += 1
            continue

        # νούμερα
        if char in DIGITS:
            num = ''
            while i < len(code) and code[i] in DIGITS:
                num += code[i]
                i += 1
            tokens.append(("NUMBER", num, line))
            continue

        # γράμματα
        if char in LETTERS:
            ident = ''
            while i < len(code) and (code[i] in LETTERS or code[i] in DIGITS or code[i] == '_'):
                ident += code[i]
                i += 1
            if ident in KEYWORDS:
                tokens.append(("KEYWORD", ident, line))
            else:
                tokens.append(("IDENTIFIER", ident, line))
            continue

        # πράξη ανάθεσης
        if char == ":" and i + 1 < len(code) and code[i + 1] == "=":
            tokens.append(("OPERATOR", ":=", line))
            i += 2
            continue
        # λοιπές πράξεις
        if char in OPERATORS:
            op = char
            i += 1
            if i < len(code) and code[i] in OPERATORS:
                op += code[i]
                i += 1
            tokens.append(("OPERATOR", op, line))
            continue

        # ερωτηματικό, κόμμα , άνω και κάτω τελεία
        if char in DELIMITERS:
            tokens.append(("DELIMITER", char, line))
            i += 1
            continue
        # αγκύλες
        if char in GROUPING:
            tokens.append(("GROUPING", char, line))
            i += 1
            continue

        # σχόλια
        if char in COMMENTS:
            comment = char
            i += 1
            while i < len(code) and code[i] != '}':
                comment += code[i]
                i += 1
            if i < len(code):
                comment += '}'
                i += 1
            tokens.append(("COMMENT", comment, line))
            continue

        # αναφορά
        if char in REFERENCE:
            tokens.append(("REFERENCE", char, line))
            i += 1
            continue

        # σφάλμα άγνωστου χαρακτήρα
        print(f"Σφάλμα: Άγνωστος χαρακτήρας '{char}' στη γραμμή {line}")
        i += 1
    return tokens

class QuadIRGenerator:
    def __init__(self, symbol_table):
        self.quads = []  #quads
        self.next_label = 100
        self.temp_counter = 1  #T_1, T_2...
        self.label_counter = 0
        self.current_block = None
        self.pending_jumps = {}
        self.symbol_table = symbol_table

    #Βοηθητικές functions
    def nextquad(self):
        return len(self.quads) + 100  # Ξεκίνα από 100

    def genquad(self, op, x, y, z):
        self.quads.append((op, x, y, z))
        return len(self.quads) + 99

    def gen_label(self, label_name):
        self.genquad("label", label_name, "_", "_")

    def write_quads_to_file(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            for i, quad in enumerate(self.quads):
                f.write(f"{i + 100}: {quad}\n")

    def newtemp(self):
        temp = f"T_{self.temp_counter}"
        self.temp_counter += 1
        self.symbol_table.add_temporary(temp)
        return temp

    def emptylist(self):
        #Άδεια λίστα labels
        return []

    def makelist(self, x):
        #Άδεια λίστα με 1 label
        return [x]

    def mergelist(self, list1, list2):
        #Merge 2 λίστες
        return list1 + list2

    def backpatch(self, lst, z):
        #Backpatch μια λίστα quads
        for quad_num in lst:
            if quad_num - 100 < len(self.quads):
                quad = list(self.quads[quad_num - 100])
                if quad[3] is None or quad[3] == '_':
                    quad[3] = z
                    self.quads[quad_num - 100] = tuple(quad)

    #Μέθοδοι quads
    def begin_block(self, name):
        # νέο block
        self.current_block = name
        self.genquad("begin_block", name, "_", "_")

    def end_block(self, name):
        # τέλος block
        self.genquad("end_block", name, "_", "_")
        self.current_block = None

    def gen_assignment(self, target, source):
        self.genquad(":=", source, "_", target)
        src_val = self.get_value(source)
        if src_val is not None:
            target_entity = self.symbol_table.lookup(target)
            if target_entity:
                target_entity.value = src_val

    def gen_arithmetic(self, op, x, y, z):
        self.genquad(op, x, y, z)
        x_val = self.get_value(x)
        y_val = self.get_value(y)
        if x_val is not None and y_val is not None:
            result = None
            if op == "+":
                result = x_val + y_val
            elif op == "-":
                result = x_val - y_val
            elif op == "*":
                result = x_val * y_val
            elif op == "/":
                result = x_val // y_val  # integer division
            if result is not None:
                z_entity = self.symbol_table.lookup(z)
                if z_entity:
                    z_entity.value = result

    def gen_jump(self, target_label):
        #unconditional jump
        self.genquad("jump", "_", "_", target_label)

    def gen_conditional_jump(self, cond_var, true_label, false_label):
        #conditional jump
        self.genquad("cjump", cond_var, true_label, false_label)

    def gen_halt(self):
        self.genquad("halt", "_", "_", "_")

    def gen_parameter(self, var, mode):
        #parameter quad
        self.genquad("par", var, mode, "_")

    def gen_call(self, func_name, has_return=False):
        #function/procedure call
        if has_return:
            ret_temp = self.newtemp()
            self.genquad("par", ret_temp, "ret", "_")
        self.genquad("call", func_name, "_", "_")
        return ret_temp if has_return else None

    def gen_return(self, value=None):
        if value:
            self.genquad("ret", value, "_", "_")
        else:
            self.genquad("ret", "_", "_", "_")

    def get_value(self, operand):
        if operand is None or operand == "_":
            return None
        if isinstance(operand, int):
            return operand
        if operand.isdigit() or (operand[0] == '-' and operand[1:].isdigit()):
            return int(operand)
        entity = self.symbol_table.lookup(operand)
        if entity and entity.value is not None:
            return entity.value
        return None

    def print_quads(self):
        for i, quad in enumerate(self.quads):
            print(f"{i + 100}: {quad}")

    def newlabel(self):
        #new label
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

# συντακτικός αναλυτής greek++
# τα συντακτικά error δεν αναφέρουν τη γραμμή που εντοπίζεται το λάθος, θα υλοποιηθεί αργότερα στη βελτιστοποίηση
# ο αναλυτής εκτυπώνει τα newlines στα comment, θα υλοποιηθεί αργότερα στη βελτιστοποίηση
# υπάρχει πρόβλημα με το 'όχι'
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        # αφαιρώ απο τη λίστα των tokens τα σχόλια, για να τα αγνοεί ο parser
        self.tokens = [token for token in self.tokens
                       if "COMMENT" != token[0]]
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None
        self.symbol_table = SymbolTable()
        self.ir = QuadIRGenerator(self.symbol_table)
        self.label_counter = 0
        self.functions = set()  # Track declared functions

        # errors
        self.error_messages = {
            'unexpected_token': "Απροσδόκητο token",
            'missing_semicolon': "Λείπει το ερωτηματικό (;)",
            'invalid_factor': "Μη έγκυρος παράγοντας"
        }

    def eat(self, token_type, value=None):
        if self.current_token is None:
            raise SyntaxError(f"Σφάλμα: Αναμενόταν περισσότερα tokens, όμως το αρχείο τελείωσε.")

        current_type = self.current_token[0]
        current_value = self.current_token[1] if self.current_token[1] else None
        # έλεγχος μήκους IDENTIFIER
        if current_type == "IDENTIFIER" and len(current_value) > 30:
            raise SyntaxError(f"Σφάλμα: Το αναγνωριστικό '{current_value}' υπερβαίνει τους 30 χαρακτήρες.")

        if current_type == token_type and (value is None or current_value == value):
            self.pos += 1
            self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None
        else:
            raise SyntaxError(
                f"Σφάλμα: Περίμενα {token_type} {value if value else ''}, αλλά βρήκα {self.current_token}")

    # μέθοδοι quads
    def new_label(self):
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

    def function_call(self, func_name):
        #quads για function calls
        self.eat("GROUPING", "(")

        #parameters
        while self.current_token and self.current_token[1] != ")":
            if self.current_token[0] == "REFERENCE":
                self.eat("REFERENCE", "%")
                var = self.current_token[1]
                self.eat("IDENTIFIER")
                self.ir.genquad("par", var, "ref", "_")
            else:
                expr = self.expression()
                self.ir.genquad("par", expr, "cv", "_")

            if self.current_token and self.current_token[1] == ",":
                self.eat("DELIMITER", ",")

        self.eat("GROUPING", ")")

        #return value
        ret_temp = self.ir.newtemp()
        self.ir.genquad("par", ret_temp, "ret", "_")
        self.ir.genquad("call", func_name, "_", "_")
        return ret_temp

        

        

        
    #ορισμός προγράμματος
    def program(self):
        self.eat("KEYWORD", "πρόγραμμα")
        self.program_name = self.current_token[1]
        self.eat("IDENTIFIER")
        self.program_block()

    def program_block(self):
        #Ξεκίνα main block
        self.ir.genquad("begin_block", self.program_name, "_", "_")
        self.declarations()
        self.subprograms()
        self.eat("KEYWORD", "αρχή_προγράμματος")
        self.sequence()
        self.eat("KEYWORD", "τέλος_προγράμματος")
        #Τέλος main block
        self.ir.genquad("halt", "_", "_", "_")
        self.ir.genquad("end_block", self.program_name, "_", "_")

    def declarations(self):
        while self.current_token and self.current_token[1] == "δήλωση":
            self.eat("KEYWORD", "δήλωση")
            if self.current_token and self.current_token[0] == "IDENTIFIER":
                self.varlist()
            else:
                raise SyntaxError(
                    f"Σφάλμα: Αναμενόταν λίστα μεταβλητών μετά τη 'δήλωση', αλλά βρέθηκε {self.current_token}")

    def varlist(self):
        name = self.current_token[1]
        self.eat("IDENTIFIER")
        self.symbol_table.add_variable(name)
        while self.current_token and self.current_token[1] == ",":
            self.eat("DELIMITER", ",")
            name = self.current_token[1]
            self.eat("IDENTIFIER")
            self.symbol_table.add_variable(name)

    #functions, procedures (υποπρογράμματα)
    def subprograms(self):
        while self.current_token and self.current_token[1] in {"συνάρτηση", "διαδικασία"}:
            if self.current_token[1] == "συνάρτηση":
                self.function()
            else:
                self.procedure()

    def function(self):
        self.eat("KEYWORD", "συνάρτηση")
        name = self.current_token[1]
        self.eat("IDENTIFIER")
        self.symbol_table.add_function(name)
        self.symbol_table.open_scope(name)
        self.ir.begin_block(name)
        self.eat("GROUPING", "(")
        self.formalparlist()
        self.eat("GROUPING", ")")
        self.funcblock()
        self.symbol_table.add_return()
        self.ir.end_block(name)
        self.symbol_table.close_scope()

    def procedure(self):
        self.eat("KEYWORD", "διαδικασία")
        name = self.current_token[1]
        self.eat("IDENTIFIER")
        self.symbol_table.add_procedure(name)
        self.symbol_table.open_scope(name)
        self.ir.begin_block(name)
        self.eat("GROUPING", "(")
        self.formalparlist()
        self.eat("GROUPING", ")")
        self.procblock()
        self.ir.end_block(name)
        self.symbol_table.close_scope()

    def formalparlist(self):
        if self.current_token and self.current_token[0] == "IDENTIFIER":
            self.varlist()

    def funcblock(self):
        self.eat("KEYWORD", "διαπροσωπεία")
        self.funcinput()
        self.funcoutput()
        self.declarations()
        self.eat("KEYWORD", "αρχή_συνάρτησης")
        self.sequence()
        self.eat("KEYWORD", "τέλος_συνάρτησης")

    def procblock(self):
        self.eat("KEYWORD", "διαπροσωπεία")
        self.funcinput()
        self.funcoutput()
        self.declarations()
        self.eat("KEYWORD", "αρχή_διαδικασίας")
        self.sequence()
        self.eat("KEYWORD", "τέλος_διαδικασίας")

    def funcinput(self):
        if self.current_token and self.current_token[0] == "KEYWORD" and self.current_token[1] == "είσοδος":
            self.eat("KEYWORD", "είσοδος")
            while self.current_token and self.current_token[0] == "IDENTIFIER":
                name = self.current_token[1]
                self.eat("IDENTIFIER")
                self.symbol_table.add_parameter(name, "by value")
                if self.current_token and self.current_token[1] == ",":
                    self.eat("DELIMITER", ",")

    def funcoutput(self):
        if self.current_token and self.current_token[0] == "KEYWORD" and self.current_token[1] == "έξοδος":
            self.eat("KEYWORD", "έξοδος")
            while self.current_token and self.current_token[0] == "IDENTIFIER":
                name = self.current_token[1]
                self.eat("IDENTIFIER")
                self.symbol_table.add_parameter(name, "by reference")
                if self.current_token and self.current_token[1] == ",":
                    self.eat("DELIMITER", ",")

    # ακολουθία εντολών
    def sequence(self):
        while self.current_token and self.current_token[0] in {"IDENTIFIER", "KEYWORD"}:
            # επιστρέφω στο if
            if self.current_token[1] in {"αλλιώς", "εάν_τέλος", "όσο_τέλος", "για_τέλος", "τέλος_προγράμματος",
                                         "τέλος_διαδικασίας", "τέλος_συνάρτησης", "τέλος_προγράμματος", "μέχρι"}:
                return

            self.statement()
            if self.current_token and self.current_token[1] == ";":
                self.eat("DELIMITER", ";")

    def statement(self):
        if self.current_token and self.current_token[0] == "IDENTIFIER":
            self.assignment()
        elif self.current_token and self.current_token[1] == "εάν":
            self.if_statement()
        elif self.current_token and self.current_token[1] == "όσο":
            self.while_stat()
        elif self.current_token and self.current_token[1] == "για":
            self.for_stat()
        elif self.current_token and self.current_token[1] == "επανάλαβε":
            self.do_stat()
        elif self.current_token and self.current_token[1] == "γράψε":
            self.print_statement()
        elif self.current_token and self.current_token[1] == "διάβασε":
            self.input_stat()
        elif self.current_token and self.current_token[1] == "εκτέλεσε":
            self.call_stat()
        else:
            raise SyntaxError(f"Άγνωστη εντολή: {self.current_token}")
 
    # εκφράσεις και πράξεις
    def assignment(self):
        var_name = self.current_token[1]
        self.eat("IDENTIFIER")
        self.eat("OPERATOR", ":=")
        expr_result = self.expression()
        self.ir.gen_assignment(var_name, expr_result)

        if self.current_token:
            if self.current_token[1] == ";":
                self.eat("DELIMITER", ";")
                return
            elif self.current_token[1] in {"αλλιώς", "εάν_τέλος", "όσο_τέλος", "για_τέλος", "μέχρι",
                                           "τέλος_προγράμματος", "τέλος_διαδικασίας", "τέλος_συνάρτησης"}:
                return
            else:
                raise SyntaxError(f"Σφάλμα: Λείπει ; μετά από εκχώρηση τιμής")

    def expression(self):
        temp = self.ir.newtemp()
        self.optional_sign()
        left = self.term()

        while self.current_token and self.current_token[1] in {"+", "-"}:
            op = self.current_token[1]
            self.eat("OPERATOR")
            right = self.term()
            new_temp = self.ir.newtemp()
            self.ir.gen_arithmetic(op, left, right, new_temp)
            left = new_temp

        return left

    def term(self):
        left = self.factor()
        while self.current_token and self.current_token[1] in {"*", "/"}:
            op = self.current_token[1]
            self.eat("OPERATOR")
            right = self.factor()
            temp = self.ir.newtemp()
            self.ir.genquad(op, left, right, temp)
            left = temp
        return left

    def factor(self):
        if self.current_token[0] == "NUMBER":
            num = self.current_token[1]
            self.eat("NUMBER")
            return num  # Return constant directly
        elif self.current_token[0] == "IDENTIFIER":
            id_name = self.current_token[1]
            self.eat("IDENTIFIER")
            if self.current_token and self.current_token[1] == "(":
                return self.function_call(id_name)
            return id_name
        elif self.current_token[1] == "(":
            self.eat("GROUPING", "(")
            expr = self.expression()
            self.eat("GROUPING", ")")
            return expr
        else:
            self.error("Invalid factor")

    def optional_sign(self):
        if self.current_token and self.current_token[1] in {"+", "-"}:
            self.addoper()

    def addoper(self):
        self.eat("OPERATOR")

    def muloper(self):
        self.eat("OPERATOR")

    # συνθήκες και λογικοί τελεστές
    def condition(self):
        self.boolterm()
        while self.current_token and self.current_token[1] == "ή":
            self.eat("KEYWORD", "ή")
            self.boolterm()

    def boolterm(self):
        self.boolfactor()
        while self.current_token and self.current_token[1] == "και":
            self.eat("KEYWORD", "και")
            self.boolfactor()

    def boolfactor(self):
        if self.current_token and self.current_token[1] == "όχι":
            self.eat("KEYWORD", "όχι")
            self.eat("GROUPING", "[")
            cond_temp = self.condition()
            self.eat("GROUPING", "]")
            temp = self.ir.newtemp()
            self.ir.gen_arithmetic("not", cond_temp, "_", temp)
            return temp

        elif self.current_token and self.current_token[1] == "[":
            self.eat("GROUPING", "[")
            cond_temp = self.condition()
            self.eat("GROUPING", "]")
            return cond_temp

        else:
            left = self.expression()
            op = self.current_token[1]
            self.relational_oper()
            right = self.expression()

            # Δημιουργία προσωρινής μεταβλητής που κρατάει τη σύγκριση
            temp = self.ir.newtemp()
            self.ir.genquad(op, left, right, temp)
            return temp

    # ορισμοί _stat
    def if_statement(self):
        self.eat("KEYWORD", "εάν")
        cond_temp = self.condition()
        self.symbol_table.open_if_scope()

        false_label = self.ir.newlabel()
        end_label = self.ir.newlabel()

        # Χρήση cjump με τη συνθήκη
        self.ir.genquad("cjump", cond_temp, "_", false_label)

        self.eat("KEYWORD", "τότε")
        self.sequence()

        if self.current_token and self.current_token[1] == "αλλιώς":
            self.ir.genquad("jump", "_", "_", end_label)
            self.ir.genquad("label", false_label, "_", "_")
            self.eat("KEYWORD", "αλλιώς")
            self.sequence()
            self.ir.genquad("label", end_label, "_", "_")
        else:
            self.ir.genquad("label", false_label, "_", "_")

        self.eat("KEYWORD", "εάν_τέλος")
        self.symbol_table.close_scope()

    def while_stat(self):
        self.symbol_table.open_while_scope()

        start_label = self.ir.newlabel()
        self.ir.genquad("label", start_label, "_", "_")

        self.eat("KEYWORD", "όσο")
        cond_temp = self.condition()

        false_label = self.ir.newlabel()
        self.ir.genquad("cjump", cond_temp, "_", false_label)

        self.eat("KEYWORD", "επανάλαβε")
        self.sequence()

        self.ir.genquad("jump", "_", "_", start_label)
        self.ir.genquad("label", false_label, "_", "_")

        self.eat("KEYWORD", "όσο_τέλος")
        self.symbol_table.close_scope()

    def do_stat(self):
        self.symbol_table.open_do_scope()

        start_label = self.ir.newlabel()
        self.ir.genquad("label", start_label, "_", "_")

        self.eat("KEYWORD", "επανάλαβε")
        self.sequence()

        self.eat("KEYWORD", "μέχρι")
        cond_temp = self.condition()

        self.ir.genquad("cjump", cond_temp, "_", start_label)  # Εάν η συνθήκη ισχύει, επανάλαβε

        self.symbol_table.close_scope()

    def for_stat(self):
        self.symbol_table.open_for_scope()

        self.eat("KEYWORD", "για")
        var_name = self.current_token[1]
        self.eat("IDENTIFIER")
        self.eat("OPERATOR", ":=")
        start_expr = self.expression()
        self.ir.gen_assignment(var_name, start_expr)

        self.eat("KEYWORD", "έως")
        end_expr = self.expression()

        step_val = "1"  # Default βήμα
        if self.current_token and self.current_token[1] == "με_βήμα":
            self.eat("KEYWORD", "με_βήμα")
            step_val = self.expression()

        loop_start = self.ir.newlabel()
        loop_end = self.ir.newlabel()

        self.ir.genquad("label", loop_start, "_", "_")

        cond_temp = self.ir.newtemp()
        self.ir.genquad("<=", var_name, end_expr, cond_temp)
        self.ir.genquad("cjump", cond_temp, "_", loop_end)

        self.eat("KEYWORD", "επανάλαβε")
        self.sequence()

        # Αύξηση με βήμα
        tmp = self.ir.newtemp()
        self.ir.genquad("+", var_name, step_val, tmp)
        self.ir.gen_assignment(var_name, tmp)

        self.ir.genquad("jump", "_", "_", loop_start)
        self.ir.genquad("label", loop_end, "_", "_")

        self.eat("KEYWORD", "για_τέλος")
        self.symbol_table.close_scope()

    def idtail(self):
        # idtail -> actualpars | (empty)
        if self.current_token and self.current_token[0] == "GROUPING" and self.current_token[1] == "(":
            self.actualpars()

    # actualpars -> '(' actualparlist ')'
    def actualpars(self):
        self.eat("GROUPING", "(")
        self.actualparlist()
        self.eat("GROUPING", ")")

    # actualparlist -> actualparitem ( ',' actualparitem )* | (empty)
    def actualparlist(self):
        if self.current_token and (
                self.current_token[0] in {"IDENTIFIER", "NUMBER"} or (self.current_token[0] == "REFERENCE")):
            self.actualparitem()
            while self.current_token and self.current_token[0] == "DELIMITER" and self.current_token[1] == ",":
                self.eat("DELIMITER", ",")
                self.actualparitem()

    # actualparitem -> expression |  '%' ID
    def actualparitem(self):
        if self.current_token and self.current_token[0] == "REFERENCE":
            self.eat("REFERENCE", "%")
            self.eat("IDENTIFIER")
        else:
            self.expression()

    # condition -> boolterm ( 'ή' boolterm )*
    def condition(self):
        #Πέρνα condition και επέστρεψε temp μεταβλητή με το result
        left = self.boolterm()
        while self.current_token and self.current_token[1] == "ή":
            self.eat("KEYWORD", "ή")
            right = self.boolterm()
            temp = self.ir.newtemp()
            self.ir.gen_arithmetic("or", left, right, temp)
            left = temp
        return left

    # boolterm -> boolfactor ( 'και' boolfactor )*
    def boolterm(self):
        left = self.boolfactor()
        while self.current_token and self.current_token[1] == "και":
            self.eat("KEYWORD", "και")
            right = self.boolfactor()
            temp = self.ir.newtemp()
            self.ir.gen_arithmetic("and", left, right, temp)
            left = temp
        return left

    # boolfactor -> 'όχι' '[' condition ']' | '[' condition ']' | expression relational_op expression
    def boolfactor(self):
        if self.current_token and self.current_token[1] == "όχι":
            self.eat("KEYWORD", "όχι")
            self.eat("GROUPING", "[")
            expr = self.condition()
            self.eat("GROUPING", "]")
            temp = self.ir.newtemp()
            self.ir.gen_arithmetic("not", expr, "_", temp)
            return temp
        elif self.current_token and self.current_token[1] == "[":
            self.eat("GROUPING", "[")
            expr = self.condition()
            self.eat("GROUPING", "]")
            return expr
        else:
            left = self.expression()
            op = self.current_token[1]
            self.relational_oper()  # This eats the operator
            right = self.expression()
            temp = self.ir.newtemp()
            self.ir.gen_arithmetic(op, left, right, temp)
            return temp

    # relational_op -> '=' , '<=' , '>=' , '<>' , '<' , '>'
    def relational_oper(self):
        valid_ops = {"=", "<=", ">=", "<>", "<", ">"}
        if self.current_token and self.current_token[0] == "OPERATOR" and self.current_token[1] in valid_ops:
            op = self.current_token[1]
            self.eat("OPERATOR")
            return op
        else:
            self.error("Αναμενόταν τελεστής συσχέτισης")

    # input_stat -> 'διάβασε' ID
    def input_stat(self):
        self.eat("KEYWORD", "διάβασε")
        self.eat("IDENTIFIER")

    # print_stat -> 'γράψε' expression
    def print_statement(self):
        self.eat("KEYWORD", "γράψε")
        self.expression()

    # call_stat -> 'εκτέλεσε' ID idtail
    def call_stat(self):
        self.eat("KEYWORD", "εκτέλεσε")
        self.eat("IDENTIFIER")
        self.idtail()

    # step -> 'με_βήμα' expression | (empty)
    def step(self):
        if self.current_token and self.current_token[0] == "KEYWORD" and self.current_token[1] == "με_βήμα":
            self.eat("KEYWORD", "με_βήμα")
            self.expression()

    def error(self, message):
        if self.current_token:
            line = self.current_token[2] if len(self.current_token) > 2 else "unknown"
            current = f"{self.current_token[0]} '{self.current_token[1]}'" if len(self.current_token) > 1 else str(
                self.current_token)
            raise SyntaxError(f"Σφάλμα στη γραμμή {line}: {message}\n"
                              f"Τρέχων token: {current}")
        else:
            raise SyntaxError(f"Σφάλμα: {message} (no current token)")



from collections import defaultdict

class RISCGenerator:
    def __init__(self, quads, symbol_table):
        self.quads = quads
        self.symbol_table = symbol_table
        self.output = []
        self.label_count = 0
        self.current_scope = 'main'
        self.offset_map = defaultdict(dict)
        self.sp_offset = 0

    def new_label(self):
        label = f"L{self.label_count}"
        self.label_count += 1
        return label

    def reg(self, var, target_reg='t0'):
        if var.isdigit() or (var.startswith('-') and var[1:].isdigit()):
            self.emit(f"li {target_reg}, {var}")
            return target_reg
        offset = self.offset_map[self.current_scope].get(var)
        if offset is None:
            self.sp_offset += 4
            offset = -self.sp_offset
            self.offset_map[self.current_scope][var] = offset
        self.emit(f"lw {target_reg}, {offset}(sp)")
        return target_reg

    def store(self, var, reg='t1'):
        offset = self.offset_map[self.current_scope].get(var)
        if offset is None:
            self.sp_offset += 4
            offset = -self.sp_offset
            self.offset_map[self.current_scope][var] = offset
        self.emit(f"sw {reg}, {offset}(sp)")

    def emit(self, line):
        self.output.append(line)

    def find_scope_of(self, var):
        for scope in reversed(self.symbol_table.all_scopes):
            if var in [e.name for e in scope.entities]:
                return scope
        raise Exception(f"Variable {var} not found in any scope")

    def gnvlcode(self, var):
        scope = self.find_scope_of(var)
        level_diff = self.symbol_table.current_scope().nesting_level - scope.nesting_level
        self.emit("mv t0, fp")
        for _ in range(level_diff):
            self.emit("lw t0, 0(t0)")
        offset = self.offset_map[scope.name][var]
        self.emit(f"addi t0, t0, {offset}")



    def initialize_offsets(self):
        for scope in self.symbol_table.all_scopes:
            offset = 0
            for entity in scope.entities:
                if entity.name not in self.offset_map[scope.name]:
                    self.offset_map[scope.name][entity.name] = offset
                    offset -= 4


    def loadvr(self, var, reg):
        if var.isdigit():
            self.emit(f"li {reg}, {var}")
        else:
            scope = self.find_scope_of(var)
            level_diff = self.symbol_table.current_scope().nesting_level - scope.nesting_level
            if level_diff == 0:
                offset = self.offset_map[scope.name][var]
                self.emit(f"lw {reg}, {offset}(sp)")
            else:
                self.gnvlcode(var)
                self.emit(f"lw {reg}, 0(t0)")

    def storerv(self, reg, var):
        scope = self.find_scope_of(var)
        level_diff = self.symbol_table.current_scope().nesting_level - scope.nesting_level
        if level_diff == 0:
            offset = self.offset_map[scope.name][var]
            self.emit(f"sw {reg}, {offset}(sp)")
        else:
            self.gnvlcode(var)
            self.emit(f"sw {reg}, 0(t0)")

    def handle_function_call(self, func_name, args, return_var=None):
        self.emit("addi sp, sp, -128")
        self.emit("sw fp, 124(sp)")
        self.emit("mv fp, sp")

        for i, arg in enumerate(args):
            reg = f"a{i}"
            self.loadvr(arg, reg)

        self.emit(f"jal {func_name}")

        if return_var:
            self.storerv('a0', return_var)

        self.emit("lw fp, 124(sp)")
        self.emit("addi sp, sp, 128")

    def gen(self):
        self.initialize_offsets()
        self.emit(".text")
        self.emit(".globl main")

        for i, quad in enumerate(self.quads):
            op, x, y, z = quad

            if op == 'begin_block':
                self.current_scope = x
                self.sp_offset = 0
                self.emit(f"{x}:")
                self.emit("addi sp, sp, -128")
                self.emit("sw ra, 124(sp)")

            elif op == 'end_block':
                self.emit("lw ra, 124(sp)")
                self.emit("addi sp, sp, 128")
                self.emit("jr ra")

            elif op == ':=':
                self.loadvr(x, 't1')
                self.storerv('t1', z)

            elif op in ['+', '-', '*', '/']:
                self.loadvr(x, 't1')
                self.loadvr(y, 't2')
                self.emit(f"{self.arith_op(op)} t3, t1, t2")
                self.storerv('t3', z)

            elif op in ['<', '<=', '>', '>=', '=', '<>']:
                self.loadvr(x, 't1')
                self.loadvr(y, 't2')
                if op == '<':
                    self.emit("slt t3, t1, t2")
                elif op == '>':
                    self.emit("slt t3, t2, t1")
                elif op == '<=':
                    self.emit("slt t3, t2, t1")
                    self.emit("xori t3, t3, 1")
                elif op == '>=':
                    self.emit("slt t3, t1, t2")
                    self.emit("xori t3, t3, 1")
                elif op == '=':
                    self.emit("sub t3, t1, t2")
                    self.emit("seqz t3, t3")
                elif op == '<>':
                    self.emit("sub t3, t1, t2")
                    self.emit("snez t3, t3")
                self.storerv('t3', z)

            elif op == 'and':
                self.loadvr(x, 't1')
                self.loadvr(y, 't2')
                self.emit("and t3, t1, t2")
                self.storerv('t3', z)

            elif op == 'or':
                self.loadvr(x, 't1')
                self.loadvr(y, 't2')
                self.emit("or t3, t1, t2")
                self.storerv('t3', z)

            elif op == 'not':
                self.loadvr(x, 't1')
                self.emit("seqz t3, t1")
                self.storerv('t3', z)

            elif op == 'cjump':
                self.loadvr(x, 't1')
                self.emit(f"beqz t1, {z}")

            elif op == 'jump':
                self.emit(f"j {z}")

            elif op == 'label':
                self.emit(f"{x}:")

            elif op == 'ret':
                self.loadvr(x, 'a0')

            elif op == 'call':
                self.emit(f"jal {x}")
                if z and z != '_':
                    self.storerv('a0', z)

            elif op == 'par':
                if y == "cv":
                    self.loadvr(x, 'a0')
                elif y == "ref":
                    self.gnvlcode(x)
                    self.emit("mv a1, t0")
                elif y == "ret":
                    self.gnvlcode(x)
                    self.emit("mv a2, t0")

            elif op == 'halt':
                self.emit("li a7, 10")
                self.emit("ecall")

            else:
                self.emit(f"# Unsupported quad: {quad}")

        return '\n'.join(self.output)

    def arith_op(self, op):
        return {'+': 'add', '-': 'sub', '*': 'mul', '/': 'div'}[op]







# όρισμα
if __name__ == "__main__":
    filename = sys.argv[1]
    with open(filename, 'r', encoding="utf-8") as file:
        code = file.read()

    tokens = lexer(code)
    # εκτύπωση tokens που βγάζει ο λεκτικός
    print("tokens από λεκτικό αναλυτή")
    for token in tokens:
        print(token)

    parser = Parser(tokens)

    parser.program()
    print("\nΤο πρόγραμμα είναι συντακτικά ορθό :)")

    parser.ir.write_quads_to_file("quads.txt")
    print("\nΟι τετράδες αποθηκεύτηκαν στο quads.txt")

    parser.symbol_table.write_to_file("symbol_table.txt")
    print("\nΠίνακας Συμβόλων αποθηκεύτηκε στο symbol_table.txt")

    gen = RISCGenerator(parser.ir.quads, parser.symbol_table)
    riscv_code = gen.gen()
    with open('output.s', 'w',encoding="utf-8") as f:
            f.write(riscv_code)


