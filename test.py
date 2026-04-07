import time
import asyncio
from pytrackio import track, counter, timer, export_jsonlines

# 1. Track a standard function
@track(name="process_data_task")
def sample_task():
    time.sleep(0.1)  # Simulate work
    return "Done"

# 2. Track an async function
@track(name="fetch_api_async")
async def async_task():
    await asyncio.sleep(0.05)
    return "Async Done"

# 3. Use a counter
hits = counter("api_hits")
hits.increment(10)

# 4. Use a context manager timer
def block_test():
    with timer("heavy_computation"):
        sum(i*i for i in range(10**6))

async def main():
    # Run some tasks to generate data
    sample_task()
    await async_task()
    block_test()
    
    print("\n--- JSON Lines Output ---")
    # Calling without a path will return the string and print it (per our report.py logic)
    jsonl_output = export_jsonlines()
    print(jsonl_output)

if __name__ == "__main__":
    asyncio.run(main())