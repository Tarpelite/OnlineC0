class OPGA:
    '''
    using G[E]:
    E -> E+T|T
    T -> T*F|F
    F ->(E)|i
    '''
    def __init__(self):
        self.default_grammary=[
            'E->E+T|T',
            'T->T*F|F',
            'F->(E)|i'
        ]
        self.Vt = []
        self.FirstVt = {}
        self.LastVt = {}
        self.Vn = []
        self.stack = []
        self.table = []
        self.priority_table = []
        self.text = ""
        self.start = "E"
        self.use_default_grammary = True

    def InputGrammar(self, g:str):
        '''
            输入文法
        '''
        self.default_grammary = []
        g.replace("\r", "")
        tmp_grammary = list(g.split('\n'))
        for tos in tmp_grammary:
            if not self.check_grammary(tos):
                print("Invalid Grammary:"+tos)
                return False
            if '|' in tos:
                if ":=" in tos:
                    tos_ = list(tos.split(":="))
                    U = tos_[0]
                    x_ = tos_[1].split('|')
                    for x in x_:
                        grammary_new = U + ":=" + x
                        self.default_grammary.append(grammary_new)
                else:
                    tos_ = list(tos.split("->"))
                    U = tos_[0]
                    x_ = tos_[1].split('|')
                    for x in x_:
                        grammary_new = U + "->" + x
                        self.default_grammary.append(grammary_new)
            else:
                self.default_grammary.append(tos)
        self.use_default_grammary = False
        return True
    
    def check_grammary(self, g:str):
        '''
            检查每一条产生式是否合法
        '''
        if ('->' not in g) and (':=' not in g):
            return False
        elif len(g) <= 3:
            return False
        elif g.startswith('->') or g.startswith(':=') or not g[0].isalpha():
            return False
        return True

    def web_output_production(self):
        table ="<table class=\"table table-striped\"><caption>"+"产生式分析结果"+"</caption>"
        head = "<thead><tr>" + "<th>序号</th>" + "<th>产生式分析结果</th>" + "</thead>"
        table += head
        body = "<tbody>"
        n = len(self.default_grammary)
        for i in range(0, n):
            line = "<tr>"
            line += "<td>" + str(i+1) + "</td>"
            line += "<td>" + str(self.default_grammary[i]) + "</td>"
            line += "</tr>"
            body += line
        body += "</tbody>"
        table += body
        table += "</table>"
        return table
    
    def web_output_VnVt(self):
        table ="<table class=\"table table-striped\"><caption>"+"符号分析结果"+"</caption>"
        head = "<thead><tr>" + "<th>类别</th>" + "<th>符号</th>" + "</thead>"
        table += head
        body = "<tbody>"
        #第一行Vt
        line1 = "<tr>"
        line1 += "<td>终结符号Vt</td>"
        block = ""
        for vt in self.Vt:
            block += str(vt)+"&nbsp"
        line1 += "<td>" + block + "</td>"
        line1 += "</tr>"
        #第二行Vn
        line2 = "<tr>"
        line2 += "<td>非终结符号Vn</td>"
        block = ""
        for vn in self.Vn:
            block += str(vn) + "&nbsp"
        line2 += "<td>" + block + "</td>"
        line2 += "</tr>"
        body += line1
        body += line2
        body += "</tbody>"
        table += body
        table += "</table>"
        return table
    
    def web_output_FirstVt(self):
        table ="<table class=\"table table-striped \"><caption>"+"FirstVt集合表"+"</caption>"
        head = "<thead><tr>" + "<th>Vn</th>" + "<th>FirstVt</th>" + "</thead>"
        table += head
        body = "<tbody>"
        for vn in self.Vn:
            fvt_set = self.firstVt(vn)
            line = "<tr>"
            line += "<td>" + str(vn) + "</td>"
            fvt_set_str = ""
            for vt in fvt_set:
                fvt_set_str +=  str(vt) + "&nbsp"
            line += "<td>" + fvt_set_str + "</td>"
            line += "</tr>"
            body += line
        body += "</tbody>"
        table += body
        table += "</table>"
        return table
    
    def web_output_LastVt(self):
        table ="<table class=\"table table-striped\"><caption>"+"LastVt集合表"+"</caption>"
        head = "<thead><tr>" + "<th>Vn</th>" + "<th>LastVt</th>" + "</thead>"
        table += head
        body = "<tbody>"
        for vn in self.Vn:
            fvt_set = self.lastVt(vn)
            line = "<tr>"
            line += "<td>" + str(vn) + "</td>"
            fvt_set_str = ""
            for vt in fvt_set:
                fvt_set_str +=  str(vt) + "&nbsp"
            line += "<td>" + fvt_set_str + "</td>"
            line += "</tr>"
            body += line
        body += "</tbody>"
        table += body
        table += "</table>"
        return table

    def FindVtVn(self):
        for g in self.default_grammary:
            if g[0] not in self.Vn and g[0] != " ":
                self.Vn.append(g[0])
        for g in self.default_grammary:
            g = g.replace("->","")
            g = g.replace(":=", "")
            for ch in g:
                if ch not in self.Vn :
                    if ch != '|':
                        if ch not in self.Vn :
                            if ch not in self.Vt and ch !=" ":
                                self.Vt.append(ch)
    
    def __F(self, U, b):
        for lis in self.table:
            if lis[0] == U and lis[1] == b:
                return lis[2]
    
    def setF(self, U, b):
        for lis in self.table:
            if lis[0] == U and lis[1] == b:
                lis[2] = True
                return
        tos = [U, b, True]
        self.table.append(tos)
    
    def Insert(self, U, b):
        '''
            将符号对(U, b)插入STACK栈中
        '''
        if not self.__F(U, b):
            self.setF(U, b)
            self.stack.append([U, b])
            return
    
    def setFirstVtTable(self):
        '''
            FirstVt建表主程序
        '''
        self.table = []
        for U in self.Vn:
            for b in self.Vt:
                tos = [U, b, False]
                self.table.append(tos)

        for U in self.Vn:
            for b in self.Vt:
                for g in self.default_grammary:
                    g_ = []
                    if ":=" in g:
                        g_ = list(g.split(":="))
                    elif "->" in g:
                        g_ = list(g.split("->"))
                    else:
                        print("语法错误:"+g)
                        return False
                    if len(g_) != 2:
                        print("语法错误："+g)
                        return False
                    if U in g_[0]:
                        if g_[1].startswith(b):
                            self.Insert(U, b)
                        else:
                            for vn in self.Vn:
                                g_[1]= g_[1].replace(vn, "")
                            if g_[1].startswith(b):
                                self.Insert(U, b)

        while len(self.stack) > 0:
            top = self.stack.pop()
            V = top[0]
            b = top[1]
            for g in self.default_grammary:
                g_ = []
                if ":=" in g:
                    g_ = list(g.split(":="))
                elif "->" in g:
                    g_ = list(g.split("->"))
                else:
                    print("语法错误:"+g)
                    return False
                if len(g_) != 2:
                    print("语法错误："+g)
                    return False

                U = g_[0]
                if g_[1].startswith(V):
                    self.Insert(U, b)
        
        for U in self.Vn:
            res = []
            for record in self.table:
                if record[0] == U and record[2]:
                    res.append(record[1])
            self.FirstVt[U] = res
    
    def setLastVtTable(self):
        '''
            LastVt建表主程序
        '''
        self.table = []
        for U in self.Vn:
            for b in self.Vt:
                tos = [U, b, False]
                self.table.append(tos)
        for U in self.Vn:
            for b in self.Vt:
                tos = [U, b, False]
                for g in self.default_grammary:
                    g_ = []
                    if ":=" in g:
                        g_ = list(g.split(":="))
                    elif "->" in g:
                        g_ = list(g.split("->"))
                    else:
                        print("语法错误:"+g)
                        return False
                    if len(g_) != 2:
                        print("语法错误："+g)
                        return False
                    if U in g_[0]:
                        if g_[1].endswith(b):
                            self.Insert(U, b)
                        else:
                            for vn in self.Vn:
                                g_[1] = g_[1].replace(vn, "")
                            if g_[1].endswith(b):
                                self.Insert(U, b)

        while len(self.stack) > 0:
            top = self.stack.pop()
            V = top[0]
            b = top[1]
            for g in self.default_grammary:
                g_ = []
                if ":=" in g:
                    g_ = list(g.split(":="))
                elif "->" in g:
                    g_ = list(g.split("->"))
                else:
                    print("语法错误:"+g)
                    return False
                if len(g_) != 2:
                    print("语法错误："+g)
                    return False

                U = g_[0]
                if g_[1].endswith(V):
                    self.Insert(U, b)

        for U in self.Vn:
            res = []
            for record in self.table:
                if record[0] == U and record[2]:
                    res.append(record[1])
            self.LastVt[U] = res

    def firstVt(self, U:str):
        '''
            返回非终结符U的FirstVt集合
            填写FirstVt的dict
        '''
        if len(self.FirstVt) == 0:
            self.setFirstVtTable()
            if self.FirstVt.__contains__(U):
                return self.FirstVt[U]
            else:
                return False
        else:
            if self.FirstVt.__contains__(U):
                return self.FirstVt[U]
            else:
                return False
    
    def lastVt(self, U:str):
        '''
            返回非终结符U的LastVt集合
            并填写lastVt的dict
        '''

        if len(self.LastVt) == 0:
            self.setLastVtTable()
            if self.LastVt.__contains__(U):
                return self.LastVt[U]
            else:
                return False
        else:
            if self.LastVt.__contains__(U):
                return self.LastVt[U]
            else:
                return False
    
    def setPriorityTable(self):
        '''
            构造算符优先表
        '''
        self.priority_table = []
        for g in self.default_grammary:
            if ":=" in g:
                g_ = list(g.split(":="))
            else:
                g_ = list(g.split("->"))
            tos = g_[1]
            length = len(tos)
            for i in range(length-1):
                if tos[i] in self.Vt and tos[i+1] in self.Vt:
                    record = [tos[i], tos[i+1], "="]
                    if record not in self.priority_table:
                        self.priority_table.append(record)
                if i <= length-3 and tos[i] in self.Vt and tos[i+2] in self.Vt and tos[i+1] in self.Vn:
                    record = [tos[i], tos[i+2], "="]
                    if record not in self.priority_table:
                        self.priority_table.append(record)
                if tos[i] in self.Vt and tos[i+1] in self.Vn:
                    res = self.firstVt(tos[i+1])
                    for b in res:
                        record = [tos[i], b, "<"]
                        if record not in self.priority_table:
                            self.priority_table.append(record)    
                if tos[i] in self.Vn and tos[i+1] in self.Vt:
                    res = self.lastVt(tos[i])
                    for a in res:
                        record = [a, tos[i+1], ">"]
                        if record not in self.priority_table:
                            self.priority_table.append(record)
        
    def output_priority_table(self):
        '''
            输出可视化表格，
        '''
        res = ""
        length = len(self.Vt)
        horizontal_line = "\n".rjust(length*18, "-")
        res += horizontal_line
        #制作表头
        header = "| ".ljust(14)
        for vt in self.Vt:
            header += "|" + str(vt).center(14)
        header += '|\n'
        res += header
        res += horizontal_line
        #制作表格 
        for vt1 in self.Vt:
            line = '|' + str(vt1).center(14)
            for vt2 in self.Vt:
                operator = self.judge(vt1, vt2)
                line += '|' + str(operator).center(14)
            line += '|\n'
            res+=line
            res += horizontal_line
        return res
    
    def web_output_priority_table(self):
        '''
            输出算符优先分析表的html代码
        '''
        html = "<table class=\"table table-bordered\"><caption>算符优先分析表</caption>"
        body = "<tbody>"
        line = "<tr><td></td>"
        for vt in self.Vt:
            if vt != " ":
                line += "<td>" + str(vt) + "</td>"
        line += "</tr>"
        body += line
        for vt1 in self.Vt:
            if vt1 == " ":
                continue
            line = "<tr>"
            line += "<td>" + str(vt1) + "</td>"
            for vt2 in self.Vt:
                if vt2 == " ":
                    continue
                operator = self.judge(vt1, vt2)
                line += "<td>" + str(operator) + "</td>"
            line += "</tr>"
            body += line
        body += "</tbody>"
        html += body + "</table>"
        return html
            
    def input_test_txt(self, txt:str):
        '''
            输入测试语句
        '''
        txt = txt.strip()
        txt = txt.replace("\r", "")
        txt = txt.replace("\n", "")
        self.text = "#"+txt+"#"
    
    def judge(self, vt1, vt2):
        '''
            查表比较两个vt的优先级大小
        '''
        if self.use_default_grammary:
            if vt1 == '+' and (vt2 == '+' or vt2 == '*'):
                return False
            if vt1 == '*' and (vt2 == '*' or vt2 == '+'):
                return False
        for record in self.priority_table:
            if record[0] == vt1 and record[1] == vt2:
                return record[2]
        return False
    
    def find_leftest_substring(self, text:str):
        '''
            寻找当前子串的最左素短语
        '''
        if self.use_default_grammary:
            if '++' in text:
                return False, False
            if '**' in text:
                return False, False
            if '+*' in text:
                return False, False
            if '*+' in text:
                return False, False

        vt_set = [["#",-1]]
        n = len(text)
        for i in range(n):
            if text[i] in self.Vt:
                vt_set.append([text[i], i])
        vt_set.append(['#',-1])
        n1 = len(vt_set)
        if n1 < 3:
            return False, False
        elif n1 == 3:
            if self.judge(vt_set[0][0], vt_set[1][0]) == '<' and self.judge(vt_set[1][0], vt_set[2][0]) == '>':
                res = text[vt_set[1][1]]
                start_index = vt_set[1][1]
                index = vt_set[1][1]
                if index -1>= 0 and text[index-1] in self.Vn:
                    res = text[index-1] + res
                    start_index = index -1
                if index + 1 <len(text) and text[index+1] in self.Vn:
                    res = res + text[index+1]
                    if index <= start_index:
                        start_index = index 
                return res, start_index

        for i in range(1, n1 - 1):
            for j in range(i, n1-1):
                if self.judge(vt_set[i-1][0], vt_set[i][0]) == '<':
                    if self.judge(vt_set[j][0], vt_set[j+1][0]) == '>':
                        flag = 0
                        for k in range(i+1, j):
                            if self.judge(vt_set[k-1][0], vt_set[k][0]) != '=':
                                flag = 1
                                break
                        if self.judge(vt_set[j-1][0], vt_set[j][0]) != '=':
                            flag = 1
                        if i == j:
                            flag = 0
                        if flag == 0:
                            in_l = vt_set[i][1]
                            in_r = vt_set[j][1]
                            res = text[in_l:in_r+1]
                            start_index = in_l
                            if in_l == in_r:
                                res = text[in_l]
                                start_index = in_l
                            if in_l - 1 >= 0:
                                if text[in_l-1] in self.Vn:
                                    res = text[in_l -1] + res
                                    start_index = in_l - 1
                            if in_r + 1 < len(text):
                                if text[in_r + 1] in self.Vn:
                                    res = res + text[in_r + 1]
                            return res, start_index
        return False, False
    
    def reduce(self, handle:str):
        '''
            对最左素短语进行规约
        '''
        vt_set = []
        for ch in handle:
            if ch in self.Vt:
                vt_set.extend(ch)
        for g in self.default_grammary:
            flag = 0
            g_ = []
            if "->" in g:
                g_ = list(g.split("->"))
            else:
                g_ = list(g.split(":="))
            for vt in vt_set:
                if vt not in g_[1]:
                    flag = 1
                    break
            if flag == 0:
                return g_[0]
        return False

    def setStart(self, E:str):
        '''
        设定起始符号Vn
        '''
        self.start = E

    def check(self, token_stack:str):
        '''
            检测是否需要终止
        '''
        if token_stack.endswith("#") and len(token_stack) >= 2:
            return False
        return True

    def curchar(self, p:int):
        '''
            返回当前分析的字符
        '''
        if p >= len(self.text):
            return False
        else:
            return self.text[p]
    
    def popvt(self, token_stack:str):
        '''
            返回符号栈最后一个vt
        '''
        n = len(token_stack)
        for i in range(n-1, -1, -1):
            if token_stack[i] in self.Vt:
                return token_stack[i]
        return False
    
    def isInDict(self, ch:str):
        '''
            检查当前字符是否属合法(在文法中出现过)
        '''
        if ch in self.Vn or ch in self.Vt:
            return True
        return False

    
    def replace(self, x_old:str, res:str, index:int, handle_len:int):
        '''
            替换旧字符串中指定index位置的handle为res
        '''
        n = handle_len
        x_old_prefix = x_old[:index]
        x_old_suffix = x_old[index+n:]
        x_new = x_old_prefix + res + x_old_suffix
        return x_new
    
    def headvt(self, p:int):
        '''
        返回输入串头部第一个vt
        '''
        reamined_text = self.text[p+1:]
        for ch in reamined_text:
            if ch in self.Vt:
                return ch
        return False
    
    def _dictcheck(self, token_stack:str):
        '''
            检查当前输入栈中的所有字符
        '''
        for ch in token_stack:
            if not self.isInDict(ch):
                return False
        return True
    
    def _default_special_check(self, token_stack:str):
        '''
            对默认语法中的一些特殊情况进行的特别检查
        '''
        if '++' in token_stack:
            return False
        if '**' in token_stack:
            return False
        if '+*' in token_stack:
            return False
        if '*+' in token_stack:
            return False
        return True


    def analyze(self):
        '''
            分析句型
        '''
        for vt in self.Vt:
            if ['#', vt, '<'] not in self.priority_table:
                self.priority_table.append(['#', vt, '<'])
            if [vt, '#', '>'] not in self.priority_table:
                self.priority_table.append([vt, '#', '>'])
        if ['#','#','='] not in self.priority_table:
            self.priority_table.append(['#','#','='])
        if '#' not in self.Vt:
            self.Vt.append('#')
        token_stack = "#"
        p = 1
        steps = []
        i = 0
        while self.check(token_stack):
            step = [i]
            ch = self.curchar(p)
            while self.curchar(p) not in self.Vt:
                if self.curchar(p) not in self.Vn:
                    step.append(token_stack)
                    operator = "Failed!"
                    step.append(operator)
                    step.append(ch)
                    step.append(self.text[p+1:])
                    steps.append(step)
                    return steps, "Failed!"
                ch = self.curchar(p)
                token_stack += ch
                p += 1
            ch = self.curchar(p)
            step.append(token_stack)
            if self.popvt(token_stack):
                pvt = self.popvt(token_stack)
                operator = self.judge(pvt, ch)
            elif self._dictcheck(token_stack):
                pass
            else:
                print(token_stack+"测试语句出错！")
                return steps, "Failed!"
            step.append(operator)
            step.append(ch)
            step.append(self.text[p+1:])
            steps.append(step)
            if operator == '<' or operator == '=':
                if operator == '=' and ch == '#':
                        step = steps.pop()
                        step[2] = "Accepted!"
                        steps.append(step)
                        break
                if ch in self.Vt:
                    token_stack += ch
                    p += 1
                while self.curchar(p) not in self.Vt:
                    ch = self.curchar(p)
                    token_stack += ch
                    p += 1
            elif operator == '>':
                handle, start_index= self.find_leftest_substring(token_stack.replace("#", ""))
                if handle:
                    res = self.reduce(handle)
                    if res:
                        token_stack = '#'+self.replace(token_stack[1:], res, start_index, len(handle))
                        #token_stack = token_stack.replace(handle, res)
                    else:
                        return steps, "Failed!"
                else:
                    return steps, "Failed!"
            else:
                return steps, "Failed!"
            i += 1

            if not self.check(token_stack):
                step = [i]
                ch = self.curchar(p)
                while self.curchar(p) not in self.Vt:
                    ch = self.curchar(p)
                    token_stack += ch
                    p += 1
                ch = self.curchar(p)
                step.append(token_stack)
                if self.popvt(token_stack):
                    pvt = self.popvt(token_stack)
                    operator = self.judge(pvt, ch)
                else:
                    print(token_stack+"测试语句出错！")
                    return steps, "Failed"
                step.append(operator)
                step.append(ch)
                step.append(self.text[p+1:])
                steps.append(step)
                if operator == '=' and ch == '#':
                        step = steps.pop()
                        step[2] = "Accepted!"
                        steps.append(step)
                        break    
        return steps, "Succeed!"

    def web_output_analyze_result(self, text:str, steps:list, status:str):
        '''
            按步骤分析结果
            输出html表格
        '''
        html = "<table class=\"table table-hover\"><caption>"+text+"的分析过程</caption>"
        head = "<thead><tr>" + "<th>步骤</th>" + "<th>符号栈</th>" + "<th>优先关系</th>" + "<th>读入符号</th>" + "<th>输入串</th>" + "</thead>"
        html += head
        body = "<tbody>"
        for step in steps:
            line = "<tr>"
            for field  in step:
                line += "<td>" + str(field) + "</td>"
            line += "</tr>"
            body += line
        status_line = "<tr><td>分析结果:</td><td>"+status+"</td></tr>"
        body += status_line+"</tbody>"
        html += body + "</table>"
        return html
        






if __name__ == "__main__":
    '''
        测试代码
    '''
    opga = OPGA()
    text = "E->E+T|T\nT->T*F|F\nF->(E)|i"
    #text = "E->E+E\nE->i"
    #opga.InputGrammar(text)
    print(opga.default_grammary)
    opga.FindVtVn()
    print("Vt:")
    string = ""
    for vt in opga.Vt:
        string += vt+" "
    print(string)
    print("FirstVt:")
    for vn in opga.Vn:
        string = vn + ":"
        res = opga.firstVt(vn)
        for b in res:
            string += b + " "
        print(string)
    print("LastVt:")
    for vn in opga.Vn:
        string = vn + ":"
        res = opga.lastVt(vn)
        for a in res:
            string += a + " "
        print(string)
    opga.setPriorityTable()
    print("poriority_table:")
    print(opga.output_priority_table())
    '''
    for record in opga.priority_table:
        print(record)
    '''
    print("==================================")
    opga.setStart('E')
    text = "i++"
    #text = "i+i"
    opga.input_test_txt(text)
    results, status = opga.analyze()
    print(text+"的分析过程")
    print("".ljust(76,'-'))
    print("|"+"步骤".ljust(12),end="")
    print("|"+"符号栈".ljust(11), end="")
    print("|"+"优先关系".ljust(10), end="")
    print("|"+"读入符号".ljust(10),end="")
    print("|"+"输入串".ljust(11), end="")
    print("|")
    print("".ljust(76,'-'))
    for res in results:
        print("|", end="")
        for field in res:
            print(str(field).ljust(14), end="")
            print("|", end="")
        print("\n",end="")
        #print("".ljust(76,'-'))
        #print("|"+str(res[0]).ljust(14)+"|"+str(res[1]).ljust(14)+"|"+str(res[2]).ljust(14)+"|"+str(res[3]).ljust(14)+"|"str(res[4]).ljust(14)+"|")
    print(status)
    #print(opga.web_output_priority_table())
