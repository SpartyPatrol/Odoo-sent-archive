import copy
import logging
from email.utils import make_msgid

from odoo import api, models

_logger = logging.getLogger(__name__)


class IrMailServer(models.Model):
    _inherit = 'ir.mail_server'

    @api.model
    def send_email(self, message, *args, **kwargs):
        archive = self.env['ir.config_parameter'].sudo().get_param('sent_archive.bcc')
        archive_msg = None
        if archive and not self.env.context.get('sent_archive_skip'):
            try:
                # Clone BEFORE core mutates the original
                archive_msg = copy.deepcopy(message)
                for header in ('To', 'Cc', 'Bcc', 'X-Forge-To',
                               'X-Msg-To-Add', 'Message-Id'):
                    del archive_msg[header]  # no error if missing
                archive_msg['To'] = archive
                archive_msg['Message-Id'] = make_msgid(
                    idstring='sent-archive', domain=archive.split('@')[-1])
            except Exception:
                _logger.exception("sent_archive: could not build archive copy")
                archive_msg = None

        # Send the real email first, exactly as before
        result = super().send_email(message, *args, **kwargs)

        if archive_msg is not None:
            try:
                self.with_context(sent_archive_skip=True).send_email(
                    archive_msg, *args, **kwargs)
                _logger.info("sent_archive: archive copy sent to %s", archive)
            except Exception:
                # Never let an archive failure break the real email
                _logger.exception("sent_archive: archive copy failed")
        return result
