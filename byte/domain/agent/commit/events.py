from byte.domain.events.event import Event


class PreCommitStarted(Event):
    """Event emitted when a commit process begins, before message generation."""

    staged_files: int
    diff_size: int


class CommitCreated(Event):
    """Event emitted when a git commit is successfully created."""

    commit_hash: str
    message: str
    files_changed: int
