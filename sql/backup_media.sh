#!/bin/bash
#Purpose = Backup of Important Data
#Created on 17-1-2012
#Author = Hafiz Haider
#Version 1.0
#START
TIME=`date +%b-%d-%y`            # This Command will add date in Backup File Name.
FILENAME=backup_media-$TIME.tar.gz    # Here i define Backup file name format.
SRCDIR=/home/workspace/licita/media/                    # Location of Important Data Directory (Source of backup).
DESDIR=/home/licita_bkp/            # Destination of backup file.
tar -cpzf $DESDIR/$FILENAME $SRCDIR
pg_dump --dbname=postgresql://walkyso:licitaeasy@127.0.0.1:5432/licita | gzip > /home/licita_bkp/$(date +%Y-%m-%d).psql.gz
#END
