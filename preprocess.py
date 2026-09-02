import json
import os

print("开始执行预处理脚本...")

input_path = "data/raw_data/PANDAX_dataset.json"
output_path = "data/processed_qa.json"

if not os.path.exists(input_path):
    print(f"❌ 文件不存在: {input_path}")
    exit(1)

try:
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception as e:
    print(f"❌ 读取 JSON 失败: {e}")
    exit(1)

print(f"✅ JSON 解析成功，数据类型：{type(data)}")

# 递归提取所有 Q/A 对
def extract_qa(obj):
    """递归遍历对象，提取所有包含 'Q' 和 'A' 的字典"""
    qa_pairs = []
    if isinstance(obj, dict):
        # 如果当前字典同时有 Q 和 A，提取
        if 'Q' in obj and 'A' in obj:
            q = obj['Q'].strip()
            a = obj['A'].strip()
            if q and a:
                qa_pairs.append({'question': q, 'answer': a})
        # 递归遍历所有值
        for value in obj.values():
            qa_pairs.extend(extract_qa(value))
    elif isinstance(obj, list):
        for item in obj:
            qa_pairs.extend(extract_qa(item))
    return qa_pairs

# 提取所有问答对
qa_list = extract_qa(data)
print(f"共提取到 {len(qa_list)} 条问答对")

# 保存
try:
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(qa_list, f, ensure_ascii=False, indent=2)
    print(f"✅ 预处理完成，结果已保存至 {output_path}")
except Exception as e:
    print(f"❌ 保存失败: {e}")
    exit(1)