# 3D 建模專案規則 (使用者指定, 每次對話都要遵守)

- **不要用 Python 建模。** 使用者要直接打開檔案，不想每次貼指令到終端機匯出。
  一律使用使用者已有的三個建模工具, 三個都放在 `/Users/coffeegabi/Documents/Blender/` 裡
  (工具名稱與用法見使用者先前的交接文件, 開工前先讀)。
- 所有 3D 建模的輸出檔與製作檔, 一律放在使用者電腦的 `/Users/coffeegabi/Documents/Blender` 底下。
- 結構: `/Users/coffeegabi/Documents/Blender/<建模工具>/project/<專案名稱>/`
  - `<建模工具>`: 這次用的建模工具的資料夾。
  - `<專案名稱>`: 每個模型專案一個子資料夾, 裡面放製作檔, 輸出放在 `output/` (3MF、STL、預覽圖)。
- 交付的檔案要能直接打開 (.3mf / .stl / .blend / .png), 不能要求使用者另外跑指令。
- 每個專案結案時, 在專案資料夾寫一份 `HANDOVER.md` 交接。
- 使用者的 3D 列印機: Bambu Lab A1 mini (列印空間 180 x 180 x 180 mm)。

## 已結案專案

- `Python/project/headboard_tissue_box/` — 床頭板衛生紙抽取盒 (2026-10-26 結案, 見該資料夾的 `HANDOVER.md`)。
  這是在「不用 Python」規則訂立前完成的, 之後不要再用 Python 修改它。
