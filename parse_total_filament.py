import sys

input_file = sys.argv[1]
output_file = input_file + "_annotated"
filament_total = float(0.00)
previous_line_buffer = []
line_buffer_length = 10

print(input_file)
print(output_file)

file_in = open(input_file,"r")
file_out = open(output_file, "w")
file_in_lines = file_in.readlines()
for line in file_in_lines:
    if len(previous_line_buffer) > line_buffer_length:
        previous_line_buffer.pop(len(previous_line_buffer) -1);
    previous_line_buffer.insert(0, line)

    print(previous_line_buffer)
    print("\n\n\n")
    file_out.write(line)
file_in.close()