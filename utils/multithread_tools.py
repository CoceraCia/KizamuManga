import threading



def run_in_paralel(target_func, args_list: list | tuple):
    if isinstance(args_list, tuple):
        thread = threading.Thread(target=target_func, args=args_list)
        thread.start()
        thread.join()
    else:
        threads = []

        for args in args_list:
            thread = threading.Thread(target=target_func, args=args)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
