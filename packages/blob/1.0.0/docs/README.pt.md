# Arquivos binários (blob)

Ingere arquivos binários de um diretório e registra o que foi processado.

## Streams

| Stream | Sinal | Padrão | Destino | O que coleta |
| --- | --- | --- | --- | --- |
| `files` | logs | ligada | `veloxagent-files.blob-v1` | Um registro por arquivo: `file.path`, `file.name`, `file.size` |

## Campos

`path` (obrigatório, padrão `/var/spool/velox/blobs/*`), `exclude` (padrões), `scan_refresh_interval` (padrão 10s) e avançados `upload_success_action` / `upload_failure_action` (`delete`, `add_suffix`, `emit_log`) com seus sufixos. O banco de rastreamento é fixo no diretório de estado do agente. `delete_after` (padrão 30d).

## Requisitos

- O usuário do agente deve ler o diretório (e escrever nele se escolher `delete` ou `add_suffix`).

## Notas

Beta. `delete` remove os arquivos do disco após um upload bem-sucedido.
