import struct
import sys
import re


def chomp(x):
    if x.endswith("\r\n"): return x[:-2]
    if x.endswith("\n") or x.endswith("\r"): return x[:-1]
    return x

def hexify_float(f):
    # hexify_float: Converts a 32-bit floating point number into the specific notation used by Mosaic
    _number = (hex(struct.unpack('<I', struct.pack('<f', f))[0]))[2:]

    return "D{:0>8}".format(_number)

input_file = sys.argv[1]
output_file = input_file + "_annotated"
filament_total = 0.00
previous_line_buffer = []
line_buffer_length = 10
max_filament_segment_length = 0.00
did_g92 = False

pings = [350.00, 700.00, 2100.00, 5000.00, 10000.00, 25000.00, 50000.00]
ping_position = 0

evalue_pattern = re.compile('G1\sX([0-9\.]*)\sY([0-9\.]*)\sE([0-9\.]*)')
retract_pattern = re.compile('G1\sE([0-9\.]*)')

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

    # insert pings
    if filament_total >= pings[ping_position]:
        file_out.write("G4 P0\n")
        file_out.write("O31 " + hexify_float(filament_total))
        file_out.write("\n")
        ping_position += 1

    
file_in.close()
file_out.close()

#O21 D0014; don't change
#O22 D93dc44b0d6fa4540; ID of printer
#O23 D0001; don't change
#O24 D0000; don't change
#O25 D1000000Black_PLA D1FF1515FireBrick_PLA D0 D0; 
#O26 D000F; Number of splices, short hex
#O27 D0007; Number of pings, short hex
#O28 D0001; no idea, never changed it
#O29 D0000; no idea, never changed it
#O30 D0 D456297ec; floating point hex of splice point
#O30 D1 D45a12f31; floating point hex of splice point
#O30 D0 D45d83f31; floating point hex of splice point
#O30 D1 D460b3335; floating point hex of splice point
#O30 D0 D462d9934; floating point hex of splice point
#O30 D1 D46520302; floating point hex of splice point
#O30 D0 D467698e2; floating point hex of splice point
#O30 D1 D468c903d; floating point hex of splice point
#O30 D0 D469bbcdb; floating point hex of splice point
#O30 D1 D46a83295; floating point hex of splice point
#O30 D0 D46b232df; floating point hex of splice point
#O30 D1 D46bab5f4; floating point hex of splice point
#O30 D0 D46c2e190; floating point hex of splice point
#O30 D1 D46cbc8a9; floating point hex of splice point
#O30 D0 D46dac000; floating point hex of splice point add extra lenght above what print uses for bowden tube.
#O32 D11 D0000 D0000 D0000; never changed it, dunno what it does.
#O1 D40_Layer_Stripe_Vase D00006D60; Description, two lines up, but Hex long, rounded up.
#M0
#T0