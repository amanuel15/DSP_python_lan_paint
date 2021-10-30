from multiprocessing import Process


# def daemonProcessLauncher(targetProcess, argsuments):
#     process = Process(target=targetProcess, args=argsuments, daemon=True)
#     return process
#
def f(name):
    print('hello', name)

if __name__ == '__main__':
    p = Process(target=f, args=(['bob'],),daemon=False)
    # p = Process(target=Client, args=(),daemon=True)
    p.start()
    print("will die in Twenty Five seconds")
    # time.sleep(25)
    # p.terminate()
    while True:
        pass

# def functionA():
#     print("a1")
#     from multiProcessing import functionB
#     print("a2")
#     functionB()
#     print("a3")
#
# def functionB():
#     print("b")
#
# print("t1")
# if __name__ == "__main__":
#     print("m1")
#     functionA()
#     print("m2")
# print("t2")
