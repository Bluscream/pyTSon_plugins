#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Multiprocessing helper."""


import multiprocessing
import sys

from concurrent import futures


class __MultiProcessed():

    def __init__(self, cpu_num, thread_num):
        self.cpu_num, self.thread_num = cpu_num, thread_num

    def _multi_cpu(self, _func, job_queue, timeout):
        if _getLen(job_queue) == 0:
            return []
        index = _get_index(job_queue, self.cpu_num)
        cpu_pool = multiprocessing.Pool(processes=self.cpu_num)
        mgr = multiprocessing.Manager()
        process_bar = mgr.list()
        for i in range(self.cpu_num):
            process_bar.append(0)
        result_queue = cpu_pool.map(
            _multi_thread,
            [[_func, self.cpu_num, self.thread_num, job_queue[int(index[i][0]):
              int(index[i][1] + 1)], timeout, process_bar, i]
             for i in range(len(index))])
        result = []
        for rl in result_queue:
            for r in rl:
                result.append(r)
        return result


def _func(argv):
    argv[2][argv[3]] = round((argv[4] * 100.0 / argv[5]), 2)
    sys.stdout.write(str(argv[2]) + ' ||' + '->' + "\r")
    sys.stdout.flush()
    return argv[0](argv[1])


def _multi_thread(argv):
    thread_num = argv[2]
    if _getLen(argv[3]) < thread_num:
        thread_num = argv[3]
    _func_argvs = [[argv[0], argv[3][i], argv[5], argv[6], i, len(argv[3])]
                   for i in range(len(argv[3]))]
    result = []
    if thread_num == 1:
        for _func_argv in _func_argvs:
            result.append(_func(_func_argv))
        return result
    thread_pool = futures.ThreadPoolExecutor(max_workers=thread_num)
    result = thread_pool.map(_func, _func_argvs, timeout=argv[4])
    return [r for r in result]


def _getLen(_list):
    return 0 if _list is None else len(_list)


def _get_index(job_queue, split_num):
    job_num = _getLen(job_queue)
    if job_num < split_num:
        split_num = job_num
    each_num = job_num / split_num
    index = [[i * each_num, i * each_num + each_num - 1]
             for i in range(split_num)]
    residual_num = job_num % split_num
    for i in range(residual_num):
        index[split_num - residual_num + i][0] += i
        index[split_num - residual_num + i][1] += i + 1
    return index


def multiprocessed(function, arguments, cpu_num=1, thread_num=1, timeout=None):
    multicpu_instance = __MultiProcessed(cpu_num, thread_num)
    return multicpu_instance._multi_cpu(function, arguments, timeout)
