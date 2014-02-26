import sys

def parse_args(argv=None):
    opts={}
    args=[]
    argv=argv or sys.argv[1:]
    try:
        while argv:
            a=argv[0]
            if len(a)>1 and a[0] in ('+','-'):
                if a[0]=='+':
                    opts[a[1:]]=True
                elif a[0]=='-':
                    opts[a[1:]]=argv[1]
                    del argv[1]
            else:
                args.append(a)
            del argv[0]
    except IndexError: pass
    return opts,args
