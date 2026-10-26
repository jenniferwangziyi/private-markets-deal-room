from dataclasses import dataclass, field
from pathlib import Path
import yaml

@dataclass(frozen=True)
class Names:
    catalog: str
    prefix: str
    warehouse_id: str
    profile: str
    roles: dict = field(default_factory=dict)
    ai_cfg: dict = field(default_factory=dict)
    app_sp: str = ""
    sharepoint: dict = field(default_factory=dict)

    def _s(self, name: str) -> str:
        return f"{self.catalog}.{self.prefix}{name}"

    @property
    def vdr(self) -> str: return self._s("vdr")
    @property
    def semantic(self) -> str: return self._s("semantic")
    @property
    def governance(self) -> str: return self._s("governance")
    @property
    def ai(self) -> str: return self._s("ai")

def load_names(path="config/demo.yml") -> Names:
    d = yaml.safe_load(Path(path).read_text())
    return Names(catalog=d["catalog"], prefix=d.get("schema_prefix") or "",
                 warehouse_id=d["warehouse_id"], profile=d["profile"], roles=d.get("roles") or {}, ai_cfg=d.get("ai") or {},
                 app_sp=d.get("app_sp") or "", sharepoint=d.get("sharepoint") or {})
