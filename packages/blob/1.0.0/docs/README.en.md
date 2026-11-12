# Binary files (blob)

Ingest binary files from a directory and track what was processed.

## Streams

| Stream | Signal | Default | Destination | What it collects |
| --- | --- | --- | --- | --- |
| `files` | logs | on | `veloxagent-files.blob-v1` | One record per file: `file.path`, `file.name`, `file.size` |

## Fields

`path` (required, default `/var/spool/velox/blobs/*`), `exclude` (patterns), `scan_refresh_interval` (default 10s) and advanced `upload_success_action` / `upload_failure_action` (`delete`, `add_suffix`, `emit_log`) with their suffixes. The tracking database is fixed under the agent state directory. `delete_after` (default 30d).

## Requirements

- The agent user must read the directory (and write to it if you choose `delete` or `add_suffix`).

## Notes

Beta. `delete` removes files from disk after a successful upload.
