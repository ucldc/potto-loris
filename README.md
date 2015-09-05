# Potto

Alternative deployment for [loris IIF image server](https://github.com/loris-imageserver/loris),
designed to run in [Amazon Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk/) 
and serve images stored in Amazon Simple Storage Service (S3)

The Loris `setup.py` is more like an application installer rather than something that should be run by `pip`.  (It wants specific users on the system to exist, for example.).

To deploy to a beanstalk python app server, this uses `git` to grab the `#development` branch of the offical Loris, and then it subclasses (to override configuration style and to provide an S3 resolver) and monkey patches (to provide a stub for a healh check URL) loris.  `./deploy-version.sh` creates a `.zip` file of the application and deploys it to a beanstalk environment.

## Configuration

See [Configuring Python Containers with Elastic Beanstalk](http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-container.html)

Set these in the environment.

`SOURCE_ROOT` s3:// URL to s3 bucket and prefix where jp2s are stored

`SOURCE_REGION` region in Amazon (you should usually run in the same
region as the bucket)

## deploy script

`./deploy-version.sh` will need to be customized to your app (setting correct application etc.).

## pictures of animals

### We are Potto
<img width="511" alt="potto" src="https://cloud.githubusercontent.com/assets/227374/9700690/02418f4a-53c1-11e5-9e6b-1db47fd8caa3.png">

[potto picture source](https://commons.wikimedia.org/wiki/File:PottoCincyZoo.jpg) CC BY 3.0 [Ltshears](https://commons.wikimedia.org/wiki/User:Ltshears)

### Our cousin Loris
<img width="261" alt="loris" src="https://cloud.githubusercontent.com/assets/227374/9700689/fcfebb02-53c0-11e5-8ab6-c96fb98ba126.png">

[loris picture source](https://commons.wikimedia.org/wiki/File:Smit.Faces_of_Lorises.jpg)

## License

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
