import re
import sys

CONST_EXPR = re.compile(r"\b(\d+)\s*([+\-*/])\s*(\d+)\b")

FOR_HEADER = re.compile(r"^(?P<indent>\s*)for\s*\(\s*(?P<var>\w+)\s*=.*\)\s*\{")

def fold_constants(line):
    while True:
        m = CONST_EXPR.search(line)
        if not m:
            break
        a, op, b = m.groups()
        try:
            # safe eval of integers
            c = str(eval(f"{a}{op}{b}"))
        except Exception:
            break
        line = line[:m.start()] + c + line[m.end():]
    return line


def hoist_invariants(lines):
    out = []
    i = 0
    while i < len(lines):
        header = lines[i]
        m = FOR_HEADER.match(header)
        if m:
            indent = m.group('indent')
            loop_var = m.group('var')
            body = []
            brace = 1
            i += 1
            while i < len(lines) and brace > 0:
                line = lines[i]
                if '{' in line: brace += 1
                if '}' in line: brace -= 1
                if brace > 0:
                    body.append(line)
                i += 1
            invariants = {}
            for ln in body:
                for expr in re.findall(r"\b\w+\s*\[\s*([^\]]+)\s*\]", ln):
                    if loop_var not in expr:
                        temp = f"_hoist_{len(invariants)}"
                        invariants[expr] = temp
            for expr, temp in invariants.items():
                out.append(f"{indent}{temp} = {expr};  // hoisted invariant\n")
            out.append(header)
            for ln in body:
                new_ln = ln
                for expr, temp in invariants.items():
                    new_ln = new_ln.replace(expr, temp)
                out.append(new_ln)
            out.append(f"{indent}}}\n")
        else:
            out.append(header)
            i += 1
    return out


def main():
    if len(sys.argv) != 3:
        print("Usage: python optimize.py input.txt output.txt")
        sys.exit(1)

    # Read and process lines
    with open(sys.argv[1], 'r') as f:
        lines = f.readlines()

    # 1) Constant Folding
    lines = [fold_constants(ln) for ln in lines]
    # 2) Code Hoisting
    lines = hoist_invariants(lines)

    # Write optimized output
    with open(sys.argv[2], 'w') as f:
        f.writelines(lines)

    print(f"Optimized code written to {sys.argv[2]}")


if __name__ == '__main__':
    main()
