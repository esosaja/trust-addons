# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2016 TrustCode - www.trustcode.com.br                         #
#              Danimar Ribeiro <danimaribeiro@gmail.com>                      #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU Affero General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################


from openerp import api, fields, models


class CrmHelpesk(models.Model):
    _name = 'crm.helpdesk.trustcode'
    _description = "Chamados Trustcode"
    _order = "id desc"
    _inherit = ['mail.thread']

    def _default_email_from(self):
        if "default_trustcode_solicitation" in self.env.context:
            return self.env.user.partner_id.email or self.env.user.login

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    company_id = fields.Many2one('res.company', 'Company')
    date_closed = fields.Datetime('Closed', readonly=True)
    email_from = fields.Char('Email', size=128,
                             help="Destination email for email gateway",
                             default=_default_email_from)
    date = fields.Datetime('Date', readonly=True, default=fields.Datetime.now())
    priority = fields.Selection([('0', 'Low'), ('1', 'Normal'), ('2', 'High')], 'Priority')
    state = fields.Selection(
        [('draft', 'Novo'),
         ('open', 'Em progresso'),
         ('pending', 'Pendente'),
         ('done', 'Fechado'),
         ('cancel', 'Cancelado')], 'Status',
        readonly=True, track_visibility='onchange',
        default='draft',
    )
    responsible = fields.Char('Atendente', readonly=True, size=50)
    responsible_id = fields.Many2one('res.users', string='Atendente', readonly=True, size=50)
    attachment = fields.Binary(u'Anexo')
    version = fields.Integer(u'Versão', default=0)
    interaction_ids = fields.One2many(
        'crm.helpdesk.trustcode.interaction',
        'crm_help_id', string="Interações")

    @api.model
    def create(self, vals):
        self.send_to_trustcode()
        return super(CrmHelpesk, self).create(vals)

    @api.multi
    def send_to_trustcode(self):
        pass

    @api.model
    def synchronize_helpdesk_solicitation(self):
        solicitations = self.search([('state', '!=', 'done'),
                                     ('state', '!=', 'cancel')])
        for solicitation in solicitations:
            print solicitation.trustcode_id


class CrmHelpdeskInteraction(models.Model):
    _name = 'crm.helpdesk.trustcode.interaction'
    _description = u'Interações do chamado'

    def _default_responsible(self):
        return self.env.user.partner_id.id

    trustcode_id = fields.Char(u"Id Único", size=80)
    date = fields.Datetime(u'Data', default=fields.Datetime.now())
    time_since_last_interaction = fields.Float(u'Última interação')
    state = fields.Selection([('new', 'Novo'), ('read', 'Lida')],
                             u'Status', default='new')
    name = fields.Text(string=u'Resposta')
    crm_help_id = fields.Many2one('crm.helpdesk.trustcode', string=u"Chamado")
    attachment = fields.Binary(u'Anexo')
    responsible = fields.Char(u'Atendente', size=50, readonly=True)
    responsible_id = fields.Many2one('res.users', string='Atendente', readonly=True, size=50)

    @api.multi
    def mark_as_read(self):
        self.write({'state': 'read'})