from django.shortcuts import render
from django.views.decorators import csrf
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
from django.utils.safestring import mark_safe
from .OPGA import OPGA
defalut_gramma = "E->E+T|T\nT->T*F|F\nF->(E)|i"
# Create your views here.
def complie(request):
    '''
      对POST请求进行处理，去掉表单中多余的字符后交由OPG分析器，
      再将渲染的结果返回给客户端
    '''
    context = {}
    context['title'] = "OPGA_response"
    if request.POST:
        opga = OPGA()
        print(request.POST)
        gramma_file = request.FILES.get('gramma_file')
        code_file = request.FILES.get('code_file')
        check = request.POST.__contains__('check')
        if check:
            if gramma_file:
                size = gramma_file.size
                if size >= 2.5*1024:
                    messages.warning(request, "语法文件大于2.5M")
                else:
                    gramma = gramma_file.read()
                    gramma = str(gramma.decode("utf-8")).strip()
            else:
                gramma = request.POST['grammary']
                gramma = str(gramma).strip()
            if not gramma:
                messages.warning(request, "自定义语法不能为空")
            else:
                opga.InputGrammar(gramma)
            start = request.POST['start']
            start = str(start).strip()
            if not start:
                messages.warning(request, "开始符号不能为空")
            else:
                opga.setStart(start)
        else:
            gramma = defalut_gramma
        if code_file:
            size = code_file.size
            if size >= 2.5*1024:
                messages.warning(request, "上传文件大于2.5M")
            else:
                code = code_file.read()
                code = str(code.decode("utf-8")).strip()
        else:
            code = request.POST['code']
        if not code:
            messages.warning(request, "测试语句不能为空")
        opga.InputGrammar(gramma.strip())
        print(gramma)
        opga.FindVtVn()
        opga.setPriorityTable()
        priority_table = opga.web_output_priority_table()
        opga.input_test_txt(code)
        results, status = opga.analyze()
        production_table = opga.web_output_production()
        vtvn_table = opga.web_output_VnVt()
        fvt_table = opga.web_output_FirstVt()
        lvt_table = opga.web_output_LastVt()
        step_table = opga.web_output_analyze_result(code,results,status)
        #print(priority_table)
        context['表格1'] = mark_safe(production_table)
        context['表格2'] = mark_safe(vtvn_table)
        context['表格3'] = mark_safe(fvt_table)
        context['表格4'] = mark_safe(lvt_table)
        context['表格5'] = mark_safe(priority_table)
        context['表格6'] = mark_safe(step_table)
        #print("priority_table:")
        #print(mark_safe(priority_table))
        #print("results:")
        #print(results)
        #print(step_table)
    return render(request, 'OPGA/opgay.html', context=context)