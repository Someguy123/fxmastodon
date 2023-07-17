#!/usr/bin/env python3
"""

Copyright::

 +===================================================+
 |                 © 2023 Someguy123                 |
 |               https://github.com/Someguy123       |
 +===================================================+
 |                                                   |
 |        Fix Mastodon Embeds (FxMastodon)           |
 |        License: MIT X/11                          |
 |                                                   |
 |        https://github.com/Someguy123/fxmastodon   |
 |                                                   |
 |        Core Developer(s):                         |
 |                                                   |
 |          (+)  Chris (@someguy123)                 |
 |                                                   |
 +===================================================+

"""
from flask import Flask, render_template, jsonify, request, session, abort, redirect, flash
from privex.loghelper import LogHelper
from os import getenv as env
from privex.helpers import env_bool
import logging
import requests
import lxml.html

DEBUG = env_bool('DEBUG', False)

_lh = LogHelper(__name__, handler_level=logging.DEBUG if DEBUG else logging.WARN)
_lh.add_console_handler()
log = _lh.get_logger()

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def handle_embed(path: str):
    p = path.strip('/').split('/')
    if len(p) < 2:
        return "Invalid Mastodon URL! Must be formatted like: mastodon.social/@username/1234567 or mastodon.social/123456 or @username@mastodon.social/123456"
    if len(p) == 2:
        dom, mstatus = p
        if '@' in dom:
            dom = dom.split('@')[-1]
    else:
        dom, uname, mstatus = p[:3]

    api_url = f"https://{dom}/api/v1/statuses/{mstatus}"
    r = requests.get(api_url)
    r.raise_for_status()
    res = r.json()
    has_media = len(res.get('media_attachments', [])) > 0
    content = lxml.html.fromstring(res['content']).text_content()
    favourites_count = res.get('favourites_count'),
    reblogs_count = res.get('reblogs_count'),
    replies_count = res.get('replies_count'),
    data = dict(
        full_url=res['uri'],
        username=f"@{res['account']['username']}@{dom}",
        display_name=res['account']['display_name'],
        img_url="" if not has_media else res['media_attachments'][0]['url'],
        img_width='0' if not has_media else res['media_attachments'][0]['meta']['original']['width'],
        img_height='0' if not has_media else res['media_attachments'][0]['meta']['original']['height'],
        post_contents=f"{content} \n\n 💖 {favourites_count} ↩️ {reblogs_count} 💬{replies_count}",
    )

    if has_media and res['media_attachments'][0]['type'] in ['gifv', 'gif', 'video']:
        return render_template('video.html', **data)
    return render_template('image.html', **data)


if __name__ == '__main__':
    app.run(debug=DEBUG)
