# minisearch + ask.py

三人合作的迷你全文检索工具：给一个目录建一张索引表，再按关键词查这张表。
W3 在它上面加了一张「嘴」：把检索结果交给大模型，只按资料回答并标出处。

- 组别：D1　｜　代码目录：`groups/26级-D1/`
- 运行环境：Python 3.12（W2 只用标准库；W3 可选 `requests`），Windows + PowerShell
- W3 起需要一个大模型 key（DeepSeek / 通义 / 智谱任选，OpenAI 兼容即可）

## 目录结构

```
groups/26级-D1/
├── minisearch.py     命令行入口（argparse + 调用下面两个模块）
├── indexer.py        遍历目录、统计、生成索引
├── searcher.py       查关键词、拼输出
├── ask.py            W3：检索 + 调大模型 + 输出答案与出处
├── api.md            W3：接口说明（输入/输出/退出码/错误）
├── eval.md           W3：10 条评测题与真实输出
├── README.md         本文件
├── scope.md          这个工具做什么、不做什么
├── tests.md          8 条测试与真实输出
├── review.md         交叉互评记录
├── requirements.txt  W3 依赖（requests）
├── tools/            开发辅助：验题、造素材、假模型、一键助手
└── docs/             演示语料（含 scope.md 副本与两条边界素材）
```

测试素材放在 `tests/fixtures/`。

## W2：三条命令

在 `groups/26级-D1/` 下执行：

```powershell
python minisearch.py index docs              # 建索引，写出 index.json
python minisearch.py search docs python      # 查关键词
python minisearch.py index docs --top 10     # 每个文件保留 10 个高频词（默认 5）
python minisearch.py index docs --json       # 给程序读：只打印一个 JSON 对象
python minisearch.py search docs python --json
```

真实输出（`python minisearch.py index docs`）：

```
索引 4 个文件 → index.json
```

真实输出（`python minisearch.py search docs python`）：

```
docs/notes.txt: 2
  python 处理文件
docs/scope.md: 1
  - 一个目录（可以有任意层子目录），例如 `python minisearch.py index docs`
```

真实输出（`python minisearch.py search docs python --json`）：

```json
{
  "command": "search",
  "root": "docs",
  "keyword": "python",
  "count": 2,
  "hits": [
    {"path": "docs/notes.txt", "count": 2, "line": "python 处理文件"},
    {"path": "docs/scope.md", "count": 1, "line": "- 一个目录（可以有任意层子目录），例如 `python minisearch.py index docs`"}
  ]
}
```

`--json` 时 stdout 只有那一个 JSON 对象，提示与警告一律走 stderr；退出码与文本模式相同。

## W3：ask.py

```powershell
$env:LLM_API_KEY="你的key"
$env:LLM_BASE_URL="https://api.deepseek.com"   # 可选
$env:LLM_MODEL="deepseek-chat"                 # 可选

python ask.py ask "典型使用场景是什么？"
python ask.py ask "典型使用场景是什么？" --json
```

真实输出：

```
典型使用场景是：作业写完了想确认「某个词到底在哪个文件里出现过」，或者「哪份文档里出现得最多」。(docs/scope.md:8)

来源：docs/scope.md:8、docs/scope.md:25
```

流程：读 `index.json` → 关键词检索取前 3 行 → 与 `file:line` 一起拼进 Prompt → 调 chat completions
→ 输出答案与来源；**检索零命中时直接回答「文档里没有」，不调用模型**。

接口、错误码与四类错误的实测输出见 [`api.md`](api.md)；评测见 [`eval.md`](eval.md)。

## 评测（测出来的结论）

10 条：5 条能答、3 条该拒答、2 条边界。结果 **10 / 10 通过**，每条都带 `file:line` 出处。

```powershell
python tools\check_eval.py eval.md index.json   # 只验检索，不花钱
python tools\wizard.py                          # 1 准备 / 2 评测 / 3 错误处理
```

## 退出码

| 退出码 | 含义 |
| --- | --- |
| `0` | 成功：索引写好了 / 搜索有命中 / 问题得到回答或正确拒答 |
| `1` | 目录不存在、还没建索引、没有命中、缺 key、网络或模型报错 |
| `2` | 参数错误（`argparse` 自动给出） |

## 已知限制

- 中文不做分词，`top_words` 只到单字：英文/数字按词统计，中文每个字算一条，`words` 仍按空白切分。`search` 用子串包含，中文词组能查。
- 只索引 `.md` 和 `.txt`，非 UTF-8 文件跳过并在 stderr 警告，不中断。
- 检索是「中文两字组合 + 命中行数」排序，不是向量检索；换个说法可能搜不到。
- 每类资料只取前 3 行，答案跨段落时可能漏。
- 大目录全量读进内存；`search` 依赖当前目录的 `index.json`。
