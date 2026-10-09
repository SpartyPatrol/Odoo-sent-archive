#import logging

#from odoo import models

#_logger = logging.getLogger(__name__)


#class IrMailServer(models.Model):
#    _inherit = 'ir.mail_server'

#    def _prepare_email_message__(self, message, *args, **kwargs):
#        result = super()._prepare_email_message__(message, *args, **kwargs)
#        archive = self.env['ir.config_parameter'].sudo().get_param('sent_archive.bcc')
#        if not archive:
#            return result
#        try:
#            smtp_from, smtp_to_list, prepared_message = result
#            if archive.lower() not in [a.lower() for a in smtp_to_list]:
#                smtp_to_list = list(smtp_to_list) + [archive]
#            _logger.info("sent_archive: envelope recipients now %s", smtp_to_list)
#            return smtp_from, smtp_to_list, prepared_message
#        except Exception:
#            # Never block the real email because of the archive
#            _logger.exception("sent_archive: could not add archive recipient")
#            return result
