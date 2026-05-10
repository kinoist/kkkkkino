# 公众号:文商科学码自救小组，时间：2024.01.05
import pandas as pd
import pyperclip
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import base64
from io import BytesIO
import regex
import sys
import os
def fill_ownership_structure(df):
 for i, row in df.iterrows():
 ownership_line = ""
 for j in range(df.shape[1]-2, -1, -2):
 shareholder = row[j]
 if pd.notnull(shareholder):
 ownership_line = '-' + shareholder + ownership_line
 if pd.isnull(shareholder) and ownership_line!='':
 df.iloc[i,j] = df.iloc[0:i,j].dropna().iloc[-1]
 df.iloc[i,j+1] = df.iloc[0:i,j+1].dropna().iloc[-1]
 return df
def gen_mermaid(df_holder, df_holding, issuer):
 root_node = regex.sub(r'[\p{P}\s]', '_', issuer)
 added_edges = []
 for _, row in df_holder.iterrows():
 for i in range(df_holder.shape[1]-2, -1, -2):
 if pd.notna(row[i]):
 node_label_str = regex.sub(r'[\p{P}\s]', '_', row[i])
 node_label = f"{i//2}_{node_label_str}"
 if i == 0:
 edge = f" {node_label}[\"{row[i]}\"] -->|{row[i+1]:.2%}| {root_node}"
 else:
 prev_node_label_str = regex.sub(r'[\p{P}\s]', '_', row[i-2])
 prev_node_label = f"{(i-2)//2}_{prev_node_label_str}"
 edge = f" {node_label}[\"{row[i]}\"] -->|{row[i+1]:.2%}| {prev_node_label}[\"{row[i-2]}\"]"
 if edge not in added_edges:
 added_edges.append(edge)
 for _, row in df_holding.iterrows():
 for i in range(0, df_holding.shape[1]-2, 2):
 if pd.notna(row[i]):
 node_label_str = regex.sub(r'[\p{P}\s]', '_', row[i])
 node_label = f"{i//2}_{node_label_str}"
 if i == 0:
 edge = f" {root_node} -->|{row[i+1]:.2%}| {node_label}[\"{row[i]}\"]"
 else:
 prev_node_label_str = regex.sub(r'[\p{P}\s]', '_', row[i-2])
 prev_node_label = f"{(i-2)//2}_{prev_node_label_str}"
 edge = f" {prev_node_label}[\"{row[i-2]}\"] -->|{row[i+1]:.2%}| {node_label}[\"{row[i]}\"]"
 if edge not in added_edges:
 added_edges.append(edge)
 mermaid_text = "
".join(added_edges)
 return mermaid_text
def get_excel_path():
 if len(sys.argv) > 1:
 path = sys.argv[1]
 if os.path.exists(path):
 return path
 else:
 print(f"命令行参数指定的文件不存在: {path}")
 root = tk.Tk()
 root.withdraw()
 root.attributes('-topmost', True)
 file_path = filedialog.askopenfilename(
 title="请选择股权结构表 Excel 文件",
 filetypes=[("Excel 文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
 )
 root.destroy()
 return file_path
if __name__ == "__main__":
 excel_path = get_excel_path()
 if not excel_path:
 print("未选择文件，程序退出。")
 sys.exit(0)
 print(f"正在处理文件: {excel_path}")
 try:
 df_shareholder_structure = fill_ownership_structure(df = pd.read_excel(excel_path, sheet_name = "股东"))
 df_shareholding_structure = fill_ownership_structure(df = pd.read_excel(excel_path, sheet_name = "持股"))
 except Exception as e:
 messagebox.showerror("错误", f"读取Excel文件失败:
{e}
请确保文件中包含名为 '股东' 和 '持股' 的工作表。")
 sys.exit(1)
 mermaid_text = "graph TD
"+gen_mermaid(df_holder = df_shareholder_structure, df_holding = df_shareholding_structure, issuer = "发行人公司名称")
 pyperclip.copy(mermaid_text)
 print("Mermaid代码文本已复制到剪贴板")
 root = tk.Tk()
 root.title("提示")
 label = tk.Label(root, text = "
Mermaid代码文本已复制到剪贴板", justify = tk.LEFT)
 label.pack()
 def open_link(event):
 webbrowser.open_new("https://app.diagrams.net/")
 link = tk.Label(root, text = "点击访问draw.io：https://app.diagrams.net/", fg = "blue", cursor = "hand2")
 link.pack()
 link.bind("<Button-1>", open_link)
 label_text = """进入draw.io后，左上角"调整图形"→"插入"→"高级"→"Mermaid"，然后将剪贴板里的Mermaid代码文本粘贴进去
生成结构图后，任意点击一个形状，ctrl+A全选，点击 此处 将连接线改为直角连接线"""
 label = tk.Label(root, text = label_text, justify = tk.LEFT)
 label.pack()
 root.mainloop()
