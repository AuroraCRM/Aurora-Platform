# file: fix_settings_calls.py
import libcst as cst
import libcst.matchers as m
from pathlib import Path

class StripSettingsCall(cst.CSTTransformer):
    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.CSTNode:
        # matcher para settings.<NOME>()
        if m.matches(
            original_node.func,
            m.Attribute(value=m.Name("settings"), attr=m.Name())
        ) and not original_node.args:
            # transforma Call(func, []) em Name/Attribute(func)
            return updated_node.func
        return updated_node

def process_file(path: Path):
    src = path.read_text(encoding="utf8")
    mod = cst.parse_module(src)
    new_mod = mod.visit(StripSettingsCall())
    if new_mod.code != src:
        path.write_text(new_mod.code, encoding="utf8")
        print(f"Corrigido: {path}")

if __name__ == "__main__":
    for py in Path("src/aurora_platform").rglob("*.py"):
        process_file(py)