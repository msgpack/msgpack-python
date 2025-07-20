#!/usr/bin/env python3
from concurrent.futures import ThreadPoolExecutor
from msgpack import Packer
import threading


def run_threaded(
    func,
    num_threads=8,
    pass_count=False,
    pass_barrier=False,
    outer_iterations=1,
    prepare_args=None,
):
    """Runs a function many times in parallel"""
    for _ in range(outer_iterations):
        with ThreadPoolExecutor(max_workers=num_threads) as tpe:
            if prepare_args is None:
                args = []
            else:
                args = prepare_args()
            if pass_barrier:
                barrier = threading.Barrier(num_threads)
                args.append(barrier)
            if pass_count:
                all_args = [(func, i, *args) for i in range(num_threads)]
            else:
                all_args = [(func, *args) for i in range(num_threads)]
            try:
                futures = []
                for arg in all_args:
                    futures.append(tpe.submit(*arg))
            finally:
                if len(futures) < num_threads and pass_barrier:
                    barrier.abort()
            for f in futures:
                f.result()


def test_multithread_packing():
    output = []
    test_data = "abcd" * 10_000_000
    packer = Packer()

    def closure(b):
        data = packer.pack(test_data)
        output.append(data)
        b.wait()

    run_threaded(closure, num_threads=10, pass_barrier=True, pass_count=False)
