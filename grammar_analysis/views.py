from django.shortcuts import render
from django.views.decorators import csrf
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
from django.utils.safestring import mark_safe

from .lexer import C0lexer
from .utils import special_lexer, norm_C0_compiler
# Create your views here.

def compile(request):
    context = {}
    context['title'] = "gramma_response"
    if request.POST:
        lexer = special_lexer()
        compiler = norm_C0_compiler()
        test_file = request.FILES.get('test_file')
        code = request.POST['code']
        if test_file:
            size = test_file.size
            if size >= 2.5*1024:
                messages.warning(request, "测试代码文件大于2.5M")
            else:
                test_code = test_file.read()
                test_code = str(test_code.decode("utf-8")).strip()
        else:
            test_code = code
        if not test_code:
            messages.warning(request, "测试代码不能为空")
        else:
            lexer.web_input(test_code)
        print(test_code)
        context['代码'] = test_code
        flag = 0
        try:
            lexer.web_word_analyze()
            words = lexer.RESULT
            print(words)
            errors = lexer.error_message_box
            compiler.words = words
            compiler.error_msg_box = errors
            compiler.s_program()
        except Exception as e:
            print("error1")
            print(e)
            flag = 1
        if len(compiler.error_msg_box) > 0 or flag == 1:
            print("OK4")
            error_table = compiler.web_output_error_table()
            print(error_table)
            context = {}
            context['表格4'] = mark_safe(error_table)
            context['代码'] = test_code
        else:
            display_table = compiler.web_output_display_table()
            rconst_table = compiler.web_output_rconst_table()
            Pcode_table = compiler.web_output_Pcode_table()
            compiler.report_result()
            context = {}
            context['表格1'] = mark_safe(display_table)
            context['表格2'] = mark_safe(rconst_table)
            context['表格3'] = mark_safe(Pcode_table)
            context['代码'] = test_code
        print(context)
    return render(request, 'grammar_analysis/gramma.html', context=context)
