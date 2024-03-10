import sel
import sys

content = input()
out = sel.eval(content)
sys.stdout.write(str(out))