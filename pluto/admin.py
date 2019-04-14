from django.contrib import admin
from pluto.sql_models import site
from pluto.sql_models import SQLModel
from pluto.sql_models import PlutoConfig
from django_mssql_admin import settings

# Register your models here.

a = SQLModel(settings.SQL_ARGS, settings.SQL_DATABASE['brandcheck'], 'masasys.dbo.tb_sys_all_brand_clean', 'BrandClean')
b = SQLModel(settings.SQL_ARGS, settings.SQL_DATABASE['brandcheck'], 'masasys.dbo.tb_sys_brand_info', 'BrandInfo')
c = SQLModel(settings.SQL_ARGS, settings.SQL_DATABASE['catecheck2'], 'catSort.dbo.venncate_2018', 'Cate')

class AConfig(PlutoConfig):
    have_checkbox = False
    pk = 'brandid'
    list_display = ['brandid', 'media', 'code', 'itemBrand']


class BConfig(PlutoConfig):
    list_display = ['brandId', 'brandStr', 'brandcn', 'branden']
    pk = 'brandId'
    fields = ['brandId', 'brandStr', 'brandcn', 'brandxn']

class CConfig(PlutoConfig):
    pk = 'sid'
    list_display = ['sid', 'lcatname', 'mcatname', 'scatname']

site.register(a, AConfig)
site.register(b, BConfig)
site.register(c, CConfig)
