#!/usr/bin/env bash
function set_variables() {
  # shellcheck disable=SC2046
  export $(grep -v '^#' ./API/API/environment/"${ENV_FILE_TYPE}" | xargs)
}

function sudo_check() {
  if ! type -p sudo >/dev/null; then
    SUDO=""
  else
    SUDO="sudo"
  fi
}

function start_tests() {
  ${SUDO} docker exec "$API_CONTAINER_NAME" pytest -c tests/pytest.ini tests/route__docs/test_base.py

  ${SUDO} docker exec "$API_CONTAINER_NAME" pytest -c tests/pytest.ini tests/route__redoc/test_base.py

  ${SUDO} docker exec "$API_CONTAINER_NAME" pytest -c tests/pytest.ini tests/route__posts_search/test_base.py
  ${SUDO} docker exec "$API_CONTAINER_NAME" pytest -c tests/pytest.ini tests/route__posts_search/test_search_url_with_text.py

  ${SUDO} docker exec "$API_CONTAINER_NAME" pytest -c tests/pytest.ini tests/route__posts_delete/test_base.py
  ${SUDO} docker exec "$API_CONTAINER_NAME" pytest -c tests/pytest.ini tests/route__posts_delete/test_delete_post_by_valid_int_id.py
}

function check_containers() {
  if
    [ ! "$(docker container inspect -f '{{.State.Running}}' "$ELASTIC_CONTAINER_NAME")" == "true" ] &&
      [ ! "$(docker container inspect -f '{{.State.Running}}' "$POSTGRES_CONTAINER_NAME")" == "true" ] &&
      [ ! "$(docker container inspect -f '{{.State.Running}}' "$API_CONTAINER_NAME")" == "true" ]
  then
    echo "Selected containers not up"
    exit 1
  fi
}

function print_help() {
  echo
  echo "Usage \`$0\`"
  echo "Flags:"
  echo "  -d           Режим для разработки."
  echo "  -p           Основной режим работы."
  echo "  -t prod      Запустить тесты для основных контейнеров."
  echo "  -t dev       Запустить тесты для тестовых контейнеров."
  echo "  -i           Информация."
  echo

  exit 0
}

function parse_param() {
  if [[ $# == 0 ]] || [[ $# -gt 2 ]]; then
    echo "Must be 1 arg"
    print_help
  fi

  while getopts ":dpt:i" ARG; do
    case "$ARG" in
    d)
      ENV_FILE_TYPE="dev.env"
      MODE="dev"
      export MODE ENV_FILE_TYPE
      ;;
    p)
      ENV_FILE_TYPE="prod.env"
      MODE="prod"
      export MODE ENV_FILE_TYPE
      ;;
    t)
      MODE="test"
      if [[ $OPTARG == "dev" ]]; then
        ENV_FILE_TYPE="dev.env"
      elif [[ $OPTARG == "prod" ]]; then
        ENV_FILE_TYPE="prod.env"
      else
        echo "Unexpected value"
        echo "Use: -t dev or -t prod"
        exit 1
      fi
      export MODE ENV_FILE_TYPE
      ;;
    i)
      print_help
      ;;
    :)
      echo "Flag -$OPTARG missing required argument"
      echo "Use -i for info"
      exit 1
      ;;
    \?)
      echo "Unexpected argument"
      exit 1
      ;;
    esac
  done

  shift "$((OPTIND - 1))"
}

function start() {
  parse_param "$@"
  set_variables

  if [[ $MODE == "test" ]]; then
    check_containers
    start_tests
  else
    ${SUDO} docker-compose -f docker-compose."${MODE}".yaml up --build --remove-orphans -d
  fi
}

start "$@"
