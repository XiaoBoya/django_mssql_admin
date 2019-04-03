import pyodbc
from DBUtils import PooledDB

from django.db import models

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

class SQLBase(SQLConnect):

    def __init__(self, connect_args,connect_kwargs, tablename):
        SQLConnect.__init__(self, connect_args,connect_kwargs)
        self.tablename = tablename
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
        cur.execute('select * from %s' % self.tablename)
        res = cur.fetchall()
        cur.close()
        conn.close()
        return res

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
        print(res)
        return res

    def _set_fields(self):
        SQLObject(self.fieldlist)

class SQLObject(object):

    def __init__(self, fields_list):
        print(*fields_list)

a = SQLBase(settings.SQL_ARGS, settings.SQL_DATABASE['brandcheck'], 'masasys.dbo.tb_sys_all_brand_clean')
print(a.fieldlist)
n = a.filter(brandid='16774520', media='ali')
print(n)

