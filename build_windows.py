"""Build the Windows executable from an explicit, losslessly optimized asset list."""

import argparse
import os
import importlib.metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ASSETS = (
    "as.jpg", "sary.png", "poisson.ico", "poisson.png", "requin.png",
    "espadon.png", "bulles.png", "sounds/click.wav", "sounds/go.wav", "sounds/tir.wav",
)


def stage_assets(root, stage):
    from PIL import Image

    original = optimized = 0
    for name in ASSETS:
        source, target = root / "assets" / name, stage / "assets" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        original += source.stat().st_size
        if source.suffix.lower() == ".png":
            with Image.open(source) as image:
                expected = image.convert("RGBA").tobytes()
                output = image.copy()
                if output.mode == "RGBA" and output.getextrema()[3] == (255, 255):
                    output = output.convert("RGB")
                output.save(target, optimize=True, compress_level=9)
                with Image.open(target) as check:
                    if image.size != check.size or expected != check.convert("RGBA").tobytes():
                        raise RuntimeError(f"Lossless verification failed: {name}")
            if target.stat().st_size > source.stat().st_size:
                shutil.copy2(source, target)
        else:
            shutil.copy2(source, target)
        optimized += target.stat().st_size
    return original, optimized


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--work-dir", type=Path)
    args = parser.parse_args()
    if sys.platform != "win32":
        parser.error("Build this Windows executable on Windows.")
    root = args.project_root.resolve()
    output = (args.output_dir or root / "dist").resolve()
    work = (args.work_dir or root / "build" / "windows").resolve()
    output.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)
    asset_original, asset_optimized = stage_assets(root, work / "staged")
    all_assets = sum(file.stat().st_size for file in (root / "assets").rglob("*") if file.is_file())

    import PyInstaller.__main__
    start = time.perf_counter()
    command = [
        str(root / "main.py"), "--onefile", "--windowed", "--name", "TrappedGoldfish",
        "--icon", str(root / "assets" / "poisson.ico"),
        "--add-data", f"{work / 'staged' / 'assets'}:assets",
        "--paths", str(root), "--distpath", str(output),
        "--workpath", str(work / "pyinstaller"), "--specpath", str(work),
        "--noupx", "--noconfirm", "--log-level", "WARN",
    ]
    for module in ("PIL", "tkinter", "unittest", "numpy", "pygame.tests", "pygame.examples"):
        command.extend(("--exclude-module", module))
    PyInstaller.__main__.run(command)
    exe = output / "TrappedGoldfish.exe"
    runtime_report = work / "executable-check.json"
    environment = os.environ.copy()
    environment.pop("PYTHONHOME", None)
    environment.pop("PYTHONPATH", None)
    windows = Path(environment.get("SYSTEMROOT", "C:/Windows"))
    environment["PATH"] = os.pathsep.join((str(windows / "System32"), str(windows)))
    check = subprocess.run([str(exe), "--self-test", str(runtime_report)],
                           cwd=work, env=environment, timeout=90)
    runtime = json.loads(runtime_report.read_text(encoding="utf-8")) if runtime_report.exists() else {}
    if check.returncode != 0 or not runtime.get("ok") or not runtime.get("frozen"):
        raise RuntimeError(f"Executable verification failed: {runtime}")
    report = {
        "executable": exe.name, "executable_bytes": exe.stat().st_size,
        "all_source_assets_bytes": all_assets,
        "used_assets_original_bytes": asset_original,
        "used_assets_optimized_bytes": asset_optimized,
        "lossless_pixel_verification": True, "asset_files": list(ASSETS),
        "standalone_executable_test": runtime,
        "build_seconds": round(time.perf_counter() - start, 2),
        "versions": {name: importlib.metadata.version(name)
                     for name in ("pygame", "PyInstaller", "Pillow")},
    }
    (output / "build-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
