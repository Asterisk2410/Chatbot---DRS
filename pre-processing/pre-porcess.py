def remove_duplicates(input_file, output_file):
    # Read the lines from the input file
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Remove duplicates by converting the list to a set and back to a list
    unique_lines = list(set(lines))

    # Write the unique lines to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        for line in unique_lines:
            file.write(line)

# Specify the input and output file names
input_file = 'website_paragraphs.txt'
output_file = 'unique_paragraphs.txt'

# Call the function to remove duplicates
remove_duplicates(input_file, output_file)

print(f"Duplicates removed. Unique lines saved to {output_file}")
