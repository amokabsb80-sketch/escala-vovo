import sys
from pathlib import Path

# Adiciona a pasta 'src' ao caminho do Python
root_dir = Path(__file__).parent
src_dir = root_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Executa o seu app real, que está dentro de src/escala_vovo
exec(open(root_dir / "src" / "escala_vovo" / "app.py", encoding="utf-8").read())