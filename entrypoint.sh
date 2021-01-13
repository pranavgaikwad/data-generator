#!/bin/bash

# Total size of data inside each mount 
[[ -z "${SIZE}" ]] && Size="1000Mi" || Size="${SIZE}"

# Max files
[[ -z "${MAX_FILES}" ]] && MaxFiles="1000" || MaxFiles="${MAX_FILES}"

# Min files
[[ -z "${MIN_FILES}" ]] && MinFiles="10" || MinFiles="${MIN_FILES}"

# Min files
[[ -z "${ROLE}" ]] && Role="generator" || Role="${ROLE}"

# Wiggle Room for file operations
[[ -z "${BUFFER}" ]] && Buffer="10Mi" || Buffer="${BUFFER}"

if [ ${Role} == "generator" ]; then
    echo "Generating sample data..."
    /usr/local/bin/file-generator --max-files "${MaxFiles}" --min-files "${MinFiles}" --size "${Size}" --dest-dir "/opt/mounts/mnt1"
    /usr/bin/sleep infinity
fi

if [ ${Role} == "operations" ]; then
    echo "Running random file operations..."
    /usr/local/bin/file-operations --dest-dir "/opt/mounts/mnt1" --buffer "${Buffer}"
    /usr/bin/sleep infinity
fi