from odoo import api, models


class IrMailServer(models.Model):
    _inherit = 'ir.mail_server'

    @api.model
    def send_email(self, message, *args, **kwargs):
        bcc = self.env['ir.config_parameter'].sudo().get_param('sent_archive.bcc')
        if bcc:
            existing = message['Bcc']
            if not existing:
                message['Bcc'] = bcc
            elif bcc not in existing:
                message.replace_header('Bcc', f'{existing}, {bcc}')
        return super().send_email(message, *args, **kwargs)
