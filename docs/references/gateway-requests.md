### add_file

Add file to AI context as editable.

**Method name**: `add_file`

**Parameters**:

- `file_path` (string, required) — Relative or absolute path to the file

**Response**: `{"ok": true}`

**Errors**: `-32001` (Internal Error) if operation fails

### configure

Configure gateway parameters.

**Method name**: `configure`

**Parameters**:

- `model` (string, optional) — The LLM model to use
- `context_limit` (integer, optional) — Maximum context length

**Response**: `{"ok": true}`

**Errors**: `-32001` (Internal Error) if operation fails

### context_add_file

Add file contents to session context.

**Method name**: `context_add_file`

**Parameters**:

- `file_path` (string, required) — Relative or absolute path to the file

**Response**: `{"ok": true}`

**Errors**: `-32001` (Internal Error) if operation fails

### context_drop_file

Drop file contents from session context.

**Method name**: `context_drop_file`

**Parameters**:

- `file_path` (string, required) — Relative or absolute path to the file

**Response**: `{"ok": true}`

**Errors**: `-32001` (Internal Error) if operation fails

### drop_file

Remove file from AI context.

**Method name**: `drop_file`

**Parameters**:

- `file_path` (string, required) — Relative or absolute path to the file

**Response**: `{"ok": true}`

**Errors**: `-32001` (Internal Error) if operation fails
