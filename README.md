# Odoo Sent Mail Archive (`sent_archive`) v19.0.2.0.0

Two jobs for Odoo 19 behind an SMTP relay (Mailjet) with a Gmail/Workspace mailbox that Odoo also polls:

1. **Archive BCC** – adds an archive address to the SMTP *envelope* of every outgoing email (never visible in headers).
2. **Loop guard** – drops inbound mail that Odoo itself sent (or that is on a drop list) *before* it is routed, so Odoo can never re-ingest its own notifications and re-notify followers.

## Why the loop guard exists
Mailjet rewrites each `Message-ID`, so Odoo cannot recognise its own mail when it comes back through the polled inbox. Because the `References` header still holds Odoo's `...-openerp-<id>-<model>@...` IDs, the copy is routed to the original record, posted again and sent to the followers again. The guard stops this at the door by checking the `From` address.

## System parameters (Settings → Technical → System Parameters)
| Key | Value | Notes |
|---|---|---|
| `sent_archive.bcc` | `joinwsp+odoosent@example.com` | Archive address. Empty = no BCC. |
| `sent_archive.own_senders` | `joinwsp+notifications@example.com` | **Set this.** Comma-separated addresses Odoo sends from. Inbound mail From any of them is dropped. |
| `sent_archive.drop_sender_domains` | `instagram.com,signupgenius.com` | Optional. Inbound mail from these domains (and subdomains) is dropped. |
| `sent_archive.drop_bulk` | `1` | Optional, off by default. Drops mail with `List-Unsubscribe`, `Precedence: bulk/list/junk` or `Auto-Submitted`. Check that your website contact-form mail does not carry those headers first. |

Own addresses are also detected automatically from `mail.default.from` and the alias domain (default-from, bounce, catchall) and from the archive address.

## Log lines
- `sent_archive: envelope recipients now [...]` – BCC added.
- `sent_archive: dropped inbound mail, not processed (...)` – guard fired. The reason is in the brackets.

## Recommended hardening outside this module
- Set the recruiter user's *Notification* preference to **Handle in Odoo** so Odoo does not email the polled mailbox.
- Gmail filter: `from:joinwsp+notifications@example.com` → skip inbox, mark as read (Odoo only fetches unread mail).
- Gmail filter on the archive copy: `deliveredto:joinwsp+odoosent@example.com`.
- Untick *Keep Original* on the incoming mail server.

## Compatibility
Hooks `ir.mail_server._prepare_email_message__` (renamed between 18 and 19) and `mail.thread.message_process`. Re-check both on major upgrades. The guard fails open: if it errors, mail is processed normally.

License: LGPL-3
