#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_iconv_to_dic.py - 让 .dic 的源形与 .aff 的 ICONV 保持一致。

背景:
    ICONV 在 Hunspell 里是**输入**折算：查询先被改写，再进查词/词形分析。
    因此 .aff 里写了 `ICONV 圖 図` 之后，`.dic` 里以 `圖` 为源形的行
    （單字行或 `圖書館 st:…` 这类词级行）就永远命中不了——输入已经变成 `図`。
    结果是映射静默失效，spell() 侧看不出来。

做法:
    把每一行的 head 用同一张 ICONV 表折算一遍，其余（flags / st: / morph）不动。
      - `圖/Zz st:図`   -> `図/Zz st:図`
      - `關聯圖 st:関連図` -> `関連図 st:関連図`
      - `彎曲 st:湾曲`  -> `弯曲 st:湾曲`（逐字折算，目标不动）
    折算后若与已有行重复则去重；去重时忽略未定义旗标 Zz，
    因为折叠会让「一边带 Zz、一边不带」的同一条词相遇。
    Zz 的补全交给 add_homonym_flag.py（本脚本之后跑一次）。

用法:
    python3 apply_iconv_to_dic.py ja_JP.aff ja_JP.dic            # dry-run
    python3 apply_iconv_to_dic.py ja_JP.aff ja_JP.dic --apply
    python3 apply_iconv_to_dic.py ja_JP.aff ja_JP.part.txt --plain --apply

    --plain  源文件没有行数头（如 mazegaki-dic/ja_JP.part.txt）
"""
import argparse
import os
import re
import shutil
import sys

HOMONYM_FLAG = "Zz"


def read_iconv(aff_path):
    """返回 {源字: 目标字}，只取单字对单字、且两者不同的行。"""
    pairs = {}
    with open(aff_path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("ICONV"):
                continue
            parts = line.split()
            if len(parts) < 3 or parts[1].isdigit():
                continue
            src, dst = parts[1], parts[2]
            if len(src) == 1 and len(dst) == 1 and src != dst:
                pairs[src] = dst
    return pairs


def strip_homonym_flag(flags):
    """FLAG long：按两字符一组去掉 HOMONYM_FLAG。"""
    tag = HOMONYM_FLAG
    return "".join(
        flags[i:i + 2] for i in range(0, len(flags) - 1, 2)
        if flags[i:i + 2] != tag
    )


def main():
    ap = argparse.ArgumentParser(description="按 .aff 的 ICONV 折算 .dic 的 head")
    ap.add_argument("aff")
    ap.add_argument("dic")
    ap.add_argument("--plain", action="store_true", help="文件没有行数头")
    ap.add_argument("--apply", action="store_true", help="落盘（默认 dry-run）")
    args = ap.parse_args()

    pairs = read_iconv(args.aff)
    if not pairs:
        sys.exit("未从 .aff 读到单字 ICONV 对")

    def iconv(s):
        return "".join(pairs.get(ch, ch) for ch in s)

    with open(args.dic, encoding="utf-8") as f:
        lines = f.read().split("\n")
    header, body = (None, lines) if args.plain else (lines[0], lines[1:])

    out, seen, changed, dropped, folded = [], set(), 0, 0, 0
    for line in body:
        if not line:
            continue
        headfield, sep, morph = line.partition(" ")
        head, slash, flags = headfield.partition("/")
        new_head = iconv(head)
        if new_head != head:
            changed += 1
            headfield = new_head + (slash + flags if slash else "")
        # 折算后 st: 目标可能正好等于源形（原本 圖→図，现在 図→図）。
        # 这种自指 st: 没有信息，去掉；词条本身还在。
        targets = re.findall(r"st:(\S+)", morph)
        if targets and all(t == new_head for t in targets):
            morph = re.sub(r"(?:^|\s)st:\S+", "", morph).strip()
            sep = " " if morph else ""
            folded += 1
        rest = (sep + morph) if sep else ""
        key = (new_head, strip_homonym_flag(flags), rest)
        if key in seen:
            dropped += 1
            continue
        seen.add(key)
        out.append(headfield + rest)

    print(f"[info] ICONV 单字对: {len(pairs)}")
    print(f"[info] 改写 {changed} 行 | 自指 st: 折叠 {folded} 行 | "
          f"去重丢弃 {dropped} 行 | {len(body)} -> {len(out)}")
    shown = 0
    for line in body:
        head = line.split(" ")[0].split("/")[0]
        if head and iconv(head) != head and shown < 8:
            rest = line[len(head):]
            print(f"   {line}  ->  {iconv(head)}{rest}")
            shown += 1

    if not args.apply:
        print("[dry-run] 未写入。加 --apply 落盘。")
        return

    bak = args.dic + ".bak"
    shutil.copy2(args.dic, bak)
    text = "\n".join(([str(len(out))] if header is not None else []) + out) + "\n"
    with open(args.dic, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(f"已写入 {args.dic}（备份 {bak}）")


if __name__ == "__main__":
    main()
