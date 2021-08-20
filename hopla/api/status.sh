#!/usr/bin/env bash

source "${library_dir}/api_proxy.sh"
source "${library_dir}/logging.sh"

get_status() {
  debug "get_status"
  get_curl "status"
}

parse_habitica_status_result() {
  debug "parse_habitica_status_result"
  local json="$1"
  echo "${json}" | jq --raw-output '.data.status'
}

main () {
  parse_habitica_status_result "$(get_status)"
}
main