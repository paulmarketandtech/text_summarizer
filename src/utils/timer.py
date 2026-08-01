class Timer:
    def __init__(self, description="Operation"):
        self.description = description
        self.start = None
        self.end = None

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.perf_counter()
        elapsed = self.end - self.start
        print(f"{self.description} took {elapsed:.6f} seconds")

        # Optional: Re-raise exception if one occurred inside the block
        if exc_type:
            return False
        return True


"""
usage:
wtih Timer():
    ...
"""
