
# Function to check $PATH for given peath. use $FIND_PATH abs. next
function search_path {

    for dir in $DIRS; do
        if [[ "$dir" == *"$1"* ]]; then 
            # found the dir in the $PATH so return found
            if [[ -d "$dir" ]]; then
                FIND_PATH=0; return
            fi
        fi
    done
    # else not found
    FIND_PATH=1
}
