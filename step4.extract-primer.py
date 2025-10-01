import pandas as pd

# 读取CSV文件
combined_primers = pd.read_csv('combined_primer_results_with_names.csv')

# 提取引物名称、正向引物和反向引物信息
primers_info = combined_primers.iloc[:, [0, 4, 5]]  # 假设引物名称在第一列，正向引物在第5列，反向引物在第6列

# 将信息保存为FASTA格式文件
with open('primers.fasta', 'w') as fasta_file:
    for index, row in primers_info.iterrows():
        fasta_file.write(f'>{row.iloc[0]}_forward\n')  # 引物名称
        fasta_file.write(f'{row.iloc[1]}\n')  # 正向引物序列
        fasta_file.write(f'>{row.iloc[0]}_reverse\n')  # 反向引物名称
        fasta_file.write(f'{row.iloc[2]}\n')  # 反向引物序列

