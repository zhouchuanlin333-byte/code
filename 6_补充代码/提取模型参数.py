import csv
import ast

# 读取CSV文件并提取参数
def extract_model_parameters(csv_file):
    models_params = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            # 直接读取文件内容并处理
            content = f.read()
            rows = content.strip().split('\n')
            
            # 获取列名
            header = rows[0].split(',')
            
            # 处理数据行
            for row in rows[1:]:
                if not row.strip():
                    continue
                    
                # 分割行数据，注意处理带引号的字段
                import re
                fields = re.findall(r'"([^"]*)"|([^,]*)', row)
                fields = [''.join(field) for field in fields if ''.join(field)]
                
                if len(fields) >= 2:
                    model_name = fields[0]
                    params_str = fields[1]
                    
                    try:
                        # 处理nan值，将其替换为None
                        processed_params_str = params_str.replace('nan', 'None')
                        
                        # 解析参数字符串为字典
                        params_dict = ast.literal_eval(processed_params_str)
                        
                        # 提取指定参数
                        extracted_params = {
                            '模型名称': model_name,
                            'learning_rate': params_dict.get('learning_rate', '无此参数'),
                            'max_depth': params_dict.get('max_depth', '无此参数'),
                            'n_estimators': params_dict.get('n_estimators', '无此参数'),
                            'max_features': params_dict.get('max_features', '无此参数')
                        }
                        
                        models_params.append(extracted_params)
                    except Exception as e:
                        print(f"解析{model_name}参数时出错: {e}")
    except Exception as e:
        print(f"读取文件时出错: {e}")
    
    return models_params

# 格式化输出
def format_output(params_list):
    print("通过网格搜索算法获得的三类机器学习模型参数组合：")
    print("=" * 60)
    
    # 打印表头
    print(f"{'模型名称':<10} {'learning_rate':<15} {'max_depth':<10} {'n_estimators':<15} {'max_features':<15}")
    print("-" * 60)
    
    # 打印每行数据
    for params in params_list:
        print(f"{params['模型名称']:<10} {str(params['learning_rate']):<15} {str(params['max_depth']):<10} {str(params['n_estimators']):<15} {str(params['max_features']):<15}")

# 主函数
def main():
    csv_file = 'd:/Desktop/项目论文/建模/机器学习模型预测验证/最佳参数设置.csv'
    params_list = extract_model_parameters(csv_file)
    format_output(params_list)

if __name__ == "__main__":
    main()