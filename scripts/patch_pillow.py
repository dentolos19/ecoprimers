"""Backport upload-parser fixes until Pyodide supplies Pillow 13 wheels."""

import hashlib
import os
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Upstream fixes and redistribution license are linked in docs/cloudflare.md.
PATCH_FILES = {
    "GifImagePlugin.py": (
        "fe956c85ac3a65ba9f01daec1acc3fc58b485dabcf25c90fe9b686039acae361",
        "7f99fce0e453f9f8dd30f66549ddbe8850f2eb80e34b2d09c7488d76e53b886c",
        (
            (
                "        info: dict[str, Any] = {}\n",
                (
                    "        info: dict[str, Any] = {}\n"
                    "        comment_blocks: list[bytes] = []\n"
                ),
            ),
            (
                (
                    '                    comment = b""\n'
                    "\n"
                    "                    # Read this comment block\n"
                    "                    while block:\n"
                    "                        comment += block\n"
                    "                        block = self.data()\n"
                    "\n"
                    '                    if "comment" in info:\n'
                    "                        # If multiple comment blocks in frame, separate "
                    "with \\n\n"
                    '                        info["comment"] += b"\\n" + comment\n'
                    "                    else:\n"
                    '                        info["comment"] = comment\n'
                ),
                (
                    "                    if block and comment_blocks:\n"
                    "                        # If multiple comment blocks in frame, separate "
                    "with \\n\n"
                    '                        comment_blocks.append(b"\\n")\n'
                    "                    while block:\n"
                    "                        comment_blocks.append(block)\n"
                    "                        block = self.data()\n"
                ),
            ),
            (
                (
                    '        if info.get("comment"):\n'
                    '            self.info["comment"] = info["comment"]\n'
                ),
                (
                    "        if comment_blocks:\n"
                    '            self.info["comment"] = b"".join(comment_blocks)\n'
                ),
            ),
        ),
    ),
    "Image.py": (
        "1a3d2ef3dbcbd056fbb4de3415302873348c60e90129a9a107b8829395ea47ea",
        "d81a588201cc7d44b2bb616f8485e2b3fd8c8b46e53d444245101709e430bba4",
        (
            (
                (
                    '        while data and data.startswith(b"Exif\\x00\\x00"):\n'
                    "            data = data[6:]\n"
                ),
                '        data = re.sub(b"^(Exif\\x00\\x00){1,2}", b"", data)\n',
            ),
        ),
    ),
    "PngImagePlugin.py": (
        "374d11e97fee95ed486309103d1926865f848d0b3d19966d6632353c28865276",
        "f367d6c81b5944b07404fae714558e51c0914bbf0e054ec7447c56c2807e5351",
        (
            (
                (
                    "        self.dispose: _imaging.ImagingCore | None\n"
                    "        dispose_extent = None\n"
                ),
                "        dispose_extent = None\n",
            ),
            (
                "            self._prev_im = None\n            self.dispose = None\n",
                "            self._prev_im: _imaging.ImagingCore | None = None\n",
            ),
            (
                (
                    "            # ensure previous frame was loaded\n"
                    "            self.load()\n"
                    "\n"
                    "            if self.dispose:\n"
                    "                self.im.paste(self.dispose, self.dispose_extent)\n"
                ),
                (
                    "            if self.dispose_op == Disposal.OP_BACKGROUND:\n"
                    "                x0, y0, x1, y1 = self.dispose_extent\n"
                    "                dispose = Image.core.fill(self.mode, (x1 - x0, y1 - "
                    "y0))\n"
                    "            elif self.dispose_op == Disposal.OP_PREVIOUS and "
                    "self._prev_im is not None:\n"
                    "                dispose = self._crop(self._prev_im.copy(), "
                    "self.dispose_extent)\n"
                    "            else:\n"
                    "                dispose = None\n"
                    "\n"
                    "            # ensure previous frame was loaded\n"
                    "            self.load()\n"
                    "\n"
                    "            if dispose:\n"
                    "                self.im.paste(dispose, self.dispose_extent)\n"
                ),
            ),
            (
                (
                    "        self.dispose = None\n"
                    "        if self.dispose_op == Disposal.OP_PREVIOUS:\n"
                    "            if self._prev_im:\n"
                    "                self.dispose = self._prev_im.copy()\n"
                    "                self.dispose = self._crop(self.dispose, "
                    "self.dispose_extent)\n"
                    "        elif self.dispose_op == Disposal.OP_BACKGROUND:\n"
                    "            self.dispose = Image.core.fill(self.mode, self.size)\n"
                    "            self.dispose = self._crop(self.dispose, "
                    "self.dispose_extent)\n"
                    "\n"
                    "    def tell(self) -> int:\n"
                ),
                "\n    def tell(self) -> int:\n",
            ),
        ),
    ),
    "TiffImagePlugin.py": (
        "04a9f289226b5fc503b114d526ba61ceb29b06849d7182de0cf99b43cefc5d4d",
        "cc58b75e63a19d7acaaf1b68eaf8e1e57747b9f1363cae778cadabba429012d6",
        (
            (
                "        self._offset = fp.tell()\n",
                (
                    "        self._offset = fp.tell()\n"
                    "        fp.seek(0, io.SEEK_END)\n"
                    "        file_size = fp.tell()\n"
                    "        fp.seek(self._offset)\n"
                ),
            ),
            (
                "            for i in range(tag_count):\n",
                "            total_size = 0\n            for i in range(tag_count):\n",
            ),
            (
                (
                    '                    msg += f" Tag Location: {here} - Data Location: '
                    '{offset}"\n'
                    "                    fp.seek(offset)\n"
                ),
                (
                    '                    msg += f" Tag Location: {here} - Data Location: '
                    '{offset}"\n'
                    "                    # Well-formed IFD values should fit within the "
                    "stream they\n"
                    "                    # are read from, even before accounting for "
                    "overlaps.\n"
                    "                    total_size += size\n"
                    "                    if total_size > file_size:\n"
                    '                        warnings.warn(f"Tag data larger than file. '
                    'Skipping tag {tag}")\n'
                    "                        continue\n"
                    "                    fp.seek(offset)\n"
                ),
            ),
        ),
    ),
}


def patch_pillow(package: Path) -> None:
    version_text = (package / "_version.py").read_text()
    match = re.search(
        r'^__version__ = "(\d+)\.(\d+)\.(\d+)"$', version_text, re.MULTILINE
    )
    if match is None:
        raise RuntimeError("Cannot determine the vendored Pillow version")
    version = tuple(map(int, match.groups()))
    if version >= (13, 0, 0):
        return
    if version != (12, 2, 0):
        raise RuntimeError(
            "Unsupported vendored Pillow version; review the parser backports"
        )

    updates: list[tuple[Path, bytes]] = []
    for name, (original_hash, patched_hash, patches) in PATCH_FILES.items():
        path = package / name
        source = path.read_bytes()
        digest = hashlib.sha256(source).hexdigest()
        if digest == patched_hash:
            continue
        if digest != original_hash:
            raise RuntimeError(
                "Unknown Pillow parser source; refusing to build: " + name
            )

        text = source.decode("utf-8")
        for before, after in patches:
            if text.count(before) != 1:
                raise RuntimeError(
                    "Pillow backport does not match the vendored source: " + name
                )
            text = text.replace(before, after, 1)
        patched = text.encode("utf-8")
        if hashlib.sha256(patched).hexdigest() != patched_hash:
            raise RuntimeError("Pillow backport produced unexpected source: " + name)
        updates.append((path, patched))

    temporary_dir = ROOT / ".tmp"
    temporary_dir.mkdir(exist_ok=True)
    for path, patched in updates:
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                dir=temporary_dir, prefix="pillow-", delete=False
            ) as file:
                temporary = Path(file.name)
                file.write(patched)
            os.chmod(temporary, path.stat().st_mode & 0o777)
            os.replace(temporary, path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    patch_pillow(ROOT / "python_modules" / "PIL")
