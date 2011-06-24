#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Humberto Arocha           <humberto@openerp.com.ve>
#              Maria Gabriela Quilarque  <gabriela@vauxoo.com>
#              Javier Duran              <javier@vauxoo.com>
#    Planified by: Nhomar Hernandez
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha humberto@openerp.com.ve
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
from osv import osv
from osv import fields
from tools import config
from tools.translate import _
import time

class l10n_ut(osv.osv):
    """
    OpenERP Model : l10n_ut
    """
    
    _name = 'l10n.ut'
    _description = __doc__
    _order = 'date desc'
    _columns = {
        'name':fields.char('Law Number Reference', size=64, required=True, readonly=False),
        'date': fields.date('Date', required=True),
        'amount': fields.float('Amount', digits=(16, int(config['price_accuracy'])), help="Amount Bs per UT.", required=True),
    }
    _defaults = {
        'name': lambda *a: None,
    }


    def get_amount_ut(self, cr, uid, date=False, *args):
        rate = 0
        date= date or time.strftime('%Y-%m-%d')        
        cr.execute("SELECT amount FROM l10n_ut WHERE date <= '%s' ORDER BY date desc LIMIT 1" % (date))
        if cr.rowcount:
            rate=cr.fetchall()[0][0]
        return rate

    def compute(self, cr, uid, from_amount, date=False, context={}):
        result = 0.0
        ut = self.get_amount_ut(cr, uid, date=False)
        if ut:
            result = from_amount / ut

        return result

    def compute_ut_to_money(self, cr, uid, amount_ut, date=False, context={}):
        money = 0.0
        ut = self.get_amount_ut(cr, uid, date)
        if ut:
            money = amount_ut * ut
        return money

l10n_ut()


