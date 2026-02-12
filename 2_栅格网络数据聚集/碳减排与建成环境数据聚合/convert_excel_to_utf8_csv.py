import pandas as pd
import os

# 设置文件路径
morning_excel_path = 'd:/Desktop/项目论文/建模/早高峰_标准化.xlsx'
evening_excel_path = 'd:/Desktop/项目论文/建模/晚高峰_标准化.xlsx'

# 设置输出文件路径
morning_csv_path = 'd:/Desktop/项目论文/建模/早高峰_标准化_utf8.csv'
evening_csv_path = 'd:/Desktop/项目论文/建模/晚高峰_标准化_utf8.csv'

def convert_excel_to_utf8_csv(excel_path, csv_path):
    print(f"正在处理: {os.path.basename(excel_path)} -> {os.path.basename(csv_path)}")
    
    # 读取Excel文件
    try:
        # 使用pandas读取Excel，自动处理大多数编码问题
        df = pd.read_excel(excel_path)
        print(f"成功读取Excel文件，共 {len(df)} 行数据")
        print(f"数据列名: {list(df.columns)}")
        
        # 保存为UTF-8编码的CSV文件
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"成功保存为UTF-8编码的CSV文件: {os.path.basename(csv_path)}")
        
        # 验证保存的文件
        verify_df = pd.read_csv(csv_path, encoding='utf-8-sig')
        print(f"验证CSV文件: 读取成功，共 {len(verify_df)} 行数据")
        print("验证前3行数据:")
        print(verify_df.head(3))
        print("\n" + "="*50 + "\n")
        
        return True
    except Exception as e:
        print(f"处理文件时出错: {str(e)}")
        return False

# 执行转换
print("开始转换Excel文件到UTF-8编码的CSV格式...\n")
morning_success = convert_excel_to_utf8_csv(morning_excel_path, morning_csv_path)
evening_success = convert_excel_to_utf8_csv(evening_excel_path, evening_csv_path)

# 输出总体结果
print("转换完成!")
print(f"早高峰文件转换: {'成功' if morning_success else '失败'}")
print(f"晚高峰文件转换: {'成功' if evening_success else '失败'}")
print("\n生成的文件:")
print(f"- {morning_csv_path}")
print(f"- {evening_csv_path}")
print("\n这些CSV文件使用UTF-8编码，适合编程使用。")