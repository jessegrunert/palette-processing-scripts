import sys

input_file = sys.argv[1]
output_file = input_file + "_annotated"
filament_total = float(0.00)
previous_line_buffer = 

print(input_file)
print(output_file)

file_in = open(input_file,"r")
file_out = open(output_file, "w")
file_in_lines = file_in.readlines()
for line in file_in_lines:
    file_out.write(line)
file_in.close()