import GraphUtils as util
import Iota
import HexRegistry
import MathUtils
from bisect import insort, bisect_left

class Hex:
    def __init__(self,size):
        self.linkGraph = util.Graph(size)
        self.Patterns = [None] * size

    def number_embed(self,number):
        return ["consideration",number]

    def pushPattern(self,node,namespace,outLink):
        for link in outLink:
            self.setLink(node,link[0])
        self.Patterns[node] = [namespace,outLink]

    def setLink(self,fromNode,toNode):
        self.linkGraph.connect(fromNode,toNode)

    def swindler_manip(self,fromPermutation,Top): # we calculate to the left
        #turn it into numbers for easier calculation
        base = fromPermutation.copy()
        toPermutation = []
        header = [None] * len(Top)
        plen = len(base)

        cutoff = plen
        for i in range(plen):
            if base[i] in Top:
                cutoff = min(i,cutoff)
                header[Top.index(base[i])] = plen - i - 1

            base[i] = plen - i - 1
        
        base = base[cutoff:]

        toPermutation = list(filter(lambda x: not x in header,base))
        toPermutation.sort(reverse=True)
        toPermutation = toPermutation + header
        plen = len(base)
        code = []
        sorted_list = []

        for i in range(plen):
            current = toPermutation[i]
            # Find the count of smaller elements using binary search
            smaller_count = bisect_left(sorted_list, current)
            code.append(plen - 1 - current - (i - smaller_count))
            # Insert the current element into the sorted list
            insort(sorted_list, current)

        # Calculate the encoded number
        encoded_number = sum(code[i] * MathUtils.Fac(plen - 1 - i) for i in range(plen))

        return encoded_number

    def L(self,l):
        return list(map(HexRegistry.getPatternAngle,l))

    def P(self,l):
        return HexRegistry.getPatternAngle(l)

    def greedyIotaTop(self,iotaStack,topStack): # say, [0,5,3,6,7,2,8] and [3,6,2] into [0,5,8,7,3,6,2]
        print(iotaStack,topStack)
        swindler_number = self.swindler_manip(list(map(lambda x:[x[0],x[1]],iotaStack)),topStack)
        if swindler_number == 0:
            return []
        if swindler_number == 1:
            return ["jester"]
        if swindler_number == 3:
            return ["rotation"]
        if swindler_number == 4:
            return ["rotation_2"]
        
        return self.number_embed(swindler_number)+["swindler"]

    def predictStack(self,stack,patterns):
        pass
        
    stack = []
    intro = 0
    exec_cnt = 0
    collected = None
    collect = False
    def executePattern(self,pattern,statemng = False):
        if self.collect:
            if self.intro == 0:
                self.stack.append([self.exec_cnt,0,pattern])
            self.collect = False
        else:
            print(pattern)
            ptr = HexRegistry.getPattern(pattern)
            self.stack = ptr[3](self.stack,ptr,self.exec_cnt,statemng)
            
            if self.P(pattern) == "qqqaw":
                self.collect = True
                self.intro = 0
            if not statemng:
                self.exec_cnt = self.exec_cnt + 1

    def clearStack(self):
        self.stack = []
        self.exec_cnt = 0
        self.collected = None
        self.collect = False

    def executePatterns(self,patterns,statemng = False):
        intro = 0
        for i in patterns:
            self.executePattern(i,statemng)

    def compile(self):
        #Compliation Phase 1, pattern sequence
        t,d = self.linkGraph.sort()
        
        if not t:
            return "Error: Not a DAG"

        sequence = list(filter(lambda x: self.Patterns[x] != None, d))

        print("Sequence: ",sequence,d,self.Patterns)

        self.clearStack()
        #Compliation Phase 2, wiring up iota data

        hex = []
        mask = [None] * len(self.Patterns)
        i = 0
        for x in sequence: 
            print(x)
            mask[x] = i
            
            adjusthex = self.greedyIotaTop(self.stack,list(map(lambda x:[mask[x[0]],x[1]],self.Patterns[x][1])))

            print("B: ",self.stack)
            self.executePatterns(adjusthex,True)
            self.executePattern(self.Patterns[x])
            print("A: ",self.stack)

            hex = hex + adjusthex
            hex.append(self.Patterns[x][0])
            i=i+1

        print(hex)
        return hex
        #print(iotaUseCount) 
    
    def assemble(self, hex):
        return list(map(lambda x:{"startDir":"EAST","angles":HexRegistry.getPattern(x)[2]}if HexRegistry.getPattern(x) != None else x,hex))


