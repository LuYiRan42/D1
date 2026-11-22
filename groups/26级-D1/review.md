# review.md — 交叉互评

- 组别：**D1**（陆奕然 / 胡轩也 / 李福程）
- 互评对象：**D2**（倪生浩 / 李科学 / 史智轩）
- 代码来源：课程仓库 `yangtianlong407-afk/XiW` 的 **PR #15 `Nishenghao:w2-d2`**（`groups/26级-D2/`，head `48d8519`），不是猜的，下面每条都能对上文件行。
- 状态：**已完成**（W2 时我们只留了空壳并写了原因，这一版把两条都补上了）。

---

## 一、我们给 D2 的两条

### 1. 做得好的：`top_words` 一开始就按「英文分词、中文单字」统计

他们的 `analyze_file` 里是这么取词的（`groups/26级-D2/minisearch.py:43`）：

```python
text = re.findall(r'[a-zA-Z]+', context.lower()) + re.findall(r'[\u4e00-\u9fa5]', context)
```

英文按连续字母切、中文按单字切，`top_words` 直接就是对的。
这正是我们 W2 被要求返工的点——我们一开始写的是 `text.lower().split()`，中文整串算一个词，
`index.json` 里出现过 `"是一个迷你全文检索工具。"` 这种整句当词的条目（见我们 `scope.md` 第 40 行的说明）。
他们还顺手兜了 `PermissionError`（`minisearch.py:38`），这一点我们没做。这一条我们认输。

### 2. 可以更好的：`index.json` 里存了绝对路径，换个目录/换台机器就静默搜不到

`build_index` 写索引时是（`groups/26级-D2/minisearch.py:65`）：

```python
index = {"root": root.resolve().as_posix(), "files": files}
```

`root.resolve()` 把 `docs` 变成了绝对路径，于是仓库里的 `index.json` 长这样：

```json
"root": "C:/Users/NiShh/Desktop/XiW/groups/26级-D2/docs"
```

这带来两个问题：

1. **换台机器 clone 下来，`search` 会静默失败**。`search()` 里读文件失败的分支是
   `except OSError: continue`（`minisearch.py:95-96`），所有文件都被 `continue` 掉之后
   `results` 是空的，于是走到 `print(f'没有找到 "{keyword}"')`（`minisearch.py:114`），
   **退出码还是 0**。用户看到的是「没搜到」，而不是「索引路径不对」。
2. 本机用户名 `NiShh` 被写进了提交进仓库的文件里（他们 `tests.md` 第 40、49 行的输出也能直接看到）。

**我们实测过**：把 `groups/26级-D2/` 整个复制到另一个目录 `D:\社团\_check\d2run`，
不重新建索引，直接跑

```powershell
python minisearch.py search "python"
```

得到：

```
没有找到 "python"

exit=0
```

在原目录跑同样的命令是 `sub/b.txt: 3` + `a.md: 1`。重新 `index` 之后恢复，但输出变成了
`D:/社团/_check/d2run/docs/sub/b.txt: 3`，仍然是绝对路径。

**建议**：`root` 存相对路径（`docs`），读的时候按脚本目录拼：

```python
INDEX_PATH = Path(__file__).resolve().parent / "index.json"
root = Path(index["root"])          # "docs"
if not root.is_absolute():
    root = INDEX_PATH.parent / root
```

顺带输出就变成任务书要求的 `docs/sub/b.txt: 3` 这种形式了。

### 附带一条（不影响验收，供参考）

`--json` 只加在了 `index` 子命令上（`minisearch.py:130`），`search` 子命令没有
（`minisearch.py:132-133`）。W2 补件要求两个子命令都能给程序读，`search` 这边补一个会更好。

---

## 二、D2 给我们的两条（原文照抄，不改写）

摘自 `groups/26级-D2/review.md`：

> **bug**
> *   **现象**：跨目录执行 `search` 命令时，程序崩溃或提示找不到索引文件。
> *   **复现命令**：
>     1. 在根目录执行：`python minisearch.py index docs/`
>     2. 进入子目录：`cd docs`
>     3. 在子目录执行搜索：`python ../minisearch.py search ../docs/ python`
> *   **期望 vs 实际**：
>     *   期望：应该能正常搜出结果。
>     *   实际：报错提示"请先运行 index 建立索引"或抛出路径异常。

> **使用问题**
> *   **现象**：无法检索到子目录中的文件（如 `docs/guide/intro.md` 搜不到）。
> *   **建议**：`indexer.py` 第 13 行使用了 `base.glob("*")`，这只会遍历当前层，不会进入子文件夹。建议改成 `base.rglob("*")` 或 `base.glob("**/*")` 以支持递归遍历。

### 我们对第 1 条的处理：属实，已修

我们的 `index.json` 原来是按「当前工作目录」找的（`open("index.json")`），
在 `docs/` 里执行确实会报「请先运行 index 建立索引」。这一版改成固定按脚本目录找：

- `minisearch.py`：新增 `INDEX_PATH = Path(__file__).resolve().parent / "index.json"`，读和写都用它；
- `searcher.search(index, keyword, base=None)` 新增 `base` 参数，显示路径仍是 `docs/xxx.md`；
- `ask.py` 用 `HERE = Path(__file__).resolve().parent` 定位 `index.json` 和 `docs/`。

实测：在 `groups/26级-D1/docs/`、在 `C:\` 下分别执行
`python D:\D1\groups\26级-D1\minisearch.py search docs python`，都正常输出

```
docs/notes.txt: 2
  python 处理文件
docs/scope.md: 1
  - 一个目录（可以有任意层子目录），例如 `python minisearch.py index docs`
```

### 我们对第 2 条的处理：和代码对不上，判断是看了更早的版本

我们 `indexer.py` 第 13 行是 `def iter_files(root):`，真正遍历在第 18 行：

```python
for path in sorted(base.rglob("*")):
```

**从一开始就是 `rglob`**，不是 `base.glob("*")`。`tests.md` 第 3 条（`docs/guide/intro.md` 在子目录里）
和第 1 条（`docs/` 下 4 个文件含 `guide/intro.md`）都能证明确实递归了。
所以这条不需要改；如果他们在某个 commit 上看到过 `glob`，欢迎把 sha 发我们，我们照着复查。

---

## 三、自评（提 PR 前对一遍）

1. **接口先定死**：`index.json` 的七个字段在 README 里冻结，A 生产、B 消费、C 校验，三个人不需要读对方的实现。字段改了要走「群里说 → README 改 → 再改代码」。
2. **依赖单向**：`minisearch.py → indexer.py`、`minisearch.py → searcher.py`；`searcher.py` 不 import `indexer`。任何一个人换掉自己那个文件内部写法，另外两个都不用动。
3. **两次一致**：同一目录连续跑两次 `index`，`index.json` 逐字节相同，SHA256 = `352EC4C952AD0B10681745353790294BF4FEBEAFF6E1A6E7E6A86B4800DE85DD`（改了 `top_words` 口径后的新值，`tests.md` 有记录）。
4. **异常不吞**：非 UTF-8 文件跳过 + stderr 警告 + 退出码仍为 0；目录不存在退出码 1；参数错误退出码 2。三条都有实测记录在 `tests.md`。
5. **能在任意目录跑**：这是 D2 指出后修的，`minisearch.py`、`ask.py` 都按脚本目录定位 `index.json` 和 `docs/`，不用先 `cd`。
6. **三个人的 commit 都在 PR 里**：A 的 `indexer.py`、B 的 `searcher.py`/`minisearch.py`、C 的目录与文档，作者分别显示为 `Hxy070627-NUIST`、`liguchengniubi`、`LuYiRan42`。

## 四、我们踩过、写下来提醒自己的坑

- 网页上传文件很容易传错分支或传错目录（我们有过一次把 `indexer.py` 传到 `main` 根目录），**改代码走本地 git，别用网页上传**。
- 分支要基于 `w2-d1` 起，不是基于 `main`、也不是基于别人的个人分支，否则文件会落在仓库根目录。
- `tests.md` 里的实际输出必须从终端整段复制，手打的输出验收现场一跑就露馅。
- 索引里存绝对路径这种错，自己机器上永远测不出来——必须把整个目录复制到别处跑一次。这次就是 D2 提醒才发现我们自己的 `index.json` 也有同类问题（按 CWD 找）。
