import sys
from pathlib import Path

# Adiciona src ao path
root_dir = Path(__file__).parent
src_dir = root_dir / "src"
sys.path.insert(0, str(src_dir))

# Executa o app real
exec(open(src_dir / "escala_vovo" / "app.py", encoding="utf-8").read())