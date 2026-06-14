# Gateway Requests

**Category**: Explanation

Gateway requests are the RPC methods that external clients can invoke. Each request is defined as a dataclass on the `Requests` namespace in `src/byte/gateway/requests.py`. The gateway uses automatic discovery to convert request class names to snake_case method names and build a dispatch table at session boot.

## Current Requests

### configure

Configure gateway parameters.

**Method name**: `configure`

**Parameters**:

- `model` (string, optional) — The LLM model to use
- `context_limit` (integer, optional) — Maximum context length

**Response**: `{"ok": true}`

**Errors**: `-32001` (Internal Error) if configuration fails

### add_file

Add a file to the AI context as editable.

**Method name**: `add_file`

**Parameters**:

- `file_path` (string, required) — Relative or absolute path to the file

**Response**: `{"ok": true, "file_path": "..."}` on success

**Errors**: `-32001` (Internal Error) if the file doesn't exist, isn't readable, or is already in context

**Notes**: The file is tracked by the file service and appears in context summaries. Editable files are candidates for modification by the AI.

### drop_file

Remove a file from the AI context.

**Method name**: `drop_file`

**Parameters**:

- `file_path` (string, required) — Relative or absolute path to the file

**Response**: `{"ok": true, "file_path": "..."}` on success

**Errors**: `-32001` (Internal Error) if the file doesn't exist or isn't in context

**Notes**: Once dropped, the file is no longer editable by the AI and doesn't appear in context summaries.

### context_add_file

Add file contents to the session context without marking it as editable.

**Method name**: `context_add_file`

**Parameters**:

- `file_path` (string, required) — Relative or absolute path to the file

**Response**: `{"ok": true, "file_path": "..."}` on success

**Errors**:

- `-32001` (Internal Error) if the file doesn't exist
- `-32001` if the path is not a file (e.g., a directory)
- `-32001` if the file can't be read

**Notes**: This is for reference material. The file content is added to the context, but the file itself is not marked as editable. Useful for including examples, documentation, or read-only configuration files.

### context_drop_file

Remove file contents from the session context.

**Method name**: `context_drop_file`

**Parameters**:

- `file_path` (string, required) — Relative or absolute path to the file

**Response**: `{"ok": true, "file_path": "..."}` on success

**Errors**: `-32001` (Internal Error) if the path can't be resolved or the context entry doesn't exist

**Notes**: Removes the previously added context entry for this file. Has no effect on editable files managed by `add_file`.
