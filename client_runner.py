from Optimized_Client import clientStarter as ct

def clientRunner():
    process = ct()
    return  process

if __name__ == "__main__":
    process = clientRunner()
    process.start()
    process.join()