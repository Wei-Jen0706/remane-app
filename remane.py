import os
import re
import pandas as pd
import streamlit as st

st.set_page_config(page_title="PDF 批次檔名裁切工具", layout="wide")

st.title("✂️ PDF 檔名裁切工具 (保留 1234_5678 格式)")
st.write("自動識別檔名開頭的 **4位數字_4位數字**，並將後面的文字與數字全部刪除。")

# 1. 輸入資料夾路徑
folder_path = st.text_input("請輸入資料夾完整路徑：", placeholder=r"C:\Users\User\Desktop\PDF_AI_Tool")

if folder_path and os.path.exists(folder_path):
    all_files = os.listdir(folder_path)
    # 只抓取 .pdf 檔案
    pdf_files = [f for f in all_files if f.lower().endswith('.pdf') and os.path.isfile(os.path.join(folder_path, f))]
    
    if not pdf_files:
        st.warning("⚠️ 該資料夾內沒有找到任何 .pdf 檔案。")
    else:
        st.success(f"📂 成功讀取到 {len(pdf_files)} 個 PDF 檔案。")
        
        rename_map = {}
        # 正則表達式：匹配開頭的 4位數字 + 底線 + 4位數字
        pattern = re.compile(r"^(\d{4}_\d{4})")

        for filename in pdf_files:
            name, ext = os.path.splitext(filename)
            match = pattern.match(name)
            
            if match:
                # 抓取第一組 1234_5678 格式並加上副檔名
                new_filename = match.group(1) + ext
                rename_map[filename] = new_filename
            else:
                # 若檔名不符合 1234_5678 格式，則保持原樣或提示
                rename_map[filename] = filename

        # 2. 顯示對照預覽
        st.subheader("👁️ 改名預覽")
        df_preview = pd.DataFrame([
            {
                "原始檔名": old_f, 
                "修改後檔名": new_f, 
                "狀態": "✨ 將進行修改" if old_f != new_f else "⚠️ 未匹配格式（不變）"
            }
            for old_f, new_f in rename_map.items()
        ])
        
        st.dataframe(df_preview, use_container_width=True)

        # 檢查是否有可修改的項目
        changable_count = sum(1 for k, v in rename_map.items() if k != v)

        if changable_count > 0:
            if st.button(f"🚀 確定執行批次改名 ({changable_count} 個檔案)", type="primary"):
                success_count = 0
                error_count = 0
                
                for old_f, new_f in rename_map.items():
                    if old_f == new_f:
                        continue
                    
                    old_path = os.path.join(folder_path, old_f)
                    new_path = os.path.join(folder_path, new_f)
                    
                    try:
                        os.rename(old_path, new_path)
                        success_count += 1
                    except Exception as e:
                        st.error(f"修改 {old_f} 失敗: {e}")
                        error_count += 1
                
                if success_count > 0:
                    st.balloons()
                    st.success(f"🎉 成功修改 {success_count} 個檔案名稱！")
                    st.rerun()
        else:
            st.info("沒有需要修改的檔案名稱。")

elif folder_path:
    st.error("❌ 找不到該資料夾路徑，請確認路徑輸入正確。")