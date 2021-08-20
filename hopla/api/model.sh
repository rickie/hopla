#!/usr/bin/env bash

source "${library_dir}/api_proxy.sh"
source "${library_dir}/logging.sh"

set -o errexit
set -o nounset
set -o pipefail


get_model() {
  # https://habitica.com/apidoc/#api-Meta-GetUserModelPaths
  declare -r model_name="$1"

  debug "get_models model=${model_name}"

  get_curl "models/${model_name}/paths"
}

parse_habitica_model_result() {
  debug "parse_habitica_model_result"
  declare -r json="$1"
  echo "${json}" | jq '.data'
}

main () {
  if (( $# == 0 )) ; then
    hopla api model --help
    exit 1
  fi
  parse_habitica_model_result "$(get_model "$1")"
}
main "$@"
 