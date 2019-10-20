import struct
import sys
import re
import math


def chomp(x):
    if x.endswith("\r\n"): return x[:-2]
    if x.endswith("\n") or x.endswith("\r"): return x[:-1]
    return x

def hexify_float(f):
    # hexify_float: Converts a 32-bit floating point number into the specific notation used by Mosaic
    _number = (hex(struct.unpack('<I', struct.pack('<f', f))[0]))[2:]

    return "D{:0>8}".format(_number)

def hexify_short(num):
    # hexify_short: Converts a short integer into the specific notation used by Mosaic
    if num < 0:
        num += 65536
    return "D" + '{0:04x}'.format(num)

def hexify_long(num):
    # hexify_long: Converts a 32-bit integer into the specific notation used by Mosaic
    return "D" + '{0:08x}'.format(num)

input_file = sys.argv[1]
output_file = input_file + "_annotated"
filament_total = 0.00
previous_line_buffer = []
line_buffer_length = 10
max_filament_segment_length = 0.00
did_g92 = False

pings = [350.00]
ping = 0
ping_increment = 350

layers = []
layer = 0

evalue_pattern = re.compile('G1\sX([0-9\.]*)\sY([0-9\.]*)\sE([0-9\.]*)')
retract_pattern = re.compile('G1\sE([0-9\.]*)')
layer_pattern = re.compile('^;\sLayer:\s([0-9]*)')

file_in = open(input_file,"r")
file_out = open(output_file, "w")
file_in_lines = file_in.readlines()
for line in file_in_lines:
    # manage the filament buffer.
    if len(previous_line_buffer) >= line_buffer_length:
        previous_line_buffer.pop(len(previous_line_buffer) -1)
    previous_line_buffer.insert(0, line)

    # manage the filament segment length.
    evalue_match = evalue_pattern.match(line)
    if evalue_match:
        if float(evalue_match.group(3)) > float(max_filament_segment_length):
            max_filament_segment_length = float(evalue_match.group(3))

    # look for filament length resets
    if line.find("G92 E0") != -1:
        filament_total += float(max_filament_segment_length)
        max_filament_segment_length = 0
        file_out.write(chomp(line) + "; total filament: " + str(filament_total) + "\n")
        did_g92 = True
    else:
        # look for retracts
        if did_g92:
            retract_match = retract_pattern.match(line)
            if retract_match:
                if retract_match.group(1) != "":
                    filament_total -= float(retract_match.group(1))
                    did_g92 = False

        file_out.write(line)

        # count layers
    layer_match = layer_pattern.match(line)
    if layer_match:
        layers.insert(layer, filament_total)
        layer += 1

    # insert pings
    if filament_total >= pings[ping]:
        file_out.write("G4 P0\n")
        file_out.write("O31 " + hexify_float(filament_total))
        file_out.write("\n")
        pings.append(math.ceil(filament_total + ping_increment))
        ping_increment = math.ceil(ping_increment * 1.03)
        ping += 1

# remove the last ping as it will never get used.
del pings[-1]
ping -= 1

file_in.close()
file_out.close()

print("Total filament length is: " + str(filament_total) + "mm")
print("Total number of layers: " + str(len(layers)))

how_many_layers = input("How many layers would you like?")
print("Using " + str(how_many_layers) + " layers")

layers_per_color = math.ceil(int(len(layers)) / int(how_many_layers))
print("Using " + str(layers_per_color) + " layers per color.")

print("Layer splice table")
for i, val in enumerate(layers):
    print("Layer: ", i, " | ", val, "mm")

print("Ping table")
for i, val in enumerate(pings):
    print("Ping: ", i, " | ", val, "mm")

#build out the omega.
tool_order = [0, 1, 2, 3]
omega = []
tool_index = 0
bowden_offset = 500

omega.append("O21 D0014")
omega.append("O22 D93dc44b0d6fa4540")
omega.append("O23 D0001")
omega.append("O24 D0000")
omega.append("O25 D1000000Black_PLA D1FF1515FireBrick_PLA D10BF728GreenYellow_PLA D1FFFF00Yellow_PLA ")
omega.append("O26 " + hexify_short(int(how_many_layers)))
omega.append("O27 " + hexify_short(ping))
omega.append("O28 D0001")
omega.append("O29 D0000")


for i, val in enumerate(layers):
    if i > 0:
        if (i / layers_per_color).is_integer():
            # we're on a layer that needs a splice
            omega.append("O30 D" + str(tool_order[tool_index]) + " " + hexify_float(val))
            tool_index += 1
            if tool_index >= len(tool_order):
                tool_index = 0


# add in the final splice which is the end of the print + bowden tube offset
final_splice = math.ceil(filament_total + bowden_offset)
omega.append("O30 D" + str(tool_order[tool_index]) + " " + hexify_float(float(final_splice)))

omega.append("O32 D11 D0000 D0000 D0000")
omega.append("O1 DRainbow_Pet_Dish " + hexify_long(final_splice))
omega.append("M0")
omega.append("T0")

for o in omega:
    print(o)