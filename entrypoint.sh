#!/bin/bash

# How many volume mounts at location /opt/mounts
[[ -z "${NO_OF_MOUNTS}" ]] && NumberOfMounts="3" || NumberOfMounts="${NO_FILES}"

# Total size of data inside each mount 
[[ -z "${SIZE_EACH_MOUNT}" ]] && FileSize="1000Mi" || FileSize="${SIZE_EACH_MOUNT}"

# Max files
[[ -z "${MAX_FILES}" ]] && MaxFiles="1000" || MaxFiles="${MAX_FILES}"

# Min files
[[ -z "${MIN_FILES}" ]] && MinFiles="10" || MinFiles="${MIN_FILES}"

echo "Generating sample data..."
for i in $( seq 1 $NumberOfMounts )
do
    /usr/local/bin/file-generator --max-files "${MaxFiles}" --min-files "${MinFiles}" --size "${FileSize}" --dest-dir "/opt/mounts/mnt${i}"
done
