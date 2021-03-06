from .lexer import C0lexer  
import os


class special_lexer(C0lexer):
    '''
        词法分析器,是C0lexer的子类
    '''
    def __init__(self, INPUT_FILE_NAME = 'web'):
        '''lexer的初始化
        
        Args:
            INPUT_FILE_NAME: 输入文件的路径
        '''
        C0lexer.__init__(self, INPUT_FILE_NAME)
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
        if self.curChar() == '\n':
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
            self.getchar()
            res.extend(['-', '-'])

        elif self.isPlus():
            flag = 0
            self.getchar()
            res.extend(['+',  '+'])

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
        elif self.isMore():
            self.getchar()
            if self.isEqu():
                self.getchar()
                res.extend(["关系运算符", ">="])
            else:
                res.extend(["关系运算符", ">"])
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
        if len(res) < 3:
            return False
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
                if len(res) == 2:
                    res.append("error")
                    res.append("error")
                line = str(res[0]) + " " + str(res[1]) + " " + str(res[2]) + " " + str(res[3])+"\n"
                line = line.encode("utf-8")
                f.write(str(res[0]) + " " + str(res[1]) + " " + str(res[2]) + " " + str(res[3])+"\n")
        f.close()
        #   如果有报错
        if len(self.error_message_box) > 0:
            with open(OUTPUT_ERROR_MESSAGE, "w+") as f:
                f.write(str(len(self.error_message_box))+"\n")
                for msg in self.error_message_box:
                    f.write(msg + "\n")
            f.close()


class norm_C0_compiler():
    '''
    C0编译器
    '''
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
        self.display_p = 0
        #   display分程序表(用于存放和检索btab)
        self.rconst = []
        self.rconst_p = 0
        #   rconst实常量表（val：当前实常量的值）
        self.stab = []
        #   stab字符串常量表(inum:字符串起始位置，slen:字符串长度)
        self.code = []
        #   pcode表,存放生成的p_code指令
        self.error_msg_box = []
        #   存放报错信息
        self.stack_p = 0
        #   运行时栈的指针
        self.cur_lev = 1
        #   当前运行时的lev
        self.lev_cnt = 1
        #   目前的lev总数
        self.pre_lev = 0
        #   记录上一层的计数
        self.is_main = False
        #   只有从main函数开始才输出Pcode
        self.bitmap = [ ]
        
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
    
    def _insert_const(self, name, value):
        '''
            在rconst中插入常数
        '''
        res = self._lookup_const(name)
        if res != "error":
            self._error("常量" + name + "重复定义")
            return False
        record = [name, value]
        self.rconst.append(record)
        self.rconst_p += 1
        return True
    
    def _lookup_const(self, word_name: str):
        '''
            查询rconst表，获取常量对应的值
        '''
        i = 0
        for word in self.rconst:
            if word_name == word[0]:
                return i
            i += 1
        return "error"
    
    def _insert_display(self, name, typ, value, address, lev):
        '''
            在display区中插入一条记录
        '''
        res = self._lookup_variable(name)
        if res != 'error':
            self._error(str(name) + "重复定义")
            return False
        res = self._lookup_const(name)
        if res != 'error':
            self._error(str(name) + "重复定义")
            return False
        if address is None:
            addr = self.display_p 
        else:
            addr = address
        self.display_p += 1
        record = [name, typ, value, addr, lev]
        self.display.append(record)
        return True

    def _new_lev(self, pre_lev: int):
        '''
            在display区中插入一个新的lev
        '''
        self.lev_cnt += 1
        self.pre_lev = self.cur_lev
        self.cur_lev = self.lev_cnt
        ret_addr_name = "ret_addr"
        self._insert_display(ret_addr_name, 'ret_addr', None, None, self.cur_lev)
        self._insert_display(self.pre_lev, 'abp', self.pre_lev, None, self.cur_lev)
    
    def _lookup_variable(self, name: str):
        '''
            在display区查找一个变量
        '''
        if type(name) == int:
            return "error"
        if name == 'ret_addr':
            return 'error'
        siz = len(self.display)
        for i in range(siz-1, -1, -1):
            record = self.display[i]
            if record[0] == name:
                if record[4] != self.cur_lev or record[4] != 1:
                    return "error"
                return i
        return "error"
        '''
        cur_lev = self.cur_lev
        i = 0
        for record in self.display:
            if record[0] == name and record[4] == cur_lev:
                return i
            elif record[4] == cur_lev and record[1] == 'abp':
                res = self._lookup_abp(record[0], name)
                if res != "error":
                    return res
                else:
                    i += 1
            else:
                i += 1
        '''
   
    def _lookup_abp(self, lev, name):
        '''
            在某一个abp内非递归的查找一个变量
        '''
        i = 0
        for record in self.display:
            if record[1] != 'abp' and record[4] == lev:
                if record[0] == name:
                    return i
                else:
                    i += 1
            else:
                i += 1
        return "error"
    
    def _gen_Pcode(self, code: list):
        '''
            生成一行Pcode
        '''
        line_no = len(self.code)
        res = [line_no]
        res.extend(code)
        code = res
        self.code.append(code)
    
    def _zipper_fill(self, JPC_id, JPC_code):
        '''
            拉链回填
        '''
        code_pre = self.code[:JPC_id]
        res = [JPC_id]
        JPC_code[-1] = JPC_code[-1] + 1
        res.extend(JPC_code)
        JPC_code = res
        if JPC_id >= len(self.code):
            return False
        code_suf = self.code[JPC_id:]
        for i in range(len(code_suf)):
            code_suf[i][0] = code_suf[i][0] + 1
            if code_suf[i][1] == 'JPC':
                code_suf[i][4] = code_suf[i][4] + 1
        code_pre.append(JPC_code)
        code_pre.extend(code_suf)
        self.code = code_pre
        return True
    
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
            if record[1] == "abp" or record[1] == "ret_addr":
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
            if record[1] == "abp" or record[1] == 'ret_addr':
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
        for record in self.rconst:
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
        for record in self.rconst:
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
    
    def parantheis_matching(self):
        '''
            错误局部化处理之一——括号匹配
        '''
        siz = len(self.words)
        self.bitmap = [0 for x in range(siz)]
        cnt = 0
        stack = []
        i = 0
        siz = len(self.words)
        for word in self.words:
            if word[2] == '专用符号' and word[3] == '(':
                stack.append(word)
                cnt += 1
                self.bitmap[i] = cnt
            elif word[2] == '专用符号' and word[3] == ')':
                left_par = stack.pop()
                self.bitmap[i] = cnt
                cnt -= 1
                if cnt < 0 or left_par[3] != '(':
                    self.error_msg_box.append("第"+str(word[0]) + "行')'无匹配")
                    return False
            elif word[2] == '专用符号' and word[3] == '{':
                stack.append(word)
                cnt += 1
                self.bitmap[i] = cnt
            elif word[2] == '专用符号' and word[3] == '}':
                left_par = stack.pop()
                self.bitmap[i] = cnt
                cnt -= 1
                if cnt <0 or left_par[3] != '{':
                    self.error_msg_box.append("第" + str(word[0]) + "行’}‘无匹配")
                    return True
            else:
                self.bitmap[i] = cnt
            i += 1
        return True

    def _error(self, hint: str):
        '''
            添加报错信息
        '''
        wd = self._curword()
        msg = "line: " + str(wd[0]) + " "+ hint 
        self.error_msg_box.append(msg)
        wd = self._curword()
        cnt = self.bitmap[self.words_p]
        while self.words_p< len(self.words) and self.bitmap[self.words_p] == cnt:
            if(wd[2] == '专用符号' and wd[3] == ';') or (wd[2]== '关键字' and wd[3] == 'ELSE'):
                break
            else:
                self._getword()
                wd = self._curword() 
    
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
        if wd[2] != '标识符':
            self._error('应为标识符')
            return False
        wd = self._getword()
        name = wd[3]
        i = self._lookup_variable(name)
        if i == "error":
            self._error(name + "未定义")
            return False
        record = self.display[i]
        addr = record[3]
        lev = record[4]
        code = ["LDA", 0, lev, addr]
        self._gen_Pcode(code)
        code = ["RED", 27, "", 1]
        self._gen_Pcode(code)
        wd = self._curword()
        if wd[3] != ')':
            self._error('应为)')
            return False
        self._getword()
        return True
    
    def s_write(self):
        '''
          ＜写语句＞ ::=  printf‘(’[<字符串>,][＜expression ＞]‘）’
　　　　　 当出现字符串时，就加印字符串, 之后打印表达式的值；
        '''
        self._getword()
        wd = self._curword()
        if wd[2] != '专用符号' or wd[3] != '(':
            self._error('应为(')
            return False
        self._getword()
        wd = self._curword()
        if wd[2] == '字符串':
            #   由于Pcode没有具体处理字符串的方法，所以增添LDS指令
            name = wd[3]
            self._insert_display(name, 'str', name, None, self.cur_lev)
            i = self._lookup_variable(name)
            lev = self.display[i][-1]
            y = self.display[i][-2]
            code = ["LDS", 101, lev, y]
            self._gen_Pcode(code)
            code = ["WRS", 28, "", 1]
            self._gen_Pcode(code)
            self._getword()
            wd = self._curword()
            if wd[2] == '专用符号' and wd[3] == ',':
                self._getword()
                wd = self._curword()
        if wd[2] == '+' or wd[2] == '-' or wd[2] == '标识符':
            res = self.s_expression()
            code = ["WRW", 29, "", 1]
            self._gen_Pcode(code)
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
        #   find return address
        record = []
        siz = len(self.display)
        for i in range(siz-1, -1, -1):
            record  = self.display[i]
            if record[0] == 'ret_addr':
                break
        '''
        for word in self.display:
            if word[0] == 'ret_addr' and word[4] == self.cur_lev:
                record = word
                break
        '''
        if len(record) == 0:
            return False
        addr = record[3]
        lev = record[4]
        self._getword()
        wd = self._curword()
        if wd[2] == '专用符号' and wd[3] == '(':
            code = ['LDA', 0, lev, addr]
            self._gen_Pcode(code)
            self._getword()
            wd = self._curword()
            if wd[2] != '+' and wd[2] != '-' and wd[2] != '标识符' and wd[2] != '整数':
                self._error('应为表达式')
                return False
            else:
                #   有返回值，调用的时函数，将返回值写入对应地址，并且输出EXF
                res = self.s_expression()
                if not res:
                    return False
                code = ["STO", 38, "", ""]
                self._gen_Pcode(code)
                code = ["EXF", 33, "", ""]
                self._gen_Pcode(code)
            wd = self._curword()
            if wd[2] != '专用符号' or wd[3] != ')':
                self._error('应为)')
                return False
            self._getword()
        else:
            #   如果没有返回值，则是调用的一个过程，因而输出EXP指令
            code = ["EXP", 32, "", ""]
            self._gen_Pcode(code)
        #   切换display到上一层
        x = self.cur_lev
        y = self.pre_lev
        code = ["DIS", 3, x, y]
        self._gen_Pcode(code)
        i = -1
        siz = len(self.display)
        for j in range(siz-1, -1, -1):
            record = self.display[j]
            if record[0] == 'ret_addr':
                i = record[3] + 1
                break
        '''
        for word in self.display:
            lev = word[4]
            name = word[0]
            if lev == self.cur_lev and name == 'ret_addr':
                i = word[3] + 1
                break
        '''
        if i == -1:
            return False
        pre_lev = self.display[i][0]
        self.cur_lev = pre_lev
        i = -1
        #   最外层特殊处理
        if self.cur_lev == 1:
            self.pre_lev = 0
        #   其他情况查询display区中的pre_lev然后回填
        else:
            for word in self.display:
                lev = word[4]
                name = word[0]
                if lev == self.cur_lev and name == 'ret_addr':
                    i = word[3] + 1
            if i == -1:
                return False
            pre_lev = self.display[i][0]
            self.pre_lev = pre_lev
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
    
    def s_value_param_list(self, display_index: int):
        '''
            ＜值参数表＞ ::=  ＜表达式＞｛，＜表达式＞｝｜＜空＞
        '''
        record = self.display[display_index]
        val = record[2]
        base_addr = record[3]
        record = self.display[display_index+1]
        lev = record[4]
        i = 0
        cnt = 0
        if val == 0:
            return True
        if val > 0:
            while self.display[base_addr+i][1] != 'int':
                i += 1
            base_addr += i
        code = ["LDA", 0, lev, base_addr]
        self._gen_Pcode(code)
        wd0 = self._curword()
        p0 = self.words_p
        cnt = 0
        res = self.s_expression()
        if not res:
            wd = wd0
            self.words_p = p0
        else:
            code = ["STO", 38, "", ""]
            self._gen_Pcode(code)
            cnt += 1
            base_addr += 1
            if cnt < val:
                code = ["LDA", 0, lev, base_addr]
                self._gen_Pcode(code)
            elif cnt > val:
                self._error("参数个数不符")
                return False
            else:
                return True
        wd = self._curword()
        while wd[2] == '专用符号' and wd[3] == ',':
            self._getword()
            wd = self._curword()
            if wd[2] != '+' and wd[2] != '-' and wd[2] != '标识符' and wd[2] != '整数':
                self._error("应为表达式")
                return False
            else:
                res = self.s_expression()
                if not res:
                    return False
                code = ["STO", 38, "", ""]
                self._gen_Pcode(code)
                cnt += 1
                base_addr += 1
                if cnt < val:
                    code = ["LDA", 0, lev, base_addr]
                    self._gen_Pcode(code)
                elif cnt > val:
                    self._error("参数个数不符")
                    return False
                wd = self._curword()
        return True
    
    def s_function_call_statement(self):
        '''
           ＜函数调用语句＞ ::=  ＜标识符＞‘（’＜值参数表＞‘）’ 
        '''
        #   在符号表找到对应的函数
        wd = self._getword()
        name = wd[3]
        i = self._lookup_variable(name)
        if i == "error":
            self._error(name + "未定义")
            return 'error'
        record = self.display[i]
        typ = record[1]
        if typ != 'func':
            self._error(name + "不是可调用的类型")
            return 'error'
        #   调用之前先压栈
        code = ["MKS", 18, "", self.cur_lev]
        self._gen_Pcode(code)
        #   先准备参数
        wd = self._curword()
        if wd[2] != '专用符号' or wd[3] != '(':
            self._error("应为(")
            return 'error'
        self._getword()
        res = self.s_value_param_list(i)
        if not res:
            return 'error'
        wd = self._curword()
        if wd[2] != '专用符号' or wd[3] != ')':
            self._error("应为)")
            return 'error'
        #   然后调用函数
        addr = record[3]
        code = ["CAL", 19, "", addr]
        self._gen_Pcode(code)
        self._getword()
        return name
    
    def s_while_statement(self):
        '''
           ＜循环语句＞ ::=  while‘（’＜条件＞‘）’＜语句＞ 
        '''
        jmp_back_code = ["JMP", 10, "", len(self.code)]
        self._getword()
        wd = self._curword()
        if wd[2] != '专用符号' or wd[3] != '(':
            self._error("应为（")
            return False
        self._getword()
        wd = self._curword()
        if wd[2] != '+' and wd[2] != '-' and wd[2] != '标识符' and wd[2] != '整数':
            self._error("应为表达式")
            return False
        res = self.s_condition()
        if not res:
            return False
        wd = self._curword()
        JPC_id = len(self.code)
        JPC_code = ["JPC", 11, "", ""]
        if wd[2] != '专用符号' or wd[3] != ')':
            self._error("应为)")
            return False
        self._getword()
        res = self.s_statement()
        if not res:
            return False
        self._gen_Pcode(jmp_back_code)
        target = len(self.code)
        JPC_code = ["JPC", 11, "", target]
        if not self._zipper_fill(JPC_id, JPC_code):
            return False
        return True
    
    def s_condition(self):
        '''
           ＜条件＞ ::=  ＜表达式＞＜关系运算符＞＜表达式＞｜＜表达式＞ 
        '''
        wd = self._curword()
        if wd[2] != '+' and wd[2] != '-' and wd[2] != '标识符' and wd[2] != '整数':
            self._error("应为表达式")
            return False
        res = self.s_expression()
        if not res:
            return False
        wd = self._curword()
        if wd[2] != '关系运算符':
            #   如果只有一个表达式，判断表达式结果是否为0
            code = ["LDC", 24, "", 0]
            self._gen_Pcode(code)
            code = ["EQL", 45, "", ""]
            self._gen_Pcode(code)
            return True
        else:
            wd = self._getword()
            operator = wd[3]
            if operator == "==":
                code = ["EQL", 45, "", ""]
            elif operator == "!=":
                code = ["NEQ", 46, "", ""]
            elif operator == "<":
                code = ["LSS", 47, "", ""]
            elif operator == "<=":
                code = ["LER", 48, "", ""]
            elif operator == ">":
                code = ["GRT", 49, "", ""]
            elif operator == ">=":
                code = ["GEQ", 50, "", ""]
            wd = self._curword()
            if wd[2] != '+' and wd[2] != '-' and wd[2] != '标识符' and wd[2] != '整数':
                return False
            res = self.s_expression()
            if not res:
                return False
            self._gen_Pcode(code)
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
        JPC_id = len(self.code)
        JPC_code = ["JPC", 11, "", ""]
        res = self.s_statement()
        JMP_id = len(self.code)
        JMP_code = ["JMP", 10, "", ""]
        if not res:
            return False
        wd = self._curword()
        flag = 0
        if wd[2] == '关键字' and wd[3] == 'ELSE':
            flag = 1
            #   拉链回填
            target = len(self.code)
            JPC_code = ["JPC", 11, "", target + 1]
            if not self._zipper_fill(JPC_id, JPC_code):
                return False
            self._getword()
            res = self.s_statement()
            target = len(self.code)
            JMP_code = ["JMP", 10, "", target]
            if not self._zipper_fill(JMP_id + 1, JMP_code):
                return False
            if not res:
                return False
        if flag == 0:
            target = len(self.code)
            JPC_code[-1] = target
            if not self._zipper_fill(JPC_id, JPC_code):
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
        wd = self._getword()
        name = wd[3]
        i = self._lookup_variable(name)
        if i == "error":
            self._error(name + "未定义")
            return False
        record = self.display[i]
        typ = record[1]
        if typ != 'int':
            self._error(name + "应是int类型，但却是" + typ)
            return False
        addr = record[3]
        lev = record[4]
        code = ["LDA", 0, lev, addr]
        self._gen_Pcode(code)
        wd = self._curword()
        if wd[2] != '专用符号' or wd[3] != '=':
            self._error("应为=")
            return False
        self._getword()
        res = self.s_expression()
        code = ["STO", 38, "", ""]
        self._gen_Pcode(code)
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
            self._getword()
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
            value = wd[3]
            code = ["LDC", 24, "", value]
            self._gen_Pcode(code)
            self._getword()
            return True
        elif wd[2] == '标识符':
            p0 = self.words_p
            self._getword()
            wd = self._curword()
            if wd[2] == '专用符号' and wd[3] == '(':
                self.words_p = p0
                res = self.s_function_call_statement()
                if res == 'error':
                    return False
                wd = self._curword()
                name = res
                i = self._lookup_variable(name)
                if i == "error":
                    self._error("未定义")
                    return False
                i= i+1
                record = self.display[i]
                lev = record[4]
                x = lev
                y = self.display[i][3]
                code = ["LOD", 1, x, y]
                self._gen_Pcode(code)
                return True
            else:
                wd = self.words[p0]
                name = wd[3]
                i = self._lookup_const(name)
                if i != "error":
                    value = self.rconst[i][1]
                    code = ["LDC", 24, "", value]
                else:
                    i = self._lookup_variable(name)
                    if i == "error":
                        self._error(name + "未定义")
                        return False
                    record = self.display[i]
                    addr = record[3]
                    lev = record[4]
                    code = ["LOD", 1, lev, addr]
                self._gen_Pcode(code)
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
            if wd[2] == '*':
                code = ["MUL", 57, "", ""]
            else:
                code = ["DIV", 58, "", ""]
            self._gen_Pcode(code)
            wd = self._curword()
        return True
    
    def s_expression(self):
        '''
            ＜表达式＞ ::=  〔＋｜－〕＜项＞｛＜加法运算符＞＜项＞｝
        '''
        wd = self._curword()
        operator_global = ""
        if wd[2] == '+' or wd[2] == '-':
            if wd[2] == '+':
                operator_global = "ADD"
            elif wd[2] == "-":
                operator_global = "SUB"
            code = ["LDC", 24, "", 0]
            self._gen_Pcode(code)
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
            if wd[2] == '+':
                code = ["ADD", 52, "", ""]
            else:
                code = ["SUB", 53, "", ""]
            self._gen_Pcode(code)
            wd = self._curword()
        if operator_global == "ADD":
            code = ["ADD", 52, "", ""]
            self._gen_Pcode(code)
        elif operator_global == 'SUB':
            code = ["SUB", 53, "", ""]
            self._gen_Pcode(code)
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
            if wd[3] != 'VOID' and wd[3] != 'INT':
                self._error("应为void或int")
                return False
        self._getword()
        wd = self._curword()
        if wd[2] != '关键字' or wd[3] != 'MAIN':
            #self._error("应为main")
            return False
        code = ["main:", "", "", ""]
        self._gen_Pcode(code)
        pre_lev = self.pre_lev
        cur_lev = self.cur_lev
        self._new_lev(self.pre_lev)
        self._getword()
        res = self.s_param()
        if not res:
            return False
        res = self.s_compound_statement()
        self.cur_lev = cur_lev
        self.pre_lev = pre_lev
        if not res:
            return False
        return True
    
    def s_param_list(self):
        '''
            ＜参数表＞ ::=  int ＜标识符＞｛，int ＜标识符＞} | 空
                  //参数表可以为空
        '''
        wd = self._curword()
        cnt = 0
        if wd[2] == '关键字' and wd[3] == 'INT':
            self._getword()
            wd = self._curword()
            if wd[2] != '标识符':
                self._error("缺少参数声明")
                return False
            cnt += 1
            name = wd[3]
            self._insert_display(name, 'int', None, None, self.cur_lev)
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
                cnt += 1
                wd = self._getword()
                name = wd[3]
                self._insert_display(name, 'int', None, None, self.cur_lev)
                wd = self._curword()
        if cnt == 0:
            return True
        return cnt
    
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
        if res == False:
            return False
        wd = self._curword()
        if wd[2] != '专用符号' or wd[3] != ')':
            self._error("应为)")
            return False
        self._getword()
        return res
    
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
                #self._error("应为标识符")
                return False
            name = wd[3]
            self._getword()
            wd = self._curword()
            addr = len(self.code)
            self._insert_display(name, 'func', None, addr, self.cur_lev)
            code = [name + ":", "", "", ""]
            self._gen_Pcode(code)
        elif wd[2] == '关键字' and wd[3] == 'INT':
            self._getword()
            wd = self._curword()
            if wd[2] == '关键字' and wd[3] == 'MAIN':
                return False
            if wd[2] != '标识符':
                self._error("应为标识符")
                return False
            wd = self._getword()
            name = wd[3]
            wd = self._curword()
            addr = len(self.code)
            self._insert_display(name, 'func', None, addr, self.cur_lev)
            code = [name + ":", "", "", ""]
            self._gen_Pcode(code)
        self.pre_lev = self.cur_lev
        self._new_lev(self.cur_lev)
        res = self.s_param()
        if not res:
            return False
        i = self._lookup_variable(name)
        self.display[i][2] = res
        wd = self._curword()
        res = self.s_compound_statement()
        #self.cur_lev = self.pre_lev
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
        while wd[2] == '专用符号' and wd[3] == ',':
            self._getword()
            wd = self._curword()
            if wd[2] != '标识符':
                self._error("应为标识符")
                return False
            name = wd[3]
            res = self._insert_display(name, "int", None, None, self.cur_lev)
            if not res:
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
        name = wd[3]
        if not self._insert_display(name,'int', None, None, self.cur_lev):
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
        name = wd[3]
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
        value = wd[3]
        if self._insert_const(name, value) == 'error':
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
        flag = 0
        if wd[2] == '关键字' and wd[3] == 'INT':
            self._getword()
            wd = self._curword()
            if wd[2] == '标识符':
                p1 = self.words_p
                self._getword()
                wd = self._curword()
                if wd[2] == "专用符号" and wd[3] == "(":
                    self.words_p = p0
                    wd = self._curword()
                    res = self.s_function_declaration()
                    if res:
                        flag = 1
                else:
                    self.words_p = p0
                    wd = self._curword()
                    res = self.s_variable_description()
                    p0 = self.words_p
                    if not res:
                        return False
        elif wd[2] == '关键字' and wd[3] == 'VOID':
            p0 = self.words
            wd = self._curword()
            res = self.s_function_declaration()
            if res:
                flag = 1
        while flag == 1:
            p0 = self.words_p
            res = self.s_function_declaration()
            if not res:
                self.words_p = p0
                flag = 0
                break
        if flag == 0:
            self.words_p = p0
        wd = self._curword()
        res = self.s_main_function()
        if not res:
            return False
        print("Grammar analysis successfully!")
        return True



if __name__ == "__main__":
    #  debugging and test_case
    
    FILE_NAME = "C:\\编译课程设计\\OnlineC0\\test\\C0\\C0_TEST1.txt"
    lexer = special_lexer(FILE_NAME)
    lexer.word_analyze()
    #lexer.print_result()
    lexer.output()
    errors = lexer.error_message_box
    words = lexer.RESULT

    input_file_name = "/home/tarpe/shared/OnlineC0/test5wout.txt"
    compiler = norm_C0_compiler()
    compiler.error_msg_box = errors
    #compiler.read(input_file_name)
    compiler.words = words
    #print(compiler.words)
    compiler.s_program()
    compiler.report_result()
