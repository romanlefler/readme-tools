import sys
import subprocess
import os
import re

import matplotlib.pyplot as plt

def get_locale_name_from_path(path: str):
    parts = path.replace("\\", "/").split("/")
    if "locale" in parts:
        i = parts.index("locale")
        if i + 1 != len(parts):
            return parts[i + 1]
    return os.path.basename(path)

def get_stats(path: str):
    cmd = [ "msgfmt", "--statistics", "-o", os.devnull, path ]
    proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()

    text = stderr.decode("utf-8", errors="ignore").strip()

    n_translated = n_fuzzy = n_untranslated = 0

    match_tr = re.search(r"(\d+)\s+translated", text)
    match_fz = re.search(r"(\d+)\s+fuzzy", text)
    match_un = re.search(r"(\d+)\s+untranslated", text)

    if match_tr:
        n_translated = int(match_tr.group(1))
    if match_fz:
        n_fuzzy = int(match_fz.group(1))
    if match_un:
        n_untranslated = int(match_un.group(1))

    total = n_translated + n_fuzzy + n_untranslated
    return total, n_translated, n_fuzzy, n_untranslated

def create_rows(paths: list[str]):
    rows = [ ]

    for f in paths:
        total, n_translated, n_fuzzy, n_untranslated = get_stats(f);
        rows.append({
            "lang": get_locale_name_from_path(f),
            "total": total,
            "translated": n_translated,
            "fuzzy": n_fuzzy,
            "untranslated": n_untranslated,
            "percent": n_translated / total * 100.0
        })
    return rows

def create_chart(inPaths: list[str], outPath: str):
    rows = create_rows(inPaths)

    rows = sorted(rows, key=lambda k: k["percent"])
    langs = [ k["lang"] for k in rows ]
    percents = [ k["percent"] for k in rows ]

    fig, ax = plt.subplots(figsize=(8, 0.5 * len(rows) + 1))

    y_positions = range(len(langs))
    ax.barh(y_positions, percents)

    ax.set_yticks(y_positions)
    ax.set_yticklabels(langs)
    ax.set_xlabel("Translated")
    ax.set_xlim(0, 100)
    ax.set_title("Translation Progress")
    ax.set_ylim(-0.5, len(langs) - 0.5)

    for i, pct in enumerate(percents):
        ax.text(
            pct + 1,
            i,
            f"{pct:.1f}%",
            va="center",
            fontsize=9,
        )

    plt.tight_layout()
    if outPath == "-":
        fig.savefig(sys.stdout.buffer, dpi=150, format="PNG")
    else:
        fig.savefig(outPath, dpi=150)
    plt.close(fig)

def main():
    args = sys.argv
    if(len(args)) < 3:
        print(f"Usage: python {args[0]} <in .po files>... <out image>")
        return

    inPaths = args[1:-1]
    outPath = args[-1]
    create_chart(inPaths, outPath)

if __name__ == "__main__":
    main()

