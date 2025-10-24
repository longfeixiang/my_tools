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
    根据选择的作者筛选数据，按时间排序，并保存为 Markdown 文件。
    """
    print(f"\n正在过滤 '{selected_author}' 的数据...")
    
    # 1. 筛选数据
    filtered_data = [
        item for item in all_data 
        if item.get('authorName') == selected_author
    ]

    # --- 关键改动：按时间戳排序 ---
    # 2. 根据 timestamp 排序，日期靠前的在前面 (升序)
    #    使用 .get('timestamp', '') 确保缺少时间戳的条目不会导致崩溃
    try:
        filtered_data.sort(key=lambda item: item.get('timestamp', ''))
        print("数据已按时间戳升序排序。")
    except Exception as e:
        print(f"排序时发生错误: {e}。数据将保持原有顺序。")
    # ---------------------------------

    if not filtered_data:
        print("错误：未能在数据中找到该作者的条目。")
        return

    # 3. 创建安全的文件名
    safe_name = re.sub(r'[\\/*?:"<>|]', '', selected_author).replace(' ', '_')
    if not safe_name.strip() or safe_name.strip() == '.':
        safe_name = 'filtered_author_data'
        
    output_filename = f"{safe_name}.md"
    output_path = output_dir / output_filename

    # 4. 构建 Markdown 内容字符串 (现在基于已排序的 filtered_data)
    md_content = []
    
    md_content.append(f"# {selected_author} 的留言 (按时间排序)\n\n")

    for i, item in enumerate(filtered_data):
        timestamp = item.get('timestamp', 'N/A')
        content = item.get('content', '无内容').strip()

        md_content.append(f"**时间:** {timestamp}\n\n")
        
        content_lines = content.split('\n')
        for line in content_lines:
            md_content.append(f"> {line}\n")
        
        if i < len(filtered_data) - 1:
            md_content.append(f"\n---\n\n")

    # 5. 写入文件
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(md_content)
        
        print(f"\n--- 成功! ---")
        print(f"已将 '{selected_author}' 的 {len(filtered_data)} 条数据保存为 Markdown 文件:")
        print(f"{output_path}")

    except Exception as e:
        print(f"保存文件时出错: {e}")
        print(f"目标路径: {output_path}")


# --- 脚本执行入口 ---
if __name__ == "__main__":
    
    result = display_author_menu()
    
    if result:
        selected_author, all_data, script_directory = result
        
        save_author_as_markdown(all_data, selected_author, script_directory)