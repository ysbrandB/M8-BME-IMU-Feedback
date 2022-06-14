from termcolor import colored, cprint

print_error = lambda x: cprint(f"🚫 {x}", 'red')
print_waring = lambda x: cprint(f"⚠️{x}", 'yellow')
print_green = lambda x: cprint(x, 'green')
def print_blue(x): cprint(x, 'blue')
def print_cyan(x): cprint(x, 'cyan')
