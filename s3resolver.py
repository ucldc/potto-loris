# -*- coding: utf-8 -*-
from loris.resolver import _AbstractResolver, ResolverException
from urllib import unquote
import urlparse
from os.path import join, exists, isfile
import boto
import logging

logger = logging.getLogger('webapp')


class S3Resolver(_AbstractResolver):
    '''
    Resolver for images coming from AWS S3 bucket.
    The config dictionary MUST contain
     * `cache_root`, which is the absolute path to the directory where source images
        should be cached.
     * `source_root`, the s3 root for source images.
     * `source_region`, the Amazon region of the s3 bucket
    '''
    def __init__(self, config):
        ''' setup object and validate '''
        super(S3Resolver, self).__init__(config)
        self.cache_root = self.config.get('cache_root')
        source_root = self.config.get('source_root')
        self.source_region = self.config.get('source_region')
        assert source_root, 'please set SOURCE_ROOT in environment'
        assert self.source_region, 'please set SOURCE_REGION in environment'
        scheme, self.s3bucket, self.prefix, ___, ___ = urlparse.urlsplit(
            source_root
        )
        assert scheme == 's3', '{0} not an s3 url'.format(source_root)


    def is_resolvable(self, ident):
        '''does this file even exist?'''
        ident = unquote(ident)
        local_fp = join(self.cache_root, ident)
        if exists(local_fp):
            return True
        else:
            # check that we can get to this object on S3
            s3 = boto.connect_s3()

            try:
                bucket = s3.get_bucket(self.s3bucket)
            except boto.exception.S3ResponseError as e:
                logger.error(e)
                return False

            if bucket.get_key(u'{0}{1}'.format(self.prefix, ident)):
                return True
            else:
                logger.debug('AWS key %s does not exist' % (ident))
                return False


    def resolve(self, ident):
        '''get me the file'''
        ident = unquote(ident)
        local_fp = join(self.cache_root, ident)
        logger.debug('local_fp: %s' % (local_fp))
 
        if exists(local_fp):
            format = 'jp2' # FIXME
            logger.debug('src image from local disk: %s' % (local_fp,))
            return (local_fp, format)
        else:
            # get image from S3
            bucketname = self.s3bucket 
            keyname = '{0}{1}'.format(self.prefix, ident)
            logger.debug('Getting img from AWS S3. bucketname, keyname: %s, %s' % (bucketname, keyname))    
            
            s3 = boto.connect_s3()
            bucket = s3.get_bucket(bucketname)
            key = bucket.get_key(keyname)
            try:
                res = key.get_contents_to_filename(local_fp)
            except boto.exception.S3ResponseError as e:
                logger.warn(e)
            format = 'jp2' #FIXME
            logger.debug('src format %s' % (format,))

            return (local_fp, format)

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
