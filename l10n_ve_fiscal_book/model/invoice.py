#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by:       Luis Escobar <luis@vauxoo.com>
#                    Tulio Ruiz <tulio@vauxoo.com>
#    Planified by: Nhomar Hernandez
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################
from openerp.osv import osv, fields


class inherited_invoice(osv.osv):
    _inherit = "account.invoice"

    def _get_inv_number(self,cr,uid,ids,name,args,context=None):
        '''
        Get Invoice Number
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i:''})
        if res:
            for r in res:
                ret.update({r.id : r.number and str(r.number) or ''})
        return ret

    def _get_total(self,cr,uid,ids,name,args,context=None):
        '''
        Get Total Invoice Amount
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i:0})
        if res:
            for r in res:
                ret.update({ r.id : r.amount_total })
        return ret
        
    def _get_wh_number(self,cr,uid,ids,name,args,context=None):
        '''
        Get Wh Number if any
        '''
        whl_obj = self.pool.get('account.wh.iva.line')

        ret = {}
        for i in ids:
            ret.update({i:''})
        
        for r in ids:
            ret.update({r : False})
            whl_ids = whl_obj.search(cr, uid, [('invoice_id', '=', r)])
            whl_brw = whl_obj.browse(cr, uid, whl_ids)
            if whl_brw:
                for whl in whl_brw:
                    ret.update({r: whl.retention_id.number})
        return ret

    def _get_inv_tax_line(self, s):
        '''
        Get Tax Line
        '''
        name = s.name
        cont = 0
        if name.find('SDCF')>=0:
            if cont==0:
                return 0
        else:
            cont = cont + 1
        return s.base_amount

    def _get_taxes(self,cr,uid,ids,name,args,context=None):
        '''
        Get Invoice Taxes
        '''
        tax_obj = self.pool.get('account.invoice.tax')
        ret = {}
        for inv in ids:
            tax_ids = tax_obj.search(cr, uid, [('invoice_id', '=', inv)])
            tam = len(tax_ids)
            data = tax_obj.browse(cr, uid, tax_ids)
            
            for tax in data:
                if 'SDCF' in tax.name and tax.tax_id.amount == 0.00 and tam>=2:
                    tax_ids.remove(tax.id)
                elif 'EXENTO' in tax.name and tax.tax_id.amount == 0.00 and tam>=2:
                    tax_ids.remove(tax.id)
                elif tax.tax_id.amount == 0.00 and tam>=2:
                    tax_ids.remove(tax.id)
            
            data = tax_obj.browse(cr, uid, tax_ids)
            if data:
                ret.update({inv:data})
            else:
                ret.update({inv:False})
                
        return ret

    def _get_papel_anulado(self, cr, uid,ids, name, args, context=None):
        '''
        Get Operation Type
        '''
        tipo = '03-ANU'
        data = '01-REG'
        res = self.browse(cr, uid, ids)
        ret = {}
        if res:
            for l in res:
                if l.name:
                    if l.name.find('PAPELANULADO')>=0: 
                        ret.update({l.id: tipo})
                    else: 
                        ret.update({l.id: data})
                else:
                    ret.update({l.id: data})
        return ret
        
    def _get_lang(self,cr,uid,ids,name,args,context=None):
        '''
        Get Lang from partner
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        if res:
            for r in res:
                ret.update({r.id:r.company_id.partner_id.lang})
        return ret

    def _get_nro_inport_form(self, cr, uid,ids, name, args, context=None):
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i:''})
        for r in res:
            if hasattr(r, 'num_import_form'):
                if r.num_import_form:
                    ret.pudate({r.id : r.num_import_form})
        return ret

    def _get_nro_inport_expe(self, cr, uid,ids, name, args, context=None):
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i:''})
        for r in res:
            if hasattr(r, 'num_import_expe'):
                if r.num_import_expe:
                    ret.pudate({r.id : r.nro_inport_expe})
        return ret

    def _get_import_spreadsheets(self, cr, uid, ids, name, args, context=None):
        '''
        Get Import Spreadsheets
        '''
        ret = {}
        for i in ids:
            ret.update({i:[]})
        for inv in ids:
            isp_ids = self.search(cr, uid, [('affected_invoice', '=', inv),
                                            ('state', 'in',[ 'done', 'paid', 'open'])
                                            ])
#            print isp_ids
            if isp_ids:
                res = self.browse(cr, uid, isp_ids)
                ret.update({inv: res})
#                print ret
        return ret
                
    def _get_invoice_printer(self, cr, uid, ids, name, args, context=None):
        '''
        Get Fiscal Printer Invoice Number
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i:''})
        for r in res:
            ret.update({r.id : r.invoice_printer})
        return ret

    def _get_fiscal_printer(self, cr, uid, ids, name, args, context=None):
        '''
        Get Fiscal Machine Number
        '''
        res = self.browse(cr, uid, ids)
        ret = {}
        for i in ids:
            ret.update({i:''})
        for r in res:
            ret.update({r.id : r.fiscal_printer})
        return ret

    _columns = {
        'get_total': fields.function(_get_total, method=True, string='Invoice total', type='float',
                            help=""),
        'get_wh_number': fields.function(_get_wh_number, method=True, string='Wh document number', type='char',
                            help=""),
        'get_tax_line': fields.function(_get_inv_tax_line, method=True, string='Tax line', type='char',
                            help=""),
        'get_lang': fields.function(_get_lang, method=True, string='Language', type='char',
                            help=""),
        'get_taxes': fields.function(_get_taxes, method=True, string='Invoice Taxes', type='char',
                            help=""),
        'get_papel_anulado': fields.function(_get_papel_anulado, method=True, string='Transaction type', type='char',
                            help=""),
        'get_nro_inport_form': fields.function(_get_nro_inport_form, method=True, string='Import form number', type='char',
                            help=""),
        'get_nro_inport_expe': fields.function(_get_nro_inport_expe, method=True, string='Import file number', type='char',
                            help=""),
        'get_import_exp': fields.function(_get_nro_inport_expe, method=True, string='kind of document', type='char',
                            help=""),
        'get_import_spreadsheets': fields.function(_get_import_spreadsheets, method=True, string='Import spreadsheets', type='date',
                            help=""),    
        'get_invoice_printer': fields.function(_get_invoice_printer, method=True, string='Fiscal printer invoice number', type='char',
                            help=""),    
        'get_fiscal_printer': fields.function(_get_fiscal_printer, method=True, string='Fiscal machine number', type='char',
                            help=""),


        'fb_id':fields.many2one('fiscal.book','Fiscal Book',
            help='Fiscal Book where this line is related to'),
        #TODO: THIS FIELD TO BE CHANGED TO A STORABLE FUNCTIONAL FIELD
        #CHANGE EVEN FROM boolean to selection
        'issue_fb_id':fields.many2one('fiscal.book','Fiscal Book',
            help='Fiscal Book where this invoice needs to be add'),
        'fb_submitted':fields.boolean('Fiscal Book Submitted?',
                help='Indicates if this invoice is in a Fiscal Book which has'\
                        ' being already submitted to the statutory institute'),
        'num_import_expe': fields.char('Import File number', 15,
            help="Import the file number for this invoice"),
        'num_import_form': fields.char('Import Form number', 15,
            help="Import the form number for this invoice"),
        }

inherited_invoice()
