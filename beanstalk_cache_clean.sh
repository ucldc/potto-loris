#!/usr/bin/env bash
# beanstalk_cache_clean.sh
# Cron script for maintaining the loris cache size.
#
# CAUTION - This script deletes files. Be careful where you point it!
#

if [[ -n "$DEBUG" ]]; then 
  set -x
fi

set -o pipefail  # trace ERR through pipes
set -o errtrace  # trace ERR through 'time command' and other functions
set -o nounset   ## set -u : exit the script if you try to use an uninitialised variable
set -o errexit   ## set -e : exit the script if any statement returns a non-true return value

# play nice
renice -n 10 $$ >& /dev/null
ionice -c3 -p$$

# On this scheme for putting this in beanstalk, all of the 
# loris work files end up in `APP_WORK` directory

LOG="$APP_WORK/log/cache_clean.$(date +"%F")"
touch $LOG  # otherwise, empty log directory might get deleted below

current_usage () {
  pcent=$(df --output=pcent $APP_WORK | tail -1)
  echo ${pcent%\%}
}

REDUCE_TO=85  # percent(%) used on $APP_WORK application workspace
usage=$(current_usage)

if [ $usage -lt $REDUCE_TO ]
  then
    echo "$(date +[%c]) at $usage% target $REDUCE_TO% (no deletes required)." >> $LOG
    exit
fi

delete_total=0
# expect SIGPIPE
set +o pipefail
oldest_file=$(find $APP_WORK -type f -printf '%As\n' | sort | head -n 1)  # http://superuser.com/a/552606
set -o pipefail

max_age=$(( ( $(date +"%s") - oldest_file) / 86400 ))  # http://unix.stackexchange.com/a/24636/40198
start_size=$usage

APP_WORK=/home/wsgi

while [ "$usage" -gt "$REDUCE_TO" ] && [ "$max_age" -ge 1 ]
  do
    # files. loop (instead of -delete) so that we can keep count
    for f in $(find $APP_WORK -type f -atime +$max_age)
      do
        rm $f
        let delete_total+=1
    done

    # empty  directories
    find $APP_WORK -mindepth 2 -type d -empty -delete

    # broken symlinks
    # When the -L option is in effect, the -type predicate will
    # always match against the type of the file that a symbolic link
    # points to rather than the link itself (unless the symbolic  link
    # is broken).
    # should the links be deleted first in the above find?
    find -L $APP_WORK -mindepth 2 -type l -delete

    # command will exit 1 when max_age goes to zero
    # x=1; let x-=1; echo $? ==> 1
    set +e; let max_age-=1; set -e
    usage=$(current_usage)
done

echo "$(date +[%c]) Deleted $delete_total files to get cache from $start_size% to $usage%." >> $LOG

# derived from https://github.com/loris-imageserver/loris/blob/c929b5a10db78ceda777c6455d64e157494bf46a/bin/loris-http_cache_clean.sh
# loris-http_cache_clean.sh written by Jon Stroop and edited by Gunter Vasold

