import re
import sys


digit = r"\d+(?:\.\d*)?"
PAT_MD = re.compile(fr"({digit})\s*([*/])\s*({digit})")
PAT_AS = re.compile(fr"({digit})\s*([+\-])\s*({digit})")
PAT_PAREN = re.compile(r"\(\s*(\d+(?:\.\d*)?)\s*\)")


def fold_constants(lines):
    out = []
    for ln in lines:
        line = ln
        # quitar paréntesis simples alrededor de literales
        line = PAT_PAREN.sub(r"\1", line)
        changed = True
        while changed:
            changed = False
            # actualizar paréntesis tras cada sustitución
            line = PAT_PAREN.sub(r"\1", line)
            # paso MD
            m = PAT_MD.search(line)
            if m:
                a, op, b = m.groups()
                val = eval(f"{a}{op}{b}")
                if isinstance(val, float) and val.is_integer(): val = int(val)
                line = line[:m.start()] + str(val) + line[m.end():]
                changed = True
                continue
            # paso AS
            m = PAT_AS.search(line)
            if m:
                a, op, b = m.groups()
                val = eval(f"{a}{op}{b}")
                if isinstance(val, float) and val.is_integer(): val = int(val)
                line = line[:m.start()] + str(val) + line[m.end():]
                changed = True
        out.append(line)
    return out


def hoist_invariants(lines):
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(\s*)(for|while)\s*\(([^)]*)\)\s*(\{)?", line)
        if m:
            indent, kind, cond, brace = m.groups()
            # extraer var de control (solo for)
            loop_var = None
            if kind == 'for':
                parts = cond.split(';')
                m2 = re.match(r"\s*(\w+)\s*=" , parts[0])
                if m2: loop_var = m2.group(1)
            # saltar línea de apertura
            if brace:
                i += 1
            elif i+1 < len(lines) and lines[i+1].strip() == '{':
                i += 2
            else:
                i += 1
            # capturar cuerpo
            body = []
            depth = 1
            while i < len(lines) and depth:
                if '{' in lines[i]: depth += 1
                if '}' in lines[i]: depth -= 1
                if depth: body.append(lines[i])
                i += 1
            # recursión para anidados
            body = hoist_invariants(body)
            # buscar primera multiplicación genérica invariantes
            invariant = None
            for b in body:
                m3 = re.search(r"(\w+)\s*\*\s*(\w+)", b)
                if m3:
                    expr = m3.group(0)
                    # evitar si usa var de control
                    if loop_var and loop_var in expr:
                        continue
                    invariant = expr
                    break
            # hoisting antes del for/while
            if invariant:
                tmp = '_hoist'
                out.append(f"{indent}{tmp} = {invariant};\n")
            # escribir cabecera
            out.append(f"{indent}{kind}({cond}) {{\n")
            # reemplazar en cuerpo
            if invariant:
                body = [ln.replace(invariant, tmp) for ln in body]
            # escribir cuerpo y cierre
            out.extend(body)
            out.append(f"{indent}}}\n")
        else:
            out.append(line)
            i += 1
    return out


def main():
    if len(sys.argv) != 3:
        print("Uso: python optimize.py entrada.txt salida.txt")
        sys.exit(1)
    lines = open(sys.argv[1], 'r').read().splitlines(keepends=True)
    # 1) Folding inicial (ahora quita paréntesis)
    lines = fold_constants(lines)
    # 2) Hoisting antes del bucle
    lines = hoist_invariants(lines)
    # 3) Folding final
    lines = fold_constants(lines)
    open(sys.argv[2], 'w').writelines(lines)
    print(f"Optimización completada: {sys.argv[2]}")

if __name__ == '__main__':
    main()
