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
    return render(request, 'grammar_analysis/gramma.html',context=context)
