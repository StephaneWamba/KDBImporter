from __future__ import annotations
import re
import unicodedata
# from config import get_logger
import os

_RX_BAD_FS_CHARS = re.compile(r'[\\/:\*\?"<>|]')

def _clean_title(raw_title: str) -> str:
    """Normalise et purifie un titre pour la DB.

    - Unicode NFKC
    - supprime caractères de contrôle (dont NULL)
    - remplace les caractères gênants pour les noms de fichier / SQL
    - réduit les blancs, strip
    """
    if raw_title is None:
        raise ValueError("Title cannot be None")

    title = unicodedata.normalize("NFKC", str(raw_title))
    # retire caractères non imprimables / contrôle
    title = "".join(ch for ch in title if ch.isprintable())
    # remplace les mauvais caractères par un espace
    title = _RX_BAD_FS_CHARS.sub(" ", title)
    # collapse whitespace
    title = re.sub(r"\s+", " ", title).strip()

    if not title:
        raise ValueError("Title became empty after sanitisation")

    return title

def running_in_docker() -> bool:
        # Heuristic 1: special Docker env file
    if os.path.exists('/.dockerenv'):
        return True

    # Heuristic 2: look for "docker" or "containerd" in /proc/1/cgroup
    try:
        with open('/proc/1/cgroup', 'rt') as f:
            content = f.read()
            if 'docker' in content or 'containerd' in content:
                return True
    except Exception:
        pass

    return False
    # return sys.modules.idlelib
    # try:
    #     with open('/proc/1/cgroup', 'rt') as f:
    #         return 'docker' in f.read()
    # except FileNotFoundError:
    #     return False