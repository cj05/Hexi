class Graph:
    def __init__(self,count):
        self.data = {}
        for i in range(count):
            self.create(i)
    
    def connect(self,a,b):  # a to b
        self.data[a].append(b)

    def isConnected(self,a,b):
        return a in self.data and b in self.data[a]

    def exist(self,a):
        return a in self.data

    def create(self,a):
        self.data[a]=[]

    def sort(self):
        visited = [0] * len(self.data)
        

        def dfs(graph,node):
            if visited[node] == 1:
                return False , []
            if visited[node] == 2:
                return True , []
            visited[node] = 1

            isDAG = True
            data = []
            for i in graph[node]:
                t,d = dfs(graph,i)
                isDAG = isDAG and t
                data = data + d
            

            data = data + [node]
            visited[node] = 2
            return isDAG , data
            
        isDAG = True
        data = []
        for node in self.data:
            if visited[node] == 0:
                t,d = dfs(self.data,node)
                isDAG = isDAG and t
                data = data + d
        
        return isDAG,data
        

