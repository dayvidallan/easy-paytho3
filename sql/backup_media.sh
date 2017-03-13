#!/bin/bash
#Purpose = Backup of Important Data
#Created on 17-1-2012
#Author = Hafiz Haider
#Version 1.0
#START
TIME=`date +%b-%d-%y`            # This Command will add date in Backup File Name.
FILENAME=licita_backup_media-$TIME.tar.gz    # Here i define Backup file name format.
SRCDIR=/home/workspace/licita/media/                    # Location of Important Data Directory (Source of backup).
DESDIR=~/Dropbox/licita_bkp/            # Destination of backup file.
tar -cpzf $DESDIR/$FILENAME $SRCDIR
FILENAME=guamare_backup_media-$TIME.tar.gz    # Here i define Backup file name format.
SRCDIR=/home/workspace/guamare/licita/media/                    # Location of Important Data Directory (Source of backup).
DESDIR=~/Dropbox/licita_bkp/            # Destination of backup file.
tar -cpzf $DESDIR/$FILENAME $SRCDIR
pg_dump --dbname=postgresql://walkyso:licitaeasy@127.0.0.1:5432/licita | gzip > ~/Dropbox/licita_bkp/licita_$(date +%Y-%m-%d).psql.gz
pg_dump --dbname=postgresql://walkyso:licitaeasy@127.0.0.1:5432/guamare | gzip > ~/Dropbox/licita_bkp/guamare_$(date +%Y-%m-%d).psql.gz
#END
