from django.shortcuts import render
from django.views.decorators import csrf
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
from .lexer import C0lexer

# Create your views here.

def complie(request):
    '''
        对POST请求进行处理，去掉表单中多余的字符后交由词法分析器，
        再将渲染的结果返回给客户端
    '''
    context = {}
    context["title"] = "source_code"
    if request.POST:
        print(request.POST)
        f = request.FILES.get("test_file")
        if f:
            size = f.size
            if size >= 2.5*1024:#控制源文件大小
                messages.warning(request, "上传文件大于2.5m")
            pro = f.read()
            pro = pro.decode("utf-8")
        else:
            pro = request.POST['source_code']
        pro = str(pro).strip()
        print("pro",pro)
        if not pro.strip():
            context["result"] = '不能提交空代码'
        check = request.POST.__contains__('check')
        if check:
            pro = str(pro)
            lexy = C0lexer(" ")
            lexy.web_input(pro)
            lexy.web_word_analyze()
            context['结果'] = lexy.web_reply()
            print(context['结果'])
        else:
             messages.warning(request, "小伙子不要搞事情，请确认代码没有安全问题")#安全控制
    return render(request, 'lexer/lexery.html', context=context)
            