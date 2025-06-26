#!/bin/bash

echo "=== UtecCompiler Auto-Build Installer ==="

# 1) Crear carpeta de trabajo en el home
WORKDIR="$HOME/uteccompiler-build"
mkdir -p "$WORKDIR"
cd "$WORKDIR"

echo "=== Cloning source code from GitHub..."
# 2) Clonar tu repositorio
#    El punto al final indica clonar dentro de WORKDIR
git clone https://github.com/Vasc0D/uteccompiler.git .

echo "=== Compiling UtecC and UtecCop..."
# 3) Compilar ambos ejecutables
#    Ajusta los nombres de archivos según tu proyecto
g++ main.cpp parser.cpp scanner.cpp token.cpp visitor.cpp exp.cpp -o UtecC
g++ main.cpp parser.cpp scanner.cpp token.cpp visitor.cpp exp.cpp -o UtecCop

echo "=== Installing executables to /usr/local/bin (sudo)..."
# 4) Mover los binarios a una ruta global
sudo mv UtecC   /usr/local/bin/UtecC
sudo mv UtecCop /usr/local/bin/UtecCop

echo "=== Cleaning up..."
# 5) Eliminar carpeta temporal
rm -rf "$WORKDIR"

echo "=== Installation complete!"
