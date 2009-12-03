# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Latinux Inc (http://www.latinux.com/) All Rights Reserved.
#                    Javier Duran <jduran@corvus.com.ve>
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

import time
from osv import fields, osv



class account_invoice(osv.osv):
    _inherit = 'account.invoice'


#    def _retenida(self, cr, uid, ids, name, args, context):
#        res = {}
#        for id in ids:
#            res[id] = self.test_paid(cr, uid, [id])
#        return res


    _description = "Retencion de Impuesto"
    _columns = {
#        'retention': fields.function(_retenida, method=True, string='Retention', type='boolean',
#            store={
#                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, None, 50),
#                'account.move.line': (_get_invoice_from_line, None, 50),
#                'account.move.reconcile': (_get_invoice_from_reconcile, None, 50),
#            }, help="The account moves of the invoice have been reconciled with account moves of the payment(s)."),
        'retention': fields.boolean('¿Retención Realizada?', readonly=True, help="Indica si la factura ha sido retenida"),
        'p_ret': fields.float('Retención Por 100', digits=(14,4), readonly=True, states={'draft':[('readonly',False)]}, help="Porcentaje de Retencion ha aplicar a la factura"),
        'num_ret': fields.char('Numero de Retencion', size=32, readonly=True, help="Numero del comprobante de retencion donde se declaro la factura"),
        'nro_ctrl': fields.char('Nro. de Control', size=32, readonly=True, states={'draft':[('readonly',False)]}, help="Numero de control de la factura"),
        'sin_cred': fields.boolean('¿Sin derecho a credito fiscal?', readonly=True, help="Determina si la factura esta sujeta o no a credito fiscal"),
    }
    

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,
            date_invoice=False, payment_term=False, partner_bank_id=False):

        data = super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id,
            date_invoice, payment_term, partner_bank_id)
        if partner_id:
            part = self.pool.get('res.partner').browse(cr, uid, partner_id)
            data[data.keys()[0]]['p_ret'] =  part.retention
        return data


    def create(self, cr, uid, vals, context={}):
        partner_id = vals.get('partner_id',False)
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid,partner_id)
            vals['p_ret'] = partner.retention
        return super(account_invoice, self).create(cr, uid, vals, context)


#    def test_paid(self, cr, uid, ids, *args):
#        res = self.move_line_id_payment_get(cr, uid, ids)
#        if not res:
#            return False
#        ok = True
#        for id in res:
#            cr.execute('select reconcile_id from account_move_line where id=%s', (id,))
#            ok = ok and  bool(cr.fetchone()[0])
#        return ok


account_invoice()





class account_invoice_tax(osv.osv):
    _inherit = 'account.invoice.tax'
    _description = "Retencion de Impuesto"
    _columns = {
        'amount_ret': fields.float('Monto Retenido', digits=(16,4), help="Indica el monto que se retiene"),
        'base_ret': fields.float('Base Retenida', digits=(16,4), help="La base a la cual se le ha hecho la retencion"),
    }
    
    def compute(self, cr, uid, invoice_id, context={}):
        tax_grouped = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context)
        cur = inv.currency_id
        company_currency = inv.company_id.currency_id.id

        for line in inv.invoice_line:
            for tax in tax_obj.compute(cr, uid, line.invoice_line_tax_id, (line.price_unit* (1-(line.discount or 0.0)/100.0)), line.quantity, inv.address_invoice_id.id, line.product_id, inv.partner_id, inv.p_ret):
                val={}
                val['invoice_id'] = inv.id
                val['name'] = tax['name']
                val['amount'] = tax['amount']
                val['manual'] = False
                val['sequence'] = tax['sequence']
                val['base'] = tax['price_unit'] * line['quantity']
                val['amount_ret'] = tax['amount_ret']
                val['base_ret'] = 0.0
                if tax['ret']:
                    val['base_ret'] = tax['price_unit'] * line['quantity']




                if inv.type in ('out_invoice','in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')})
                    val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')})
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['ref_base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')})
                    val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['ref_tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')})
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']
                    tax_grouped[key]['amount_ret'] += val['amount_ret']
                    tax_grouped[key]['base_ret'] += val['base_ret']

        for t in tax_grouped.values():
            t['amount'] = cur_obj.round(cr, uid, cur, t['amount'])
            t['amount_ret'] = cur_obj.round(cr, uid, cur, t['amount_ret'])
        return tax_grouped




account_invoice_tax()