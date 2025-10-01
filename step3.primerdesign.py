import os
import primer3
import pandas as pd

# Define global primer design parameters
global_args = {
    'PRIMER_NUM_RETURN': 5,
    'PRIMER_OPT_SIZE': 22,
    'PRIMER_MIN_SIZE': 20,
    'PRIMER_MAX_SIZE': 24,
    'PRIMER_OPT_TM': 58.0,
    'PRIMER_MIN_TM': 56.0,
    'PRIMER_MAX_TM': 60.0,
    'PRIMER_MIN_GC': 40.0,
    'PRIMER_MAX_GC': 60.0,
    'PRIMER_THERMODYNAMIC_OLIGO_ALIGNMENT': 1,
    'PRIMER_MAX_POLY_X': 100,
    'PRIMER_INTERNAL_MAX_POLY_X': 100,
    'PRIMER_SALT_MONOVALENT': 50.0,
    'PRIMER_DNA_CONC': 50.0,
    'PRIMER_MAX_NS_ACCEPTED': 0,
    'PRIMER_MAX_SELF_ANY': 12,
    'PRIMER_MAX_SELF_END': 8,
    'PRIMER_PAIR_MAX_COMPL_ANY': 12,
    'PRIMER_PAIR_MAX_COMPL_END': 8,
    'PRIMER_PRODUCT_SIZE_RANGE': [260, 280],
    'PRIMER_GC_CLAMP': 1
}

# Read sequences from final_sequences_350bp.fasta file
def read_fasta(file_path):
    sequences = []
    with open(file_path, 'r') as file:
        sequence = {'header': '', 'sequence': ''}
        for line in file:
            if line.startswith('>'):
                if sequence['header']:
                    sequences.append(sequence)
                sequence = {'header': line.strip(), 'sequence': ''}
            else:
                sequence['sequence'] += line.strip()
        if sequence['header']:
            sequences.append(sequence)
    return sequences

# Extract sequence ID from header
def extract_seq_id(header):
    # Extracting everything before _pos
    return header.split('_pos')[0].replace('>', '')

# Define the path to final_sequences_350bp.fasta file
input_folder = './'  # Change to the folder where final_sequences_350bp.fasta is located
file_path = os.path.join(input_folder, 'final_sequences_300bp.fasta')

# Read sequences from the final_sequences_350bp.fasta file
sequences = read_fasta(file_path)

# Function to design primers for sequences
def design_primers(sequence, global_args):
    # Extracting the sequence ID
    seq_id = extract_seq_id(sequence['header'])
    seq_args = {
        'SEQUENCE_ID': seq_id,
        'SEQUENCE_TEMPLATE': sequence['sequence'],
        'SEQUENCE_INCLUDED_REGION': [0, len(sequence['sequence']) - 1],
    }
    primer3_result = primer3.bindings.design_primers(seq_args, global_args)
    primer3_result_table_dict = {}
    
    for j in range(primer3_result["PRIMER_PAIR_NUM_RETURNED"]):
        primer_id = str(j)
        for key in primer3_result:
            if primer_id in key:
                info_tag = key.replace("_" + primer_id, "")
                primer3_result_table_dict.setdefault(info_tag, []).append(primer3_result[key])

    # Use the extracted sequence ID as part of the index, now including the sequence name for identification
    df_index = [f"{seq_id}_primer_{str(m + 1)}" for m in range(primer3_result["PRIMER_PAIR_NUM_RETURNED"])]
    primer3_result_df = pd.DataFrame(primer3_result_table_dict, index=df_index)
    
    return primer3_result_df

# Create an empty DataFrame to store all results
combined_df = pd.DataFrame()

# Design primers for each sequence in final_sequences_350bp.fasta
for sequence in sequences:
    primer_df = design_primers(sequence, global_args)
    combined_df = pd.concat([combined_df, primer_df], ignore_index=False)

# Save the combined results as a CSV file
combined_output_file = 'combined_primer_results_with_names.csv'
combined_df.to_csv(combined_output_file)

print("引物设计完成，结果已保存为", combined_output_file)
