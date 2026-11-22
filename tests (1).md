# tests.md · D1 组 8 条测试（W2）+ T10 补件

环境：Windows 11 + Python 3.12.14（中文 Windows 终端，UTF-8 输出）。
所有命令都在 `groups/26级-D1/` 目录下执行；`fixtures/` 已随仓库提交，照抄即可复现。
下面 `实际` 是真实的终端输出（Windows 下警告里的路径分隔符是 `\`，Linux 上是 `/`）。

8 条测试由 3 人分担：胡轩也负责 1、6；李福程负责 2、7；陆奕然负责 3、4、5、8。
另：T10（`--json` 输出，W2 补件）由胡轩也补。

---

## T1 正常目录（含子目录）· 胡轩也

- **输入**：`fixtures/site/`，含 `README.md`、`guide/intro.md`、`guide/install.txt`、`notes/dup.txt`、`notes/empty.md`、`notes/gbk.txt`（GBK 编码，故意放的）。
- **命令**：`python minisearch.py index fixtures/site/`
- **预期**：退出码 0；打印 `索引 5 个文件`（gbk.txt 被跳过）；index.json 里路径按 `/` 分隔且升序；每个文件的 `lines/words/chars/top_words` 齐全。
- **实际**：

```
索引 5 个文件
警告：跳过非 UTF-8 文件：fixtures\site\notes\gbk.txt
```

index.json 中 5 条记录（`path / lines / words / chars / top_words`）：

```
README.md           6   42   94  [['python',2],['个',2],['文',2],['用',2],['的',2]]
guide/install.txt   3   15   92  [['python',2],['docs',1],['first',1],['index',1],['install',1]]
guide/intro.md      5   37   71  [['索',3],['python',2],['引',2],['门',2],['md',1]]
notes/dup.txt       3    8   46  [['python',4],['file',2],['end',1],['the',1]]
notes/empty.md      0    0    0  []
```

- **是否通过**：✅ 通过。子目录被递归扫到，gbk.txt 不在索引里，文件按路径升序。

---

## T2 空目录 · 李福程

- **输入**：`fixtures/empty/`（目录里只有 `.gitkeep`，不是 `.md`/`.txt`）。
- **命令**：`python minisearch.py index fixtures/empty/`
- **预期**：退出码 0；打印 `索引 0 个文件`；生成 `files: []` 的空索引，不报错。
- **实际**：

```
索引 0 个文件
```

此时 index.json：

```json
{
  "files": [],
  "root": "fixtures/empty"
}
```

- **是否通过**：✅ 通过。（测完记得跑 `python minisearch.py index fixtures/site/` 把索引恢复成正常数据）

---

## T3 空文件 · 陆奕然

- **输入**：`fixtures/site/notes/empty.md`，0 字节。
- **命令**：`python minisearch.py index fixtures/site/` 后查看该文件记录。
- **预期**：`lines = 0`、`words = 0`、`chars = 0`、`top_words = []`，且不影响其他文件。
- **实际**：

```
notes/empty.md      0    0    0  []
```

- **是否通过**：✅ 通过。三个计数都是 0，没有出现除零或空列表报错。

---

## T4 目录不存在 · 陆奕然

- **输入**：不存在的路径 `fixtures/does-not-exist`。
- **命令**：`python minisearch.py index fixtures/does-not-exist`（Windows PowerShell 下可用 `echo $LASTEXITCODE` 看退出码）
- **预期**：打印 `目录不存在：fixtures/does-not-exist`，退出码 1，不生成/不覆盖 index.json。
- **实际**：

```
目录不存在：fixtures/does-not-exist
（退出码：1）
```

- **是否通过**：✅ 通过。退出码 1，index.json 没有被改写。

---

## T5 非 UTF-8 文件 · 陆奕然

- **输入**：`fixtures/site/notes/gbk.txt`，内容用 GBK 编码写入（`bytes` 里不是合法 UTF-8）。
- **命令**：`python minisearch.py index fixtures/site/`
- **预期**：stderr 打一条 `警告：跳过非 UTF-8 文件：...`；该文件不进索引；其余文件正常；退出码 0。
- **实际**：

```
索引 5 个文件
警告：跳过非 UTF-8 文件：fixtures\site\notes\gbk.txt
```

（索引里没有 `notes/gbk.txt`，stdout 与 stderr 分开，警告没混进“索引 5 个文件”这行）

- **是否通过**：✅ 通过。跳过且不中断，退出码 0。

---

## T6 同一个词出现多次，计数是否对 · 胡轩也

- **输入**：`fixtures/site/notes/dup.txt`，正文：

```
python python python python
file file
the end
```

- **命令**：`python minisearch.py index fixtures/site/` 然后 `python minisearch.py search "python"`
- **预期**：`notes/dup.txt` 记 4 次、排第一；`README.md` 2 次、`guide/install.txt` 2 次、`guide/intro.md` 2 次；次数相同按路径升序。
- **实际**：

```
fixtures/site/notes/dup.txt: 4
  python python python python
fixtures/site/README.md: 2
  python 适合写小工具，python 的 pathlib 很好用。
fixtures/site/guide/install.txt: 2
  install python first
fixtures/site/guide/intro.md: 2
  python 是一门脚本语言，python 的标准库够用。
```

- **是否通过**：✅ 通过。4 次与人工数一致；2 次的三个文件按路径升序排列；匹配行是文件里第一次出现的那一行。

---

## T7 中文关键词搜索 · 李福程

- **输入**：关键词 `索引`，对 `fixtures/site/` 的索引检索。
- **命令**：`python minisearch.py search "索引"`
- **预期**：能命中中文子串，不做分词；`guide/intro.md` 2 次（“再做索引”“索引 只统计”），`README.md` 1 次；按次数降序。
- **实际**：

```
fixtures/site/guide/intro.md: 2
  先读文件，再做索引，最后检索。
fixtures/site/README.md: 1
  这个目录用来演示 minisearch 的索引结果。
```

- **是否通过**：✅ 通过。中文按原子串匹配，次数和匹配行都对；`索引` 出现在句子中间也能命中。

---

## T8 搜不到的关键词 · 陆奕然

- **输入**：关键词 `zzz不存在`。
- **命令**：`python minisearch.py search "zzz不存在"`
- **预期**：只打印 `没有找到 "zzz不存在"`，不打印任何文件行，退出码 0。
- **实际**：

```
没有找到 "zzz不存在"
（退出码：0）
```

- **是否通过**：✅ 通过。文案与预期完全一致，没有多余输出。

---

## T10 `--json` 输出（W2 补件，第 10 条）· 胡轩也

- **输入**：`fixtures/site/`（5 个可索引文件 + 1 个 GBK 文件）；换成仓库真实文档时把命令里的目录改成 `docs/` 即可。
- **命令**（四条按顺序执行，全部不需要 key）：

```bash
python minisearch.py index fixtures/site/
python minisearch.py index fixtures/site/ --json
python minisearch.py search "python"
python minisearch.py search "python" --json
```

- **预期**：第 1、3 条走 stdout 给人看；第 2 条 JSON 走 stdout、`索引 5 个文件` 改走 stderr；第 4 条 JSON 数组走 stdout、`"python" 命中 4 个文件` 走 stderr。四条退出码都是 0，`--json` 的 stdout 里不能混进任何中文提示。
- **实际**：

第 1 条 `python minisearch.py index fixtures/site/`（退出码 0）：

```
索引 5 个文件
警告：跳过非 UTF-8 文件：fixtures\site\notes\gbk.txt
```

第 2 条 `python minisearch.py index fixtures/site/ --json`（退出码 0，stdout 共 120 行，与同目录 `index.json` 逐字节一致）：

```json
{
  "files": [
    {
      "chars": 94,
      "lines": 6,
      "path": "README.md",
      "top_words": [
        [
          "python",
          2
        ],
        [
          "个",
          2
        ],
        [
          "文",
          2
        ],
        [
          "用",
          2
        ],
        [
          "的",
          2
        ]
      ],
      "words": 42
    },
    {
      "chars": 92,
      "lines": 3,
      "path": "guide/install.txt",
      "top_words": [
        [
          "python",
          2
        ],
        [
          "docs",
          1
        ],
        [
          "first",
          1
        ],
        [
          "index",
          1
        ],
        [
          "install",
          1
        ]
      ],
      "words": 15
    },
    {
      "chars": 71,
      "lines": 5,
      "path": "guide/intro.md",
      "top_words": [
        [
          "索",
          3
        ],
        [
          "python",
          2
        ],
        [
          "引",
          2
        ],
        [
          "门",
          2
        ],
        [
          "md",
          1
        ]
      ],
      "words": 37
    },
    {
      "chars": 46,
      "lines": 3,
      "path": "notes/dup.txt",
      "top_words": [
        [
          "python",
          4
        ],
        [
          "file",
          2
        ],
        [
          "end",
          1
        ],
        [
          "the",
          1
        ]
      ],
      "words": 8
    },
    {
      "chars": 0,
      "lines": 0,
      "path": "notes/empty.md",
      "top_words": [],
      "words": 0
    }
  ],
  "root": "fixtures/site"
}
```

stderr（与 JSON 分开，没污染 stdout）：

```
警告：跳过非 UTF-8 文件：fixtures\site\notes\gbk.txt
索引 5 个文件
```

第 3 条 `python minisearch.py search "python"`（退出码 0）：

```
fixtures/site/notes/dup.txt: 4
  python python python python
fixtures/site/README.md: 2
  python 适合写小工具，python 的 pathlib 很好用。
fixtures/site/guide/install.txt: 2
  install python first
fixtures/site/guide/intro.md: 2
  python 是一门脚本语言，python 的标准库够用。
```

第 4 条 `python minisearch.py search "python" --json`（退出码 0）：

```json
[
  {
    "path": "fixtures/site/notes/dup.txt",
    "count": 4,
    "line": "python python python python"
  },
  {
    "path": "fixtures/site/README.md",
    "count": 2,
    "line": "python 适合写小工具，python 的 pathlib 很好用。"
  },
  {
    "path": "fixtures/site/guide/install.txt",
    "count": 2,
    "line": "install python first"
  },
  {
    "path": "fixtures/site/guide/intro.md",
    "count": 2,
    "line": "python 是一门脚本语言，python 的标准库够用。"
  }
]
```

stderr：

```
"python" 命中 4 个文件
```

- **是否通过**：✅ 通过。四条退出码都是 0；`--json` 的 stdout 只含 JSON、摘要全部走 stderr；第 4 条的 `count`/`line` 与第 3 条的人工可读输出一一对应（4/2/2/2，匹配行都是文件里第一次出现的那一行）。
- **写法说明**：本仓库的 `minisearch.py` 里 `index` 必须显式给目录、`search` 只能有一个关键词，所以写成
  `index fixtures/site/ --json`、`search "python" --json`。写成 `index --json`（少目录）或
  `search docs python`（多一个位置参数）会被 argparse 直接拒绝：退出码 2，stderr 打印
  `error: the following arguments are required: directory` / `error: unrecognized arguments: python`。

---

## 补充回归（不计入 8 条，但每次改代码都跑）

1. **两次运行一致**：`python minisearch.py index fixtures/site/` 连跑两次，`index.json` 的 MD5 都是 `BE6E000E4B7CD52B886F1E115C033A7A`（逐字节一致）。
2. **大小写**：`python minisearch.py search "PYTHON"` 的输出与 `search "python"` 完全一致（英文不区分大小写）。
3. **`--json` 分离输出**：`python minisearch.py index fixtures/site/ --top 2 --json`，JSON 走 stdout，`索引 5 个文件` 走 stderr。
4. **索引缺失**：删掉 index.json 后 `python minisearch.py search "python"` 打印 `索引文件不存在：index.json（先运行 python minisearch.py index <目录>）`，退出码 1。
5. **空关键词**：`python minisearch.py search "   "` 在 stderr 打印 `关键词不能为空`，退出码 2。

## 复现方法（一键）

```bash
cd groups/26级-D1
python minisearch.py index fixtures/site/   # T1/T5/T6 前提
python minisearch.py index fixtures/empty/  # T2
python minisearch.py index fixtures/does-not-exist  # T4
python minisearch.py index fixtures/site/   # 恢复索引
python minisearch.py search "python"        # T6
python minisearch.py search "索引"           # T7
python minisearch.py search "zzz不存在"      # T8
python minisearch.py index fixtures/site/ --json    # T10-2
python minisearch.py search "python" --json         # T10-4
```
