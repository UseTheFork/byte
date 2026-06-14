# Add Files to AI Context

**Category**: How-to Guide

Files shape what Byte sees. This guide shows you how to add files to the AI context so Byte can read and modify them, remove files when you're done, and leverage Byte's automatic file detection through AI comment markers.

## Prerequisites

- Byte installed on your system
- A project with files you want to work on

## Step 1: Add Files with the `/add` Command

Use `/add` to make a file available for AI modification. Byte loads the file into context and enables AI-powered editing.

```
/add src/main.py
```

Tab completion works — type `/add src/` and press Tab to see matching files in your project:

```
/add src/
  src/main.py
  src/utils.py
  src/config.py
```

Once added, the file stays in context until you explicitly remove it or start a new session. Byte shows you how many files are currently loaded:

```
Added src/main.py to context
Active files: 3
```

### Example: Add Multiple Files

Add related files one at a time:

```
/add src/main.py
/add src/config.py
/add tests/test_main.py
```

Or use tab completion to find and add files quickly:

```
/add models/
  /add models/user.py
  /add models/order.py
```

## Step 2: Remove Files with the `/drop` Command

Use `/drop` to remove a file from context when you no longer need it. This reduces noise and keeps Byte focused on the relevant code.

```
/drop src/main.py
```

Tab completion shows only files currently in context — type `/drop` and press Tab to see what's loaded:

```
/drop
  src/main.py
  src/config.py
  tests/test_main.py
```

Once dropped, the file is no longer available to Byte for modification:

```
Removed src/main.py from context
Active files: 2
```

### Example: Clean Up Context

Remove files you're no longer working on:

```
/drop tests/test_main.py
/drop src/config.py
```

## Step 3: Leverage AI Comment Markers for Automatic Detection

Byte can automatically add files to context when it detects AI comment markers in code. Enable this feature in your config and mark your code with special comments.

### Enable File Watching

Edit `.byte/config.jsonc` in your project root and set `watch.enable` to `true`:

```jsonc
{
  "files": {
    "watch": {
      "enable": true,
    },
  },
}
```

With file watching enabled, Byte monitors your project for AI comment markers and automatically processes them.

### AI Comment Markers

Four markers tell Byte what to do:

| Marker | Behavior                                                    | Use Case                  |
| ------ | ----------------------------------------------------------- | ------------------------- |
| `AI:`  | Auto-add file to context, wait for next user input          | General instructions      |
| `AI!`  | Auto-add file to context, immediately invoke `/coder` agent | Urgent tasks              |
| `AI?`  | Auto-add file to context, immediately invoke `/ask` agent   | Questions needing answers |

### Example 1: General Instruction with `AI:`

Mark a task in your code with `AI:`. Byte adds the file and waits for you to provide context or confirm:

```python
# src/auth.py

def verify_password(user, password):
    # AI: Implement bcrypt password hashing for security
    return password == user.password
```

When Byte detects this marker:

1. Automatically adds `src/auth.py` to context
2. Waits for your next command

You can then ask Byte to fix it:

```
/ask How should I implement bcrypt hashing here?
/coder Implement bcrypt password hashing in this function
```

### Example 2: Urgent Task with `AI!`

Use `AI!` for tasks that need immediate execution. Byte adds the file and invokes the coder agent automatically:

```python
# src/database.py

def query(sql):
    # AI! Fix the SQL injection vulnerability in this function
    return db.execute(sql)
```

Byte detects the marker and immediately starts the coder agent to fix the vulnerability.

### Example 3: Question with `AI?`

Use `AI?` to ask Byte a question. Byte adds the file and invokes the ask agent:

```python
# src/payment.py

def process_payment(amount):
    # AI? Should we validate the amount before calling the payment API?
    return stripe_api.charge(amount)
```

Byte detects the marker and immediately invokes the ask agent to answer your question.

### Example 4: Multiple Markers in One File

Mix markers as needed:

```python
# src/api.py

def create_user(data):
    # AI: Validate user input before saving
    user = User.create(data)
    return user

def delete_user(user_id):
    # AI! Implement soft delete instead of permanent deletion
    User.objects.filter(id=user_id).delete()

def get_user(user_id):
    # AI? What's the best way to handle user not found errors?
    return User.objects.get(id=user_id)
```

Byte processes all markers in all context files and acts based on the marker types present.

### Clean Up After Completion

Once Byte completes a task triggered by an AI comment marker, remove the marker from your code:

```python
# Before
def verify_password(user, password):
    # AI: Implement bcrypt password hashing for security
    return bcrypt.checkpw(password.encode(), user.password_hash)

# After (marker removed)
def verify_password(user, password):
    return bcrypt.checkpw(password.encode(), user.password_hash)
```

## Step 4: Configure File Settings

Control which files Byte sees and how it watches for changes.

### Configure Ignore Patterns

By default, Byte ignores common folders and files like `.git`, `node_modules`, `.venv`, and `__pycache__`. Edit `.byte/config.jsonc` to customize these patterns:

```jsonc
{
  "files": {
    "ignore": [".byte", ".git", ".venv", "node_modules", "dist", "*.log", ".DS_Store"],
  },
}
```

Patterns follow gitignore syntax and support wildcards. These settings control which files appear in tab completion and are discovered by file watching.

### Full Files Configuration Example

Here's a complete files config:

```jsonc
{
  "files": {
    "watch": {
      "enable": true,
    },
    "ignore": [".byte", ".git", ".venv", "node_modules", "dist", "*.log", ".env"],
  },
}
```

## Troubleshooting

**Error: "File not found, not readable, or is already in context"**

The file doesn't exist, isn't readable, or you've already added it. Check the path and try again:

```
/add src/main.py
# Instead of:
/add src/mian.py  # typo
```

**AI comment markers aren't being detected**

Make sure `watch.enable` is set to `true` in `.byte/config.jsonc`. File watching is disabled by default:

```jsonc
{
  "files": {
    "watch": {
      "enable": true,
    },
  },
}
```

**Files disappear from context unexpectedly**

Context persists only for the current session. Starting a new Byte session clears all context. Use `/add` to re-add files or set up AI comment markers for automatic detection.

**Tab completion shows no files**

Your ignore patterns may be too broad, or files don't exist in your project. Check `.byte/config.jsonc` and verify your project structure.

## Next Steps

Now that you can add and remove files, explore how Byte agents use them. Check the tutorials for hands-on examples of working with file context.
