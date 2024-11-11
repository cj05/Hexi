class Factorial:
    def __init__(self):
        self.acc = 1
        self.n = 1

    def __iter__(self):
        return self

    def __next__(self):
        val = self.acc
        self.acc *= self.n
        self.n += 1
        return val


from bisect import insort, bisect_left

def factorial(x):
    if x == 0:
        return 0
    else:
        fact_iter = Factorial()
        for _ in range(x):
            next(fact_iter)  # Advance the iterator
        return next(fact_iter)


def ixed_factorial(value, stack):
    strides = []
    fact_iter = Factorial()
    
    # Collect strides (factorials) while they are less than or equal to value
    while True:
        stride = next(fact_iter)
        if stride > value:
            break
        strides.append(stride)

    # Check if the stack can accommodate the manipulations
    if len(stack) < len(strides):
        raise ValueError("Manipulating too many elements on the stack!")

    stride_offset = len(stack) - len(strides)
    edit_target = stack[stride_offset:]
    swap = edit_target.copy()
    output = []
    while strides:
        divisor = strides.pop()
        index = value // divisor
        value %= divisor
        output.append(swap.pop(index))

    return output

def swindler_manip(fromPermutation,Top): # we calculate to the left
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
    
    
    factorials = [1] * plen
    
    # Precompute factorials
    for i in range(1, plen):
        factorials[i] = factorials[i - 1] * (i)

    # Calculate the encoded number
    encoded_number = sum(code[i] * factorials[plen - 1 - i] for i in range(plen))

    return encoded_number


def main():
    max_len = 6
    template = [chr(i) for i in range(ord('a') + max_len - 1, ord('a') - 1, -1)]

    print("Code Permutation")

    for x in range(1, max_len + 1):
        slice_ = template[-x:]
        print(f"Permuting {''.join(slice_)}")
        
        fact = factorial(x)
        prev_fact = factorial(x - 1)
        
        for code in range(prev_fact, fact):
            permed = slice_.copy()
            t = ixed_factorial(code, permed)
            print(f"{code} {''.join(t)} {swindler_manip([1,2,3,7]+slice_.copy(),t.copy())}")
            if code != swindler_manip([1,2,3,7]+slice_.copy(),t.copy()):
                return



if __name__ == "__main__":
    main()
