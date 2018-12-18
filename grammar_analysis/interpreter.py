from .utils import special_lexer, norm_C0_compiler
import os
class Interpreter():
    def __init__(self, display_table:list, Pcode_list:list , input_stream=""):
        self.display_table = display_table
        self.Pcode = Pcode_list
        self.code_p = 0
        self.stack = []
        self.stack_p = 0
        self.display = 0
        self.run_stack = []
        self.run_p_stack = []
        self.res = ""
        self.error_msg_box = []
        self.input_stream = input_stream

    
    def _search_table(self, x, y):
        for record in self.display_table:
            if record[4] == x and record[3] == y:
                return record[2]
        return "error"
    
    def _LDA(self, x, y):
        addr = [x, y]
        self._push_stack(addr)
        self.code_p += 1
    
    def _push_stack(self, x):
        self.stack.append(x)
        self.stack_p += 1
    
    def _pop_stack(self):
        val = self.stack[-1]
        self.stack = self.stack[:-1]
        self.stack_p -= 1
        return val
    
    def _LOD(self,x, y):
        val = self._search_table(x, y)
        self._push_stack(val)
        self.code_p += 1
    
    def _DIS(self, x, y):
        self.display = x
        self.code_p += 1
    
    def _JMP(self, x, y):
        self.code_p = y
    
    def _JPC(self,x, y):
        val = self._pop_stack()
        if val <= 0:
            self.code_p = y
        else:
            self.code_p += 1
    
    def _MKS(self,x, y):
        self.code_p += 1
        pass
    
    def _CAL(self,x, y):
        self.run_stack.append(self.stack)
        self.run_p_stack.append(self.code_p)
        self.code_p = y
        self.code_p += 1
    
    def _LDC(self,x, y):
        self._push_stack(y)
        self.code_p +=1
    
    def _WRS(self,x,y):
        val = self._pop_stack()
        self.res += val + "\n"
        self.code_p += 1
    
    def _WRW(self,x,y):
        val = self._pop_stack()
        self.res += str(val) + "\n"
        self.code_p += 1
    
    def _EXP(self, x,y):
        self.code_p = self.run_p_stack[-1]
        self.run_p_stack = self.run_p_stack[:-1]
        self.code_p += 1
    
    def _EXF(self, x,y):
        self.code_p = self.run_p_stack[-1]
        self.run_p_stack = self.run_p_stack[:-1]
        self.code_p += 1
    
    def _STO(self, x,y):
        val = self._pop_stack()
        addr = self._pop_stack()
        x = addr[0]
        y = addr[1]
        for i in range(len(self.display_table)):
            if self.display_table[i][4] == x and self.display_table[i][3] == y:
                self.display_table[i][2] = val
                break
        self.code_p +=1
    
    def _EQL(self, x, y):
        val1 = self._pop_stack()
        val2 = self._pop_stack()
        if val1 == val2:
            self._push_stack(1)
        else:
            self._push_stack(0)
        self.code_p += 1
    
    def _NEQ(self, x, y):
        val1 = self._pop_stack()
        val2 = self._pop_stack()
        if val1 != val2:
            self._push_stack(1)
        else:
            self._push_stack(0)
        self.code_p += 1
    
    def _RED(self, x, y):
        token = ""
        i = 0
        while i < len(self.input_stream) and self.input_stream[i] != ' ':
            token += self.input_stream[i]
            i+=1
        val = int(token)
        addr = self._pop_stack()
        x = addr[0]
        y = addr[1]
        for i in range(len(self.display_table)):
            if self.display_table[i][4] == x and self.display_table[i][3] == y:
                self.display_table[i][2] = val
                break
        self.code_p += 1
    
    def _LSS(self, x, y):
        val1 = self._pop_stack()
        val2 = self._pop_stack()
        if val2 < val1:
            self._push_stack(1)
        else:
            self._push_stack(0)
        self.code_p += 1
    
    def _LER(self, x, y):
        val1 = self._pop_stack()
        val2 = self._pop_stack()
        if val2 <= val1:
            self._push_stack(1)
        else:
            self._push_stack(0)
        self.code_p += 1
    
    def _GRT(self, x, y):
        val1 = self._pop_stack()
        val2 = self._pop_stack()
        if val2 > val1:
            self._push_stack(1)
        else:
            self._push_stack(0)
        self.code_p += 1
    
    def _GEQ(self, x, y):
        val1 = self._pop_stack()
        val2 = self._pop_stack()
        if val2 > val1:
            self._push_stack(1)
        else:
            self._push_stack(0)
        self.code_p += 1
    
    def _ADD(self, x, y):
        val1 = self._pop_stack()
        val2 = self._pop_stack()
        res = val1 + val2
        self._push_stack(res)
        self.code_p += 1
    
    def _SUB(self, x, y):
        val1 = self._pop_stack()
        val2 = self._pop_stack()
        res = val2 - val1
        self._push_stack(res)
        self.code_p += 1
    
    def _MUL(self, x, y):
        val1 = self._pop_stack()
        val2 = self._pop_stack()
        res = val2*val1
        self._push_stack(res)
        self.code_p += 1
    
    def _DIV(self, x, y):
        val1 = self._pop_stack()
        val2 = self._pop_stack()
        res = int(val2/val1)
        self._push_stack(res)
        self.code_p += 1
    
    def _LDS(self, x, y):
        res = ""
        for i in range(len(self.display_table)):
            if self.display_table[i][4] == x and self.display_table[i][3] == y:
                res = self.display_table[i][2]
                break
        self._push_stack(res)
        self.code_p += 1



    
    def _error(self, s):
        self.error_msg_box.append(s)
    
    def main(self):
        flag = False
        for i in range(len(self.Pcode)):
            record = self.Pcode[i]
            if record[1] == "main:":
                flag = True
                sta = i
                break
        if not flag:
            self._error("程序没有定义入口")
            return False
        flag = False
        for i in range(sta + 1, len(self.Pcode)):
            record = self.Pcode[i]
            if record[1] == "EXP" or record[0] == "EXF":
                flag = True
                end = i
                break
        if not flag:
            self._error("主程序没有返回")
            return False
        self.code_p = sta + 1
        while(self.code_p != end):
            code = self.Pcode[self.code_p]
            cmd = "self._"
            if code[3] == '':
                x = '0'
            else:
                x = code[3]
            if code[4] == '':
                y = '0'
            else:
                y = code[4]
            cmd += code[1] + "(" + str(x) + "," + str(y) + ")"
            exec(cmd)

if __name__ == "__main__":
    FILE_NAME = "/home/tarpe/shared/OnlineC0/OnlineC0/grammar_analysis/test5.txt"
    lexer = special_lexer(FILE_NAME)
    lexer.word_analyze()
    #lexer.print_result()
    lexer.output()
    errors = lexer.error_message_box
    words = lexer.RESULT

    input_file_name = "/home/tarpe/shared/OnlineC0/test2wout.txt"
    compiler = norm_C0_compiler()
    compiler.error_msg_box = errors
    #compiler.read(input_file_name)
    compiler.words = words
    #print(compiler.words)
    compiler.s_program()
    compiler.report_result()

    display_table = compiler.display
    Pcode = compiler.code

    input_stream = "3"
    interpreter = Interpreter(display_table, Pcode, input_stream=input_stream)
    interpreter.main()
    print("执行结果：")
    print(interpreter.res)




        
        
    










