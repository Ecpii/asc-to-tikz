import sys

# todo: units should not be done on bv or bi

asc_type_to_tikz = {
    "res": "resistor",
    "current": "isource",
    "voltage": "vsource",
    "bi": "cisource",
    "f": "cisource",
    "bv": "cvsource",
    "h": "cvsource",
    "e": "cvsource",
    "diode": "diode",
    "npn": "npn",
    "nmos": "nmos",
    "OpAmps\\\\opamp": "op amp",
    "cap": "capacitor",
    "ind": "cute inductor",
}
rotations = ["R0", "R90", "R180", "R270"]
mirrors = ["M180", "M270", "M0", "M90"]
offsets = {
    "resistor": [(16, 16), (-16, 16), (-16, -16), (16, -16)],
    "isource": [(0, 0), (0, 0), (0, 0), (0, 0)],
    "cisource": [(0, 0), (0, 0), (0, 0), (0, 0)],
    "vsource": [(0, 16), (-16, 0), (0, -16), (16, 0)],
    "cvsource": [(0, 16), (-16, 0), (0, -16), (16, 0)],
    "diode": [(16, 0), (0, -16), (-16, 0), (0, 16)],
    "capacitor": [(16, 0), (0, 16), (-16, 0), (0, -16)],
    "npn": [(64, 48), (-48, 64), (-64, -48), (48, -64)],
    "nmos": [(48, 48), (-48, 48), (-48, -48), (48, -48)],
    "op amp": [(0, 64), (-64, 0), (0, -64), (64, 0)],
    "cute inductor": [(16, 16), (-16, 16), (-16, -16), (16, -16)],
}
lengths = {
    "resistor": [(0, -2.5), (-2.5, 0), (0, 2.5), (2.5, 0)],
    "isource": [(0, -2.5), (-2.5, 0), (0, 2.5), (2.5, 0)],
    "cisource": [(0, -2.5), (-2.5, 0), (0, 2.5), (2.5, 0)],
    "vsource": [(0, -2.5), (-2.5, 0), (0, 2.5), (2.5, 0)],
    "cvsource": [(0, -2.5), (-2.5, 0), (0, 2.5), (2.5, 0)],
    "diode": [(0, -2), (-2, 0), (0, 2), (2, 0)],
    "capacitor": [(0, -2), (-2, 0), (0, 2), (2, 0)],
    "cute inductor": [(0, -2.5), (-2.5, 0), (0, 2.5), (2.5, 0)],
}
units = {
    "resistor": "ohm",
    "isource": "A",
    "cisource": "A",
    "vsource": "V",
    "cvsource": "V",
    "diode": "",
    "capacitor": "F",
    "cute inductor": "H",
}


def clean_name(name):
    trans_table = str.maketrans("", "", "_{}")
    return name.translate(trans_table)


class Device:
    def __init__(self, type, raw_coords, rotation):
        self.type = asc_type_to_tikz[type]
        rotation_index = rotations.index(rotation)
        x_offset, y_offset = offsets[self.type][rotation_index]
        self.start = (
            (raw_coords[0] + x_offset) / 32,
            -(raw_coords[1] + y_offset) / 32,
        )
        x_length, y_length = lengths[self.type][rotation_index]
        self.end = (self.start[0] + x_length, self.start[1] + y_length)
        self.name = ""
        self.value = ""

    def format_value(self):
        suffix = units[self.type]
        prefix = self.value[-1]
        if prefix.isdigit():
            return f"\\({self.value} \\unit{{\\{suffix}}}\\)"
        else:
            num_value = self.value[:-1]
            return f"\\({num_value} \\unit{{\\{prefix}{suffix}}}\\)"

    def __repr__(self):
        return (
            f"\t\t\\draw {self.start} "
            f"to [{self.type}, "
            f"l^=\\({self.name}\\)"
            + (f", a_={self.format_value()}" if self.value else "")
            + f"] {self.end};\n"
        )


class Transistor:
    UPPER_NODE_OFFSETS = [(0, 1.5), (1.5, 0), (0, -1.5), (-1.5, 0)]
    LOWER_NODE_OFFSETS = [(0, -1.5), (-1.5, 0), (0, 1.5), (1.5, 0)]
    START_NODE_OFFSETS = [(-2, 0), (0, 2), (2, 0), (0, -2)]

    def __init__(self, type, raw_coords, rotation):
        self.type = asc_type_to_tikz[type]
        rotation_index = rotations.index(rotation)
        self.rotation = 90 * rotation_index
        x_offset, y_offset = offsets[self.type][rotation_index]
        self.origin = (
            (raw_coords[0] + x_offset) / 32,
            -(raw_coords[1] + y_offset) / 32,
        )
        self.start_node = (
            self.origin[0] + Transistor.START_NODE_OFFSETS[rotation_index][0],
            self.origin[1] + Transistor.START_NODE_OFFSETS[rotation_index][1],
        )
        self.upper_node = (
            self.origin[0] + Transistor.UPPER_NODE_OFFSETS[rotation_index][0],
            self.origin[1] + Transistor.UPPER_NODE_OFFSETS[rotation_index][1],
        )
        self.lower_node = (
            self.origin[0] + Transistor.LOWER_NODE_OFFSETS[rotation_index][0],
            self.origin[1] + Transistor.LOWER_NODE_OFFSETS[rotation_index][1],
        )
        self.name = ""
        self.value = ""

    def __repr__(self):
        rotation_clause = f""
        label_clause = f"label={{right:\\({self.name}\\)}}"
        if self.rotation == 90:
            rotation_clause = f"rotate=-90"
            label_clause = f"label={{below:\\({self.name}\\)}}"
        elif self.rotation == 180:
            rotation_clause = "rotate=-180"
            label_clause = f"label={{left:\\({self.name}\\)}}"
        elif self.rotation == 270:
            rotation_clause = "rotate=-270"
            label_clause = f"label={{above:\\({self.name}\\)}}"
        return (
            f"\t\t\\node ({clean_name(self.name)}) at {self.origin}"
            f" [{self.type}"
            + (f", {rotation_clause}" if rotation_clause else f"")
            + (f", {label_clause}" if label_clause else f"")
            + f"] {{}};\n"
            f"\t\t\\draw {self.start_node} to [short] ({clean_name(self.name)}.B);\n"
            f"\t\t\\draw ({clean_name(self.name)}.C) to [short] {self.upper_node};\n"
            f"\t\t\\draw ({clean_name(self.name)}.E) to [short] {self.lower_node};\n"
        )


class Amplifier:
    MIRRORED_OFFSETS = [(0, 64), (64, 0), (0, -64), (-64, 0)]

    def __init__(self, type, raw_coords, rotation):
        self.type = asc_type_to_tikz[type]
        self.rotation = int(rotation[1:])
        self.flipped = False
        if rotation[0] == "M":
            self.flipped = True
            # self.rotation = (self.rotation + 180) % 360
        rotation_index = self.rotation // 90

        x_offset, y_offset = (
            offsets[self.type][rotation_index]
            if not self.flipped
            else Amplifier.MIRRORED_OFFSETS[rotation_index]
        )
        self.origin = (
            (raw_coords[0] + x_offset) / 32,
            -(raw_coords[1] + y_offset) / 32,
        )
        self.name = ""
        self.value = ""

    def __repr__(self):
        flip_clause = f""
        rotation_clause = f""
        label_clause = f"\\({self.name}\\)"
        if self.flipped:
            flip_clause = "xscale=-1"
            label_clause = f"\\ctikzflipx{{\\({self.name}\\)}}"
        if self.rotation == 90:
            rotation_clause = f"rotate=-90"
            if self.flipped:
                flip_clause = "yscale=-1"
                label_clause = f"\\ctikzflipy{{\\({self.name}\\)}}"
        elif self.rotation == 180:
            rotation_clause = "rotate=-180"
            label_clause = f"\\ctikzflipxy{{\\({self.name}\\)}}"
            if self.flipped:
                flip_clause = "xscale=-1"
                label_clause = f"\\ctikzflipy{{\\({self.name}\\)}}"
        elif self.rotation == 270:
            rotation_clause = "rotate=-270"
            if self.flipped:
                flip_clause = "yscale=-1"
                label_clause = f"\\ctikzflipy{{\\({self.name}\\)}}"
        return (
            f"\t\t\\node ({clean_name(self.name)}) at {self.origin}"
            f" [{self.type}"
            + (f", {rotation_clause}" if rotation_clause else f"")
            + (f", {flip_clause}" if flip_clause else f"")
            + f"] {{{label_clause}}};\n"
        )


if len(sys.argv) > 2:
    print(f"Usage: {sys.argv[0]} <input file path>")
    sys.exit(1)

input_file_name = sys.argv[1]
out_file_name = input_file_name.replace(".asc", ".tex")
out_file = open(out_file_name, "w")
out_file.write("\\begin{center}\n")
out_file.write("\t\\begin{tikzpicture}\n")
with open(input_file_name) as in_file:
    device = None
    for line in in_file.readlines():
        tokens = line.split()
        if tokens[0] == "WIRE":
            if device is not None:
                out_file.write(repr(device))
                device = None
            coords = [int(token) / 32 for token in tokens[1:]]
            # multiply y by -1 since tikz and ltspice use different y conventions
            start = (coords[0], -coords[1])
            end = (coords[2], -coords[3])
            out_file.write(f"\t\t\\draw {start} to [short] {end};\n")
        elif tokens[0] == "SYMBOL":
            if device is not None:
                out_file.write(repr(device))
                device = None
            type = tokens[1]
            raw_coords = (int(tokens[2]), int(tokens[3]))
            rotation = tokens[4]
            if type in ("npn", "nmos"):
                device = Transistor(type, raw_coords, rotation)
            elif type == "OpAmps\\\\opamp":
                device = Amplifier(type, raw_coords, rotation)
            else:
                device = Device(type, raw_coords, rotation)
        elif tokens[0] == "SYMATTR":
            if tokens[1] == "InstName":
                device.name = tokens[2]
            elif tokens[1] == "Value":
                device.value = tokens[2]
        elif tokens[0] == "FLAG":
            coords = (int(tokens[1]) / 32, -int(tokens[2]) / 32)
            name = tokens[3]
            if name == "0":
                # ground
                out_file.write(
                    f"\t\t\\node (ground) at {coords} [ground] {{}};\n"
                )
            else:
                out_file.write(
                    f"\t\t\\node ({name}) at {coords} [label={{above:\\({name}\\)}}, circ] {{}};\n"
                )
if device is not None:
    out_file.write(repr(device))
    device = None

out_file.write("\t\\end{tikzpicture}\n")
out_file.write("\\end{center}\n")
