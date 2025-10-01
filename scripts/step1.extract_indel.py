# Read IDs from indelposition.txt
ids_to_extract = []
with open('indelposition.txt', 'r') as id_file:
    for line in id_file:
        # Check if the line has content before splitting
        if line.strip():
            id_value = line.split()[0]
            ids_to_extract.append(id_value)

output_file = open('extracted_sequences.fasta', 'w')

extracting = False
with open('unigene.fasta', 'r') as fasta_file:
    for line in fasta_file:
        if line.startswith('>'):
            sequence_id = line.strip().split()[0][1:]  # Extracting ID from the header
            extracting = sequence_id in ids_to_extract
        if extracting:
            output_file.write(line)

output_file.close()


