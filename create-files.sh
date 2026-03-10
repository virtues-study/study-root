#!/bin/bash

input="items.csv"

while IFS=',' read -r type category name
do
    [ -z "$type" ] && continue

    type=$(echo "$type" | xargs)
    category=$(echo "$category" | xargs)
    name=$(echo "$name" | xargs)

    dir="./${type}/${category}"
    file="${dir}/${name}.md"

    mkdir -p "$dir"

    if [ ! -f "$file" ]; then
        cat > "$file" <<EOF
---
type: $type
category: $category
name: $name
---

# $name

EOF
    fi

done < "$input"
