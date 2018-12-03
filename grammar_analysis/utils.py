from ..lexer.lexer import C0lexer


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
            print(str(i), "行："+ str(res[0]) + "个:" + str(res[1]) + "类型:" + str(res[2]) + "值:" + str(res[3]))
    
    def output(self):
        '''
            输出词法分析结果文件
        '''
        length = len(self.RESULT)
        (_ , tempfilename) = os.path.split(self.INPUT_FILE_NAME)
        (filename, _) = os.path.splitext(tempfilename)
        OUTPUT_FILE_NAME = filename + "wout.txt"
        with open(OUTPUT_FILE_NAME, "w+") as f:
            f.writelines(str(length))
            for res in self.RESULT:
                f.writelines(str(res[3]) + " " + str(res[4]))
        f.close()

if __name__ == "__main__":
    #  debugging and test_case
    







                



                








        
        
