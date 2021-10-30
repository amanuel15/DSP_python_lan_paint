
from Optimized_Server_2 import serverStarter

def serverRunner(arguments):
    process = serverStarter(arguments)
    return process




if __name__ == "__main__":

    process =serverRunner(arguments=())
    process.start()
    process.join()
    print("server has exited")

