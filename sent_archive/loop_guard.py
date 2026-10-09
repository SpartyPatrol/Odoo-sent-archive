"""Pure-Python helpers for the inbound mail-loop guard.

No Odoo imports here on purpose, so the logic can be unit-tested on its own.
"""
import re
from email import policy
from email.parser import BytesHeaderParser
from email.utils import getaddresses, parseaddr

BULK_PRECEDENCE = {'bulk', 'list', 'junk'}
BOUNCE_LOCALPARTS = {'mailer-daemon', 'postmaster'}


def normalize(address):
    """'Jeff <A@B.com>' -> 'a@b.com' ('' if nothing parseable)."""
    return parseaddr(str(address or ''))[1].strip().lower()


def split_list(value):
    """'a@x.com, b@y.com;c' -> ['a@x.com', 'b@y.com', 'c'] (lower-cased)."""
    return [p.lower() for p in re.split(r'[,\s;]+', value or '') if p]


def _domain_matches(domain, patterns):
    domain = domain.lower()
    for pat in patterns:
        pat = pat.lstrip('@*.').lower()
        if pat and (domain == pat or domain.endswith('.' + pat)):
            return pat
    return None


def inspect(raw, own_senders=(), drop_domains=(), drop_bulk=False):
    """Return a short reason string if the inbound message must be dropped,
    otherwise None. Only the headers are parsed (bodies can be many MB)."""
    if isinstance(raw, str):
        raw = raw.encode('utf-8', 'replace')
    msg = BytesHeaderParser(policy=policy.default).parsebytes(raw)

    senders = [
        a.strip().lower()
        for _, a in getaddresses([str(h) for h in msg.get_all('From', [])])
        if a
    ]
    own = {normalize(o) for o in own_senders if o}

    # 1. Mail that Odoo itself sent (the loop): the From address is ours.
    for sender in senders:
        if sender in own:
            return "sent by our own address %s" % sender

    # 2. Explicit sender-domain drop list (Instagram, SignUpGenius, ...).
    for sender in senders:
        domain = sender.rpartition('@')[2]
        hit = _domain_matches(domain, drop_domains)
        if hit:
            return "sender domain %s is on the drop list (%s)" % (domain, hit)

    # 3. Optional: bulk / list / auto-generated mail. Off by default.
    if drop_bulk:
        is_bounce = (
            any(s.partition('@')[0] in BOUNCE_LOCALPARTS for s in senders)
            or msg.get_content_type() == 'multipart/report'
        )
        if not is_bounce:
            precedence = str(msg.get('Precedence', '')).strip().lower()
            auto = str(msg.get('Auto-Submitted', 'no')).strip().lower()
            if (
                precedence in BULK_PRECEDENCE
                or msg.get('List-Unsubscribe') is not None
                or auto not in ('', 'no')
            ):
                return "bulk/automatic mail (Precedence/List-Unsubscribe/Auto-Submitted)"
    return None
