import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class IrMailServer(models.Model):
    _inherit = 'ir.mail_server'

    @api.model
    def send_email(self, message, *args, **kwargs):
        bcc = self.env['ir.config_parameter'].sudo().get_param('sent_archive.bcc')
        _logger.info(
            "sent_archive: send_email called, bcc param=%r, existing Bcc=%r, To=%r",
            bcc, message['Bcc'], message['To'],
        )
        if bcc:
            existing = message['Bcc']
            if not existing:
                message['Bcc'] = bcc
            elif bcc not in existing:
                message.replace_header('Bcc', f'{existing}, {bcc}')
        return super().send_email(message, *args, **kwargs)
