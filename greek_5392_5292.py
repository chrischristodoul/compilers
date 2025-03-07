import sys
#made in Python 3.13.2
#Χριστοδούλου Χρήστος 5392, Μπάμπαλης Στυλιανός 5292

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

#λεκτικός αναλυτής greek++
def lexer(code):
    tokens = []
    i = 0
    line = 1
    while i < len(code):
        char = code[i]  #στοιχείο κώδικα

        #κενά, tabs, newlines αγνούνται
        if char in " \t":
            i += 1
            continue
        if char == "\n":
            line += 1
            i += 1
            continue

        #νούμερα
        if char in DIGITS:
            num = ''
            while i < len(code) and code[i] in DIGITS:
                num += code[i]
                i += 1
            tokens.append(("NUMBER", num, line))
            continue

        #γράμματα
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


        #πράξη ανάθεσης
        if char == ":" and i + 1 < len(code) and code[i + 1] == "=":
            tokens.append(("OPERATOR", ":=", line))
            i += 2
            continue
        #λοιπές πράξεις
        if char in OPERATORS:
            op = char
            i += 1
            if i < len(code) and code[i] in OPERATORS:
                op += code[i]
                i += 1
            tokens.append(("OPERATOR", op, line))
            continue

        #ερωτηματικό, κόμμα , άνω και κάτω τελεία
        if char in DELIMITERS:
            tokens.append(("DELIMITER", char, line))
            i += 1
            continue
        #αγκύλες
        if char in GROUPING:
            tokens.append(("GROUPING", char, line))
            i += 1
            continue

        #σχόλια
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

        #αναφορά
        if char in REFERENCE:
            tokens.append(("REFERENCE", char, line))
            i += 1
            continue

        #σφάλμα άγνωστου χαρακτήρα
        print(f"Σφάλμα: Άγνωστος χαρακτήρας '{char}' στη γραμμή {line}")
        i += 1
    return tokens


#συντακτικός αναλυτής greek++
#τα συντακτικά error δεν αναφέρουν τη γραμμή που εντοπίζεται το λάθος, θα υλοποιηθεί αργότερα στη βελτιστοποίηση
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        #αφαιρώ απο τη λίστα των tokens τα σχόλια, για να τα αγνοεί ο parser
        self.tokens = [token for token in self.tokens
                       if "COMMENT" != token[0]]
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None

    def eat(self, token_type, value=None):
        if self.current_token is None:
            raise SyntaxError(f"Σφάλμα: Αναμενόταν περισσότερα tokens, όμως το αρχείο τελείωσε.")

        current_type = self.current_token[0]
        current_value = self.current_token[1] if self.current_token[1] else None

        #έλεγχος μήκους IDENTIFIER
        if current_type == "IDENTIFIER" and len(current_value) > 30:
            raise SyntaxError(f"Σφάλμα: Το αναγνωριστικό '{current_value}' υπερβαίνει τους 30 χαρακτήρες.")

        if current_type == token_type and (value is None or current_value == value):
            self.pos += 1
            self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None
        else:
            raise SyntaxError( f"Σφάλμα: Περίμενα {token_type} {value if value else ''}, αλλά βρήκα {self.current_token}")

    #ορισμός προγράμματος
    def program(self):
        self.eat("KEYWORD", "πρόγραμμα")
        self.eat("IDENTIFIER")
        self.program_block()

    def program_block(self):
        self.declarations()
        self.subprograms()
        self.eat("KEYWORD", "αρχή_προγράμματος")
        self.sequence()
        self.eat("KEYWORD", "τέλος_προγράμματος")

    #δηλώσεις μεταβλητών
    def declarations(self):
        while self.current_token and self.current_token[1] == "δήλωση":
            self.eat("KEYWORD", "δήλωση")
            if self.current_token and self.current_token[0] == "IDENTIFIER":
                self.varlist()
            else:
                raise SyntaxError(f"Σφάλμα: Αναμενόταν λίστα μεταβλητών μετά τη 'δήλωση', αλλά βρέθηκε {self.current_token}")

    def varlist(self):
        self.eat("IDENTIFIER")
        while self.current_token and self.current_token[1] == ",":
            self.eat("DELIMITER", ",")
            if self.current_token and self.current_token[0] == "IDENTIFIER":
                self.eat("IDENTIFIER")
            else:
                raise SyntaxError(f"Σφάλμα: Περίμενα αναγνωριστικό μετά το ',', αλλά βρήκα {self.current_token}")

    #functions, procedures (υποπρογράμματα)
    def subprograms(self):
        while self.current_token and self.current_token[1] in {"συνάρτηση", "διαδικασία"}:
            if self.current_token[1] == "συνάρτηση":
                self.function()
            else:
                self.procedure()

    def function(self):
        self.eat("KEYWORD", "συνάρτηση")
        self.eat("IDENTIFIER")
        self.eat("GROUPING", "(")
        self.formalparlist()
        self.eat("GROUPING", ")")
        self.funcblock()

    def procedure(self):
        self.eat("KEYWORD", "διαδικασία")
        self.eat("IDENTIFIER")
        self.eat("GROUPING", "(")
        self.formalparlist()
        self.eat("GROUPING", ")")
        self.procblock()

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
            self.varlist()

    def funcoutput(self):
        if self.current_token and self.current_token[0] == "KEYWORD" and self.current_token[1] == "έξοδος":
            self.eat("KEYWORD", "έξοδος")
            self.varlist()

    #ακολουθία εντολών
    def sequence(self):
        while self.current_token and self.current_token[0] in {"IDENTIFIER", "KEYWORD"}:
            #επιστρέφω στο if
            if self.current_token[1] in {"αλλιώς", "εάν_τέλος", "όσο_τέλος", "για_τέλος", "τέλος_προγράμματος", "τέλος_διαδικασίας" , "τέλος_συνάρτησης", "τέλος_προγράμματος" , "μέχρι"}:
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

    #εκφράσεις και πράξεις
    def assignment(self):
        self.eat("IDENTIFIER")
        self.eat("OPERATOR", ":=")
        self.expression()
        if self.current_token and self.current_token[1] == ";":
            self.eat("DELIMITER", ";")
            return
        raise SyntaxError(f"Σφάλμα: Λείπει ; μετά από εκχώρηση τιμής")

    def expression(self):
        self.optional_sign()
        self.term()
        while self.current_token and self.current_token[1] in {"+", "-"}:
            self.addoper()
            self.term()

    def term(self):
        self.factor()
        while self.current_token and self.current_token[1] in {"*", "/"}:
            self.muloper()
            self.factor()

    def factor(self):
        if self.current_token[0] == "NUMBER":
            self.eat("NUMBER")
        elif self.current_token[0] == "IDENTIFIER":
            self.eat("IDENTIFIER")
            self.idtail()
        elif self.current_token[1] == "(":
            self.eat("GROUPING", "(")
            self.expression()
            self.eat("GROUPING", ")")
        else:
            raise SyntaxError(f"Σφάλμα στην παράσταση: {self.current_token}")

    def optional_sign(self):
        if self.current_token and self.current_token[1] in {"+", "-"}:
            self.addoper()

    def addoper(self):
        self.eat("OPERATOR")

    def muloper(self):
        self.eat("OPERATOR")

    #συνθήκες και λογικοί τελεστές
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
        if self.current_token[1] == "όχι":
            self.eat("KEYWORD", "όχι")
            self.eat("GROUPING", "[")
            self.condition()
            self.eat("GROUPING", "]")
        elif self.current_token[1] == "[":
            self.eat("GROUPING", "[")
            self.condition()
            self.eat("GROUPING", "]")
        else:
            self.expression()
            self.eat("OPERATOR")

    def if_statement(self):
        self.eat("KEYWORD", "εάν")
        self.condition()
        self.eat("KEYWORD", "τότε")
        self.sequence()

        if self.current_token and self.current_token[1] == "αλλιώς":
            self.eat("KEYWORD", "αλλιώς")
            self.sequence()

        #μετά το if-else, περιμένω το εάν_τέλος
        self.eat("KEYWORD", "εάν_τέλος")

    #ορισμοί _stat
    def while_stat(self):
        self.eat("KEYWORD", "όσο")
        self.condition()
        self.eat("KEYWORD", "επανάλαβε")
        self.sequence()
        self.eat("KEYWORD", "όσο_τέλος")

    def do_stat(self):
        self.eat("KEYWORD", "επανάλαβε")
        self.sequence()
        self.eat("KEYWORD", "μέχρι")
        self.condition()

    def for_stat(self):
        self.eat("KEYWORD", "για")
        self.eat("IDENTIFIER")
        self.eat("OPERATOR", ":=")
        self.expression()
        self.eat("KEYWORD", "έως")
        self.expression()
        self.step()
        self.eat("KEYWORD", "επανάλαβε")
        self.sequence()
        self.eat("KEYWORD", "για_τέλος")

    def idtail(self):
        #idtail -> actualpars | (empty)
        if self.current_token and self.current_token[0] == "GROUPING" and self.current_token[1] == "(":
            self.actualpars()

    #actualpars -> '(' actualparlist ')'
    def actualpars(self):
        self.eat("GROUPING", "(")
        self.actualparlist()
        self.eat("GROUPING", ")")

    #actualparlist -> actualparitem ( ',' actualparitem )* | (empty)
    def actualparlist(self):
        if self.current_token and (self.current_token[0] in {"IDENTIFIER", "NUMBER"} or (self.current_token[0] == "REFERENCE")):
            self.actualparitem()
            while self.current_token and self.current_token[0] == "DELIMITER" and self.current_token[1] == ",":
                self.eat("DELIMITER", ",")
                self.actualparitem()

    #actualparitem -> expression |  '%' ID
    def actualparitem(self):
        if self.current_token and self.current_token[0] == "REFERENCE":
            self.eat("REFERENCE", "%")
            self.eat("IDENTIFIER")
        else:
            self.expression()

    #condition -> boolterm ( 'ή' boolterm )*
    def condition(self):

        self.boolterm()
        while self.current_token and self.current_token[0] == "KEYWORD" and self.current_token[1] == "ή":
            self.eat("KEYWORD", "ή")
            self.boolterm()
    #boolterm -> boolfactor ( 'και' boolfactor )*
    def boolterm(self):
        self.boolfactor()
        while self.current_token and self.current_token[0] == "KEYWORD" and self.current_token[1] == "και":
            self.eat("KEYWORD", "και")
            self.boolfactor()

    #boolfactor -> 'όχι' '[' condition ']' | '[' condition ']' | expression relational_op expression
    def boolfactor(self):
        if self.current_token and self.current_token[0] == "KEYWORD" and self.current_token[1] == "όχι":
            self.eat("KEYWORD", "όχι")
            self.eat("GROUPING", "[")
            self.condition()
            self.eat("GROUPING", "]")
        elif self.current_token and self.current_token[0] == "GROUPING" and self.current_token[1] == "[":
            self.eat("GROUPING", "[")
            self.condition()
            self.eat("GROUPING", "]")
        else:
            self.expression()
            self.relational_oper()
            self.expression()

    #relational_op -> '=' , '<=' , '>=' , '<>' , '<' , '>'
    def relational_oper(self):
        if self.current_token and self.current_token[0] == "OPERATOR" and self.current_token[1] in {"=", "<=", ">=", "<>", "<", ">"}:
            self.eat("OPERATOR")
        else:
            self.error("Αναμενόταν τελεστής συσχέτισης")

    #input_stat -> 'διάβασε' ID
    def input_stat(self):
        self.eat("KEYWORD", "διάβασε")
        self.eat("IDENTIFIER")
    #print_stat -> 'γράψε' expression
    def print_statement(self):
        self.eat("KEYWORD", "γράψε")
        self.expression()
    #call_stat -> 'εκτέλεσε' ID idtail
    def call_stat(self):
        self.eat("KEYWORD", "εκτέλεσε")
        self.eat("IDENTIFIER")
        self.idtail()
    #step -> 'με_βήμα' expression | (empty)
    def step(self):
        if self.current_token and self.current_token[0] == "KEYWORD" and self.current_token[1] == "με_βήμα":
            self.eat("KEYWORD", "με_βήμα")
            self.expression()

#όρισμα
if __name__ == "__main__":
    filename = sys.argv[1]
    with open(filename, 'r', encoding="utf-8") as file:
        code = file.read()

    tokens = lexer(code)
    #εκτύπωση tokens που βγάζει ο λεκτικός
    print("tokens από λεκτικό αναλυτή")
    for token in tokens:
        print(token)
    parser = Parser(tokens)
    parser.program()

    print("\nΤο πρόγραμμα είναι συντακτικά ορθό :)")



