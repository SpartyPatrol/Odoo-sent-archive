# Odoo Sent Mail Archive (`sent_archive`)

A tiny Odoo 19 module that silently sends a blind copy of **every outgoing email** to an archive address of your choice.

It was built for a setup where Odoo sends mail through an SMTP relay (Mailjet) on behalf of a Gmail / Google Workspace address. Because the relay delivers the mail directly, no copy lands in the Gmail **Sent** folder. This module fixes that by adding an archive recipient to every message.

## How it works

Odoo 19 prepares each outgoing message in `ir.mail_server._prepare_email_message__()`, which returns `(smtp_from, smtp_to_list, message)`. This module wraps that method and appends the archive address to `smtp_to_list` (the SMTP *envelope* recipients).

Because only the envelope is changed:

- The archive address **never appears in any email header**, so real recipients cannot see it, and "Reply All" cannot reach it.
- The message the recipient receives is unchanged.
- If anything goes wrong while adding the address, the error is logged and the original email is still sent normally.

## Requirements

- Odoo Community or Enterprise **19.0**
- Depends only on the `mail` module
- An SMTP provider that honours envelope recipients (Mailjet does)

## Installation

1. Add this repository to your Odoo hosting. On CloudPepper: instance **Details → Addons → add from GitHub**, select this repo, select `sent_archive`, and click **Add module**.
2. In Odoo, enable developer mode, go to **Apps → Update Apps List**, search for **Sent Mail Archive**, and install it.

## Configuration

Create one system parameter under **Settings → Technical → System Parameters**:

| Key | Value |
|---|---|
| `sent_archive.bcc` | `your-address+odoosent@example.com` |

If the parameter is empty or missing, the module does nothing.

Gmail and Google Workspace deliver `name+anything@domain` to `name@domain`, so a plus-address lets you keep the archive separate without a second account.

## Recommended Gmail filter

The archive copy arrives in your normal mailbox, so create a filter to keep it tidy and, if Odoo reads your inbox (for example the Recruiting app creating contacts from unread mail), to prevent a feedback loop.

In Gmail, open the search options and put this in **Has the words**:

```
deliveredto:your-address+odoosent@example.com
```

Then choose these actions:

- Skip the Inbox (Archive it)
- Mark as read
- Apply the label `Odoo Sent`
- Never send it to Spam

Use `deliveredto:` rather than `to:`. The archive address is only in the SMTP envelope, so it is never in the `To` header and a `to:` filter will not match.

## Why no loop occurs

1. The filter marks the copy as read and skips the inbox on delivery.
2. Odoo's incoming mail fetch only reads unread mail, so it never sees the copy.
3. The copy is addressed to the plus-address, not to any Odoo alias.

## Troubleshooting

- **Look for the log line.** Each send logs `sent_archive: envelope recipients now [...]`. If the archive address is listed there, Odoo did its part; check your SMTP provider's activity log.
- **Nothing in Gmail?** Search `in:anywhere deliveredto:your-address+odoosent@example.com` to include Spam and Trash.
- **No log line at all?** The module may not be installed, the system parameter may be missing or misspelled, or a future Odoo version may have renamed `_prepare_email_message__`.
- **One copy per recipient.** Odoo often sends one message per recipient, so you may receive one archive copy for each.
- **Provider volume.** Each archive recipient may count toward your SMTP provider's sending limits.
- **Not seeing sent mail under Settings → Technical → Emails?** Odoo deletes successfully sent `mail.mail` records. Check the record's chatter instead.

## Compatibility note

This module hooks a private, double-underscore method that Odoo renamed between 18 and 19. It may need adjusting for future major versions.

## Credits

Designed and debugged by the repository owner with code and documentation written with the assistance of **Claude** (Anthropic). The v19 recipient-handling approach was worked out through real-world testing against server logs.

## License

LGPL-3
