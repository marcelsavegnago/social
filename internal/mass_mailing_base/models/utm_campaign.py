# Copyright (C) 2020 - SUNNIT dev@sunnit.com.br
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api
from odoo.addons.mass_mailing.models.mailing import MASS_MAILING_BUSINESS_MODELS


class UtmCampaign(models.Model):
    _inherit = 'utm.campaign'

    mailing_activities_ids = fields.One2many(
        comodel_name='mailing.mailing',
        inverse_name='campaign_id',
        string='Mass Activities',
    )

    mailing_activities_count = fields.Integer(
        string='Number of Mass Activities',
        compute="_compute_mailing_activities_count",
    )

    mailing_whatsapp_count = fields.Integer(
        string='Number of Mass Whatsapp',
        compute="_compute_mailing_whatsapp_count",
    )
    mailing_model_real = fields.Char(
        compute='_compute_model',
        string='Recipients Real Model',
        default='mailing.contact',
        required=True
    )
    mailing_model_id = fields.Many2one(
        'ir.model',
        string='Recipients Model',
        domain=[('model', 'in', MASS_MAILING_BUSINESS_MODELS)],
        default=lambda self: self.env.ref('mass_mailing.model_mailing_list').id
    )
    mailing_model_name = fields.Char(
        related='mailing_model_id.model',
        string='Recipients Model Name',
        readonly=True,
        related_sudo=True
    )
    mailing_domain = fields.Char(string='Domain', default=[])

    contact_list_ids = fields.Many2many(
        'mailing.list',
        'mass_utm_campaign_list_rel',
        string='Mailing Lists'
    )

    @api.depends('mailing_activities_ids')
    def _compute_mailing_activities_count(self):
        for campaign in self:
            campaign.mailing_activities_count = len(campaign.mailing_activities_ids)

    @api.depends('mailing_activities_ids')
    def _compute_mailing_whatsapp_count(self):
        for campaign in self:
            qty_activities = campaign.mailing_activities_ids.filtered(lambda m: m.mailing_type == 'whatsapp')
            campaign.mailing_whatsapp_count = len(qty_activities)

    @api.depends('mailing_sms_ids')
    def _compute_mailing_sms_count(self):
        for campaign in self:
            qty_activities = campaign.mailing_activities_ids.filtered(lambda m: m.mailing_type == 'sms')
            campaign.mailing_sms_count = len(qty_activities)

    @api.depends('mailing_mail_ids')
    def _compute_mailing_mail_count(self):
        for campaign in self:
            qty_activities = campaign.mailing_activities_ids.filtered(lambda m: m.mailing_type == 'mail')
            campaign.mailing_mail_count = len(qty_activities)

    @api.depends('mailing_model_id')
    def _compute_model(self):
        for record in self:
            record.mailing_model_real = (record.mailing_model_name != 'mailing.list') and record.mailing_model_name or 'mailing.contact'

    def action_create_mass_whatsapp(self):
        action = self.env.ref('mass_mailing.action_create_mass_mailings_from_campaign').read()[0]
        action['context'] = {
            'default_campaign_id': self.id,
            'default_mailing_type': 'whatsapp',
            'search_default_assigned_to_me': 1,
            'search_default_campaign_id': self.id,
            'default_user_id': self.env.user.id,
            'mailing_sms': True,
        }
        return action

    def action_redirect_to_mailing_whatsapp(self):
        action = self.env.ref('mass_mailing.action_view_mass_mailings_from_campaign').read()[0]
        action['context'] = {
            'default_campaign_id': self.id,
            'default_mailing_type': 'whatsapp',
            'search_default_assigned_to_me': 1,
            'search_default_campaign_id': self.id,
            'default_user_id': self.env.user.id,
            'mailing_sms': True,
        }
        action['domain'] = [('mailing_type', '=', 'whatsapp')]
        return action

    def prepare_action_wizard_mailing(self, type):

        context = {
            'default_mailing_type': type,
            'search_default_assigned_to_me': 1,
            'search_default_campaign_id': self.id,
            'default_user_id': self.env.user.id,
            'mailing_sms': True,
            'default_campaign_id': self.id,
        }
        if type == 'whatsapp':
            name = f"New Activity using {type.capitalize()}"
            view_id = self.env.ref('mass_mailing_base.mailing_mailing_view_form_whatsapp').id
        elif type == 'sms':
            name = f"New Activity using {type.upper()}"
            view_id = self.env.ref('mass_mailing_sms.mailing_mailing_view_form_sms').id
        elif type == 'mail':
            name = "New Activity using E-mail"
            view_id = self.env.ref('mass_mailing.view_mail_mass_mailing_form').id
            context.pop('mailing_sms')
        else:
            view_id = False

        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mailing.mailing',
            'view_id': view_id,
            'target': 'new',
            'context': context
        }

    def action_wizard_mailing_whatsapp(self):
        return self.prepare_action_wizard_mailing('whatsapp')

    def action_wizard_mailing_sms(self):
        return self.prepare_action_wizard_mailing('sms')

    def action_wizard_mailing_mail(self):
        return self.prepare_action_wizard_mailing('mail')

    def action_start_campaign(self):
        pass

    def action_schedule_campaign(self):
        pass

    def action_stop_campaign(self):
        pass
