# TCSVT version (IEEEtran journal)

從 `../ACM-MM_edited/`(acmart sigconf)轉版而來。原 ACM 版**未被修改**。

## 編譯

```bash
latexmk -pdf main.tex
# 或
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

> ⚠️ 這台機器目前**沒有安裝 TeX 發行版**(`pdflatex` / `kpsewhich` / `tlmgr` 皆不存在),
> 所以本目錄**尚未經過實際編譯驗證**。已做的是靜態檢查:
> 環境配對、34 labels / 27 refs 無 dangling reference、30 個 cite key 全部存在於
> `main.bib`、所有 `\includegraphics` 檔案存在、無 acmart 專屬巨集殘留。

## 投稿模式切換

`main.tex` 第一行:

```latex
\documentclass[journal]{IEEEtran}                                 % 兩欄(最終/預印本)
% \documentclass[journal,onecolumn,draftclsnofoot,11pt]{IEEEtran}  % 單欄 double-spaced(初稿審查)
```

TCSVT 初次投稿一般要求後者。兩種模式共用同一份 source。

## 需要你填的空白(全部有 `% TODO` 標記)

| 檔案 | 內容 |
|---|---|
| `tex/0_authors.tex` | 作者姓名、IEEE membership、單位、城市/國家、e-mail、通訊作者、投稿日期、經費、DOI |
| `main.tex` | `\markboth{}` 的 Vol./No./年月;`\begin{IEEEbiography}`(最終版需要作者小傳 + 照片) |

## 與 ACM 版的差異

- `acmart.cls` / `ACM-Reference-Format.bst` → `IEEEtran.cls` / `IEEEtran.bst`(CTAN 原版,隨稿附上)
- CCS concepts 移除;`\keywords` → `\begin{IEEEkeywords}`
- `teaserfigure` → 一般 `figure*` 全寬浮動(Fig. 1)
- `tex/supplementary.tex` → `\appendices`,標籤 `sec:supp_*` → `app:*`;
  正文中所有「in the supplementary material」改為 Appendix 交叉引用
- ACM 版遺留但已不再引用的檔案(舊 percentile 消融表、`whyUseDiscrete`、
  被取代的 `ablationPhase2`、舊版 `pipeline.png`)**不收進本 repo**;
  需要時到 `KaiCobra/ACM-MM_edited` 取回

## 內容改寫方向

**尚未做**。轉版只動版面,論文的說法、實驗、表格都還是 ACM 投稿版。
要改什麼、加哪些新實驗、supplementary 哪些該搬上來,全部寫在:

👉 `../docs/reports/TCSVT_migration_notes.md`
