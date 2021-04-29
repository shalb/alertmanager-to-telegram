# alertmanager-to-telegram

Service to accept `alertmanager` web hooks and send alerts to `telegram`

Example receiver:

```
receivers:
- name: my_telegram
  webhook_configs:
    - url: http://alertmanager-to-telegram:9647
```

## build

~~~~
docker login
docker-compose -f docker-compose-build.yml build
docker-compose -f docker-compose-build.yml push
~~~~

## configuration

customize your configuration via environment variables (see example in `docker-compose.yml`)

## run

~~~~
docker-compose up
~~~~

## dependencies if want to run without container

~~~~
pip3 install --user pyaml prometheus_client
~~~~

