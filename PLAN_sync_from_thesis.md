# 從 NTUST 中文論文同步回 TCSVT — 逐段逐行修改清單

> 來源:`NTUST_Thesis_Kai/`(2026-08-17 10:48 版)
> 目標:`TCSVT_edited/`
> 原則:中文版是新的 source of truth。以下每一項都標注
> 「TCSVT 檔案:行號」→「中文版出處」→「英文改法」。

---

## 0. 先決三件事(會推翻我前兩輪的改動)

| # | 中文版怎麼做 | TCSVT 現況 | 動作 |
|---|---|---|---|
| 0-1 | 主表 ours 維持 **0.0316 / 23.44 / 0.8565 / 0.0833 / 0.2613 / 0.2290 / 0.2785 / 0.7344**(`tabs/relatedWorksComparison.tex:142-152`) | 已被我換成 (0.33,0.43) 真跑的 0.0421 / 22.53 / 0.8606 / … | **退回**原數值,並把四個欄位極值改回 SSIM max `0.8565`、LPIPS min `0.0833`、CLIPw max `0.2642`、IR max `0.7344` |
| 0-2 | 標記慣例 = **粗體最佳、底線次佳**(`tabs/relatedWorksComparison.tex:3`) | 已被我改成「粗體 = ours」,`\AutoCellUp/Down` 第 4 參數語意也改了 | **退回** `main.tex` 的巨集(恢復「等於極值→粗體、旗標 1→底線」),並把八張表的標記還原 |
| 0-3 | 參數寫 **$c_{\max}=0.33$、$\kappa_{\max}=0.43$**(`chapters/4_result.tex:19`) | 我已改成 0.33/0.43 ✓ | **保留**。注意中文版是「舊分數 + 新參數」的組合,這是刻意的 |

> 0-1 與 0-3 的組合意味著:主表數字與 §V 的校準敘事來自不同的跑,中文版選擇不去對齊,
> 而是用 §4.4 開頭的「本節數字的口徑」段落把兩者切開(見 3-1)。

---

## 1. `tex/1_abstract.tex`

**第 13 行(整段)** ← `front-matter/en_abstract.tex:6`(中文版已有英文摘要,直接採用)

中文版英文摘要與目前 TCSVT 摘要的差異:
- 中文版**保留** `\textit{understanding-before-editing}` 這句:
  "Guided by an \textit{understanding-before-editing} philosophy, the model first resolves
  which spatial regions correspond to the edit via its own cross-modal attention, then
  rewrites only the targeted tokens."
  → TCSVT 目前沒有這句(標題改掉後被拿掉了)。**要加回來**。
- 中文版結尾:"attains the best SSIM and LPIPS among recent training-free baselines together
  with competitive editing quality, while providing a simpler, faster, and inversion-free pipeline."
  → 取代我上一輪寫的「best SSIM and CLIP whole … second on LPIPS」整句。
- 中文版**沒有**我加的 "whose parameters are calibrated so that…" 與 "the instance-adaptive
  correction is a small refinement…" 兩句 → **刪除**。

⚠️ 決策點:標題已改成 "Attention-Masked Token Composition…",摘要若放回
`understanding-before-editing`,兩者調性要一致。建議保留(它是 Phase 2 的說理依據)。

---

## 2. `tex/2_introduction.tex`

| TCSVT | 中文版出處 | 改法 |
|---|---|---|
| **第 6 行末** | `chapters/1_introduction.tex:6` | 中文版結尾是:「這些組件共同實現了一條 \textit{understanding-before-editing} pipeline」。TCSVT 目前寫的是 "Together, these components localize the edit from the model's own attention before any token is rewritten" —— 語意相同但沒有名字。**改成點名 understanding-before-editing** |
| **第 6 行中段** | 同上 | 中文版把 binarization 的說理**縮短**成一句「二值化 threshold 則會根據每個實例的 attention distribution 形狀自適應地進行校準」。TCSVT 目前有三句長論證(rank-based / mean-relative 為何失敗)。**建議保留 TCSVT 的長版**——期刊篇幅夠,且那是方法的核心賣點 |
| **第 15 行(貢獻 2)** | `chapters/1_introduction.tex:12` | 中文版簡化成「IQR-filtered attention aggregation 與 adaptive mask thresholding」,**拿掉了四階段 protocol 的描述**。TCSVT 現在還寫著 "derive the rule's parameters through a four-stage protocol --- statistical derivation of the search space, offline grid search under a composite objective, leave-one-category-out validation, and an untouched holdout category"。**必須改**:那套 protocol 已被三步校準取代 → 改成 "and calibrate its parameters in three steps, each tied to an independently checkable quantity" |
| **第 17 行(貢獻 3)** | `chapters/1_introduction.tex:14` | 中文版:「於 SSIM 與 LPIPS 兩項指標取得全表最佳、兩項 CLIP 指標取得次佳……且在單張 RTX 5090 上約 2.5 秒」。TCSVT 目前寫 "outperforms … across nearly all metrics"。**改成中文版的精確說法** |
| **第 19 行(貢獻 4)** | — | 中文版**沒有第 4 條貢獻**(我上一輪刪掉 §V-G 時已把它縮短)。中文版把 §V-G 的內容放回 §4.4.4,但**沒有**升格成貢獻。**維持現在的三條貢獻即可** |

---

## 3. `tex/6_analysis.tex` — 改動最大,等同重寫

中文版把這節放在第 4 章之內(`\section{Threshold 的統計依據與參數選擇}`,`sec:param_selection`),
結構是 **4 個 subsection**,而 TCSVT 目前是 6 個。對應如下:

| 中文版 | TCSVT 現況 | 動作 |
|---|---|---|
| §4.4 前言 + 「本節數字的口徑」+「雜訊尺度」(`4_result.tex:105-111`) | 第 20-48 行 | **大致可留**,但中文版的口徑段落更精確,見 3-1 |
| §4.4.1 變異係數實際編碼了什麼(`:114-128`) | §V-A 第 50-84 行 | 內容相同,**保留** |
| §4.4.2 $h$ 描出一條平滑的 frontier(`:131-145`) | §V-B 第 86-103 行 | 內容相同,**保留** |
| §4.4.3 **三步校準**(`:148-180`) | §V-C 第 105-154 行 + §V-D 第 155-215 行 | **兩節合併重寫成一節**,見 3-2 |
| §4.4.4 **為何 $h$ 只能是全域常數**(`:183-190`) | 已被我刪除 | **加回來**,見 3-3 |
| — | §V-E Phase 2(第 217-260 行) | 中文版把 β 消融放在 §4.3 消融實驗,**用簡單的 With/Without 兩列表**。見第 4 節 |
| — | §V-F 組合規則與錨定(第 262-286 行) | 中文版**沒有這節**。見 3-4 |

### 3-1. 口徑段落(TCSVT 第 28-39 行)

← `chapters/4_result.tex:107-108`。中文版比我寫的多了兩個具體資訊,要補進去:
- 明確列出那組固定設定的內容:「minimal prompt rewrite、二值合成、$N{=}2$、PIE-Bench 全 700 案例、seed 1」
  → 目前 TCSVT 只寫 "one common recipe" 沒說是什麼。
- 明確寫「每個實驗只變動其中一個成分」。

英文:
> Every row in this section is produced under one fixed recipe --- minimal prompt rewriting,
> binary composition, $N{=}2$, all 700 PIE-Bench cases, seed 1 --- and each experiment varies
> exactly one component of it, so rows within the section are comparable and any difference
> can be attributed to the component that was varied.

### 3-2. 三步校準(取代 TCSVT 第 105-215 行的 §V-C + §V-D)

← `chapters/4_result.tex:148-180` + `tabs/cvPercentile.tex`

**要刪掉的**:
- `\input{tabs/adaptiveGain}`(第 108 行)與 `tabs/adaptiveGain.tex` 整檔
- `\input{tabs/protocol}`(第 158 行)與 `tabs/protocol.tex` 整檔
- `\input{imgs/fig_adaptive_frontier}`(第 109 行)、`\input{imgs/fig_protocol}`(第 159 行)
- 四階段 protocol 的 Stage 1--4 全部文字(第 160-215 行)

**要新增的**:`tabs/cv_percentile.tex`(譯自 `tabs/cvPercentile.tex`)

新節標題:`\subsection{Three-Step Calibration: How the Parameters Were Obtained}`
`\label{sec:calibration}`

開頭:
> The parameters $(h, c_{\max}, \kappa_{\max})$ are neither hand-tuned nor grid-searched.
> We calibrate them in three steps, each tied to a quantity that can be checked independently:
> the operating point, the clamp rate, and the median of the threshold that is actually realized.

**步驟 1**(← `:155-156`):
> \noindent\textit{Step 1: $h$ is read off the frontier, not tuned.}
> Table~\ref{tab:frontier_h} is a measured curve, so choosing an operating point is the same as
> choosing a target threshold $\tau_{\mathrm{target}}$ on it. We take the balanced point
> $\tau_{\mathrm{target}} \approx 0.54$. Since $\kappa_{\min} = 0$ guarantees $\tau_k \ge h$ by
> construction, $h$ is the lower bound of $\tau_k$, and we set $h = 0.50$ as the base.

**步驟 2**(← `:158-159`):
> \noindent\textit{Step 2: $c_{\max}$ follows from the per-scale CV distribution.}
> The criterion is that $c_{\max}$ must be high enough for the mapping of
> Eq.~\ref{eq:kappa} to stay discriminative over the large majority of (case, scale) pairs; if
> $c_{\max}$ is too low, a large fraction is clamped at $\kappa_{\max}$ and the mapping stops
> doing anything. Table~\ref{tab:cv_percentile} lists the quantiles of $c_k$ over \emph{all}
> generation scales ($n = 14245$). We take $c_{\max} = 0.33$, about the 88th percentile, so only
> about $12\%$ of pairs are clamped. For contrast, $c_{\max} = 0.20$ sits at roughly the 65th
> percentile of this distribution and would clamp $35$--$41\%$ of scales, disabling the mapping
> for a third of them.

**步驟 3**(← `:161-169`),含新方程式 `eq:calib`:
> \noindent\textit{Step 3: $\kappa_{\max}$ is calibrated, not searched.}
> The requirement is simply that the median of the realized threshold land on the operating point
> chosen in Step 1. Let
> \begin{equation}
>     m = \operatorname{median}\!\Bigl(\operatorname{clamp}\bigl(c_k/c_{\max},\,0,\,1\bigr)\cdot
>     \tilde{\sigma}_k\Bigr), \label{eq:calib}
> \end{equation}
> measured as $m = 0.086$. Then
> $\kappa_{\max} = (\tau_{\mathrm{target}} - h)/m = (0.54 - 0.50)/0.086 \approx 0.47$.
> We use $\kappa_{\max} = 0.43$, for which the measured median $\tau_k$ is $0.537$ against the
> target $0.540$ --- an error of $0.003$.

**「為何必須使用逐尺度的統計量」**(← `:171-174`)—— 這段是中文版最重要的新增:
> \noindent\textbf{Why per-scale statistics are required.}
> Step 3 hides a detail that decides whether the calibration works at all: $\tilde{\sigma}_k$ is
> computed \emph{separately at each scale}, and it falls monotonically with depth --- its median
> goes from $0.299$ at the second scale to $0.139$ at the last, a factor of $2.15$. $c_k$ is
> likewise larger at the coarse scales, so $\kappa$ saturates at $\kappa_{\max}$ for $24$--$41\%$
> of cases depending on depth, and the induced focus coverage falls from $25\%$ at the second
> scale to $5.8\%$ at the last. The threshold is therefore tightest exactly where the layout is
> decided.
>
> This means Eq.~\ref{eq:calib} \textbf{must use the per-scale $\tilde{\sigma}$ (median $0.190$)}.
> Calibrating on the last scale alone ($0.138$) yields a $\kappa_{\max}$ larger by a factor of
> $1.38$, and the realized median $\tau_k$ lands at $0.58$ rather than the intended $0.54$ --- a
> different operating point on the frontier. The general lesson is that \textbf{any calibration
> performed on the statistics of a single scale does not transfer to the multi-scale run.}

**「自適應確實在作用」**(← `:176-177`):TCSVT 第 124-129 行已有,**保留**。

**「自適應項的貢獻有多大」**(← `:179-180`):TCSVT 第 116-122 行已有我寫的版本,
中文版內容一致(+0.012 / +0.012 / +0.006、HPS +0.0016~+0.0021、LPIPS −0.0012~−0.0018、
PSNR +0.24~+0.34),**保留**,但要移到本節末尾。

⚠️ 連帶:子節標題 `\subsection{The Adaptive Term Shifts the Frontier Outward}` 要改掉
(結論已經不是「往外推」)。中文版沒有對應標題,建議併入三步校準節。

### 3-3. 加回「為何 $h$ 只能是全域常數」

← `chapters/4_result.tex:183-190`。這是我上一輪刪掉的 §V-G,但中文版**重寫過**:
框架從「單次門檻的天花板」改成「為什麼 $h$ 必須是全域常數」,而且**換了新數據**。

新標題:`\subsection{Why $h$ Can Only Be a Global Constant}` `\label{sec:tau_predictability}`

> A natural follow-up is whether, $h$ being the only knob, its best value could be predicted per
> case. The answer is no, and the answer is quantified.
>
> A perfect per-case oracle that picks the best $h$ for every case would reach ImageReward
> $0.987$, well above the $0.777$ of a fixed $h{=}0.52$, so \textbf{the headroom is real}. The
> problem is the input signal. We examined twelve attention statistics --- normalized mean and
> standard deviation, coverage at several levels, entropy, skewness, kurtosis, the mass fraction
> in the top $5\%$, and others --- and \textbf{all of them correlate with the per-case optimal
> $h$ at $|\rho| \le 0.15$} ($c_k$ itself reaches only $0.11$). Widening the search to nineteen
> factors and four target definitions, the strongest correlation is $|\rho| = 0.23$, explaining
> about $5\%$ of the variance.
>
> Two direct attempts confirm this. Optimizing $(h, c_{\min}, c_{\max}, \kappa_{\max})$ jointly
> \emph{degenerates} to a fixed $h \approx 0.5$; and a gradient-boosting predictor of the
> per-case optimal $h$, fed with attention features, a one-hot editing category and CLIP
> features, loses to a plain fixed $h$ under 5-fold cross-validation. \textbf{Learnability is not
> the bottleneck; the input signal is.} We therefore treat $h$ as a global choice of operating
> point, with Sec.~\ref{sec:frontier} giving its full trade-off curve, rather than as a
> per-case prediction.

⚠️ 這段用的 oracle 數字是 **0.987**(對 fixed $h{=}0.52$ 的 0.777),
和我先前刪掉的舊版 §V-G 的 **1.024 @ SSIM 0.861** 不同。以中文版為準。

⚠️ 連帶:`tex/8_discussion.tex:51` 我寫的
`\subsection{The Threshold Is Global, Not Per Case}` 與這節重複,**刪掉那節**,
或改成一句話指向 `\ref{sec:tau_predictability}`。

### 3-4. §V-F 組合規則與錨定(TCSVT 第 262-286 行)

中文版**完全沒有**這節,也沒有 `tabs/anchoring.tex`、`imgs/fig_anchoring.tex`。

- [?] **決策點**:刪掉,還是留著?
  留著的理由:cum0 + N=2 是配方的一部分,審稿人可能會問「為什麼是 binary + explicit N」。
  刪掉的理由:中文版已經判定它不是主線,而且它跑在 $h{=}0.60$ 的固定臂上,config 不一致。
  **我的建議**:壓縮成 §V-B 末尾的兩句話 + 一個腳註,不留整節與整表。

---

## 4. `tex/7_experiments.tex`

| TCSVT | 中文版出處 | 改法 |
|---|---|---|
| **第 10-12 行 Metrics** | `4_result.tex:11,13` | 中文版**多一整段**講 HPS/IR 的計分口徑,TCSVT 目前只有半句。見 4-1。另外中文版明確寫「生成解析度為 1k,所有指標依 PIE-Bench 標準協定於 $512{\times}512$ 下計算」→ 這句直接解掉 `% TODO(resolution)` |
| **第 21-22 行 Implementation** | `4_result.tex:19` | 已對齊(0.33/0.43)✓。中文版多寫了 `\ell = h - 0.01 = 0.49` 的展開值,可補 |
| **第 30-38 行 Quantitative** | `4_result.tex:25` | **退回**成中文版:best SSIM (0.8565) 與 LPIPS (0.0833),CLIPw (0.2613) 與 CLIPe (0.2290) 次佳。並**新增中文版的最後一句**:見 4-2 |
| **第 40 行(新增)** | `4_result.tex:27-28` | **整段新增「人類偏好指標」**,見 4-3 |
| **第 42-43 行 vs diffusion** | `4_result.tex:31` | 退回成 SSIM +7.5\%、LPIPS +21.5\%(我上一輪算成 8.0\%/17.5\% 是配合新 ours,現在要退回) |
| **第 45-49 行 vs flow** | `4_result.tex:34` | 退回成中文版的簡短版:"we attain better SSIM and LPIPS despite the $6\times$ parameter gap, though ReFlex achieves higher PSNR" |
| **第 53 行 vs AREdit** | `4_result.tex:37` | 退回舊數字,並採用中文版的重點:**「更關鍵的差異在於 mask 的來源」**。見 4-4 |
| **第 69-80 行 Scale-N** | `4_result.tex:56-60` | 中文版多了一段質性說明(共享太少→背景退化、太多→阻礙編輯;VAR 早期尺度決定結構)。**補上**,見 4-5 |
| **第 81-88 行 IQR** | `4_result.tex:86-89` | 內容相同 ✓。中文版明確寫「完整模型(IQR-filtered,blocks 2--31)vs 直接對所有 32 個 block 平均」→ 補上這個對照定義 |
| **(新增子節)** | `4_result.tex:70-84` + `tabs/ablationThreshold.tex` | **新增「Instance-adaptive vs fixed percentile」消融**,見 4-6 |
| **(新增子節)** | `4_result.tex:63-68` + `tabs/ablationPhase2.tex` | **新增 Phase 2 消融**(簡單兩列版),見 4-7 |

### 4-1. Metrics 的計分口徑段(新增於第 12 行後)

← `4_result.tex:13`
> Beyond the six official metrics we additionally measure two \textit{human-preference} models,
> HPS~v2.1~\cite{hpsv2} and ImageReward~\cite{imagereward}. They are not part of the PIE-Bench
> metric set; we report them because CLIP similarity measures only image--text alignment and is
> insensitive both to whether the edit was actually carried out and to whether the result agrees
> with human preference. One convention must be stated explicitly: both preference metrics are
> always scored against the original \texttt{editing\_prompt} in the PIE-Bench
> \texttt{mapping\_file.json}, \textbf{never against a rewritten prompt}. This matters --- mixing
> the two conventions shifts ImageReward by as much as $0.33$, which is enough to invalidate any
> cross-method comparison.

### 4-2. Quantitative 末尾新增(第 38 行後)

← `4_result.tex:25` 末句
> We are not best on Structure Distance or PSNR, and this reflects the choice of operating point:
> as Sec.~\ref{sec:frontier} shows, background preservation and edit strength trade off along a
> continuous frontier, and we select a point that balances the two.

### 4-3. 人類偏好指標段(新增)

← `4_result.tex:28`
> \noindent\textbf{Human-preference metrics.}
> On the two additional preference metrics our ImageReward is $0.7344$, essentially identical to
> the closest baseline ReFlex ($0.7334$); the gap of $0.001$ is far below the full-benchmark
> run-to-run spread (about $\pm 0.02$, Sec.~\ref{sec:param_selection}), so the two should be read
> as \textit{level} rather than as a lead. The substantive conclusion on ImageReward is that we
> are on par with two 12B flow-based models (ReFlex, and FlowEdit at $0.7229$) with one sixth of
> their parameters. On HPSv2 we reach $0.2785$, third behind FlowEdit ($0.2931$) and RF-Inversion
> ($0.2847$). Note that no official implementation of AREdit has been released, so we cannot
> obtain its outputs and cannot compute either metric for it.

### 4-4. vs AREdit(改寫第 53 行)

← `4_result.tex:37`。中文版把重點從「兩者在同一條 trade-off 曲線上」移到 **mask 來源**:
> Compared with AREdit~\cite{AREdit}, a VAR-based method on the same 2B backbone, we are better on
> SSIM, LPIPS and both CLIP metrics, while AREdit is slightly ahead on Structure Distance and PSNR.
> The more consequential difference is where the mask comes from: AREdit requires the user to
> supply a threshold per editing category, whereas our masks are derived entirely from the model's
> own cross-attention with no per-category tuning --- which is precisely the advantage of
> attention-driven mask construction over cached token statistics.

### 4-5. Scale-N 質性段(新增)

← `4_result.tex:60`
> Qualitatively, sharing too few scales degrades the background, while sharing too many blocks the
> edit, because the global layout is locked in early. VAR fixes the overall structure within its
> first few scales, so edits that involve a change of shape must modify early tokens --- something
> uniform replacement cannot do selectively. Our attention mask resolves this tension by replacing
> only the background tokens, achieving faithful editing and content preservation at once.

### 4-6. 新增子節:Instance-adaptive vs fixed percentile

← `4_result.tex:70-75,84` + `tabs/ablationThreshold.tex`(面板 a)
這是**排序式門檻家族內部**的比較,用來支持「門檻必須逐實例調整」,再由 §IV-C 論證
為何最終改採絕對能量判準。四列:Instance-adaptive / 90\% / 80\% / 70\%。
需新增 `tabs/ablation_threshold.tex` 與 `imgs/ablationDynamic.png`。

### 4-7. 新增子節:Phase 2 消融

← `4_result.tex:63-68` + `tabs/ablationPhase2.tex`
兩列(With / W/O Phase 2),數字:0.0518 / 17.02 / 0.6228 / 0.2047 / 0.2522 / 0.2212。
提升幅度:PSNR +37.7\%、SSIM +37.5\%、LPIPS −59.3\%、S.D. −39.0\%、CLIP +3.5--3.6\%。

⚠️ 這組數字與 TCSVT 現有的 `tabs/ablationBeta.tex`(三個工作點、ΔIR −0.32)**完全不同**,
是不同的實驗。中文版只保留簡單版。
- [?] **決策點**:期刊版要用哪個?我建議**兩個都放** —— 簡單版放 §VI 消融,
  三工作點版放 §V(它證明的是「Phase 2 移動整條 frontier」,比單點比較強得多)。

---

## 5. `tex/5_method.tex` — 三處實質新增

| TCSVT | 中文版出處 | 改法 |
|---|---|---|
| **第 26 行**(IQR 段) | `3_method.tex:58` | **新增 block 預先排除的說明**:「$b$ 的取值範圍已預先排除最前面數個 block(32 個中的 blocks 2--31),因為它們在所有尺度上都持續呈現 global layer effect;下文以 $B$ 表示納入統計的 block 數」。目前 TCSVT 用了 $B$ 卻沒定義 |
| **第 49 行後**(τ 公式後) | `3_method.tex:81` | **新增 raw/normalized 不對稱的說明**——這是全篇最關鍵的新增:見 5-1 |
| **第 51 行**(mask 定義後) | `3_method.tex:83` | **新增 focus/preserve 的語意說明**:見 5-2 |
| **第 70 行**(pipeline 開頭) | `3_method.tex:100` | **新增粗尺度處理**:「對於 $k < N$ 的粗尺度(實驗上 $N{=}2$,亦即最粗的尺度 $k{=}1$),所有 token 都直接以 $r_k^s$ 取代而不套用任何 mask」 |
| **第 76 行**(Phase 2) | `3_method.tex:108` | **新增 target focus mask 的交集運算**:見 5-3。**目前 TCSVT 完全沒有這步** |
| **第 76 行後** | `3_method.tex:110` | **新增強調段**:「這一輪生成所產生的 token 全部被丟棄,$M_{k,t}^{\mathrm{f}}$ 是 Phase 2 唯一的產物」,並點明這是性質 (iii) 的結構依據 |
| **第 83-84 行** | — | 中文版**沒有** "Explicit coarse-scale anchoring" 這段(cumulative probability field 的討論)。配合 3-4 一起決定去留 |

### 5-1. raw / normalized 不對稱(關鍵新增)
> Note that $c_k$ is computed on the \emph{unnormalized} $\hat{a}_k$ --- it measures the shape of
> the distribution --- whereas $\tilde{\sigma}_k$ is computed on the \emph{normalized}
> $\tilde{a}_k$ --- it sets the absolute magnitude of the correction. This asymmetry is
> deliberate, and it is what makes the calibration of $\kappa_{\max}$ in
> Sec.~\ref{sec:calibration} possible.

### 5-2. focus / preserve 語意
> The rule is applied separately to the source and the target stream, giving $M_{k,s}^{\mathrm{f}},
> M_{k,s}^{\mathrm{p}}$ and $M_{k,t}^{\mathrm{f}}$ (Sec.~\ref{sec:pipeline}). The focus mask marks
> the high-attention regions that correspond to the edit-relevant words and that must \textit{not}
> be overwritten by source tokens; the preserve mask marks pure background positions, used to pin
> source content and prevent structural drift.

### 5-3. Phase 2 的交集運算(新增,目前完全缺漏)
> …and mask it against the preserve mask,
> $M_{k,t}^{\mathrm{f}} \leftarrow M_{k,t}^{\mathrm{f}} \wedge \neg M_{k,s}^{\mathrm{p}}$, so that
> positions already identified as pure background are not pulled into the edited region by a
> residual target-side attention response.

---

## 6. `tex/8_discussion.tex` 與附錄

中文版第 5 章「深入分析與討論」有三節,TCSVT 目前只涵蓋其中一部分:

| 中文版 | TCSVT | 動作 |
|---|---|---|
| §5.1 各類別定量分析(`5_discussion.tex:7-22`)+ `tabs/categoryScore.tex` | **沒有** | **新增**。三個規律:像素層級指標在 Change Material / Change Background 最佳;**StructDist 行為與其他三項不一致**(在 Change Style 0.0210 最低,因為它量的是 DINO 特徵結構而非像素);CLIPe 在 Change Style 最高、Delete Object 最低 |
| §5.2 失敗案例分析(`:25-41`) | 第 4-27 行有類似內容 | **補上中文版釐清三個尺度數字的段落**:$N{=}2$ 是主動錨定範圍、$k{=}1$--$2$ 是版面開始鎖定、$k \le 4$ 是版面大致底定。這段解掉了「$N=2$ 但為什麼說 $k\le4$」的潛在混淆 |
| §5.3 T2I 編輯結果(`:44-80`)+ 3 張圖 45 組 | `A_appendix.tex` 有 `app:t2i` 但**還沒寫** | **新增**。中文版有完整內容可直接譯,包含三個 bullet:細粒度語意控制、全域與局部編輯、背景保留 |
| §4.5 補充質性比較(`4_result.tex:192-236`)6 張圖 42 組 | **沒有** | **新增到附錄**。六段 caption 都寫好了可直接譯 |
| — | 第 51 行 `The Threshold Is Global, Not Per Case` | **刪除**(與 3-3 重複) |

---

## 7. `tex/9_conclusion.tex`

← `chapters/6_conclusion.tex:85`
- 中文版結論**明確寫**「在 SSIM 與 LPIPS 兩項背景保留指標上取得全表最佳」→ TCSVT 目前是純敘述無數字,**補上**。
- 中文版**沒有**我加的那段「我們也界定了公式化的範圍…」→ 已刪 ✓。
- 限制段(`:88`)內容與 TCSVT 第 4-27 行重疊,確認不要重複陳述。

---

## 8. 執行順序建議

1. **先做 §0 的三個退回**(主表數字、標記慣例、巨集)—— 其他改動都建立在這個基準上
2. `tex/5_method.tex` 的五處新增(5-1 ~ 5-3 是純新增,無衝突,最安全)
3. `tex/6_analysis.tex` 重寫(3-2 三步校準 + 3-3 加回 §V-G),同時刪 `adaptiveGain` / `protocol` 兩表
4. `tex/7_experiments.tex` 的退回與四段新增
5. 新增 `tabs/cv_percentile.tex`、`tabs/ablation_threshold.tex`、`tabs/ablation_phase2.tex`、`tabs/category_score.tex`
6. 附錄:T2I(45 組)+ 補充質性(42 組)
7. 待決:§V-F 錨定節去留、Phase 2 消融用哪一版(或兩版都放)
