# 3D 建模專案規則 (使用者指定, 每次對話都要遵守)

- 所有 3D 建模的輸出檔與製作檔, 一律放在使用者電腦的 `/Users/coffeegabi/Documents/Blender` 底下。
- 結構: `/Users/coffeegabi/Documents/Blender/<建模工具>/project/<專案名稱>/`
  - `<建模工具>`: 這次用的建模工具, 例如 `Blender`、`Python` (Python + manifold3d/trimesh 程式建模)。
  - `<專案名稱>`: 每個模型專案一個子資料夾, 裡面放製作檔 (程式/.blend), 輸出放在 `output/` (STL、預覽圖)。
- 在雲端環境 (沒有那個 Mac 路徑) 工作時, 在 repo 裡用同樣的相對結構 `<建模工具>/project/<專案名稱>/`,
  讓使用者可以原樣下載到 `/Users/coffeegabi/Documents/Blender/` 底下。
- 使用者的 3D 列印機: Bambu Lab A1 mini (列印空間 180 x 180 x 180 mm)。
