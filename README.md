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

## prepare helm chart

~~~~
helm package examples/helmfile/alertmanager-to-telegram/
mv alertmanager-to-telegram-0.0.1.tgz charts/
helm repo index charts --url https://raw.githubusercontent.com/shalb/alertmanager-to-telegram/main/charts/
~~~~

## dependencies if want to run without container

~~~~
pip3 install --user pyaml prometheus_client
~~~~

