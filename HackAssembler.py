import sys

OUTPUT_FILE = "Prog.hack"


class Parser:
    """reads and interpolate commands"""
    def __init__(self, file_path):
        self.file_path = file_path

    def constructor(self):
        """Manages ASM file for reading, and close file in end of run"""
        with open(self.file_path, "r") as input_file:
            for line in input_file:
                yield line

    def hasmorelines(self):
        """boolean function that returns False when file finished reading"""
        try:
            yield from self.constructor()
        except StopIteration:
            return False

    def advance(self, line):
        """Cleans the command of any white space or instructions
        returns a clean var with the next command,
         if line had no command return null"""
        if line[0] != "/" and line != "\n":
            line_strip_space = line.replace(" ", "")
            line_strip_newline = line_strip_space.replace("\n", "")
            the_current_instruction = line_strip_newline.split("/", 1)
            return the_current_instruction[0]
        else:
            return "null"

    def instruction_type(self, command):
        """analyze the command and return the proper string for translating"""
        if command[0] == "@":
            return self.symbol(command)
        else:
            return self.c_instruction(command)

    def symbol(self, command):
        """For instruction A or L, if (XXX) returns XXX string,
         if @XXX returns XXX string"""
        if command[0] == "(":
            symbol = command.replace("(", "").replace(")", "")
            return symbol
        elif command[0] == "@":
            return str(command[1:])

    def c_instruction(self, instruction):
        """divide and return the command in the proper parameters"""
        if ";" in instruction:
            split_instruction = instruction.split(";")
            dest = "null"
            comp = split_instruction[0]
            jump = split_instruction[-1]
        else:
            split_instruction = instruction.split("=")
            dest = split_instruction[0]
            comp = split_instruction[1]
            jump = "null"
        return "C", dest, comp, jump


class Code:
    """only for C instructions,
    return for each symbolic field its binary equivalent"""
    def __init__(self, dest, comp, jump):
        self.dest = dest
        self.comp = comp
        self.jump = jump

    def comp_dest(self):
        code = ["0", "0", "0"]
        dest_code = ""
        if "M" in self.dest:
            code[2] = "1"
        if "A" in self.dest:
            code[0] = "1"
        if "D" in self.dest:
            code[1] = "1"

        for item in code:
            dest_code += item
        return dest_code

    def comp_comp(self):
        instruction = self.comp
        a = "0"
        code_library = {
                    "0": "101010", "1": "111111", "-1": "111010", "D": "001100",
                    "!D": "001101", "-D": "001111", "D+1": "011111", "D-1": "001110",
                    "A": "110000", "!A": "110001", "-A": "110011", "A+1": "110111",
                    "A-1": "110010", "D+A": "000010", "D-A": "010011", "A-D": "000111",
                    "D&A": "000000", "D|A": "010101"
                    }
        if "M" in instruction:
            a = "1"
            instruction = instruction.replace("M", "A")
        binary_code = a + code_library[instruction]
        return binary_code

    def comp_jump(self):
        jump_dic = {
            "null": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
                    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"
        }
        return jump_dic[self.jump]


class SymbolTable:
    def __init__(self, file_path):
        self.file_path = file_path
        self.inittable = self.init_table()
        self.firstpass = {**self.inittable, **self.first_pass()}
        self.symboltable = {**self.firstpass}
        self.counter = 16

    def lines_gen(self):
        with open(self.file_path, "r") as file:
            for line in file:
                if line[0] != "/" and line != "\n":
                    line_strip_space = line.replace(" ", "")
                    line_strip_newline = line_strip_space.replace("\n", "")
                    line_split = line_strip_newline.split("/", 1)
                    yield line_split[0] + "\n"

    def init_table(self):
        ramtable = {}
        for n in range(0, 16):
            ramtable["R" + str(n)] = str(n)
        return {
            **ramtable, "SCREEN": "16384", "KBD": "24576", "SP": "0",
            "LCL": "1", "ARG": "2", "THIS": "3", "THAT": "4"
        }

    def first_pass(self):
        first_pass = {}
        i = 0
        commands = self.lines_gen()
        for line in commands:
            if line[0] == "(":
                first_pass[line.replace("(", "").replace(")", "").strip("\n")] = str(i)
                i = i - 1
            i = i + 1
        return first_pass

    def addentry(self, symbol):
        self.symboltable[symbol] = self.counter
        self.counter += 1

    def does_contain(self, symbol):
        if symbol not in self.symboltable:
            self.addentry(symbol)
        return self.getaddress(symbol)

    def getaddress(self, symbol):
        return self.symboltable[symbol]


def main():
    command_arg = sys.argv
    try:
        input_file = str(command_arg[1])
    except:
        input_file = "Prog.asm"

    output_file = input_file.split(".")[0] + ".hack"

    pars_con = Parser(input_file)
    symboltable_con = SymbolTable(input_file)
    lines_gen = pars_con.hasmorelines()
    with open(output_file, "w") as out_file:
        for line in lines_gen:
            the_current_instruction = pars_con.advance(line)
            if the_current_instruction == "null" or the_current_instruction[0] == "(":
                continue

            instruction_type = pars_con.instruction_type(the_current_instruction)
            if instruction_type[0] == "C":
                code_con = Code(instruction_type[1], instruction_type[2], instruction_type[3])
                binary_dest = code_con.comp_dest()
                binary_comp = code_con.comp_comp()
                binary_jump = code_con.comp_jump()
                binary_code = "111" + binary_comp + binary_dest + binary_jump

            elif instruction_type.isdigit():
                binary_code = bin(int(instruction_type))[2:].zfill(16)

            else:
                symbol_number = symboltable_con.does_contain(instruction_type)
                binary_code = bin(int(symbol_number))[2:].zfill(16)

            out_file.write(binary_code + "\n")


if __name__ == "__main__":
    main()
