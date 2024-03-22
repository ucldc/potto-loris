# -*- coding: utf-8 -*-
import os
from loris.resolver import _AbstractResolver
from loris.loris_exception import ResolverException
from urllib.parse import unquote, unquote_plus
import urllib.parse
from os.path import join, exists
import boto3
import botocore
import logging
from loris.img_info import ImageInfo

logger = logging.getLogger('webapp')


class S3Resolver(_AbstractResolver):
    '''
    Resolver for images coming from AWS S3 bucket.
    The config dictionary MUST contain
     * `cache_root`, which is the absolute path to the directory where source images
        should be cached.
     * `source_root`, the s3 root for source images.
    '''
    def __init__(self, config):
        ''' setup object and validate '''
        super(S3Resolver, self).__init__(config)
        self.cache_root = self.config.get('cache_root')
        source_root = self.config.get('source_root')
        assert source_root, 'please set SOURCE_ROOT in environment'
        scheme, self.s3bucket, self.prefix, ___, ___ = urllib.parse.urlsplit(
            source_root
        )
        self.prefix = self.prefix.strip("/")
        assert scheme == 's3', '{0} not an s3 url'.format(source_root)


    def is_resolvable(self, ident):
        '''does this file even exist?'''
        local_fp = join(self.cache_root, unquote(ident))
        if exists(local_fp):
            return True
        else:
            # check that we can get to this object on S3
            #
            bucketname = self.s3bucket
            key = unquote_plus(ident)
            if key.startswith("iiif/"):
                keyname = f"{self.prefix}/{key[5:]}"
            else:
                keyname = f"{self.prefix}/{key}"

            s3 = boto3.client('s3')
            response = s3.list_objects_v2(
                Bucket=bucketname,
                Prefix=keyname,
            )
            for obj in response.get('Contents', []):
                if obj['Key'] == keyname:
                    return obj['Size']


    #def resolve(self, ident):
    def resolve(self, app, ident, base_uri):
        local_fp = join(self.cache_root, unquote(ident))
        logger.debug('local_fp: %s' % (local_fp))
 
        if exists(local_fp):
            format_ = 'jp2' # FIXME
            logger.debug('src image from local disk: %s' % (local_fp,))
        else:
            # create subdirectory
            local_dir_parts = local_fp.split('/')[:-1]
            local_dir = '/'.join(local_dir_parts)
            logger.debug(f"Creating local_dir: {local_dir}")
            try:
                os.makedirs(local_dir, exist_ok=True)
            except OSError as exc:
                raise ConfigError("Error creating local_dir %s: %r" % (local_dir, exc))

            # get image from S3
            bucketname = self.s3bucket
            key = unquote_plus(ident)
            if key.startswith("iiif/"):
                keyname = f"{self.prefix}/{key[5:]}"
            else:
                keyname = f"{self.prefix}/{key}"
            logger.debug('Getting img from AWS S3. bucketname, keyname: %s, %s' % (bucketname, keyname))    

            s3 = boto3.client('s3')
            try:
                s3.download_file(bucketname, keyname, local_fp)
            except botocore.exceptions.ClientError as e:
                message = 'Source image not found for identifier: %s.' % (ident,)
                logger.warn(e, message)
                raise ResolverException(404, message)
            format_ = 'jp2' #FIXME
            logger.debug('src format %s' % (format,))

        return ImageInfo(app=app, src_img_fp=local_fp, src_format=format_, auth_rules={})

"""
Copyright © 2020, Regents of the University of California
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
