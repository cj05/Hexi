factorials = []
top_index = 0
    
def Fac(x):
    global top_index
    global factorials
    # Compute factorials
    diff = x - top_index+1
    if diff > 0:
        factorials = factorials + [1] * diff
        for i in range(max(top_index,1), x+1):
            factorials[i] = factorials[i - 1] * (i)
        top_index = x

    return factorials[x]

def FacList(x):
    Fac(x)
    return factorials[:x+1].copy()

def maxFacList(v):
    x = 0
    while Fac(x) < v:
        x = x + 1
    
    return factorials[:x].copy()