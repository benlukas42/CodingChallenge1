maxNumber = 75;

'''
Prints the numbers from 1 to maxNumber line by line
But, if the number is divisible by:
    -> 4 and 7, print "Mission Control" instead.
    -> 4, print "Mission" instead.
    -> 5, print "Control" instead.
'''
def printNumbers():
    for i in range(1, maxNumber+1):
        if (i % 4 == 0) and (i % 7 == 0):
            print(str(i) + ": Mission Control")
        elif i % 4 == 0:
            print(str(i) + ": Mission")
        elif i % 5 == 0:
            print(str(i) + ": Control")
        else:
            print(i)
        continue
    return


'''
Prints numbers a more coherent way
    In the email it said to print "Mission Control" on 4 and 7 but doesn't it make more
    sense to do it on 4 and 5?
If the number is divisible by:
    -> 4 and 5, print "Mission Control" instead.
    -> 4, print "Mission" instead.
    -> 5, print "Control" instead.
'''
def printNumbersFix():
    for i in range(1, maxNumber+1):
        if (i % 4 == 0) and (i % 5 == 0):
            print("Mission Control")
        elif i % 4 == 0:
            print("Mission")
        elif i % 5 == 0:
            print("Control")
        else:
            print(i)
    return


def main():
    # printNumbers()
    printNumbersFix()


if __name__ == '__main__':
    main()
