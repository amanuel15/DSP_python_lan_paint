import nmap
import socket



class NetworkDicovery:
    def __init__(self):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.allhosts = []

    def lastPointFinder(self,ip):
        index = 0
        for i in range(len(ip)):
            if ip[i] == ".":
                index = i
        return index

    def formatForNmap(self,ip):
        return ip[:self.lastPointFinder(ip) + 1] + "0/24"

    def isRouterIP(self,ip):
        if ip[self.lastPointFinder(ip)+1:] == "1":
            return True
        else:
            return False

    def scan(self):
        nm = nmap.PortScanner()
        nm.scan(hosts=self.formatForNmap(self.ip), arguments='-sn -n -sP -PE -PA21,23,80,3389')
        hosts_list = [(x, nm[x]['status']['state']) for x in nm.all_hosts()]
        for host, status in hosts_list:
            if not self.isRouterIP(host):
                self.allhosts.append(host)

    def getAllHosts(self):
        self.scan()
        return self.allhosts

# start = time.time()
# print(NetworkDicovery().getAllHosts())
# print(time.time()-start )



