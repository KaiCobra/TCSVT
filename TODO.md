# TCSVT 待辦清單

> 更新:2026-08-11。背後理由與實驗取捨見 `../docs/reports/TCSVT_migration_notes.md`。
> **圖例**:🔴 必做 ・ 🟡 建議 ・ 🔵 加分
> **狀態**:`[x]` 已做 ・ `[ ]` 待辦 ・ `[~]` 需先跑實驗 ・ `[?]` 需你決定

---

## 0. 這輪定案的四件事

| # | 決定 | 影響 |
|:--:|---|---|
| 1 | 投稿版的方法是 `τ = μ + κσ`,**正確的是 `τ_norm = h + κ(CV)·σ_norm`**;表格數字正確 | 方法章節與演算法**已改寫**(§1) |
| 2 | **全篇只考慮 method 15**,method 16/17 不列入 | 候選挑選相關內容全部移除;§V 改為「單發自適應閾值的分析與上限」 |
| 3 | ACM 沒上 → **不是期刊延伸稿** | 不用寫「與 preliminary version 的差異」聲明;審稿意見僅當作「已知弱點清單」參考 |
| 4 | 採用新章節架構 | **已實作**(§2) |
| 5 | 標題改為 *Attention-Masked Token Composition for Training-Free Image Editing with Visual Autoregressive Models* | 標題、running head、以及 intro/§IV-D 兩處品牌式宣稱**已改**(§1-2) |

---

## 1. ✅ 已完成:方法描述改成正確的公式

- [x] 🔴 `tex/5_method.tex` §IV-C 全新改寫成三段論證:
  1. **排序式閾值結構上不足** — 永遠選出前 (1−p) 比例的位置,無法表達「focus 該是空的」
     (add_object / change_style 的 source 端根本沒有對應區域)
  2. **`μ + κσ` 為什麼失效** — CV 的類別間差異幾乎全由 μ 驅動(σ 中位跨類 <2×、
     μ >3× 且方向相反)→ CV 實質在量「focus 佔全圖比例」;而 σ ≈ μ/10,
     所以 τ 幾乎由 μ 決定,κ 怎麼調都只動 −9.5%,但 coverage 卻從 19.4% 翻到 37.9%
  3. **最終公式**:min-max 正規化 → `τ = h + κ(CV)·σ̃`,並列出三個性質:
     κ_min=0 保證 τ ≥ h(h 仍是唯一有語意的旋鈕)、focus mask 可以是空的、
     ℓ 不是超參數

- [x] 🔴 `equations/Eq_methods.tex` 新增 `\EqNormalize` / `\EqKappa` / `\EqTau`,`\EqMasks` 改用正規化後的圖與 ℓ
- [x] 🔴 `equations/algor1.tex` Algorithm 1 重寫成 **Instance-Adaptive Mask Binarization**(原本是 hot-spot ratio → percentile)
- [x] 🔴 `equations/algor2.tex` Algorithm 2 更新(加入兩條 source 通道、明示 Phase 2 的 token 被丟棄)
- [x] 🔴 連帶改掉描述的四處:`1_abstract.tex`、`2_introduction.tex`(內文 + 貢獻列)、`7_experiments.tex` 的 implementation details
- [x] 🔴 移除 `tabs/ablationThreshold.tex` 的 (a) 表(adaptive vs 70/80/90% fixed percentile)—— 那是舊排序式公式的消融,新公式下不成立;(b) 的 IQR 部分拆成 `tabs/ablationIQRtable.tex` 保留

### 1-2. ✅ 標題與 "understanding" 宣稱

- [x] 🔴 `main.tex` `\title{}` 改為
      **Attention-Masked Token Composition for Training-Free Image Editing with Visual Autoregressive Models**
- [x] 🔴 `\markboth{}` running head 用短版 "Attention-Masked Token Composition for Training-Free Image Editing"
- [x] 🟡 內文兩處品牌式宣稱改寫成描述機制(我的判斷,可還原):
      - `tex/2_introduction.tex`:"realize an *understanding-before-editing* pipeline"
        → "localize the edit from the model's own attention before any token is rewritten"
      - `tex/5_method.tex` §IV-D:"Central to our *understanding-before-editing* design"
        → "Composition needs to know which regions the edit will affect before any token is replaced"
      理由:標題拿掉這個宣稱是因為它未經量測;內文留著會變成「有宣稱、沒證據、標題也不再幫忙鋪陳」,
      比原本更糟。全篇已無 "understanding-before-editing" 字樣。
- [ ] 🟡 **未動**:intro 第一條貢獻仍寫 "the **first** attention-map-driven editing framework for VAR"。
      AREdit / EditInfinity 都在這條線上,這個 "first" 是同類型的免費攻擊點,建議一併軟化。

### 還需要你確認的

- [ ] 🔴 **核對參數值**。我在論文裡寫的是
      `h = 0.50, c_min = 0, c_max = 0.20, κ_min = 0, κ_max = 0.60`
      (依 `m15_param_protocol` 的「論文採用」欄)。
      請對 Table 1 那個 result dir 的 CLI log 確認。
      兩處有 `% TODO(verify)` 標記:`tex/5_method.tex`、`tex/7_experiments.tex`。

- [?] 🟡 **要不要寫 `μ+κσ → h+κσ̃` 的演進?**
      我現在的寫法是把 `μ+κσ` 當成「一個自然但會失效的選擇」在 §IV-C 第二段駁掉,
      不提「我們以前用過」。既然 ACM 沒上、沒有公開的前版,這樣寫最乾淨。
      如果你想強調這是自己走過的路,可以在該段加一句 "in an earlier iteration of
      this work we used ...",但沒有必要。

---

## 2. ✅ 已完成:新章節架構

```
I.    Introduction                tex/2_introduction.tex
II.   Related Work                tex/3_relatedWorks.tex
III.  Preliminaries               tex/4_preliminaries.tex     ← 新拆出(含「兩條 source 通道」)
IV.   Methodology                 tex/5_method.tex            ← 重寫
        A. Overview
        B. IQR-Filtered Attention Aggregation
        C. Instance-Adaptive Mask Binarization   ← 正確公式 + Algorithm 1
        D. Three-Phase Editing Pipeline          ← Algorithm 2 + 顯式 coarse anchoring 的理由
V.    What Controls the Trade-off? tex/6_analysis.tex         ← 全新
        A. The Statistics Behind the Threshold
        B. h Traces a Smooth Frontier
        C. The Adaptive Term Shifts the Frontier Outward
        D. How the Parameters Were Obtained
        E. Phase 2 Contributes Structurally, Not Parametrically
        F. Composition Rule and Coarse Anchoring
        G. How Far Can a Single-Shot Threshold Go?
VI.   Experiments                 tex/7_experiments.tex
        A. Settings  B. SOTA 比較  C. Attention Masking vs Scale-N  D. IQR Filtering
VII.  Discussion and Limitations  tex/8_discussion.tex        ← 全新
VIII. Conclusion                  tex/9_conclusion.tex
Appendix A–E                      tex/A_appendix.tex
```

**新增的表**(數字全部來自 `docs/reports/`,每個檔頭都註明出處與 recipe):

| 檔案 | 內容 |
|---|---|
| `tabs/frontier_h.tex` | h 從 0.48 掃到 0.75(κ_max=0),10 個工作點 × 6 指標 |
| `tabs/adaptiveGain.tex` | 自適應項 vs 固定閾值 frontier 內插,SSIM 與 LPIPS 兩種口徑 |
| `tabs/protocol.tex` | 參數選擇(含 IR-only 退化列)+ `0_random` holdout |
| `tabs/ablationBeta.tex` | Phase 2 消融 3 個工作點 + 逐類別(delete_object 當天然對照) |
| `tabs/anchoring.tex` | (a) cum-prob vs 顯式 N=2 vs 無錨定;(b) ℓ 十點掃描的全距 |
| `tabs/ablationIQRtable.tex` | 從舊 ablationThreshold 拆出的 IQR 部分 |

**搬進正文的 supplementary 內容**:Algorithm 1 → §IV-C、Algorithm 2 → §IV-D、
`shape_diff` + `coarse2fine` 兩張圖 → §VI-C。

**沒有收進本 repo 的 ACM 版遺留**(不再被引用;需要時到 `KaiCobra/ACM-MM_edited` 取回):
`ablationThreshold.tex`、`ablationPhase2.tex`(被 `ablationBeta` 取代)、
`ablationDynamic.tex` + `ablationDynamic.png`(percentile mask 的質化圖,公式改了就不成立)、
`whyUseDiscrete.tex` + `whyUseDiscrete.png`(caption 本來就是 `Nothing here`)、
`ablationIQR.tex`(空檔案)、`pipeline.png`(舊版,現用 `pipeline2.png`)。

### 靜態檢查結果(重構後)

39 個 tex / 62 labels / 48 refs 無 dangling ・ 17 張圖 ・ 8 張表 ・
所有 `\input` 目標與圖檔存在 ・ cite key 全部在 `main.bib` ・ 環境與括號配對正確。

---

## 3. 🔴 我留空的地方(11 處,全部有 `% TODO`)

### 3-1. `tex/0_authors.tex` — 整個作者區塊

| # | 欄位 | 現況 |
|:--:|---|---|
| 1 | 作者姓名 | `Anonymous~Author` ×3 |
| 2 | IEEE membership | `Student Member / Member / Senior Member` 佔位(非會員就把 `\IEEEmembership{}` 刪掉) |
| 3 | 單位 / 城市 / 國家 | `[Department], [University], [City, Country]` |
| 4 | e-mail | `[e-mail]` |
| 5 | 通訊作者 | `Corresponding author: [name]` |
| 6 | 投稿 / 修訂日期 | `Manuscript received XX XX, 20XX` |
| 7 | 經費 | `supported in part by [funding agency, grant no.]`(沒有就刪整行) |
| 8 | 彩圖聲明 | 接受後才有,初稿可註解掉 |
| 9 | DOI | 同上 |

> TCSVT 是**單盲**(作者具名),所以初稿就要填真名。

### 3-2. `main.tex`

| # | 位置 | 現況 |
|:--:|---|---|
| 10 | `\markboth{}` | `Vol.~XX, No.~XX` 可以留;但 `Author \MakeLowercase{\textit{et al.}}` 要換成第一作者姓 |
| 11 | `\begin{IEEEbiography}` | 整段註解著。**最終版必須有**每位作者小傳 + 1in×1.25in 照片 |

---

## 4. 🔴 無法驗證的事:沒有 TeX 可編譯

這台機器沒有任何 TeX 發行版(`pdflatex` / `kpsewhich` / `tlmgr` 全系統搜尋皆無),
所以**這份稿子從未被實際編譯過**。上面 §2 的檢查是靜態 lint。

真編譯才抓得到的風險:

- `hyperref` + IEEEtran 的 `\IEEEmembership` 相容性
- `subcaption` 與 IEEEtran 內建 caption 的衝突(影響 §VI-C 的 `shape_diff`)
- `algorithm` 浮動在兩欄下的排版(現在有兩個演算法都在 §IV,可能擠)
- `\resizebox{\linewidth}` 的六張新表在 IEEE 單欄寬下會不會太小
- `\rowcolor` 在 `\resizebox` 內的行為(`ablationBeta` / `anchoring` / `protocol` 有用)

```bash
cd TCSVT_edited && latexmk -pdf main.tex
```

- [?] 要我裝 TinyTeX(~250 MB,`~/.TinyTeX`,可完整移除)跑一次真 build 嗎?

---

## 5. 🔴 內容還要處理的

### 5-1. Config 不一致(最重要)

`tex/6_analysis.tex` 開頭有一個大的 `⚠ CONFIG NOTE`:

**§V 的每一個數字都來自 `minimal rewrite + cum0 + N2` 的 recipe,
而 Table 1 是另一個 config。**

三個選項,挑一個:

- [?] (a) 用 §V 的 recipe 重跑 Table 1
- [?] (b) 用 Table 1 的 recipe 重跑 §V 的所有實驗
- [?] (c) 在 §V 開頭明講兩者的差異

⚠️ 不能就這樣放著。這是這批報告最容易出事的地方 —— 混用世代的數字。

### 5-2. Table 1

- [ ] 🔴 加 baseline:**EditInfinity**(NeurIPS 2025, arXiv 2510.20217)、**BitResEdit**、**VARIN**
      → `tex/7_experiments.tex` 有 `% TODO(baselines)` 標記
- [ ] 🔴 加兩欄:**mask 來源**(外部分割 / 手畫 / 自動 attention)、**是否需 per-image 訓練**
      → 這兩欄是你在「不用外部 mask + 不用訓練」象限唯一的證據
- [ ] 🟡 resolution 不一致 → caption 說明,或補同解析度重跑
- [?] 🔵 要不要加一列 preservation-first 工作點(高 h)?
      ⚠️ 必須是**與 Table 1 其餘列同 config** 的真跑,不能拿 §V 的臂直接貼

### 5-3. AREdit 比較(已改寫,但要確認語氣)

- [x] `tex/7_experiments.tex` 已從「uniformly better across all six」改成誠實版:
      我們贏 SSIM / LPIPS / CLIPw / CLIPe,AREdit 贏 S.D. / PSNR;
      並補上兩點差異(它要 per-category 閾值、我們的工作點是連續可調的)
- [?] 若採用 5-2 的 preservation-first 列,這段可以再加一句(已留 `% TODO(optional)`)

### 5-4. 還沒寫的附錄

`tex/A_appendix.tex` 已寫好兩節(Implementation Details、Evaluation Protocol),
另外三節是骨架 + 內容清單:

- [ ] 🟡 **Appendix C — T2I 編輯模式**:從舊 supplementary 搬質化結果過來
- [ ] 🟡 **Appendix D — Focus-word 抽取的失敗模式**:
      230/700 案 source prompt 差分不出 focus(add 75/80、style 76/80);
      條件式最小補丁在被補丁類別 IR +0.19~+0.41 且保留零損失;
      整句改寫嚴格傷分且隨長度單調(0.653 → 0.372 → 0.206)。
      ⚠️ **主表不要含 rewrite 模組** —— 定位成「失敗模式分析 + 可選前處理」,
      否則會被質疑 training-free 的定義被稀釋(用了外部 LLM)
- [ ] 🟡 **Appendix E — 更多質化結果**:每類別 2–3 組。期刊附錄有空間,
      這是回應「evaluation scope 太窄」最便宜的做法

### 5-5. ✅ 圖已補齊(17 張)

`figs/make_paper_figures.py` 從原始 per-case 評估輸出重新產生所有分析圖(英文、論文口徑)。
報告裡的原圖不能用:`m14_no_beta_ablation` / `m14_minimal_rewrite_pipeline` 的圖是**中文軸標**,
質化圖的欄位標題也是中文燒進去的。

新增:`fig_cv_decomposition`(CV 分解)、`fig_frontier_h`、`fig_adaptive_frontier`(增益殘差)、
`fig_protocol`(搜尋範圍 + 效用面 + LOCO)、`fig_beta_frontier` / `fig_beta_category` /
`fig_beta_qualitative`、`fig_anchoring`、`fig_besth_vs_cv`、`fig_blend`。

重跑時修正的三個數字:平坦區 45%(非 48%)、LOCO 共識 (0.175, 0.55)(非與全域最優重合)、
144/700 案的 unedited-region 指標為 NaN 故須逐指標 nanmean。

~~原本待做的產圖(已完成)~~:

- [ ] 🟡 CV / σ / μ 的 violin plot + τ-vs-coverage 對照
      → `docs/reports/pie_attn_cv_analysis/make_violin.py`、`make_kappa_compare.py`
- [ ] 🟡 參數 protocol 三連圖(Stage-1 CV 直方圖 + 搜尋範圍、Stage-2 frontier 散點、
      效用 heatmap + 9 折 LOCO 最優)
      → `docs/reports/m15_param_protocol/run_protocol.py`
- [ ] 🟡 h-frontier 曲線圖(PSNR–IR)
      → `docs/reports/m14_no_beta_ablation/make_figures.py` 已有 frontier 版本

---

## 6. 🔴 要先補跑的實驗

| # | 實驗 | 為什麼 | 指令 / 狀態 |
|:--:|---|---|---|
| 1 | **參數 protocol 的 Stage 4 真跑確認** | 報告 §5 明說還沒跑;§4 已量到**離線模擬對 IR 高估 ~0.055**。§V-D 的 caveat 段已誠實寫出這件事,但最好是跑完把它改成「已確認」 | `bash scripts/exp_m15_param_consensus.sh` |
| 2 | **Config 統一**(見 5-1) | §V 與 Table 1 recipe 不同 | 依你選 (a)/(b)/(c) |
| 3 | 🟡 同解析度 baseline 重跑 | Table 1 的 resolution 欄不一致 | — |

> method 16/17 相關的真跑需求(runtime `--tau_candidates`)**已不需要** —— 全篇只用 method 15。

---

## 7. 已知弱點 → 目前的處理位置

ACM 沒上,所以下表純粹當「這些弱點是真的、TCSVT 審稿人也可能提」的檢查表。

| 弱點 | 目前寫在哪 | 狀態 |
|---|---|---|
| coarse-scale anchoring 剝奪幾何編輯能力 | §VII-A + §VI-C(`shape_diff` 已搬進正文)+ §V-F | ✅ 已從 limitation 改寫成「量化過的取捨 + 可調 N」 |
| hard mask 阻斷光影互動 | §VII-B(full-res blend 當 preliminary study,誠實給雙向取捨) | 🟡 要不要放由你決定(有 `% TODO(optional)`) |
| N=2 的理由沒說清楚 | §IV-D + §V-F(cum-prob 是隱性有偏錨定,顯式 N=2 PSNR +1.66 / LPIPS −0.013) | ✅ |
| 閾值規則沒說清楚、傷 reproducibility | §IV-C + Algorithm 1 + §V-D 四階段 protocol + Appendix A/B | ✅ |
| design choices 是 heuristic | §V-D(統計推導搜尋空間、單指標會退化、LOCO 9/9、平坦區 48%) | ✅ |
| prompt 不對稱時的 robustness | §VII-D + Appendix D | 🟡 附錄待寫 |
| 只在 PIE-Bench 上測 | — | ⚠️ 未處理。GranD-f 那條線(mask 品質 AUROC)這次沒放進來 |
| understanding-before-editing 缺直接證據 | **已從標題與內文移除**(2026-08-11)。標題改為 Attention-Masked Token Composition...;intro 與 §IV-D 的兩句品牌式宣稱改寫成描述機制 | ✅ 不再宣稱,故不需要 mask-vs-GT 量化;若日後想放回,需先補 GranD-f AUROC 並處理與 §VI-D IQR 消融的張力 |
| 「勝過 AREdit 全部六項」不正確 | §VI-B | ✅ 已改成 4 勝 2 負 + 差異說明 |
| baseline 解析度不一致 | §VI-B(`% TODO(R3-W9)`) | ⚠️ 待處理 |

> 兩個我這次**刻意沒放**的東西,想加再說:
> - **GranD-f mask 品質(AUROC)** —— 它會和 §VI-D 的 IQR 消融打架
>   (GranD-f 上 block 級 IQR 是負貢獻,PIE 上 with-IQR 比較好),
>   要處理這個張力得補一個 per-head IQR 的 PIE 下游實驗,成本不低
> - **full-res blend** —— §VII-B 現在只有一段文字,沒有表。要升級成完整小節的話
>   `docs/new_exp/` §2 的全量 700 三臂數字現成可用
