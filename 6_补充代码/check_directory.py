import os

# 检查目录结构
def check_directory(path):
    print(f"检查目录: {path}")
    if not os.path.exists(path):
        print("目录不存在")
        return
    
    print("目录内容:")
    items = os.listdir(path)
    for item in items:
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            print(f"  [目录] {item}")
        else:
            print(f"  [文件] {item}")
    
    # 检查最新创建的目录
    print("\n最新创建的目录:")
    directories = [item for item in items if os.path.isdir(os.path.join(path, item))]
    if directories:
        directories.sort(key=lambda x: os.path.getmtime(os.path.join(path, x)), reverse=True)
        latest_dir = directories[0]
        latest_dir_path = os.path.join(path, latest_dir)
        print(f"  {latest_dir} (创建时间: {os.path.getmtime(latest_dir_path):.0f})")
        
        # 查看最新目录的内容
        print(f"  {latest_dir} 目录内容:")
        latest_items = os.listdir(latest_dir_path)
        for item in latest_items:
            item_path = os.path.join(latest_dir_path, item)
            if os.path.isdir(item_path):
                print(f"    [目录] {item}")
                # 查看子目录内容
                sub_items = os.listdir(item_path)
                for sub_item in sub_items[:5]:  # 只显示前5个文件
                    print(f"      {sub_item}")
                if len(sub_items) > 5:
                    print(f"      ... 还有 {len(sub_items) - 5} 个文件")
            else:
                print(f"    [文件] {item}")

# 执行检查
check_directory("d:/Desktop/项目论文/SHAP值解释性分析")