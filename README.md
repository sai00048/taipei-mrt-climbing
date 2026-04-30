# 🧗 雙北捷運攀岩地圖 · MRT Climbing Map

> 依捷運路線分類的台北 / 新北 / 桃園機捷沿線攀岩館完整資訊。含票價、地址、官方社群連結，地址可直接跳轉 Google Maps。

## ✨ 功能特色

- **依捷運路線分類**：6 條北捷路線 + 桃園機場捷運，方便搭乘大眾運輸前往
- **完整票價資訊**：平日 / 假日 / 星光時段，分時段顯示
- **一鍵 Google Maps**：點擊地址直接開啟 Google Maps 導航
- **官方社群連結**：Facebook 優先、Instagram、官網一次收錄
- **含天然岩場與河濱免費場地**：大砲岩、熱海女巫、瑠公、公館水岸、獅子頭等
- **響應式設計**：手機、平板、電腦都能順暢瀏覽
- **暗色介面**：減少眼睛疲勞，適合夜間規劃

## 📍 收錄場地（共 28 個攀岩場地）

| 路線 | 場地數 | 代表場地 |
|---|---|---|
| 🔴 淡水信義線 | 6 | 北投大砲岩、熱海女巫岩場、原岩明德、REDRock 紅石、北投運動中心、小岩館 |
| 🟢 松山新店線 | 7 | 原岩新店、瑠公基地、公館水岸、獅子頭廣場、永和攀岩場、Corner 中山/華山 |
| 🟠 中和新蘆線 | 3 | EnJoin'、Mega Stone、Double 8 大稻埕館 |
| 🔵 板南線 | 5 | 土城運動中心、原岩萬華、Double 8 Y17、市民抱石、原岩南港 |
| 🟤 文湖線 | 3 | 光合作用內湖、Flow 心流抱石、奇岩 Kirin |
| 🟡 環狀線 | 3 | 原岩中和、新莊運動中心、文山運動中心 |
| 🟣 桃園機捷 | 1 | 原岩 A19 |

包含 **室內岩館**、**運動中心攀岩牆**、**戶外天然岩場** 與 **河濱免費抱石場**。

## 🚀 GitHub Pages 部署步驟

### 第 1 步：建立 GitHub Repo

1. 登入 [GitHub](https://github.com)，點右上角 **+** → **New repository**
2. **Repository name** 填 `taipei-mrt-climbing`（或你想要的英文名稱）
3. 設為 **Public**（公開）
4. 勾選 **Add a README file** → 點 **Create repository**

### 第 2 步：上傳檔案

**方法 A：網頁上傳（推薦給非開發者）**

1. 進到剛建立的 repo 頁面
2. 點 **Add file** → **Upload files**
3. 把 `index.html`（以及 `README.md`、`LICENSE`）拖曳上去
4. 拉到最下方點 **Commit changes**

**方法 B：Git 指令**

```bash
git clone https://github.com/你的帳號/taipei-mrt-climbing.git
cd taipei-mrt-climbing
git add index.html README.md LICENSE
git commit -m "Initial upload"
git push
```

### 第 3 步：啟用 GitHub Pages

1. 在 repo 頁面點上方 **Settings**
2. 左側選單點 **Pages**
3. **Source** 選 **Deploy from a branch**
4. **Branch** 選 `main`，資料夾選 `/ (root)`
5. 點 **Save**

### 第 4 步：等待網址產生（約 1–2 分鐘）

```
Your site is live at https://你的帳號.github.io/taipei-mrt-climbing/
```

## 🔧 自訂

### 想改 Repo 名稱

在 repo 頁面 → **Settings** → **General** → **Repository name** 改名後 **Rename**。

### 想改內容

直接在 GitHub 網頁上點 `index.html` → 點右上角鉛筆圖示 → 編輯 → 拉到底 **Commit changes** 即可。

## 📝 資料來源

- 各岩館官方 Facebook 粉絲頁
- 各岩館官方網站
- [轟菌體能 - 全台各地攀岩館及票價一覽](https://shenlee799.com/climbinggyms-taiwan/)
- 整理時間：2024–2025 年

## ⚠ 免責聲明

本資料僅供參考，**票價及營業時間以實際現場公告為準**。出發前建議再次查詢官方社群確認最新資訊。

部分場地（如 EnJoin、運動中心攀岩館等）資訊待補充，歡迎提供。

## 🤝 歡迎貢獻

發現資料有誤、新增岩館、或想要協助維護？歡迎在這個 repo 提出 [Issue](../../issues) 或 [Pull Request](../../pulls)！

## 📜 授權

本專案以 [MIT License](LICENSE) 釋出。內容資訊版權歸各岩館所有。

---

Made with 🧗 by climbers, for climbers.
