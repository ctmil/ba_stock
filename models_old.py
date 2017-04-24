# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import tools
import datetime
import logging
import poplib
import time
import email

from openerp.osv import fields, osv
from openerp import tools, api, SUPERUSER_ID
from openerp.tools.translate import _
from openerp.exceptions import UserError

_logger = logging.getLogger(__name__)

class ba_stock_quant(osv.osv):
	_name = "ba.stock.quant"
	_description = "AS Stock Quant"
	_auto = False

	_columns = {
		'location_id': fields.many2one('stock.location','Location'),
		'company_id': fields.many2one('res.company','Company'),
		'product_id': fields.many2one('product.product','Product'),
		'qty': fields.integer('Qty'),
		}

	def init(self, cr):
        	tools.sql.drop_view_if_exists(cr, 'ba_stock_quant')
	        cr.execute("""
			create view ba_stock_quant as 
				select max(a.id) as id,a.location_id as location_id,a.company_id as company_id,
					a.product_id as product_id,sum(qty) as qty from stock_quant a group by 2,3,4
	        	""")


class ba_stock_move(osv.osv):
	_name = "ba.stock.move"
	_description = "AS Stock Move"
	_auto = False

	_columns = {
		'picking_id': fields.many2one('stock.picking','Reference'),
		'date': fields.date('Date'),
		'company_id': fields.many2one('res.company','Company'),
		'product_id': fields.many2one('product.product','Product'),
		'location_id': fields.many2one('stock.location','Location'),
		'location_usage': fields.char('Location Usage'),
		'location_dest_id': fields.many2one('stock.location','Location'),
		'location_dest_usage': fields.char('Location Usage'),
		'product_uom_qty': fields.integer('Qty'),
		'cantidad': fields.integer('Qty'),
		'loc_id': fields.many2one('stock.location','Location'),
		}

	def init(self, cr):
        	tools.sql.drop_view_if_exists(cr, 'ba_stock_move')
	        cr.execute("""
			create view ba_stock_move as 
				select a.id as id,a.picking_id as picking_id,a.date,a.company_id as company_id,a.product_id as product_id,a.location_id as location_id,b.usage as location_usage,
					a.location_dest_id as location_dest_id,c.usage as location_dest_usage,a.product_uom_qty as product_uom_qty,
					case b.usage when 'internal' then a.product_uom_qty * (-1) else a.product_uom_qty end as cantidad, 
					case b.usage when 'internal' then a.location_id else a.location_dest_id end as loc_id 
					from stock_move a inner join stock_location b on a.location_id = b.id inner join stock_location c on c.id = a.location_dest_id 
					where (b.usage = 'internal' and c.usage <> 'internal') or (b.usage <> 'internal' and c.usage = 'internal') 
					and a.state = 'done'
					and a.location_id <> a.location_dest_id
				union
				select a.id as id,a.picking_id as picking_id,a.date,a.company_id as company_id,a.product_id as product_id,a.location_id as location_id,b.usage as location_usage,
					a.location_dest_id as location_dest_id,c.usage as location_dest_usage,a.product_uom_qty as product_uom_qty,
					a.product_uom_qty * (-1) as cantidad, 
					a.location_id as loc_id 
					from stock_move a inner join stock_location b on a.location_id = b.id inner join stock_location c on c.id = a.location_dest_id 
					where (b.usage = 'internal' and c.usage = 'internal') 
					and a.state = 'done'
					and a.location_id <> a.location_dest_id
				union
				select  1000000 + a.id as id,a.picking_id as picking_id,a.date,a.company_id as company_id,a.product_id as product_id,
					a.location_id as location_id,b.usage as location_usage,
					a.location_dest_id as location_dest_id,c.usage as location_dest_usage,a.product_uom_qty as product_uom_qty,
					a.product_uom_qty as cantidad, 
					a.location_dest_id as loc_id 
					from stock_move a inner join stock_location b on a.location_id = b.id inner join stock_location c on c.id = a.location_dest_id 
					where (b.usage = 'internal' and c.usage = 'internal') 
					and a.state = 'done'
					and a.location_id <> a.location_dest_id
	        	""")
