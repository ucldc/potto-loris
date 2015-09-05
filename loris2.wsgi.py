#!/usr/bin/env python
# -*- coding: utf-8 -*-
from decimal import getcontext
from os.path import join
import logging
import sys
import os
import platform
from werkzeug.wrappers import Response
from werkzeug.exceptions import InternalServerError

''' subclass loris application for AWS S3 and Elastic Beanstalk '''

getcontext().prec = 25  # Decimal precision. This should be plenty.

DIR = os.path.dirname(os.path.realpath(__file__))

sys.path.append(join(DIR, 'loris'))
import loris
import loris.webapp

loris.webapp.logger = logging.getLogger('webapp')

application = loris.webapp.Loris(
    {
        'loris.Loris': {
            'tmp_dp': join(DIR, 'tmp'),
            'www_dp': join(DIR, 'loris', 'www'),
            'enable_caching': True,
            'redirect_canonical_image_request': False,
            'redirect_id_slash_to_info': True
        },
        'logging': {
            'log_to': 'file',
            'log_level': 'ERROR',
            'log_dir': join(DIR, 'log'),
            'max_size': 5242880,
            'max_backups': 5,
            'format': '%(asctime)s (%(name)s) [%(levelname)s]: %(message)s'
        },
        'resolver': {
            'impl': 's3resolver.S3Resolver',
            'cache_root': join(DIR, 'cache'),
            'source_root': os.getenv('SOURCE_ROOT'),
            'source_region': os.getenv('SOURCE_REGION'),
        },
        'img.ImageCache': {
            'cache_dp': join(DIR, 'cache-loris2'),
            'cache_links': join(DIR, 'cache-links')
        },
        'img_info.InfoCache': {
            'cache_dp': join(DIR, 'cache-loris2'),
        },
        'transforms': {
            'dither_bitonal_images': False,
            'target_formats': ['jpg', 'png', 'gif', 'webp'],
            'jpg': {'impl': 'JPG_Transformer'},
            'tif': {'impl': 'TIF_Transformer'},
            'jp2': {
                'impl': 'KakaduJP2Transformer',
                'tmp_dp': join(DIR, 'tmp'),
                'kdu_expand': join(DIR, 'loris/bin', platform.system(), 'x86_64/kdu_expand'),
                'kdu_libs': join(DIR, 'loris/lib/Linux/x86_64/libkdu_v74R.so'),
                'num_threads': '4',
                'mkfifo': '/usr/bin/mkfifo',
                'map_profile_to_srgb': False,
                'srgb_profile_fp': '/usr/share/color/icc/colord/sRGB.icc'
            }
        }
    }
)


def status_check():
    ''' do some sort of health check here '''
    return True

# set up for monkeypatch
stock_route = application.route


def new_route(request):
    ''' monkeypatch the url router for health check '''
    ____, ident, ____, ____ = application._dissect_uri(request)
    if ident == '':
        # "home" page doubles as health check
        if status_check():
            # looks good
            return Response('potto-loris status okay',
                            content_type='text/plain')
        else:
            # looks like things ain't working
            return InternalServerError(
                response=Response('500 potto-loris health check failed',
                                  content_type='text/plain')
            )
    # pass control back to loris router
    return stock_route(request)

# complete the monkey patch
application.route = new_route


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8989, application)
    print "Serving on port 8989..."
    httpd.serve_forever()

"""
Copyright © 2015, Regents of the University of California
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
- Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
- Neither the name of the University of California nor the names of its
  contributors may be used to endorse or promote products derived from this
  software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""
