
from parser import build_parser
from visitor import Interpreter

if __name__ == "__main__":
    parser, states, ACTION, GOTO = build_parser()
    demo = """
    x=9;
    y=2+3*4;
    print(sqrt(x)+y);
    if x then print(1) else print(0) endif;
    while y do y=y-5 endwhile;
    print(y)
    """
    ast = parser.parse(demo)
    out = Interpreter().run(ast)
    print("Salida:")
    print(out)
