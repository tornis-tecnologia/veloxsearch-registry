# Docker events

Docker daemon events of the host, collected by Velox Agent.

## Streams

| Stream | Signal | Default | Index / destination | What it collects |
| --- | --- | --- | --- | --- |
| `events` | logs | on | `veloxagent-events.docker-events-v1` | Docker daemon events: action, object type, container id, name, image and exit code. |

## Fields

`@timestamp` (from `time`), `event.action`, `event.category`, `docker.type`, `docker.scope`, `docker.status`, `docker.exit_code`, `docker.actor.id`, `docker.actor.name`, `container.id`, `container.name`, `container.image.name`, `event.outcome` (`unparsed` when the line is not an event), `velox.*`.

## Requirements

- Linux with Docker; the agent user must read `/var/run/docker.sock` (group `docker`).
- Only events from the moment the agent connects are collected; Docker does not replay history.

## Dashboard

*Docker events — overview*: events by action over time, top containers, containers that died or hit OOM, events by object type.
