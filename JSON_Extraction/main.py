import json
import re
from collections import Counter
from pathlib import Path

def display_author_menu():
    """
    读取JSON文件，统计作者出现次数，并显示一个Top 5的选择菜单。
    返回 (selected_author, all_data, script_dir) 或 None
    """
    
    # 1. 严谨的文件路径处理
    try:
        script_dir = Path(__file__).resolve().parent
    except NameError:
        script_dir = Path.cwd()
        
    file_path = script_dir / 'data.json'

    # 2. 读取JSON文件
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
    except FileNotFoundError:
        print(f"错误: 文件未找到。")
        print(f"请确保 'data.json' 存在于以下目录中: {script_dir}")
        return None
    except json.JSONDecodeError:
        print(f"错误: 无法解析 '{file_path}'。请检查文件内容是否为有效JSON。")
        return None
    except Exception as e:
        print(f"发生了一个未知错误: {e}")
        return None

    # 3. 提取并统计 authorName
    author_names = [item.get('authorName', 'N/A') for item in data]
    author_counts = Counter(author_names)
    top_authors = author_counts.most_common(5)

    if not top_authors:
        print("数据中没有找到作者信息。")
        return None

    # 4. 显示选框 (菜单)
    print("--- 请选择一个作者 (Top 5) ---")
    author_map = {}
    for i, (author, count) in enumerate(top_authors, 1):
        print(f"{i}. {author} (出现次数: {count})")
        author_map[str(i)] = author 
    print("---------------------------------")

    # 5. 获取用户输入
    while True:
        choice = input(f"请输入选项 (1-{len(top_authors)}): ")
        
        if choice in author_map:
            selected_author = author_map[choice]
            print(f"\n您选择了: {selected_author}")
            return selected_author, data, script_dir
        else:
            print(f"输入无效，请输入 1 到 {len(top_authors)} 之间的一个数字。")

def save_author_as_markdown(all_data, selected_author, output_dir):
    """
    根据选择的作者筛选数据，并将其保存为一个可读性高的 Markdown (.md) 文件。
    """
    print(f"\n正在过滤 '{selected_author}' 的数据并生成 Markdown...")
    
    # 1. 筛选数据
    filtered_data = [
        item for item in all_data 
        if item.get('authorName') == selected_author
    ]

    if not filtered_data:
        print("错误：未能在数据中找到该作者的条目。")
        return

    # 2. 创建安全的文件名
    safe_name = re.sub(r'[\\/*?:"<>|]', '', selected_author).replace(' ', '_')
    if not safe_name.strip() or safe_name.strip() == '.':
        safe_name = 'filtered_author_data'
        
    output_filename = f"{safe_name}.md"  # <-- 扩展名改为 .md
    output_path = output_dir / output_filename

    # 3. 构建 Markdown 内容字符串
    md_content = []
    
    # 添加H1主标题
    md_content.append(f"# {selected_author} 的留言\n\n")

    for i, item in enumerate(filtered_data):
        timestamp = item.get('timestamp', 'N/A')
        content = item.get('content', '无内容').strip()

        # 添加时间戳
        md_content.append(f"**时间:** {timestamp}\n\n")
        
        # 处理内容，使用区块引用 (Blockquote)
        # 这会自动处理多行文本
        content_lines = content.split('\n')
        for line in content_lines:
            md_content.append(f"> {line}\n")
        
        # 添加分隔符，除非是最后一条
        if i < len(filtered_data) - 1:
            md_content.append(f"\n---\n\n")

    # 4. 写入文件
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(md_content) # 使用 writelines 写入列表中的所有行
        
        print(f"\n--- 成功! ---")
        print(f"已将 '{selected_author}' 的 {len(filtered_data)} 条数据保存为 Markdown 文件:")
        print(f"{output_path}")

    except Exception as e:
        print(f"保存文件时出错: {e}")
        print(f"目标路径: {output_path}")


# --- 脚本执行入口 ---
if __name__ == "__main__":
    
    # 1. 显示菜单并获取用户的选择
    result = display_author_menu()
    
    if result:
        # 2. 解包返回的结果
        selected_author, all_data, script_directory = result
        
        # 3. 调用新函数来过滤并保存为 Markdown
        save_author_as_markdown(all_data, selected_author, script_directory)1