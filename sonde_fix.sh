#!/usr/bin/bash


<< 'MULTILINE-COMMENT'

When we download sonde data for Sydney
data is for either 0200 or 0300 or 0500 sonde flights
how do we merge this data files so we keep only data for that has full sonde info
for e.g if 0300 sonde is bigger file then we keep the 0300 for same date and remore/delete the 0200 file
for same date.

This script will loop over all regular files with non-hidden names in the source directory. For each file in source it will construct the corresponding pathname for a file in target directory. If the file in target exists and is a regular file (or a symbolic link to a regular file), the size of the two files are compared. If the file in source is strictly bigger, a short message is outputted.

The pattern source/*(.) will match only non-hidden names of regular files in the source directory. The (.) is a zsh-specific modifier for * that makes it match only regular files -none exist for bash!

The expression "target/${file1##*/}" will expand to a pathname starting with target/ and then containing the value of $file2 with everything before and including the last / removed. This could be changed to "target/$( basename "$file2" )".

This script is based on similar script found here
https://unix.stackexchange.com/questions/496109/compare-files-and-select-bigger-one

Nice BASH tutorial here
https://ryanstutorials.net/bash-scripting-tutorial/bash-script.php

TODO: pass the source and target folders as command line args.

MULTILINE-COMMENT


source=./f160_0200
target=./f160_0300

# run script again after switching folders to delete same but smaller files from other folder 

for file1 in $source/*; do
    file2="$target/${file1##*/}"

    file1_size=`stat -c%s $file1`
    if [ -f "$file2" ] 
    then
        file2_size=`stat -c%s $file2`
    fi

    printf 'Comparing %s with %s\n' "$file1" "$file2"
    printf 'Size %s with %s\n' "$file1_size" "$file2_size"

    
    #printf 'Difference %s\n' $(($file1_size-$file2_size))
    if [ -f "$file2" ] 
    then
        diff=$(($file1_size-$file2_size))
    fi
    #printf 'Difference %s\n' "$diff"

    #if  [ $diff -lt 0 ]
    #if [ $file1_size -lt $file2_size ]
    #if [ `stat -c%s $file1` -lt `stat -c%s $file2` ]
    # check see if file2 exists or not first (file1 will always exist!) 
    if [ -f "$file2" ] &&
       [ "$( stat -c%s "$file1" )" -lt "$( stat -c%s "$file2" )" ]
    then
        echo "$file1 is smaller then $file2 - we will delete $file1"
        #printf '%s is smaller than %s\n' "$file1" "$file2"
        rm -f $file1
    elif  [ "$( stat -c%s "$file2" )" -lt "$( stat -c%s "$file1" )" ]
    then
        echo "$file2 is smaller then $file1 - we will delete $file2"
        #printf '%s is smaller than %s\n' "$file2" "$file1"
        rm -f $file2
    fi
done
