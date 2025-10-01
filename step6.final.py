import pandas as pd

def filter_primers(filtered_blast_file, combined_primer_file, output_file):
    # 读取 filtered_blast_results.txt 的第一列
    filtered_blast_df = pd.read_csv(filtered_blast_file, sep='\t', header=0)
    filtered_primers = filtered_blast_df.iloc[:, 0]  # 第一列为特异性引物信息

    # 读取 combined_primer_results_with_names.csv
    combined_primer_df = pd.read_csv(combined_primer_file)

    # 筛选 combined_primer_df 中第一列的引物名存在于 filtered_primers 列表中的行
    filtered_combined_df = combined_primer_df[combined_primer_df.iloc[:, 0].isin(filtered_primers)]

    # 修改第一列的内容，提取第2个和第5个_之间的字符
    def extract_middle_part(name):
        parts = name.split('_')
        if len(parts) >= 5:
            return '_'.join(parts[1:4])  # 提取第2到第5个之间的字符
        return name

    # 对第一列进行处理，提取并替换字符
    filtered_combined_df.iloc[:, 0] = filtered_combined_df.iloc[:, 0].apply(extract_middle_part)

    # 将筛选后的结果保存为新的 CSV 文件
    filtered_combined_df.to_csv(output_file, index=False)

    print(f"筛选完成，结果已保存为 {output_file}")

# 执行函数，输入为 filtered_blast_results.txt 和 combined_primer_results_with_names.csv，输出为筛选后的 CSV 文件
filter_primers('filtered_blast_results.txt', 'combined_primer_results_with_names.csv', 'filtered_combined_primer_results.csv')
