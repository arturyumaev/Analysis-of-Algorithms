import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(format="[%(thread)-5d]%(asctime)s: %(message)s")
logger = logging.getLogger('async')
logger.setLevel(logging.INFO)

executor = ThreadPoolExecutor(max_workers=13)  # thread pool
loop = asyncio.get_event_loop()  # event loop


def cpu_bound_op(exec_time, *data):   # fake long-running func
    logger.info("Running cpu-bound op on {} for {} seconds".format(data, exec_time))
    time.sleep(exec_time)
    return sum(data)


async def level_a(data):
    level_b_inputs = data, 2 * data, 4 * data
    results = await asyncio.gather(*[level_b(val) for val in level_b_inputs]) # aggregate results from the level b
    result = await loop.run_in_executor(executor, cpu_bound_op, 3, *results)
    return result


async def level_b(data):
    # similar to level a
    level_c_inputs = data, 3 * data, 5 * data
    results = await asyncio.gather(*[level_c(val) for val in level_c_inputs])
    result = await loop.run_in_executor(executor, cpu_bound_op, 2, *results)
    return result


async def level_c(data):
    result = await loop.run_in_executor(executor, cpu_bound_op, 1, data)
    return result


async def process_pipeline(data):
    # Just pass the data along to level_a and return the results
    results = await level_a(data) # Waiting for the level a
    return results


def main():
    start_time = time.time()
    start_clock = time.process_time()
    result = loop.run_until_complete(process_pipeline(2))
    logger.info("Completed ({}) in {} seconds and {} cpu-time".format(result,
                                                                      time.time() - start_time,
                                                                      time.process_time() - start_clock))


if __name__ == '__main__':
    main()
