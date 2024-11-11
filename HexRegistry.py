import MathUtils

def stackOpDef(stack,pattern,patternid,statemng):
    del stack[len(stack)-pattern[0]:]
    stack = stack + list(map(lambda x:[patternid,x],list(range(pattern[1]))))
    return stack


def OpNumber(argument):
    #note it uses numerical reflection:10 rn will fix
    def stackOpNumber(stack,pattern,patternid,statemng):
        stack.append([patternid,0,float(argument)]) 
        return stack
    return [0,1,"aqaae",stackOpNumber]


def stackOpTwiddling(twiddling): # stack manipulation
    
    def Twiddling(stack,pattern,patternid,statemng):
        buffer = stack[len(stack)-pattern[0]:].copy()
        if not statemng:
            for i in range(len(buffer)):
                buffer[i][0] = patternid
        print(len(buffer))
        del stack[len(stack)-pattern[0]:]
        def management(x):
            t = buffer[x].copy()
            if not statemng:
                buffer[x][1] += 1
            return t
        stack = stack + list(map(management,twiddling))
        return stack
    
    return Twiddling

def stackOpSwindler(stack,pattern,patternid,statemng):
    swindling = stack.pop()
    swindling = swindling[2]
    strides = MathUtils.maxFacList(swindling)

    use = len(strides)
    

    buffer = stack[len(stack)-use:].copy()
    del stack[len(stack)-use:]

    #print(stack,buffer)

    while strides:
        divisor = strides.pop()
        index = swindling // divisor
        swindling %= divisor
        stack.append(buffer.pop(index))
    
    return stack


PatternRegistry = {
    
    "mind":[0,1,"qaq",stackOpDef],
    "compass":[1,1,"aa",stackOpDef],
    "compass_2":[1,1,"dd",stackOpDef],
    "alidade":[1,1,"wa",stackOpDef],
    "stadiometer":[1,1,"awq",stackOpDef],
    "pace":[1,1,"wq",stackOpDef],

    "archer":[2,1,"wqaawdd",stackOpDef],
    "architect":[2,1,"weddwaa",stackOpDef],
    "scout":[2,1,"weaqa",stackOpDef],

    "numerical_ref":OpNumber,
    "explode":[2,0,"aawaawaa",stackOpDef],
    "fireball":[2,0,"ddwddwdd",stackOpDef],
    "impulse":[2,0,"awqqqwaqw",stackOpDef],
    "blink":[2,0,"awqqqwaq",stackOpDef],
    "break_block":[1,0,"qaqqqqq",stackOpDef],
    "place_block":[1,0,"eeeeede",stackOpDef],
    "create_water":[1,0,"aqawqadaq",stackOpDef],

    "conjure_block":[1,0,"qqa",stackOpDef],
    
    "consideration":[0,0,"qqqaw",stackOpDef],

    "flocks_gambit":[6,1,"ewdqdwe",stackOpDef], # last n list, wont work as intended
    "flocks_decomp":[1,6,"qwaeawq",stackOpDef],  # splat, wont work as intended

    "additive_distil":[2,1,"waaw",stackOpDef],
    "combination_distil":[2,1,"waaw",stackOpDef],

    "gemini_decomp":[1,2,"aadaa",stackOpTwiddling([0,0])],
    "prospector":[2,3,"aaedd",stackOpTwiddling([0,1,0])],
    "undertaker":[2,3,"ddqaa",stackOpTwiddling([1,0,1])],
    "dioscuri":[2,4,"aadadaaw",stackOpTwiddling([0,1,0,1])],


    "jester":[2,2,"aawdd",stackOpTwiddling([1,0])],
    "rotation":[3,3,"aaeaa",stackOpTwiddling([1,2,0])],
    "rotation_2":[3,3,"ddqdd",stackOpTwiddling([2,0,1])],
    "swindler":[1,0,"qaawdde",stackOpSwindler]
}

def getAllPatternName():
    return list(PatternRegistry.keys())


def getPatternAngle(pattern):
    return getPattern(pattern)[2]

def getPattern(pattern):
    typ = type(pattern)
    def patternGet(patternname):
        #print(patternname)
        
        if ":" in patternname:
            a,b = patternname.split(":",1)
            return PatternRegistry[a](b)
        if not patternname in PatternRegistry:
            return
        return PatternRegistry[patternname]
    if typ is str:
        return patternGet(pattern)
    if typ is list:
        return patternGet(pattern[0])