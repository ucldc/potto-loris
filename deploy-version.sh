#!/bin/env bash
if [[ -n "$DEBUG" ]]; then 
  set -x
fi

set -o pipefail  # trace ERR through pipes
set -o errtrace  # trace ERR through 'time command' and other functions
set -o nounset   ## set -u : exit the script if you try to use an uninitialised variable
set -o errexit   ## set -e : exit the script if any statement returns a non-true return value

cd "$( dirname "${BASH_SOURCE[0]}" )" # http://stackoverflow.com/questions/59895

usage(){
    ./beanstalk-describe.sh
    echo "deploy-version.sh version-label environment-name"
    exit 1
}

if [ $# -ne 2 ];
  then
    usage
fi

set -u

ZIP=potto-loris-ebs.zip
DIR=potto-loris-beanstalk
BUCKET=xtf.dsc.cdlib.org
REGION=us-west-2
APPNAME=potto-loris

if ! [[ -d "loris" ]]; then
  git clone https://github.com/loris-imageserver/loris.git --depth=1
fi

# package app and upload
zip $ZIP -r .ebextensions/ \
  loris/*.txt \
  loris/loris/*.py \
  loris/bin/ \
  loris/lib/ \
  beanstalk_cache_clean.sh \
  crontab \
  loris2.wsgi.py \
  requirements.txt \
  s3resolver.py
aws s3 cp $ZIP s3://$BUCKET/$DIR/$ZIP
aws elasticbeanstalk create-application-version \
  --application-name $APPNAME \
  --region $REGION \
  --source-bundle S3Bucket=$BUCKET,S3Key=$DIR/$ZIP \
  --version-label "$1"

# make sure environment actually exists
env_exists=$(aws elasticbeanstalk describe-environments \
  --environment-name "$2" \
  --region $REGION \
  | jq '.Environments | length')

if [[ env_exists -ne 1 ]]
  then
    echo "environment $2 does not exist"
    usage    
fi

# deploy app to a running environment
aws elasticbeanstalk update-environment \
  --environment-name "$2" \
  --region $REGION \
  --version-label "$1"

# Copyright (c) 2015, Regents of the University of California
# 
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# - Neither the name of the University of California nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
