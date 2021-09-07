import time


# time a code block
class Timer:
    def __init__(self, code_block_name):
        self.code_block_name = code_block_name

    def __enter__(self):
        self.time_start = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.time_end = time.time()
        total_time = self.time_end - self.time_start
        print(f'{self.code_block_name}: {total_time}')
