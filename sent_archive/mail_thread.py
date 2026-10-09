import logging

from odoo import api, models

from . import loop_guard

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def message_process(self, model, message, *args, **kwargs):
        """Entry point used by the incoming mail server (fetchmail).

        Drop mail that Odoo itself sent (or that is on the configured drop
        list) BEFORE it is routed, so it can never be re-posted on a record
        and re-notified to followers. Any failure in the guard lets the mail
        through unchanged: the guard must never block real applicant mail.
        """
        reason = self._sent_archive_inbound_drop_reason(message)
        if reason:
            _logger.warning(
                "sent_archive: dropped inbound mail, not processed (%s)", reason
            )
            return False
        return super().message_process(model, message, *args, **kwargs)

    @api.model
    def _sent_archive_inbound_drop_reason(self, message):
        try:
            icp = self.env['ir.config_parameter'].sudo()
            own = set(loop_guard.split_list(icp.get_param('sent_archive.own_senders')))
            own.add(loop_guard.normalize(icp.get_param('sent_archive.bcc')))

            default_from = (icp.get_param('mail.default.from') or '').strip()
            if '@' in default_from:
                own.add(loop_guard.normalize(default_from))

            # Alias domain addresses (notifications / bounce / catchall).
            if 'mail.alias.domain' in self.env:
                for dom in self.env['mail.alias.domain'].sudo().search([]):
                    for fname in ('default_from_email', 'bounce_email', 'catchall_email'):
                        if fname in dom._fields and dom[fname]:
                            own.add(loop_guard.normalize(dom[fname]))
                    if default_from and '@' not in default_from and dom.name:
                        own.add("%s@%s" % (default_from.lower(), dom.name.lower()))
            own.discard('')

            return loop_guard.inspect(
                message,
                own_senders=own,
                drop_domains=loop_guard.split_list(
                    icp.get_param('sent_archive.drop_sender_domains')
                ),
                drop_bulk=(icp.get_param('sent_archive.drop_bulk') or '').strip().lower()
                in ('1', 'true', 'yes'),
            )
        except Exception:
            _logger.exception("sent_archive: inbound guard failed; passing mail through")
            return None
