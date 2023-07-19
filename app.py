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
from privex.helpers import env_bool, empty
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
    api_url = "unknown"
    try:
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
        try:
            r = requests.get(api_url)
            r.raise_for_status()
            res = r.json()
        except Exception as e:
            log.error("ERROR while fetching API URL %s - type: %s | message: %s", api_url, type(e), str(e))
            return render_template(
                'error.html',
                status_code=502,
                reason=f"Failed to query API for instance {dom} - instance broken/down",
                reason_full=f"An error occurred while querying the instance API at {api_url} - most likely either the remote instance is "
                            f"broken, down, not compatible with FxMastodon, or has blocked FxMastodon's server. "
                            f"An exception of type {type(e)} has occurred, full details of this can be found in the logs by the administrator",
            ), 502

        has_media = len(res.get('media_attachments', [])) > 0
        content = res.get('content', '')
        content = '' if empty(content) else content
        if not empty(content):
            content = lxml.html.fromstring(content).text_content()

        data = dict(
            full_url=res['uri'],
            username=f"@{res['account']['username']}@{dom}",
            display_name=res['account']['display_name'],
            img_url="" if not has_media else res['media_attachments'][0]['url'],
            img_width='0' if not has_media else res['media_attachments'][0]['meta']['original']['width'],
            img_height='0' if not has_media else res['media_attachments'][0]['meta']['original']['height'],
            post_contents=content,
        )

        if has_media and res['media_attachments'][0]['type'] in ['gifv', 'gif', 'video']:
            return render_template('video.html', **data)
        return render_template('image.html', **data)
    except Exception as e:
        log.exception("An exception has occurred during handle_embed() (api_url: %s) - exception: %s | message: %s", api_url, type(e), str(e))
        return render_template(
            'error.html',
            status_code=500,
            reason="UNKNOWN APP ERROR",
            reason_full=f"An exception of type {type(e)} has occurred, full details of this can be found in the logs by the administrator",
        ), 500


if __name__ == '__main__':
    app.run(debug=DEBUG)

