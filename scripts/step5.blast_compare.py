import pandas as pd

def filter_data(file_path, output_file):
    # 读取unigene_query.txt文件
    df = pd.read_csv(file_path, sep='\t', header=None, names=[
        'Original', 'Subject', 'Identity', 'Length', 'Mismatch', 'Gap',
        'Query_start', 'Query_end', 'Subject_start', 'Subject_end', 'E-value', 'Bit_score'
    ])

    # 拆分 'Original' 列为 Fasta、Primer 和 Direction 列，并去掉 Primer 前的下划线
    split_data = df['Original'].str.extract(r'(^.*?_.*?_.*?)(_primer_\d+)_(forward|reverse)')
    df['Fasta'] = split_data[0]
    df['Primer'] = split_data[1].str.replace('_', '', 1)  # 去掉Primer列前的下划线
    df['Direction'] = split_data[2]

    # 第一轮：删除Fasta和Primer相同，Direction出现超过1次的数组
    filtered_df = df.groupby(['Fasta', 'Primer']).filter(lambda x: (x['Direction'].value_counts() <= 1).all())

    # 第二轮：对于Fasta相同但Primer不同的，只保留其中一个
    grouped = filtered_df.groupby('Fasta')
    
    # 创建一个新的 DataFrame 用于存放最终结果
    final_data = []

    # 第三轮：对于每个Fasta，最多保留第一个Primer的forward和reverse对
    for fasta, group in grouped:
        primer_groups = group.groupby('Primer')

        # 选择第一个Primer组，确保包含forward和reverse对
        first_primer_group = primer_groups.first().index[0]
        first_group = group[group['Primer'] == first_primer_group]

        # 确保forward和reverse都存在，才保留这个组
        if 'forward' in first_group['Direction'].values and 'reverse' in first_group['Direction'].values:
            final_data.append(first_group)

    # 将所有保留的组拼接到一起
    final_df = pd.concat(final_data)

    # 将Fasta和Primer重新连接成新的列，保留Direction
    final_df['Original'] = final_df['Fasta'] + "_" + final_df['Primer']

    # 保存结果，保留所有的forward和reverse数据，并保留Direction
    final_df.to_csv(output_file, sep='\t', index=False, columns=[
        'Original', 'Direction', 'Subject', 'Identity', 'Length', 'Mismatch',
        'Gap', 'Query_start', 'Query_end', 'Subject_start', 'Subject_end', 'E-value', 'Bit_score'
    ])

    print(f"处理完成，结果已保存为 {output_file}")

# 执行函数，输入为unigene_query.txt文件，输出为filtered_blast_results.txt
filter_data('unigene_query.txt', 'filtered_blast_results.txt')
