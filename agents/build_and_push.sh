#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REGISTRY="registry.dev.trelent.com"
TRELENT_DIR="$HOME/.trelent"

usage() {
    echo "Usage: $0 <agent[:tag]>"
    exit 1
}

get_profile() {
    if [ -n "$TRELENT_PROFILE" ]; then
        echo "$TRELENT_PROFILE"
        return
    fi

    if [ -f "$TRELENT_DIR/active" ]; then
        cat "$TRELENT_DIR/active"
        return
    fi

    echo "default"
}

load_credentials() {
    local profile="$1"
    local profile_file="$TRELENT_DIR/profiles/$profile"

    if [ ! -f "$profile_file" ]; then
        echo "Profile '$profile' not found. Run 'trelent auth add' first." >&2
        exit 1
    fi

    source "$profile_file"
}

parse_input() {
    local input="$1"
    AGENT="${input%%:*}"
    TAG="${input#*:}"

    if [ "$TAG" = "$input" ]; then
        TAG="latest"
    fi
}

# Main
[ -z "$1" ] && usage

parse_input "$1"

if [ ! -d "$SCRIPT_DIR/$AGENT" ]; then
    echo "Directory '$AGENT' not found"
    exit 1
fi

PROFILE=$(get_profile)
load_credentials "$PROFILE"

IMAGE="$REGISTRY/$client_id/$AGENT:$TAG"

echo "$client_secret" | docker login "$REGISTRY" -u "$client_id" --password-stdin
docker build -t "$IMAGE" "$SCRIPT_DIR/$AGENT/"
docker push "$IMAGE"
