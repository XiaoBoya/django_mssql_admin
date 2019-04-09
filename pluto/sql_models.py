import pyodbc
import collections
from DBUtils import PooledDB

from django.shortcuts import render,HttpResponse
from django.forms import Form
from django.forms import fields
from django.forms import widgets
from django.db import models
from django.urls import path, re_path
from django.utils.safestring import mark_safe
from django.urls import reverse

from xbyadmin import settings

class SQLConnect(object):

    def __init__(self, conn_args, conn_kwargs):
        self.conn_args = conn_args
        self.conn_kwargs = conn_kwargs

    def new_connect(self):
        pool = PooledDB.PooledDB(pyodbc, *self.conn_args, **self.conn_kwargs)
        conn = pool.connection()
        cur = conn.cursor()
        return conn, cur


class SingleRecord(object):

    def __init__(self, data_list, field_list):
        for i, data in enumerate(data_list):
            if isinstance(data, str):
                exec('self.{0} = "{1}"'.format(field_list[i][0], data))
            else:
                exec('self.{0} = {1}'.format(field_list[i][0], data))

    def __iter__(self):
        return self

    def get(self, name):
        return self.__getattribute__(name)


class SQLModel(SQLConnect):

    def __init__(self, connect_args,connect_kwargs, tablename, alias):
        SQLConnect.__init__(self, connect_args,connect_kwargs)
        self.tablename = tablename
        self.alias = alias
        self._get_fieldname()

    def _get_fieldname(self):
        conn, cur = self.new_connect()
        cur.execute('select top 1 * from %s' % self.tablename)
        des = cur.description
        self.fieldlist = [(item[0],item[1],item[-1])  for item in des]
        cur.close()
        conn.close()

    def all(self):
        conn, cur = self.new_connect()
        cur.execute('select top 1000 * from %s' % self.tablename)
        res = cur.fetchall()
        cur.close()
        conn.close()
        result = []
        for i in res:
           result.append(SingleRecord(i, self.fieldlist))
        return result

    def filter(self,**kwargs):
        filter_llist = []
        for filter_dict in kwargs:
            filter_llist.append('%s=%s' % (filter_dict, kwargs[filter_dict] if type(filter_dict)!=str else "'%s'"%kwargs[filter_dict]))
        filter_info = ' and '.join(filter_llist)
        conn, cur = self.new_connect()
        cur.execute('select * from %s where %s' % (self.tablename, filter_info))
        res = cur.fetchall()
        cur.close()
        conn.close()
        result = []
        for i in res:
            result.append(SingleRecord(i, self.fieldlist))
        return result

    def create_form(self):
        info_dict = collections.OrderedDict()
        for field_obj in self.fieldlist:
            print(field_obj)
            if field_obj[1] == str:
                info_dict[field_obj[0]] = fields.CharField(
                    required=not field_obj[2],
                    error_messages={
                        "required":"%s不能为空"%field_obj[0],
                    },
                    widget=widgets.TextInput(
                        attrs={
                            "placeholder":field_obj[0],
                            "class":"form-control col-md-7 col-xs-12"
                        }
                    ),
                    label=field_obj[0]
                )
            elif field_obj[1] == int:
                info_dict[field_obj[0]] = fields.IntegerField(
                    required=not field_obj[2],
                    error_messages={
                        "required": "%s不能为空"%field_obj[0],
                    },
                    widget=widgets.TextInput(
                        attrs={
                            "placeholder": field_obj[0],
                            "class": "form-control col-md-7 col-xs-12"
                        }
                    ),
                    label=field_obj[0]
                )
            elif field_obj[1] == float:
                info_dict[field_obj[0]] = fields.FloatField(
                    required=not field_obj[2],
                    error_messages={
                        "required": "%s不能为空"%field_obj[0],
                    },
                    widget=widgets.TextInput(
                        attrs={
                            "placeholder": field_obj[0],
                            "class": "form-control col-md-7 col-xs-12"
                        }
                    ),
                    label=field_obj[0]
                )
        return type('%sForm'%self.alias, (Form, ), info_dict)


class PlutoConfig(object):
    '''
    list_display: 展示用的字段
    '''
    pk = 'id'
    link_field = (pk, )

    list_display = ()
    def changelist_view(self, request, *args, **kwargs):
        if self.list_display:
            thead = self.list_display
        else:
            thead = [one[0] for one in self.model_obj.fieldlist]
        show_list = []
        for single_data in self.model_obj.all():
            show_list.append([single_data.get(field_) for field_ in thead])
        return render(request, 'changelist.html', {'show_list': show_list, 'thead_': thead})

    def __init__(self, model_obj, site):
        self.model_obj = model_obj
        self.site = site
        self.request = None
        self._query_param_key = "_listfilter"
        self.search_key = "_q"

    def wrap(self, view_func):
        def inner(request, *args, **kwargs):
            self.request = request
            return view_func(request, *args, **kwargs)

        return inner

    def get_urls(self):
        model_name = self.model_obj.alias
        url_patterns = [
            re_path(r'^$', self.wrap(self.changelist_view), name="%s_changlist" % model_name),
            re_path(r'^add/$', self.wrap(self.add_view), name="%s_add" % model_name),
            re_path(r'^(\w+)/delete/$', self.wrap(self.delete_view), name="%s_delete" % model_name),
            re_path(r'^(\w+)/change/$', self.wrap(self.change_view), name="%s_change" % model_name),
        ]
        url_patterns.extend(self.extra_url())
        return url_patterns

    def extra_url(self):
        return []

    @property
    def urls(self):
        return self.get_urls()

    def add_view(self, request, *args, **kwargs):
        the_form = self.model_obj.create_form()
        return render(request, 'add.html', {'the_form': the_form})

    def delete_view(self):
        pass

    def change_view(self):
        pass

class PlutoSite(object):

    def __init__(self):
        self._registry = {}

    def register(self, model_obj, pluto_config_class=None):
        if not pluto_config_class:
            pluto_config_class = PlutoConfig
        self._registry[model_obj] = pluto_config_class(model_obj, self)

    def get_urls(self):
        url_pattern = []
        for model_obj, pluto_config_obj in self._registry.items():
            tablename = model_obj.alias
            curd_url = re_path(r'^%s/' %(tablename,) , (pluto_config_obj.urls,None,None))
            url_pattern.append(curd_url)
        return url_pattern

    @property
    def urls(self):
        return (self.get_urls(),None,'pluto')

site = PlutoSite()

a = SQLModel(settings.SQL_ARGS, settings.SQL_DATABASE['brandcheck'], 'masasys.dbo.tb_sys_all_brand_clean', 'BrandClean')
print(a.fieldlist)

class AConfig(PlutoConfig):
    pk='brandid'

site.register(a, AConfig)