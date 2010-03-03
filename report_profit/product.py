# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Netquatro C.A. (http://openerp.netquatro.com/) All Rights Reserved.
#                    Javier Duran <javier.duran@netquatro.com>
# 
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################


from osv import fields
from osv import osv
import ir
import pooler
import time
from tools import config

class product_supplierinfo(osv.osv):
    _inherit = 'product.supplierinfo'
    _name = "product.supplierinfo"

    def _last_sup_invoice(self, cr, uid, ids, name, arg, context):
        res = {}
        for supinfo in self.browse(cr, uid, ids):
            cr.execute("select inv.id, max(inv.date_invoice) from account_invoice as inv, account_invoice_line as line where inv.id=line.invoice_id and product_id=%s and partner_id=%s and state in ('open', 'paid') and type='in_invoice' group by inv.id", (supinfo.product_id.id, supinfo.name.id,))
            record = cr.fetchone()
            if record:
                res[supinfo.id] = record[0]
            else:
                res[supinfo.id] = False
        return res

    def _last_sup_invoice_date(self, cr, uid, ids, name, arg, context):
        res = {}
        inv = self.pool.get('account.invoice')
        _last_sup_invoices = self._last_sup_invoice(cr, uid, ids, name, arg, context)
        dates = inv.read(cr, uid, filter(None, _last_sup_invoices.values()), ['date_invoice'])
        for suppinfo in ids:
            date_inv = [x['date_invoice'] for x in dates if x['id']==_last_sup_invoices[suppinfo]]
            if date_inv:
                res[suppinfo] = date_inv[0]
            else:
                res[suppinfo] = False
        return res

    _columns = {
        'last_inv' : fields.function(_last_sup_invoice, type='many2one', obj='account.invoice', method=True, string='Last Invoice'),
        'last_inv_date' : fields.function(_last_sup_invoice_date, type='date', method=True, string='Last Invoice date'),
    }
product_supplierinfo()


class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'


    def _get_last_invoice_func(states, what):
        def _last_invoice(self, cr, uid, ids, name, arg, context):
            res = self._product_get_invoice(cr, uid, ids, False, False, False, context, states, what)
            return res
        return _last_invoice


    def _get_last_invoice_date_func(states, what):
        def _last_invoice_date(self, cr, uid, ids, name, arg, context):
            res = {}
            inv = self.pool.get('account.invoice')
            _last_invoices = self._product_get_invoice(cr, uid, ids, False, False, False, context, states, what)
            dates = inv.read(cr, uid, filter(None, _last_invoices.values()), ['date_invoice'])
            for prod_id in ids:
                date_inv = [x['date_invoice'] for x in dates if x['id']==_last_invoices[prod_id]]
                if date_inv:
                    res[prod_id] = date_inv[0]
                else:
                    res[prod_id] = False
            return res
        return _last_invoice_date


    def _get_last_invoice_price_func(states, what):
        def _last_invoice_price(self, cr, uid, ids, name, arg, context):
            return self._product_get_price(cr, uid, ids, False, False, False, context, states, what)
        return _last_invoice_price


    def _product_get_price(self, cr, uid, ids, invoice_id=False, supplier_id=False, date_ref=False, context={}, states=['open', 'paid'], what='in_invoice'):
        res = {}
        _last_invoices = self._product_get_invoice(cr, uid, ids, invoice_id, supplier_id, date_ref, context, states, what)
        lstprod=filter(lambda x:_last_invoices[x], _last_invoices.keys())
        for prod_id in ids:
            record = False
            if prod_id in lstprod:
                cr.execute("select line.id, max(line.price_unit) as price from account_invoice_line as line where line.invoice_id=%s and product_id=%s group by line.id order by price desc", (_last_invoices[prod_id], prod_id))
                record = cr.fetchone()
            if record:
                res[prod_id] = record[1]
            else:
                res[prod_id] = False
        return res


    def _product_get_invoice(self, cr, uid, ids, invoice_id=False, supplier_id=False, date_ref=False, context={}, states=['open', 'paid'], what='in_invoice'):
        res = {}
        states_str = ','.join(map(lambda s: "'%s'" % s, states))
        date = date_ref or time.strftime('%Y-%m-%d')
        for product in self.browse(cr, uid, ids):
            sql = "select inv.id, max(inv.date_invoice) as date from account_invoice as inv, account_invoice_line as line where inv.id=line.invoice_id and product_id=%s and state in (%s) and type='%s' and date_invoice<='%s' group by inv.id order by date desc" % (product.id,states_str,what,date)
            if supplier_id:
                sql = "select inv.id, max(inv.date_invoice) as date from account_invoice as inv, account_invoice_line as line where inv.id=line.invoice_id and product_id=%s and partner_id=%s and state in (%s) and type='%s' and date_invoice<='%s' group by inv.id order by date desc" % (product.id,supplier_id,states_str,what,date)

            cr.execute(sql)
            allrecord = cr.fetchall()
            record = allrecord and allrecord.pop(0) or False                
            if invoice_id and record[0]==invoice_id:
                record = allrecord and allrecord.pop(0) or False
            if record:
                res[product.id] = record[0]
            else:
                res[product.id] = False
        return res


    _invoice_available = _get_last_invoice_func(('open', 'paid'), 'in_invoice')
    _invoice_date_available = _get_last_invoice_date_func(('open', 'paid'), 'in_invoice')
    _invoice_price_available = _get_last_invoice_price_func(('open', 'paid'), 'in_invoice')
    _columns = {
        'last_inv' : fields.function(_invoice_available, type='many2one', obj='account.invoice', method=True, string='Last Invoice'),
        'last_inv_date' : fields.function(_invoice_date_available, type='date', method=True, string='Last Invoice date'),
        'last_inv price': fields.function(_invoice_price_available, type="float", method=True, string='Last Invoice price', digits=(16, int(config['price_accuracy']))),
    }

product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

