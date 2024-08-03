import random
def genotp():
    upper=[chr(i) for i in range(ord('A'),ord('Z')+1)]
    lower=[chr(i) for i in range(ord('a'),ord('z')+1)]
    otp=''
    for i in range(1):
        otp+=str(random.randint(0,9))
        otp=otp+random.choice(upper)
        otp=otp+random.choice(lower)
        otp+=str(random.randint(0,9))
        return  otp
