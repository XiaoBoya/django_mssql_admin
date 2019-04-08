from django.shortcuts import render,HttpResponse

# Create your views here.
from pluto.sql_models import *
def index(request):
    a = SQLModel(settings.SQL_ARGS, settings.SQL_DATABASE['brandcheck'], 'masasys.dbo.tb_sys_all_brand_clean',
                 'BrandClean')
    BrandCleanForm = a.create_form()
    return render(request, 'index.html', locals())
