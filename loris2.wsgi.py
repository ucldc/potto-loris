from loris.webapp import create_app, Loris
from decimal import getcontext

import loris

import logging
getcontext().prec = 25 # Decimal precision. This should be plenty.

loris.webapp.logger = logging.getLogger('webapp')

application = loris.webapp.Loris(
    {
        'loris.Loris': {
            'tmp_dp': '/tmp/loris2',
            'www_dp': '/var/www/loris2',
            'enable_caching': True,
            'redirect_canonical_image_request': False,
            'redirect_id_slash_to_info': True
        },
        'logging': {
            'log_to': 'file',
            'log_level': 'DEBUG',
            'log_dir': '/var/log/loris2',
            'max_size': 5242880,
            'max_backups': 5,
            'format': '%(asctime)s (%(name)s) [%(levelname)s]: %(message)s'
        },
        'resolver': {
            'impl': 's3resolver.S3Resolver',
            'cache_root': '/usr/local/share/images/loris',
            'source_root': 'ucldc-nuxeo-ref-images',
            'src_img_root': '/usr/local/share/images'
        },
        'img.ImageCache': {
            'cache_dp': '/var/cache/loris2',
            'cache_links': 'var/cache/loris/links'
        },
        'img_info.InfoCache': {
            'cache_dp': '/var/cache/loris2'
        },
        'transforms': {
            'dither_bitonal_images': False,
            'target_formats': ['jpg', 'png', 'gif', 'webp'],
            'jpg': {'impl': 'JPG_Transformer'},
            'tif': {'impl': 'TIF_Transformer'},
            'jp2': {
                'impl': 'KakaduJP2Transformer',
                'tmp_dp': '/tmp/loris2',
                'kdu_expand': '/usr/local/bin/kdu_expand',
                'kdu_libs': '/usr/local/lib/libkdu.so',
                'num_threads': '4',
                'mkfifo': '/usr/bin/mkfifo',
                'map_profile_to_srgb': False,
                'srgb_profile_fp': '/usr/share/color/icc/colord/sRGB.icc'
            }
        }
    }
)



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
