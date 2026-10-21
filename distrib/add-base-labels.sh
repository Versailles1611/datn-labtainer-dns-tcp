#!/bin/bash
#
# Labtainer refuses to run a remote student image that lacks a "base" label:
#
#   Remote image <registry>/<lab>.<container>.student is lacking a base version,
#   it needs to be retagged with trunk/distrib/retag_all.py
#
# This script adds the label
#
#   base=labtainers/labtainer.base2.<image-id-of-labtainer.base2>
#
# to every student image of the labs in this repository and pushes them to
# Docker Hub.  Run it after rebuilding/pushing lab images.
#
# Usage:  ./distrib/add-base-labels.sh [registry]
#         (default registry: haiyen1102)
#
set -u

REGISTRY="${1:-haiyen1102}"
BASE_IMAGE="labtainers/labtainer.base2"
BASE_ID=$(docker images -q "${BASE_IMAGE}:latest")
LABEL="base=${BASE_IMAGE}.${BASE_ID}"
REPO_DIR=$(cd "$(dirname "$0")/.." && pwd)

if [ -z "$BASE_ID" ]; then
    echo "ERROR: ${BASE_IMAGE}:latest is not present locally."
    echo "       docker pull ${BASE_IMAGE}:latest"
    exit 1
fi
echo "Using label: $LABEL"

failed=()
for lab_dir in "$REPO_DIR"/*/; do
    lab=$(basename "$lab_dir")
    start_config="$lab_dir/config/start.config"
    [ -f "$start_config" ] || continue

    for container in $(awk '/^CONTAINER/{print $2}' "$start_config"); do
        image="${REGISTRY}/${lab}.${container}.student"
        echo "=== $image"

        if ! docker image inspect "$image" >/dev/null 2>&1; then
            echo "  pulling..."
            if ! docker pull "$image" >/dev/null 2>&1; then
                echo "  PULL FAILED"
                failed+=("$image")
                continue
            fi
        fi

        tmp=$(mktemp -d)
        printf 'FROM %s\nLABEL %s\n' "$image" "$LABEL" > "$tmp/Dockerfile"
        if ! docker build -q -t "$image" -f "$tmp/Dockerfile" "$tmp" >/dev/null; then
            echo "  BUILD FAILED"
            failed+=("$image")
            rm -rf "$tmp"
            continue
        fi
        rm -rf "$tmp"

        if ! docker push "$image" >/dev/null 2>&1; then
            echo "  PUSH FAILED"
            failed+=("$image")
            continue
        fi
        echo "  pushed"
    done
done

echo "===================="
if [ ${#failed[@]} -eq 0 ]; then
    echo "All images labeled and pushed."
else
    echo "FAILED: ${failed[*]}"
    exit 1
fi
