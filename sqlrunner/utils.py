def touch(f_path):
    """Touch the file at the given path, making any parent directories as required."""
    f_path.parent.mkdir(parents=True, exist_ok=True)
    f_path.touch()
