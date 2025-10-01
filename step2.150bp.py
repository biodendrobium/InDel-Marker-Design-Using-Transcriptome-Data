# Read data from indelposition.txt
data = {}
with open('indelposition.txt', 'r') as file:
    header = file.readline()  # Skip header
    for line in file:
        parts = line.split()
        if len(parts) >= 2:
            gene_id = parts[0]
            pos = int(parts[1])
            data[gene_id] = pos

output_file = open('final_sequences_300bp.fasta', 'w')

# Read extracted_sequences.fasta and extract sequences
current_id = None
sequence = ""

with open('extracted_sequences.fasta', 'r') as fasta_file:
    for line in fasta_file:
        if line.startswith('>'):
            if current_id and current_id in data:
                pos = data[current_id]
                start_index = max(0, pos - 150)
                end_index = pos + 150
                extracted_sequence = sequence[start_index:end_index]

                if len(extracted_sequence) == 300:
                    output_file.write(f'>{current_id}_pos{pos}_300bp\n')
                    output_file.write(extracted_sequence + '\n')

            current_id = line.strip().split()[0][1:]
            sequence = ""
        else:
            sequence += line.strip()

    # Process the last sequence
    if current_id and current_id in data:
        pos = data[current_id]
        start_index = max(0, pos - 150)
        end_index = pos + 150
        extracted_sequence = sequence[start_index:end_index]

        if len(extracted_sequence) == 300:
            output_file.write(f'>{current_id}_pos{pos}_300bp\n')
            output_file.write(extracted_sequence + '\n')

output_file.close()

