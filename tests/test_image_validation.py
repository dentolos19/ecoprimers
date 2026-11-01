import hashlib
import importlib.util
import io
import re
import shutil
import struct
import sys
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from werkzeug.datastructures import FileStorage

import main
from routing.engagement import is_valid_image
from scripts.patch_pillow import PATCH_FILES, patch_pillow

ROOT = Path(__file__).resolve().parents[1]


class ImageValidationTests(unittest.TestCase):
    def test_supported_formats_and_disguised_eps(self):
        self.assertIsNotNone(main.app)
        for image_format in ("PNG", "JPEG", "GIF"):
            with self.subTest(image_format=image_format):
                data = io.BytesIO()
                Image.new("RGB", (1, 1)).save(data, format=image_format)
                data.seek(0)
                upload = FileStorage(stream=data, filename="upload.png")
                self.assertTrue(is_valid_image(upload))
                self.assertEqual(upload.stream.tell(), 0)

        eps = b"%!PS-Adobe-3.0 EPSF-3.0\n%%BoundingBox: 0 0 1 1\n%%EndComments\nshowpage\n%%EOF\n"
        self.assertEqual(Image.open(io.BytesIO(eps)).format, "EPS")
        self.assertFalse(
            is_valid_image(FileStorage(stream=io.BytesIO(eps), filename="upload.png"))
        )

    def test_worker_backports_and_guards(self):
        vendor = ROOT / "python_modules" / "PIL"
        if not (vendor / "GifImagePlugin.py").is_file():
            self.skipTest("Run just build to vendor the Python Worker packages")
        version = re.search(
            r'__version__ = "(\d+)\.(\d+)\.(\d+)"', (vendor / "_version.py").read_text()
        )
        assert version is not None
        if tuple(map(int, version.groups())) >= (13, 0, 0):
            self.skipTest("The Worker already has upstream's patched Pillow")

        temporary_dir = ROOT / ".tmp"
        temporary_dir.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary_dir) as directory:
            package = Path(directory)
            shutil.copyfile(vendor / "_version.py", package / "_version.py")
            for name, (original_hash, patched_hash, changes) in PATCH_FILES.items():
                source = (vendor / name).read_bytes()
                if hashlib.sha256(source).hexdigest() == patched_hash:
                    text = source.decode()
                    for before, after in reversed(changes):
                        self.assertEqual(text.count(after), 1)
                        text = text.replace(after, before, 1)
                    source = text.encode()
                self.assertEqual(hashlib.sha256(source).hexdigest(), original_hash)
                (package / name).write_bytes(source)

            patch_pillow(package)
            snapshot = {name: (package / name).read_bytes() for name in PATCH_FILES}
            for name, (_, patched_hash, _) in PATCH_FILES.items():
                self.assertEqual(
                    hashlib.sha256(snapshot[name]).hexdigest(), patched_hash
                )
            patch_pillow(package)
            self.assertEqual(
                snapshot, {name: (package / name).read_bytes() for name in PATCH_FILES}
            )

            Image.init()
            with ExitStack() as stack:
                for name in ("OPEN", "SAVE", "SAVE_ALL", "EXTENSION", "MIME"):
                    stack.enter_context(patch.dict(getattr(Image, name)))
                modules = {}
                for name in PATCH_FILES:
                    spec = importlib.util.spec_from_file_location(
                        "PIL._backport_" + name[:-3], package / name
                    )
                    assert spec is not None and spec.loader is not None
                    module = importlib.util.module_from_spec(spec)
                    stack.enter_context(patch.dict(sys.modules, {spec.name: module}))
                    spec.loader.exec_module(module)
                    modules[name] = module

                data = io.BytesIO()
                Image.new("RGB", (1, 1)).save(data, format="GIF")
                image_data = data.getvalue()
                flags = image_data[10]
                offset = 13 + (3 * (2 << (flags & 7)) if flags & 128 else 0)
                image_data = (
                    image_data[:offset]
                    + b"\x21\xfe\x01A\x00" * 1000
                    + image_data[offset:]
                )
                with Image.open(io.BytesIO(image_data), formats=["GIF"]) as image:
                    self.assertEqual(image.info["comment"], b"\n".join([b"A"] * 1000))

                png = modules["PngImagePlugin.py"]
                data = io.BytesIO()
                data.write(png._MAGIC)
                png.putchunk(
                    data,
                    b"IHDR",
                    png.o32(2**31 - 1),
                    png.o32(1),
                    b"\x08\x06\x00\x00\x00",
                )
                png.putchunk(data, b"acTL", png.o32(2), png.o32(0))
                png.putchunk(
                    data,
                    b"fcTL",
                    png.o32(0),
                    png.o32(1),
                    png.o32(1),
                    png.o32(0),
                    png.o32(0),
                    png.o16(1),
                    png.o16(10),
                    bytes([png.Disposal.OP_BACKGROUND, png.Blend.OP_SOURCE]),
                )
                png.putchunk(data, b"IDAT")
                png.putchunk(data, b"IEND")
                with (
                    patch.object(
                        Image.core,
                        "fill",
                        side_effect=AssertionError("Unsafe APNG allocation"),
                    ),
                    self.assertRaises(Image.DecompressionBombError),
                ):
                    Image.open(data, formats=["PNG"])

                with self.assertRaises(SyntaxError):
                    modules["Image.py"].Exif().load(
                        b"Exif\x00\x00" * 3 + Image.Exif().tobytes()
                    )

                ifd = modules["TiffImagePlugin.py"].ImageFileDirectory_v2()
                entries = (
                    struct.pack("<H", 2)
                    + struct.pack("<HHLL", 0, 1, 30, 0)
                    + struct.pack("<HHLL", 1, 1, 30, 0)
                    + struct.pack("<L", 0)
                )
                with self.assertWarnsRegex(UserWarning, "Tag data larger than file"):
                    ifd.load(io.BytesIO(entries))
                self.assertEqual(len(ifd[0]), 30)
                self.assertNotIn(1, ifd)

            plugin = package / "GifImagePlugin.py"
            plugin.write_bytes(
                snapshot["GifImagePlugin.py"] + b"\n# unexpected change\n"
            )
            with self.assertRaisesRegex(RuntimeError, "Unknown Pillow parser source"):
                patch_pillow(package)
            self.assertEqual(
                plugin.read_bytes(),
                snapshot["GifImagePlugin.py"] + b"\n# unexpected change\n",
            )
            (package / "_version.py").write_text('__version__ = "12.3.0"\n')
            with self.assertRaisesRegex(
                RuntimeError, "Unsupported vendored Pillow version"
            ):
                patch_pillow(package)
            (package / "_version.py").write_text('__version__ = "13.0.0"\n')
            patch_pillow(package)


if __name__ == "__main__":
    unittest.main()
