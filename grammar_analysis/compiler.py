from .utils import C0lexer, special_lexer
import os
from .interpreter import Interpreter

class Compiler():
    '''重构C0编译器'''
    def __init__(self, words, errs):
        self.words = words
        self.error_msg_box = errs
        self.words_p = 0
        self.words_lim = len(self.words)
        self.code = []
        self.cur_lev = 1
        self.lev_stack = []
        self.lev_cnt = 1
        self.display = []
        self.const = []
        self.zipper_cnt = 0
    
    def _getword(self):
        '''
            返回下一个单词
        '''
        if self.words_p < self.words_lim and self.words_p >= 0:
            res = self.words[self.words_p]
            self.words_p += 1
            return res
    
    def _curword(self):
        '''
            返回当前指针所指单词
        '''
        if self.words_p < self.words_lim and self.words_p >= 0:
            return self.words[self.words_p]
        elif self.words_p >= self.words_lim:
            return self.words[-1]
    
    def _error(self, msg):
        '''
            出错处理程序
        '''
        wd = self._curword()
        self.error_msg_box.append("第"+ str(wd[0]) + "行:" + msg)
        while (wd[2] != '专用符号' or wd[3] != ';')  and self.words_p< self.words_lim:
            self._getword()
            wd = self._curword()

    
    def _insert_const(self, name, value):
        '''
            插入常数表
        '''
        for record in self.const:
            if record[0] == name:
                self.error_msg_box.append("常量"+ name + "重复定义")
                return  False
        self.const.append([name, value])
        return True

    def _lookup_const(self, name):
        '''
            查找常数表
        '''
        for record in self.const:
            if record[0] == name:
                return record
        return False
    
    def _lookup_display(self, name):
        '''
            查找变量表
        '''
        lev = None
        for i in range(len(self.display)-1, -1, -1):
            record = self.display[i]
            if record[0] == name and record[-1] == self.cur_lev:
                return record
        for i in range(len(self.display)-1, -1, -1):
            record = self.display[i]
            if record[1] == 'abp' and record[-1] == self.cur_lev:
                lev = int(record[0])
        if lev:
            for record in self.display:
                if record[0] == name and record[-1] == lev:
                    return record
        return False
    
    def _insert_display(self, name, typ, value, address, lev):
        '''
            插入变量表
        '''
        res = self._lookup_display(name)
        if res:
            self._error('变量' + name + '重复定义')
        elif self._lookup_const(name):
            self._error('变量' + name + '重复定义')
        else:
            if address is None:
                address = len(self.display)
            self.display.append([name,typ,value,address,lev])
    
    def _force_insert_display(self, name, typ, value, address, lev):
        '''
            如果形参和全局变量重复，直接强制插入
        '''
        if address is None:
            address = len(self.display)
        self.display.append([name, typ, value, address, lev])
    
    def _new_lev(self):
        '''
            进入一个新的层次
        '''
        self.lev_stack.append(self.cur_lev)
        self.lev_cnt += 1
        self.cur_lev = self.lev_cnt
        self._insert_display('ret_addr', 'ret_addr', None, None, self.cur_lev)
        self._insert_display(self.lev_stack[-1], 'abp', self.lev_stack[-1], None, self.cur_lev)
    
    def _gen_Pcode(self, code):
        '''
            给代码加上编号
        '''
        res = [len(self.code)]
        res.extend(code)
        self.code.append(res)

    def print_Pcode(self):
        '''
            将Pcode打印成表
        '''
        print("Pcode")
        for code in self.code:
            record = ""
            for ele in code:
                record += str(ele)+"\t"
            record += "\n"
            print(record)
    
    def web_output_Pcode_table(self):
        '''
            生成H5代码
        '''
        h5 = ""
        for code in self.code:
            line = "<tr>"
            for ele in code:
                line += "<td>" + str(ele) + "</td>"
            line += "</tr>"
            h5 += line
        return h5

    
    def print_display(self):
        '''
            打印变量表
        '''
        print("变量表")
        print("name\t" + "type\t" + "value\t" + "addr\t" + "lev\t")
        for record in self.display:
            line = ""
            if record[1] == "abp" or record[1] == "ret_addr" or record[1] == "str":
                continue
            for ele in record:
                line += str(ele) + "\t"
            line += "\n"
            print(line)
    
    def web_output_display_table(self):
        '''
            生成H5表格代码
        '''
        h5 = ""
        for record in self.display:
            line = "<tr>"
            if record[1] == "abp" or record[1] == 'ret_addr' or record[1] == 'str':
                continue
            for ele in record:
                line += "<td>" + str(ele) + "</td>"
            line += "</tr>"
            h5 += line
        return h5
    
    def print_rconst(self):
        '''
            打印常量表
        '''
        print("常量表")
        print("name\t" + "value\t")
        for record in self.const:
            line = ""
            for ele in record:
                line += str(ele) + "\t"
            line += "\n"
            print(line)
    
    def web_output_rconst_table(self):
        '''
            生成H5代码
        '''
        h5 = ""
        for record in self.const:
            line = "<tr>"
            for ele in record:
                line += "<td>" + str(ele) + "</td>"
            line += "</tr>"
            h5 += line
        return h5
    
    def print_error(self):
        '''
            打印报错信息
        '''
        print("错误信息")
        for record in self.error_msg_box:
            print(record)
    
    def web_output_error_table(self):
        '''
            生成H5代码
        '''
        i = 0
        h5 = ""
        for record in self.error_msg_box:
            line = "<tr class=\"danger\" >"
            line += "<td>" + record + "</td>"
            line += "</tr>"
            h5 += line
        return h5
    
    def report_result(self):
        '''
            打印编译结果
        '''
        if len(self.error_msg_box) > 0:
            self.print_error()
        else:
            self.print_display()
            self.print_rconst()
            self.print_Pcode()
 
    def read(self, file_name: str):
        self.input_file_name = file_name
        with open(file_name, "r") as f:
            length = int(str(f.readline()).strip())
            for i in range(length):
                word = list(str(f.readline()).strip().split(" "))
                self.words.append(word)
        f.close()

    def s_program(self):
        '''
            ＜程序＞ ::=  〔＜常量说明部分＞〕〔＜变量说明部分＞〕｛＜函数定义部分＞｝＜主函数＞
        '''
        wd = self._curword()
        if wd[2] == '关键字' and wd[3] == 'CONST':
            self.s_const_statement()
        wd = self._curword()
        p0 = self.words_p
        if wd[2] == '关键字' and wd[3] == 'INT':
            self._getword()
            wd = self._curword()
            if wd[2] == '标识符':
                self._getword()
                wd = self._curword()
                if wd[2] == '专用符号' and (wd[3] == ',' or wd[3] == ';'):
                    self.words_p = p0
                    self.s_var_statement()
                else:
                    self.words_p = p0
            else:
                self.words_p = p0

        wd = self._curword()
        p0 = self.words_p
        flag = False
        if wd[2] == '关键字' and (wd[3] == 'INT' or wd[3] == 'VOID'):
            self._getword()
            wd = self._curword()
            if wd[2] == '标识符':
                self._getword()
                wd = self._curword()
                if wd[2] == '专用符号' and wd[3] == '(':
                    self.words_p = p0
                    flag = True
                    self.s_func_def()
                else:
                    self.words_p = p0
            else:
                self.words_p = p0

        while flag:
            flag = False
            p0 = self.words_p
            wd = self._curword()
            if wd[2] == '关键字' and (wd[3] == 'INT' or wd[3] == 'VOID'):
                self._getword()
                wd = self._curword()
                if wd[2] == '标识符':
                    self._getword()
                    wd = self._curword()
                    if wd[2] == '专用符号' and wd[3] == '(':
                        self.words_p = p0
                        flag = True
                        self.s_func_def()
                    else:
                        flag = False
                        self.words_p = p0
                else:
                    self.words_p = p0
        
        wd = self._curword()
        self.s_main_func()
    
    def s_const_statement(self):
        '''
            ＜常量说明部分＞  ::=  const ＜常量定义＞｛,＜常量定义＞};
        '''
        wd = self._curword()
        if wd[2]!= '关键字' or wd[3] != 'CONST':
            self._error('应为const')
        else:
            self._getword()
            self.s_const_def()
            wd = self._curword()
            while wd[2] == '专用符号' and wd[3] == ',':
                self._getword()
                self.s_const_def()
                wd = self._curword()
            wd = self._curword()
            if wd[2] != '专用符号' or wd[3] != ';':
                self.error_msg_box.append(["第"+str(wd[0])+'行：缺少;'])
            else:
                self._getword()
    
    def s_const_def(self):
        '''
            ＜常量定义＞  ::=  ＜标识符＞＝＜整数＞
        '''
        wd = self._curword()
        if wd[2] != '标识符':
            self._error("缺少标识符")
        else:
            name = wd[3]
            self._getword()
            wd = self._curword()
            if wd[2] != '专用符号' and wd[3] != '=':
                self._error("缺少=")
            else:
                self._getword()
                num = self.s_number()
                self._insert_const(name, num)
    
    def s_number(self):
        '''
            ＜整数＞ ::=  〔＋｜－〕＜非零数字＞｛＜数字＞｝｜０
        '''
        wd = self._curword()
        num = 0
        flag = 1
        if wd[2] == '+' or wd[2] == '-':
            if wd[2] == '-':
                flag = -1
            self._getword()
            wd = self._curword()
            if wd[2] != '整数':
                self._error("缺少整数")
            else:
                num = int(wd[3])*flag
                self._getword()
                return num
        elif wd[2] == '整数' and wd[3] == '0':
            self._getword() 
            return 0
        elif wd[2] == '整数':
            self._getword()
            num = int(wd[3])*flag
            return num
        else:
            self._error("缺少整数")
    
    def s_statement_head(self):
        '''
            ＜声明头部＞ ::=  int　＜标识符＞ 
        '''
        wd = self._curword()
        if wd[2] != '关键字' or wd[3] != 'INT':
            self._error("应为int")
        else:
            self._getword()
            wd = self._curword()
            if wd[2] != '标识符':
                self._error("声明头部缺少标识符")
            else:
                name = wd[3]
                self._getword()
                return name
    
    def s_var_statement(self):
        '''
            ＜变量说明部分＞ ::=  ＜声明头部＞｛，＜标识符＞｝；
        '''
        name = self.s_statement_head()
        self._insert_display(name, 'int', None, None, self.cur_lev)
        wd = self._curword()
        while wd[2] == '专用符号' and wd[3] == ',':
            self._getword()
            wd = self._curword()
            if wd[2] != '标识符':
                self._error("缺少标识符")
            else:
                name = wd[3]
                self._insert_display(name, 'int', None, None, self.cur_lev)
                self._getword()
                wd = self._curword()
        wd = self._curword()
        if wd [2] != '专用符号' or wd[3] != ';':
            self.error_msg_box.append('第' + str(wd[0]) + '行：缺少；' )
        else:
            self._getword()
            
    
    def s_func_def(self):
        '''
            ＜函数定义部分＞ ::=  （＜声明头部＞｜void ＜标识符＞）＜参数＞＜复合语句＞
        '''
        wd = self._curword()
        if wd[2] == '关键字' and wd[3] == 'INT':
            name = self.s_statement_head()
            self._insert_display(name, 'func', None, None, self.cur_lev)
            self._new_lev()
            cnt = self.s_param()
            record = self._lookup_display(name)
            self.display[record[-2]][2] = cnt
            code = [name+":", "", "",""]
            self._gen_Pcode(code)
            self.s_complex_claus()
            self._gen_Pcode(["DIS", 3, self.cur_lev, 1])
            self.cur_lev = self.lev_stack.pop()
        elif wd[2] == '关键字' and wd[3] == 'VOID':
            self._getword()
            wd = self._curword()
            if wd[2] != '标识符':
                self._error("缺少标识符")
            else:
                name = wd[3]
                self._getword()
                self._insert_display(name, 'void func', None, None, self.cur_lev)
                self._new_lev()
                cnt = self.s_param()
                record = self._lookup_display(name)
                self.display[record[-2]][2] = cnt
                code = [name+":", "", "",""]
                self._gen_Pcode(code)
                self.s_complex_claus()
                self._gen_Pcode(["DIS", 3 , self.cur_lev, 1])
                self.cur_lev = self.lev_stack.pop()
        else:
            self._error("应为INT或VOID")

    def s_complex_claus(self):
        '''
            ＜复合语句＞ ::=  ‘{’〔＜常量说明部分＞〕〔＜变量说明部分＞〕＜语句序列＞‘}’
        '''
        wd = self._curword()
        if wd[2] != '专用符号' or wd[3] != '{':
            self._error("缺少｛")
        else:
            p0 = self.words_p
            self._getword()
            wd = self._curword()
            if wd[2] == '关键字' and wd[3] == 'CONST':
                self.s_const_statement()
                p0 = self.words_p
            wd = self._curword()
            if wd[2] == '关键字' and wd[3] == 'INT':
                self.s_var_statement()
            self.s_clause_series()
            wd = self._curword()
            if wd[2] != '专用符号' or wd[3] != '}':
                self._error("缺少}")
            else:
                self._getword()

    
    def s_param(self):
        '''
            ＜参数＞ ::=  ‘(’＜参数表＞‘)’
        '''
        wd = self._curword()
        cnt = 0
        if wd[2] != '专用符号' or wd[3] != '(':
            self._error("应为(")
        else:
            self._getword()
            cnt = self.s_param_list()
            wd = self._curword()
            if wd[2] != '专用符号' or wd[3] != ')':
                self._error("应为)")
            else:
                self._getword()
        return cnt
    
    def s_param_list(self):
        '''
            ＜参数表＞ ::=  int ＜标识符＞｛，int ＜标识符＞} | 空
        '''
        wd = self._curword()
        cnt = 0
        if wd[2] == '关键字' and wd[3] == 'INT':
            self._getword()
            wd = self._curword()
            if wd[2] != '标识符':
                self._error("缺少标识符")
            else:
                name = wd[3]
                self._force_insert_display(name, 'int', None, None, self.cur_lev)
                cnt += 1
                self._getword()
        wd = self._curword()
        while wd[2] == '专用符号' and wd[3]  == ',':
            self._getword()
            wd = self._curword()
            if wd[2] != '关键字' or wd[3] != 'INT':
                self._error("缺少int")
            else:
                self._getword()
                wd = self._curword()
                if wd[2]!= '标识符':
                    self._error("缺少标识符")
                else:
                    name = wd[3]
                    self._force_insert_display(name, 'int', None, None, self.cur_lev)
                    cnt += 1
                    self._getword()
                    wd = self._curword()
        return cnt

    def s_main_func(self):
        '''
            ＜主函数＞ ::=  ( void ｜int ) main ＜参数＞＜复合语句＞
        '''
        wd = self._curword()
        if wd[2] != '关键字' or (wd[3] != 'VOID' and wd[3] != 'INT'):
            self._error("主函数必须以void main或int main开始")
        else:
            self._getword()
            wd = self._curword()
            if wd[2] != '关键字' or wd[3] != 'MAIN':
                self._error("应为main")
            else:
                code = ["main:", "", "", ""]
                self._gen_Pcode(code)
                self._new_lev()
                self._getword()
                self.s_param()
                self.s_complex_claus()
                self._gen_Pcode(["DIS", 3,self.cur_lev, self.lev_stack[-1]])
                self.cur_lev = self.lev_stack.pop()
    
    def s_expr(self):
        '''
            ＜表达式＞ ::=  〔＋｜－〕＜项＞｛＜加法运算符＞＜项＞｝
        '''
        wd = self._curword()
        op = ""
        if wd[2] == '+' or wd[2] == '-':
            if wd[2] == '+':
                op = "ADD"
            elif wd[2] == '-':
                op = 'SUB'
            code = ["LDC", 24, "", 0]
            self._gen_Pcode(code)
            self._getword()
        self.s_item()
        wd = self._curword()
        while wd[2] == '+' or wd[2] == '-':
            self._getword()
            self.s_item()
            if wd[2] == '+':
                code = ["ADD", 52, "", ""]
            else:
                code = ["SUB", 53, "", ""]
            self._gen_Pcode(code)
            wd = self._curword()
        if op == "ADD":
            code = [op, 52, "", ""]
            self._gen_Pcode(code)
        elif op == "SUB":
            code = [op, 53, "", ""]
            self._gen_Pcode(code)
    
    def s_item(self):
        '''
            ＜项＞ ::=  ＜因子＞{＜乘法运算符＞＜因子＞}
        '''
        self.s_factor()
        wd = self._curword()
        while wd[2] == '*' or wd[2] == '/':
            self._getword()
            self.s_factor()
            if wd[2] == '*':
                code = ['MUL', 57, "", ""]
            else:
                code = ['DIV', 58, "", ""]
            self._gen_Pcode(code)
            wd = self._curword()
    
    def s_factor(self):
        '''
            ＜因子＞ ::=  ＜标识符＞｜‘（’＜表达式＞‘）’｜＜整数＞｜＜函数调用语句＞
        '''
        p0 = self.words_p
        wd = self._curword()
        if wd[2] == '标识符':
            name = wd[3]
            self._getword()
            wd = self._curword()
            if wd[2] == '专用符号' and wd[3] == '(':
                self.words_p = p0
                self.s_call()
            else:
                record = self._lookup_const(name)
                if record:
                    value = record[1]
                    code = ["LDC", 24, "", value]
                    self._gen_Pcode(code)
                else:
                    record = self._lookup_display(name)
                    if not record:
                        msg = "第" + str(wd[0]) + "行:" +name +"未定义"
                        self.error_msg_box.append(msg)
                        while wd[2]!= "专用符号" or wd[3] != ")":
                            self._getword()
                            wd = self._curword()
                        #self._error(name +"未定义")
                    else:
                        lev = record[-1]
                        addr = record[-2]
                        code = ["LOD", 1, lev, addr]
                        self._gen_Pcode(code)
                pass
        elif wd[2] == '专用符号' and wd[3] == '(':
            self._getword()
            self.s_expr()
            wd = self._curword()
            if wd[2] != '专用符号' or wd[3] != ')':
                self._error("缺少）")
            else:
                self._getword()
        elif wd[2] == '+' or wd[2] == '-' or wd[2] == '整数':
            num = self.s_number()
            code = ["LDC", 24, "", num]
            self._gen_Pcode(code)
        else:
            self._error("缺少标识符或者表达式作为因子")
    
    def s_clause(self):
        '''
            ＜语句＞ ::= ＜条件语句＞｜＜循环语句＞｜‘{’<语句序列>‘}’｜＜函数调用语句＞;
                        ｜＜赋值语句＞; | <返回语句>;｜＜读语句＞;｜＜写语句＞;｜＜空＞
        '''
        wd = self._curword()
        if wd[2] == '关键字' and wd[3] == 'IF':
            self.s_if()
        elif wd[2] == '关键字' and wd[3] == 'WHILE':
            self.s_while()
        elif wd[2] == '专用符号' and  wd[3] == '{':
            self._getword()
            self.s_clause_series()
            wd = self._curword()
            if wd[2] != '专用符号' or wd[3] != '}':
                self._error("缺少}")
            else:
                self._getword()
        elif wd[2] == '标识符':
            p0 = self.words_p
            self._getword()
            wd = self._curword()
            if wd[2] == '专用符号' and  wd[3] == '(':
                self.words_p = p0
                self.s_call()
                wd = self._curword()
                if wd[2] != '专用符号' and wd[3] != ';':
                    self._error("缺少;")
                else:
                    self._getword()
            elif wd[2] == '专用符号' and wd[3] == '=':
                self.words_p = p0
                self.s_assign()
                wd = self._curword()
                if wd[2] !=' 专用符号' and wd[3] != ';':
                    self._error("缺少；")
                else:
                    self._getword()
            else:
                self.words_p = p0
        elif wd[2] == '关键字'  and wd[3] == 'RETURN':
            self.s_return()
            wd = self._curword()
            if wd[2] != '专用符号' or wd[3] != ';':
                self._error("缺少;")
            else:
                self._getword()
        elif wd[2] == '关键字' and wd[3] == 'SCANF':
            self.s_scanf()
            wd = self._curword()
            if wd[2] != '专用符号' or wd[3] != ';':
                self._error("缺少；")
            else:
                self._getword()
        elif wd[2] == '关键字' and wd[3] == 'PRINTF':
            self.s_printf()
            wd = self._curword()
            if wd[2] != '专用符号'  or wd[3] != ';':
                self._error("缺少;")
            else:
                self._getword()
        else:
            pass
        
    
    def s_assign(self):
        '''
            ＜赋值语句＞ ::=  ＜标识符＞＝＜表达式＞
        '''
        wd = self._curword()
        if wd[2] != '标识符':
            self._error("应为标识符")
        else:
            name = wd[3]
            record = self._lookup_const(name)
            if record:
                self._error("不能对常数"+name+"赋值！")
            else:
                record = self._lookup_display(name)
                if not record:
                    self._error("变量" + name + "未定义！")
                elif record[1] != 'int':
                    self._error(name + "不是int类型！")
                else:
                    self._gen_Pcode(["LDA", 0, record[-1], record[-2]])
                    self._getword()
                    wd = self._curword()
                    if wd[2] != '专用符号' and wd[3] != '=':
                        self._error("缺少=")
                    else:
                        self._getword()
                        self.s_expr()
                        self._gen_Pcode(["STO", 38, "", ""])
            
    def s_if(self):
        '''
            ＜条件语句＞ ::=  if‘（’＜条件＞‘）’＜语句＞〔else＜语句＞〕
        '''
        wd = self._curword()
        if wd[2] != '关键字' or wd[3] != 'IF':
            self._error("应为if")
        else:
            self._getword()
            wd = self._curword()
            if wd[2] != '专用符号' or wd[3] != '(':
                self._error("缺少（")
            else:
                self._getword()
                self.s_condition()
                wd = self._curword()
                if wd[2] != '专用符号' or wd[3] != ')':
                    self._error("缺少）")
                else:
                    self._getword()
                    #self._code_push(self.code)
                    self.zipper_cnt += 1
                    self._gen_Pcode(["JPC", 11, self.zipper_cnt, None])
                    #code_tag1 = len(self.code)
                    else_exist = False
                    self.s_clause()
                    wd = self._curword()
                    #code_tag2 = len(self.code)
                    tag1 = len(self.code)
                    if wd[2] == '关键字' and wd[3] == 'ELSE':
                        self.zipper_cnt += 1
                        self._gen_Pcode(["JMP", 10, self.zipper_cnt, None])
                        tag1 = len(self.code)
                        else_exist = True
                        self._getword()
                        self.s_clause()
                        #code_tag3 = len(self.code)
                        #self._code_push(self.code)
                        for i in range(len(self.code)):
                            if self.code[i][1] == "JMP" and self.code[i][-2] == self.zipper_cnt:
                                self.code[i][-2] = ""
                                self.code[i][-1] = len(self.code)
                                self.zipper_cnt -= 1
                                break
                    else:
                        pass
                    for i in range(len(self.code)):
                            if self.code[i][1] == "JPC" and self.code[i][-2] == self.zipper_cnt:
                                self.code[i][-2] = ""
                                self.code[i][-1] = tag1
                                self.zipper_cnt -= 1
                                break
                    '''
                    if not else_exist:
                        code_pre = self.code[:code_tag1]
                        code_suf = self.code[code_tag1:]
                        for i in range(len(code_suf)):
                            code_suf[i][0] += 1
                        self.code = code_pre
                        self._gen_Pcode(["JPC", 11, "", code_tag2+1])
                        self.code.extend(code_suf)
                    else:
                        code_pre = self.code[:code_tag1]
                        code_suf = self.code[code_tag1:]
                        for i in range(len(code_suf)):
                            code_suf[i][0] += 1
                        code_tag2 += 1
                        code_tag3 += 1
                        self.code = code_pre
                        self._gen_Pcode(["JPC", 11, "", code_tag2+1]) #因为code_tag2会写入JMP语句。所以再跳一格
                        self.code.extend(code_suf)
                        code_pre = self.code[:code_tag2]
                        code_suf = self.code[code_tag2:]
                        for i in range(len(code_suf)):
                            code_suf[i][0] += 1
                        self.code = code_pre
                        code_tag3 += 1
                        self._gen_Pcode(["JMP", 10, "", code_tag3])
                        self.code.extend(code_suf)
                    '''



    
    def s_condition(self):
        '''
            ＜条件＞ ::=  ＜表达式＞＜关系运算符＞＜表达式＞｜＜表达式＞
        '''
        self.s_expr()
        wd = self._curword()
        if wd[2] == '关系运算符':
            op = wd[3]
            if op == "==":
                code = ["EQL", 45, "", ""]
            elif op == "!=":
                code = ["NEQ", 46, "", ""]
            elif op == "<":
                code = ["LSS", 47, "", ""]
            elif op == "<=":
                code = ["LER", 48, "", ""]
            elif op == ">":
                code = ["GRT", 49, "", ""]
            elif op == ">=":
                code = ["GEQ", 50, "", ""]
            self._getword()
            self.s_expr()
            self._gen_Pcode(code)
        else:
            # 如果只有表达式而无关系运算符，那么判断结果是否为0
            self._gen_Pcode(["LDC", 24, "", 0])
            self._gen_Pcode(["EQL", 45, "", ""])
            pass
    
    def s_while(self):
        '''
            ＜循环语句＞ ::=  while‘（’＜条件＞‘）’＜语句＞
        '''
        jmp_back_code = ["JMP" ,10, "", len(self.code)]
        wd = self._curword()
        if wd[2] != '关键字' or wd[3] != 'WHILE':
            self._error("应为while")
        else:
            self._getword()
            wd = self._curword()
            if wd[2] != '专用符号' and wd[3] != '(':
                self._error("缺少（")
            else:
                self._getword()
                self.s_condition()
                wd = self._curword()
                if wd[2] != '专用符号' or wd[3] != ')':
                    self._error("缺少)")
                else:
                    self.zipper_cnt += 1
                    self._gen_Pcode(["JPC", 11, self.zipper_cnt, None])
                    #code_tag1 = len(self.code)
                    self._getword()
                    self.s_clause()
                    self._gen_Pcode(jmp_back_code)
                    for i in range(len(self.code)):
                        if self.code[i][-2] == self.zipper_cnt and self.code[i][1] == "JPC":
                            self.code[i][-1] = len(self.code)
                            self.code[i][-2] = ""
                            self.zipper_cnt -= 1
                            break
                    '''
                    code_tag2 = len(self.code)
                    code_pre = self.code[:code_tag1]
                    code_suf = self.code[code_tag1:]
                    for i in range(len(code_suf)):
                        code_suf[i][0] = code_suf[i][0] + 1
                    self.code = code_pre
                    code_tag2 += 1
                    self._gen_Pcode(["JPC", 11, "",code_tag2])
                    self.code.extend(code_suf)
                    '''
    
    def s_call(self):
        '''
            ＜函数调用语句＞ ::=  ＜标识符＞‘（’＜值参数表＞‘）’
        '''
        wd = self._curword()
        if wd[2] != '标识符':
            self._error("应为标识符")
        else:
            name = wd[3]
            self._getword()
            wd = self._curword()
            record = self._lookup_display(name)
            if not record:
                self._error("函数" + name + "未定义")
            elif record[1] != 'func' and record[1] != 'void func':
                self._error(name + "不是可调用的类型")
            else:
                code = ["MKS", 18, "", self.cur_lev]
                self._gen_Pcode(code)
                if wd[2] != '专用符号' or wd[3] != '(':
                    self._error("缺少（")
                else:
                    self._getword()
                    #找一下返回地址在哪，必然在函数名的下一个地址处
                    cnt = self.s_val_param_list(record[-2])
                    kind = record[1]
                    lineNo = -1
                    for code in self.code:
                        if code[1][:-1] == name:
                            lineNo = code[0]
                            break
                    self._gen_Pcode(['CAL', 19, "", lineNo])
                    if kind == 'func':
                        self._gen_Pcode(['LOD', 0, self.display[record[-2]+1][-1], self.display[record[-2]+1][-2] ])
                    else:
                        pass
                    if cnt < record[2]:
                        self._error("缺少参数,"+name+"的参数应为"+str(record[2]))
                    elif cnt > record[2]:
                        self._error("参数过多，"+name+"的参数应为"+str(record[2]))
                    wd = self._curword()
                    if wd[2]!='专用符号' or wd[3] != ')':
                        self._error("缺少）")
                    else:
                        self._getword()
    
    def s_val_param_list(self, addr):
        '''
            ＜值参数表＞ ::=  ＜表达式＞｛，＜表达式＞｝｜＜空＞
        '''
        cnt = 0
        base_addr = addr+3
        wd = self._curword()
        if wd[2] == '+' or wd[2] == '-' or (wd[2] == '专用符号' and wd[3] == '(') or wd[2] == '整数' or wd[2] == '标识符':
            self._gen_Pcode(["LDA", 0, self.display[base_addr][-1], base_addr])
            self.s_expr()
            self._gen_Pcode(["STO", 38, "", ""])
            base_addr += 1
            cnt += 1
            wd = self._curword()
            while wd[2] == '专用符号' and wd[3] == ',':
                cnt += 1
                self._gen_Pcode(["LDA", 0, self.display[base_addr][-1], base_addr])
                self._getword()
                self.s_expr()
                self._gen_Pcode(["STO", 38, "", ""])
                base_addr += 1
                wd = self._curword()
        else:
            pass
        return cnt

    def s_clause_series(self):
        '''
            ＜语句序列＞ ::=  ＜语句＞｛＜语句＞｝
        '''
        self.s_clause()
        wd = self._curword()
        while wd[2] == '标识符' or (wd[2] == '专用符号' and wd[3] == '{') or (wd[2] == '关键字' and (wd[3]== 'IF' or wd[3]== 'WHILE' or wd[3] == 'RETURN' or wd[3] == 'SCANF' or wd[3] == 'PRINTF')):
            self.s_clause()
            wd = self._curword()
    
    def s_scanf(self):
        '''
            ＜读语句＞ ::=  scanf‘(’＜标识符＞‘）’
        '''
        wd = self._curword()
        if wd[2] != '关键字' or wd[3] != 'SCANF':
            self._error("应为scanf")
        else:
            self._getword()
            wd = self._curword()
            if wd[2] != '专用符号' or wd[3] != '(':
                self._error("缺少（")
            else:
                self._getword()
                wd = self._curword()
                if wd[2] != '标识符':
                    self._error("缺少标识符")
                else:
                    name = wd[3]
                    record = self._lookup_const(name)
                    if record:
                        self._error("常量" + name + "不可修改")
                    else:
                        record = self._lookup_display(name)
                        if record[1] != 'int':
                            self._error(name+"不是int类型")
                        else:
                            self._gen_Pcode(["LDA", 0, record[-1], record[-2]])
                            self._gen_Pcode(["RED", 27, "", 1])
                            self._getword()
                            wd = self._curword()
                            if wd[2] != '专用符号' or wd[3] != ')':
                                self._error("缺少）")
                            else:
                                self._getword()

    def s_printf(self):
        '''
            ＜写语句＞ ::=  printf‘(’[<字符串>,][＜expression ＞]‘）’
　　　　　                  //当出现字符串时，就加印字符串, 之后打印表达式的值；
        '''
        wd = self._curword()
        if wd[2] != '关键字' or wd[3] != 'PRINTF':
            self._error("应为PRINTF")
        else:
            self._getword()
            wd = self._curword()
            if wd[2] != '专用符号' or wd[3] != '(':
                self._error("缺少(")
            else:
                self._getword()
                wd = self._curword()
                if wd[2] == '字符串':
                    name = wd[3] + str(len(self.display))
                    val = wd[3]
                    self._insert_display(name,"str", val, None, self.cur_lev)
                    record = self._lookup_display(name)
                    self._gen_Pcode(["LDS", 101, record[-1], record[-2]])
                    self._gen_Pcode(["WRS", 28, "", 1])
                    self._getword()
                    wd = self._curword()
                    if wd[2] == '专用符号' and wd[3] == ',':
                        self._getword()
                        wd = self._curword()
                        val = " "
                        name = val + str(len(self.display))
                        self._insert_display(name, "str", val, None, self.cur_lev)
                        record = self._lookup_display(name)
                        self._gen_Pcode(["LDS", 101, record[-1], record[-2]])
                        self._gen_Pcode(["WRS", 28, "", 1])
                        if wd[2] == '+' or wd[2] == '-' or wd[2] == '标识符' or wd[2] == '整数' or (wd[2] == '专用符号' and wd[3] == '('):
                            self.s_expr()
                            wd = self._curword()
                            self._gen_Pcode(["WRW", 29, "", 1])
                            if wd[2] != '专用符号' or wd[3] != ')':
                                self._error("缺少)")
                            else:
                                val = "\n"
                                name = val + str(len(self.display))
                                self._insert_display(name, "str", val, None, self.cur_lev)
                                record = self._lookup_display(name)
                                self._gen_Pcode(["LDS", 101, record[-1], record[-2]])
                                self._gen_Pcode(["WRS", 28, "", 1])
                                self._getword()
                        else:
                            self._error(",后应该为表达式")
                    elif wd[2] == '专用符号' and wd[3] == ')':
                        val = "\n"
                        name = val + str(len(self.display))
                        self._insert_display(name, "str", val, None, self.cur_lev)
                        record = self._lookup_display(name)
                        self._gen_Pcode(["LDS", 101, record[-1], record[-2]])
                        self._gen_Pcode(["WRS", 28, "", 1])
                        self._getword()
                    else:
                        #self._error("缺少‘)’或‘，’")
                        msg = "第"+str(wd[0])+"行：缺少‘）’或‘，’"
                        self.error_msg_box.append(msg)
                        while wd[2] != '专用符号' or wd[3] != ';':
                            self._getword()
                            wd = self._curword()
                elif wd[2] == '+' or wd[2] == '-' or wd[2] == '标识符' or wd[2] == '整数' or (wd[2] == '专用符号' and wd[3] == '('):
                    self.s_expr()
                    wd = self._curword()
                    self._gen_Pcode(["WRW", 29, "", 1])
                    val = "\n"
                    name = val + str(len(self.display))
                    self._insert_display(name, "str", val, None, self.cur_lev)
                    record = self._lookup_display(name)
                    self._gen_Pcode(["LDS", 101, record[-1], record[-2]])
                    self._gen_Pcode(["WRS", 28, "", 1])
                    if wd[2] != '专用符号' or wd[3] != ')':
                        #self._error("缺少)")
                        msg = "第"+str(wd[0])+"行缺少‘）’"
                        self.error_msg_box.append(msg)
                        while wd[2] != '专用符号' or wd[2] != ';':
                            self._getword()
                            wd = self._curword()
                    else:
                        self._getword()
                elif wd[2] == '专用符号' and wd[3] == ')':
                        val = "\n"
                        name = val + str(len(self.display))
                        self._insert_display(name, "str", val, None, self.cur_lev)
                        record = self._lookup_display(name)
                        self._gen_Pcode(["LDS", 101, record[-1], record[-2]])
                        self._gen_Pcode(["WRS", 28, "", 1])
                        self._getword()
                else:
                    #self._error("缺少）")
                    msg = "第"+str(wd[0])+"行缺少‘）’"
                    self.error_msg_box.append(msg)
                    while wd[2] != '专用符号' or wd[2] != ';':
                        self._getword()
                        self._curword()

    
    def s_return(self):
        '''
            ＜返回语句＞ ::=  return [ ‘(’＜表达式＞’)’ ] 
        '''
        wd = self._curword()
        if wd[2] != '关键字'  or wd[3] != 'RETURN':
            self._error("应为return")
        else:
            self._getword()
            wd = self._curword()
            if wd[2] == '专用符号' and wd[3] == '(':
                record = self._lookup_display('ret_addr')
                self._gen_Pcode(['LDA', 0, record[-1], record[-2]])
                self._getword()
                self.s_expr()
                wd = self._curword()
                self._gen_Pcode(["STO", 38, "", ""])
                self._gen_Pcode(["EXF", 33, "", ""])
                if wd[2] != '专用符号' and wd[2] != ')':
                    self._error("缺少）")
                else:
                    self._getword()
            else:
                self._gen_Pcode(["EXF", 33, "", ""])
                pass
        self._gen_Pcode(["DIS", 3, self.cur_lev, 1])
    

if __name__ == "__main__":
    FILE_NAME = "/home/tarpe/shared/OnlineC0/OnlineC0/test/C0/C0_TEST5.TXT"
    lexer = special_lexer(FILE_NAME)
    lexer.word_analyze()
    #lexer.print_result()
    lexer.output()
    errors = lexer.error_message_box
    words = lexer.RESULT
    compiler = Compiler(words, errors)
    compiler.s_program()
    compiler.report_result()
    if len(compiler.error_msg_box) > 0:
        exit()
    display_table = compiler.display
    Pcode = compiler.code
    input_stream = "5 4"
    interpreter = Interpreter(display_table, Pcode, input_stream=input_stream)
    interpreter.main()
    print("执行结果：")
    print(interpreter.res)
                

