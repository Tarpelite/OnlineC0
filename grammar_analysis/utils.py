from lexer import C0lexer
import os


class special_lexer(C0lexer):
    def __init__(self, INPUT_FILE_NAME: str):
        '''
            lexer的初始化
        '''
        self.INPUT_FILE_NAME = INPUT_FILE_NAME
        self.p = 0
        self.line_cnt = 0
        self.word_cnt = 0
        self.error_message_box = []
   
    def _retract(self):
        '''
          回退一个字符
        '''
        if self.p > 0:
            self.p -= 1
        if len(self.TOKEN) > 0:
            self.TOKEN = self.TOKEN[:-1]
 
    def _isNewLine(self):
        '''
          判断是否是一个新的行
        '''
        if self.curChar() == '\r':
            self.getchar()
            if self.curChar() == '\n' or self.curChar() == '\r':
                return True
            else:
                self._retract()
                return True
        elif self.curChar() == '\n':
            self.getchar()
            if self.curChar() == '\n' or self.curChar() == '\r':
                return True
            else:
                self._retract()
                return True 
        else:
            return False
    
    def _error(self):
        '''
            增加报错信息
        '''
        msg = "词法错误：第" + str(self.line_cnt) + "行,第" + str(self.word_cnt) + "个单词：" + str(self.TOKEN)
        self.error_message_box.append(msg)
        
    def getsym(self):
        self.clearToken()
        lim = len(self.SOURCE_TEXT)
        if self.p >= lim:
            return False
        while self.isSpace() or self.isTab() or self._isNewLine():
            if self._isNewLine():
                self.line_cnt += 1
                self.word_cnt = 0
            self.p += 1
            self.clearToken()
            if self.p >= lim:
                return False
        res = [self.line_cnt, self.word_cnt]
        if self.isLetter():
            while self.isLetter() or self.isDigit():
                self.getchar()
            if self.isKeyWord():
                res.extend(['关键字', self.TOKEN.upper()])
            else:
                res.extend(['标识符', self.TOKEN])
        elif self.isDigit():
            if self.TOKEN == '0':
                res.extend(['整数', self.TOKEN])
            else:
                while self.isDigit():
                    self.getchar()
                res.extend(['整数', self.TOKEN])
        elif self.isMinus():
            flag = 0
            self.getchar()
            while self.isDigit():
                if flag == 0:
                    flag = 1
                self.getchar()
            if flag == 0:
                res.extend(['-', '-'])
            else:
                res.extend(['整数', int(self.TOKEN)])
        elif self.isPlus():
            flag = 0
            self.getchar()
            while self.isDigit():
                if flag == 0:
                    flag = 1
                self.getchar()
            if flag == 0:
                res.extend(['+',  '+'])
            else:
                res.extend(['整数', int(self.TOKEN)])
        elif self.isQuote():
            flag = 0
            self.p += 1
            while not self.isQuote():
                if self.isInvalidchar():
                    self.p += 1
                    if self.p >= len(self.SOURCE_TEXT):
                        return False
                elif self.isTrans():
                    self.p += 1
                    if self.p >= len(self.SOURCE_TEXT):
                        return False
                    self.getchar()
                else:
                    self.getchar()
            self.p += 1
            res.extend(['字符串', self.TOKEN])
        elif self.isLess():
            self.getchar()
            if self.isEqu():
                self.getchar()
                res.extend(["关系运算符", "<="])
            else:
                res.extend(["关系运算符", "<"])
        elif self.isMark():
            self.getchar()
            if self.isEqu():
                self.getchar()
                res.extend(['关系运算符', '!='])
            else:
                self._error()
        elif self.isEqu():
            self.getchar()
            if self.isEqu():
                self.getchar()
                res.extend(["关系运算符", "=="])
            else:
                res.extend(['专用符号', "="])
        elif self.isMult():
            self.getchar()
            res.extend(['*', '*'])
        elif self.isDiv():
            self.getchar()
            res.extend(['/', '/'])
        elif self.isLpar():
            self.getchar()
            res.extend(['专用符号', '('])
        elif self.isRpar():
            self.getchar()
            res.extend(['专用符号', ')'])
        elif self.isBigLpar():
            self.getchar()
            res.extend(['专用符号', '{'])
        elif self.isBigRpar():
            self.getchar()
            res.extend(['专用符号', '}'])
        elif self.isComma():
            self.getchar()
            res.extend(['专用符号', ','])
        elif self.isSemi():
            self.getchar()
            res.extend(['专用符号', ';'])
        else:
            self._error()
        self.word_cnt += 1
        self.RESULT.append(res)
        self.REPLY += "[" + str(res[2]) + ", " + str(res[3]) + "]\n"
        return True

    def error_report(self):
        '''
            错误分析报告
        '''
        if len(self.error_message_box) == 0:
            return "Successfully!"
        else:
            res = ""
            for msg in self.error_message_box:
                res += msg + "\n"
            return res

    def print_result(self):
        '''
            打印结果
        '''
        i = 1
        for res in self.RESULT:
            print("行：" + str(res[0]) + " 个: " + str(res[1]) + " 类型: " + str(res[2]) + " 值: " + str(res[3]))
        print(self.error_report())
    
    def output(self):
        '''
            输出词法分析结果文件
        '''
        length = len(self.RESULT)
        (_ , tempfilename) = os.path.split(self.INPUT_FILE_NAME)
        (filename, _) = os.path.splitext(tempfilename)
        OUTPUT_FILE_NAME = filename + "wout.txt"
        OUTPUT_ERROR_MESSAGE = filename + "error.txt"
        with open(OUTPUT_FILE_NAME, "w+") as f:
            f.write(str(length)+"\n")
            for res in self.RESULT:
                f.write(str(res[0]) + " " + str(res[1]) + " " + str(res[2]) + " " + str(res[3])+"\n")
        f.close()
        #   如果有报错
        if len(self.error_message_box) > 0:
            with open(OUTPUT_ERROR_MESSAGE, "w+") as f:
                f.write(str(len(self.error_message_box))+"\n")
                for msg in self.error_message_box:
                    f.write(msg+ "\n")
            f.close()


class norm_C0_compiler():
    def __init__(self):
        self.input_file_name = ""
        self.words = []
        self.words_p = 0
        #  words 存放词法分析之后的输出
        self.tab = []
        self.tab_p = 0
        #  tab符号表(name:标识符名称
        #        obj: 标识符种类，可以是常量，变量，函数
        #        typ: 标识符类型，可以是整型，字符,字符串
        #        lev: 表示该标识符所在分程序的静态层次
        #        adr: 变量在运行栈中分配的相对地址,或常量在表中的位置，或者字符对应的ASCII码)
        self.btab = []
        #   btab分程序表(last:始终指向该分程序中说明的当前（最后）一个标识符在tab中的位置）
        #           lastpar:指向函数最后一个参数在tab表中的位置
        #           )
        self.display = []
        #   display分程序表(用于存放和检索btab)
        self.rconst = []
        #   rconst实常量表（val：当前实常量的值）
        self.stab = []
        #   stab字符串常量表(inum:字符串起始位置，slen:字符串长度)
        self.code = []
        #   pcode表,存放生成的p_code指令
        self.error_msg_box = []
        #   存放报错信息
        self.stack_p = 0
        #   运行时栈的指针
        
    def _getword(self):
        '''
            返回下一个单词
        '''
        if self.words_p < len(self.words) and self.words_p >= 0:
            res = self.words[self.words_p]
            self.words_p += 1
            return res
        return False
    
    def _curword(self):
        '''
            返回当前指针所指的单词
        '''
        if self.words_p < len(self.words) and self.words_p >= 0:
            return self.words[self.words_p]
        return False
        
    def read(self, file_name: str):
        self.input_file_name = file_name
        with open(file_name, "r") as f:
            length = int(str(f.readline()).strip())
            for i in range(length):
                word = list(str(f.readline()).strip().split(" "))
                self.words.append(word)
        f.close()

    def _error(self, hint: str):
        '''
            添加报错信息
        '''
        wd = self._curword()
        msg = "line: " + wd[0] + " word: " + wd[1] + hint 
        self.error_msg_box.append(msg)
    

    def s_read(self):
        '''
            <读语句> -> scanf'('<标识符>')'
        '''
        self._getword()
        wd = self._curword()
        if wd[2] != '专用符号' or wd[3] != '(':
            self._error('应为(')
            return False
        self._getword()
        wd = self._curword()
        if wd[2] != '标识符' :
            self._error('应为标识符')
            return False
        self._getword()
        wd = self._curword()
        if wd[2] != ')':
            self._error('应为)')
            return False
        self._getword()
        return True
    
    def s_write(self):
        '''
          ＜写语句＞ ::=  printf‘(’[<字符串>,][＜expression ＞]‘）’
　　　　　 //当出现字符串时，就加印字符串, 之后打印表达式的值；
        '''
        self._getword()
        wd = self._curword()
        flag = 0
        if wd[2] != '专用符号' or wd[3] != '(':
            self._error('应为(')
            return False
        self._getword()
        wd = self._curword()
        if wd[2] == '字符串':
            flag = 1
            self._getword()
            wd = self._curword()
            if wd[2] == '专用符号' and wd[3] == ',':
                self._getword()
                wd = self._curword()
        if wd[2] == '+' or wd[2] == '-' or wd[2] == '标识符':
            res = self.s_expression()
            flag = 1
            if not res:
                return False
        wd = self._curword()
        if wd[2] !='专用符号' and wd[3] != ')':
            self._error('应为)')
            return False
        self._getword()
        return True
    
    def s_return(self):
        '''
            ＜返回语句＞ ::=  return [ ‘(’＜表达式＞’)’ ] 
        '''
        self._getword()
        wd = self._curword()
        if wd[2] == '专用符号' and wd[3] == '(':
            self._getword()
            wd = self._curword()
            if wd[2] != '+' and wd[2] != '-' and wd[2] != '标识符':
                self._error('应为表达式')
                return False
            else:
                res = self.s_expression()
                if not res:
                    return False
            wd = self._curword()
            if wd[2] != '专用符号' or wd[3] != ')':
                self._error('应为)')
                return False
            self._getword()
        return True
    
    def s_statement_series(self):
        '''
            ＜语句序列＞ ::=  ＜语句＞｛＜语句＞｝
        '''
        res = self.s_statement()
        if not res:
            return False
        wd = self._curword()
        while (wd[2] == '关键字' and (wd[3] == 'IF' or wd[3] == 'WHILE' or wd[3] == 'RETURN' or wd[3] == 'SCANF' or wd[3] == 'PRINTF')) or wd[2] == '标识符':
            res = self.s_statement()
            if res:
                wd = self._curword()
            else:
                break
            
        return True
    
    def s_value_param_list(self):
        '''
            ＜值参数表＞ ::=  ＜表达式＞｛，＜表达式＞｝｜＜空＞
        '''
        wd0 = self._curword()
        p0 = self.words_p
        flag = 0
        res = self.s_expression()
        if not res:
            wd = wd0
            self.words_p = p0
        else:
            flag = 1
        wd = self._curword()
        while wd[2] == '专用符号' and wd[3] == ',':
            self._getword()
            wd = self._curword()
            if wd[2] != '+' and wd[2] != '-' and wd[2] != '标识符':
                self._error("应为表达式")
                return False
            else:
                res = self.s_expression()
                if not res:
                    return False
                wd = self._curword()
        return True
    
    def s_function_call_statement(self):
        '''
           ＜函数调用语句＞ ::=  ＜标识符＞‘（’＜值参数表＞‘）’ 
        '''
        self._getword()
        wd = self._curword()
        if wd[2] != '专用符号' or wd[3] != '(':
            self._error("应为(")
            return False
        self._getword()
        res = self.s_value_param_list()
        if not res:
            return False
        wd = self._curword()
        if wd[2] != '专用符号' or wd[3] != ')':
            self._error("应为)")
            return False
        self._getword()
        return True
    
    def s_while_statement(self):
        '''
           ＜循环语句＞ ::=  while‘（’＜条件＞‘）’＜语句＞ 
        '''
        self._getword()
        wd = self._curword()
        if wd[2] != '专用符号' or wd[3] != '(':
            self._error("应为（")
            return False
        self._getword()
        wd = self._curword()
        if wd[2] != '+' and wd[2] != '-' and wd[2] != '标识符':
            self._error("应为表达式")
            return False
        res = self.s_condition()
        if not res:
            return False
        wd = self._curword()
        if wd[2] != '专用符号' or wd[3] != ')':
            self._error("应为)")
            return False
        self._getword()
        res = self.s_statement()
        if not res:
            return False
        return True
    
    def s_condition(self):
        '''
           ＜条件＞ ::=  ＜表达式＞＜关系运算符＞＜表达式＞｜＜表达式＞ 
        '''
        wd = self._curword()
        if wd[2] != '+' and wd[2] != '-' and wd[2] != '标识符':
            self._error("应为表达式")
            return False
        res = self.s_expression()
        if not res:
            return False
        wd = self._curword()
        if wd[2] != '关系运算符':
            return True
        else:
            self._getword()
            wd = self._curword()
            if wd[2] != '+' and wd[2] != '-' and wd[2] != '标识符':
                return False
            res = self.s_expression()
            if not res:
                return False
            return True
    
    def s_condition_statement(self):
        '''
           ＜条件语句＞ ::=  if‘（’＜条件＞‘）’＜语句＞〔else＜语句＞〕 
        '''
        self._getword()
        wd = self._curword()
        if wd[2] != '专用符号' or wd[3] != '(':
            self._error("应为(")
            return False
        self._getword()
        res = self.s_condition()
        if not res:
            return False
        wd = self._curword()
        if wd[2] != '专用符号' or wd[3] != ')':
            self._error("应为)")
            return False
        self._getword()
        res = self.s_statement()
        if not res:
            return False
        wd = self._curword()
        if wd[2] == '关键字' and wd[3] == 'ELSE':
            self._getword()
            res = self.s_statement()
            if not res:
                return False
        return True
    
    def s_assignment_statement(self):
        '''
            ＜赋值语句＞ ::=  ＜标识符＞＝＜表达式＞
        '''
        wd = self._curword()
        if wd[2] != '标识符':
            self._error("应为标识符")
            return False
        self._getword()
        wd = self._curword()
        if wd[2] != '专用符号' or wd[3] != '=':
            self._error("应为=")
            return False
        self._getword()
        res = self.s_expression()
        if not res:
            return False
        return True
    
    def s_statement(self):
        '''
        ＜语句＞ ::= ＜条件语句＞｜＜循环语句＞｜‘{’<语句序列>‘}’｜＜函数调用语句＞;
｜＜赋值语句＞; | <返回语句>;｜＜读语句＞;｜＜写语句＞;｜＜空＞
        '''
        wd = self._curword()
        if wd[2] == '关键字' and wd[3] == 'IF':
            res = self.s_condition_statement()
            if not res:
                return False
            return True
        elif wd[2] == '关键字' and wd[3] == 'WHILE':
            res = self.s_while_statement()
            if not res:
                return False
            return True
        elif wd[2] == '专用符号' and wd[3] == '{':
            self._getword()
            res = self.s_statement_series()
            if not res:
                return False
            wd = self._curword()
            if wd[2] != '专用符号' or wd[3] != '}':
                self._error("应为}")
                return False
            return True
        elif wd[2] == '关键字' and wd[3] == 'RETURN':
            res = self.s_return()
            if not res:
                return False
            wd = self._curword()
            if wd[2] != '专用符号' or wd[3] != ';':
                self._error("缺少;")
                return False
            self._getword()
            return True
        elif wd[2] == '关键字' and wd[3] == 'SCANF':
            res = self.s_read()
            if not res:
                return False
            wd = self._curword()
            if wd[2] != '专用符号' or wd[3] != ';':
                self._error("缺少;")
                return False
            self._getword()
            return True
        elif wd[2] == '关键字' and wd[3] == 'PRINTF':
            res = self.s_write()
            if not res:
                return False
            wd = self._curword()
            if wd[2] != '专用符号' or wd[3] != ';':
                self._error("缺少;")
                return False
            self._getword()
            return True
        elif wd[2] == '标识符':
            p0 = self.words_p
            self._getword()
            wd = self._curword()
            if wd[2] == '专用符号' and wd[3] == '(':
                self.words_p = p0
                res = self.s_function_call_statement()
                if not res:
                    return False
                wd = self._curword()
                if wd[2] != '专用符号' or wd[3] != ';':
                    self._error("缺少;")
                    return False
                self._getword()
                return True
            elif wd[2] == '专用符号' and wd[3] == '=':
                self.words_p = p0
                res = self.s_assignment_statement()
                if not res:
                    return False
                wd = self._curword()
                if wd[2] != '专用符号' or wd[3] != ';':
                    self._error("缺少;")
                    return False
                self._getword()
                return True
        else:
            return True
    
    def s_factor(self):
        '''
            ＜因子＞ ::=  ＜标识符＞｜‘（’＜表达式＞‘）’｜＜整数＞｜＜函数调用语句＞
        '''
        wd = self._curword()
        if wd[2] == '专用符号' and wd[3] == '(':
            self._getword()
            res = self.s_expression()
            if not res:
                return False
            wd = self._curword()
            if wd[2] != '专用符号' or wd[3] != ')':
                self._error("应为)")
                return False
            self._getword()
            return True
        elif wd[2] == '整数':
            self._getword()
            return True
        elif wd[2] == '标识符':
            p0 = self.words_p
            self._getword()
            wd = self._curword()
            if wd[2] == '专用符号' and wd[3] == '(':
                self.words_p = p0
                res = self.s_function_call_statement()
                if not res:
                    return False
                return True
            else:
                return True
        else:
            self._error("应为标识符或（或整数")
            return False
    
    def s_item(self):
        '''
            ＜项＞ ::=  ＜因子＞{＜乘法运算符＞＜因子＞}
        '''
        res = self.s_factor()
        if not res:
            return False
        wd = self._curword()
        while wd[2] == '*' or wd[2] == '/':
            self._getword()
            res = self.s_factor()
            if not res:
                return False
            wd = self._curword()
        return True
    
    def s_expression(self):
        '''
            ＜表达式＞ ::=  〔＋｜－〕＜项＞｛＜加法运算符＞＜项＞｝
        '''
        wd = self._curword()
        if wd[2] == '+' or wd[2] == '-':
            self._getword()
            wd = self._curword()
        res = self.s_item()
        if not res:
            return False
        wd = self._curword()
        while wd[2] == '+' or wd[2] == '-':
            self._getword()
            res = self.s_item()
            if not res:
                return False
            wd = self._curword()
        return True
    
    def s_main_function(self):
        '''
            ＜主函数＞ ::=  ( void ｜int ) main ＜参数＞＜复合语句＞
        '''
        wd = self._curword()
        if wd[2] != '关键字':
            self._error("应为void或int")
            return False
        else:
            if wd[3] != 'VOID' and wd[3] != 'INT' :
                self._error("应为void或int")
                return False
        self._getword()
        wd = self._curword()
        if wd[2] != '关键字' or wd[3] != 'MAIN':
            self._error("应为main")
            return False
        self._getword()
        res = self.s_param()
        if not res:
            return False
        res = self.s_compound_statement()
        if not res:
            return False
        return True
    
    def s_param_list(self):
        '''
            ＜参数表＞ ::=  int ＜标识符＞｛，int ＜标识符＞} | 空
                  //参数表可以为空
        '''
        wd = self._curword()
        if wd[2] == '关键字' and wd[3] == 'INT':
            self._getword()
            wd = self._curword()
            if wd[2] != '标识符':
                self._error("缺少参数声明")
                return False
            self._getword()
            wd = self._curword()
            while wd[2] == '专用符号' and wd[3] == ',':
                self._getword()
                wd = self._curword()
                if wd[2] != '关键字' or wd[3] != 'INT':
                    self._error("逗号后还需要继续输入参数")
                    return False
                self._getword()
                wd = self._curword()
                if wd[2] != '标识符':
                    self._error("应为标识符")
                    return False
                self._getword()
                wd = self._curword()
        return True
    
    def s_param(self):
        '''
            ＜参数＞ ::=  ‘(’＜参数表＞‘)’
        '''
        wd = self._curword()
        if wd[2] != '专用符号' or wd[3] != '(':
            self._error("应为(")
            return False
        self._getword()
        res = self.s_param_list()
        if not res:
            return False
        wd = self._curword()
        if wd[2] != '专用符号' or wd[3] != ')':
            self._error("应为)")
            return False
        self._getword()
        return True
    
    def s_compound_statement(self):
        '''
            ＜复合语句＞ ::=  ‘{’〔＜常量说明部分＞〕〔＜变量说明部分＞〕＜语句序列＞‘}’
        '''
        wd = self._curword()
        if wd[2] != '专用符号' or wd[3] != '{':
            self._error("应为{")
            return False
        self._getword()
        wd = self._curword()
        if wd[2] == '关键字' and wd[3] == 'CONST':
            res = self.s_constant_description()
            if not res:
                return False
            wd = self._curword()
        if wd[2] == '关键字' and wd[3] == 'INT':
            res = self.s_variable_description()
            if not res:
                return False
            wd = self._curword()
        res = self.s_statement_series()
        if not res:
            return False
        wd = self._curword()
        if wd[2] != '专用符号' or wd[3] != '}':
            return False
        self._getword()
        return True
    
    def s_function_declaration(self):
        '''
            ＜函数定义部分＞ ::=  （＜声明头部＞｜void ＜标识符＞）＜参数＞＜复合语句＞
        '''
        wd = self._curword()
        if wd[2] == '关键字' and wd[3] == 'VOID':
            self._getword()
            wd = self._curword()
            if wd[2] != '标识符':
                self._error("应为标识符")
                return False
            self._getword()
            wd = self._curword()
        elif wd[2] == '关键字' and wd[3] == 'INT':
            res = self.s_declaration_head()
            if not res:
                return False
            wd = self._curword()
        res = self.s_param()
        if not res:
            return False
        wd = self._curword()
        res = self.s_compound_statement()
        if not res:
            return False
        return True
    
    def s_variable_description(self):
        '''
            ＜变量说明部分＞ ::=  ＜声明头部＞｛，＜标识符＞｝；
        '''
        res = self.s_declaration_head()
        if not res:
            return False
        wd = self._curword()
        while wd[2] == '关键字' and wd[3] == ',':
            self._getword()
            wd = self._curword()
            if wd[2] != '标识符':
                self._error("应为标识符")
                return False
            self._getword()
            wd = self._curword()
        if wd[2] != '专用符号' or wd[3] != ';':
            self._error("缺少;")
            return False
        self._getword()
        return True
    
    def s_declaration_head(self):
        '''
           ＜声明头部＞ ::=  int　＜标识符＞  
        '''
        wd = self._curword()
        if wd[2] != '关键字' or wd[3] != 'INT':
            self._error("应为INT")
            return False
        self._getword()
        wd = self._curword()
        if wd[2] != '标识符':
            self._error("应为标识符")
            return False
        self._getword()
        return True

    def s_const_definition(self):
        '''
            ＜常量定义＞  ::=  ＜标识符＞＝＜整数＞
        ''' 
        wd = self._curword()
        if wd[2] != '标识符':
            self._error("应为标识符")
            return False
        self._getword()
        wd = self._curword()
        if wd[2] != '专用符号' or wd[3] != '=':
            self._error('应为=')
            return False
        self._getword()
        wd = self._curword()
        if wd[2] != '整数':
            self._error("应为整数")
            return False
        self._getword()
        return True
    
    def s_constant_description(self):
        '''
            ＜常量说明部分＞  ::=  const ＜常量定义＞｛,＜常量定义＞};
        '''
        wd = self._curword()
        if wd[2] != '关键字' or wd[3] != 'CONST':
            self._error("应为const")
            return False
        self._getword()
        res = self.s_const_definition()
        if not res:
            return False
        wd = self._curword()
        while wd[2] == '专用符号' and wd[3] == ',':
            self._getword()
            res = self.s_const_definition()
            if not res:
                return False
            wd = self._curword()
        if wd[2] != '专用符号' or wd[3] != ';':
            self._error("缺少;")
            return False
        self._getword()
        return True

    def s_program(self):
        '''
            ＜程序＞ ::=  〔＜常量说明部分＞〕〔＜变量说明部分＞〕｛＜函数定义部分＞｝＜主函数＞
        ''' 
        wd = self._curword()
        p0 = self.words_p
        if wd[2] == '关键字' and wd[3] == 'CONST':
            res = self.s_constant_description()
            if not res:
                self.words_p = p0
                wd = self._curword()
            wd = self._curword()
            p0 = self.words_p
        if wd[2] == '关键字' and wd[3] == 'INT':
            self._getword()
            wd = self._curword()
            if wd[2] == '标识符':
                res = self.s_variable_description()
                if not res:
                    self.words_p = p0
                    wd = self._curword()
                else:
                    wd = self._curword()
            else:
                self.words_p = p0
                wd = self._curword()
        p0 = self.words_p
        res = self.s_function_declaration()
        while res:
            p0 = self.words_p
            res = self.s_function_declaration()
            if not res:
                self.words_p = p0
                break
        if not res:
            self.words_p = p0
        wd = self._curword()
        res = self.s_main_function()
        if not res:
            return False
        print("Grammar analysis successfully!")
        return True



if __name__ == "__main__":
    #  debugging and test_case
    
    FILE_NAME = "/home/tarpe/shared/OnlineC0/grammar_analysis/test2.txt"
    lexer = special_lexer(FILE_NAME)
    lexer.word_analyze()
    lexer.print_result()
    lexer.output()

    input_file_name = "/home/tarpe/shared/OnlineC0/test2wout.txt"
    compiler = norm_C0_compiler()
    compiler.read(input_file_name)
    print(compiler.words)
    if not compiler.s_program():
        for msg in compiler.error_msg_box:
            print(msg)



    

    







                



                








        
        
