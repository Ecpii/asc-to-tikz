# `.asc` to TikZ converter

Small Python script used to convert LTSpice `.asc` files into LaTeX `circuitikz` figures. Built by working through EECS 215 homeworks.

## Usage

- Download the `asc_to_tikz.py` file
- Run the following:

```
python3 asc_to_tikz.py <name_of_schematic_file>.asc
```

- This should generate a file named `<name_of_schematic_file>.tex`, which contains the `circuitikz` figure. Copy and paste the contents or put `\input{<name_of_schematic_file>}` into your LaTeX document that includes `circuitikz`:

```tex
\documentclass{article}
\usepackage{circuittikz}

\begin{document}

\input{example}

\end{document}
```

## Features

- Convert an entire schematic to a `.tex` file
- Automatically typeset units given in LTSpice
- Preserves node labels and orientations of components

## Supported Components

Supports converting the following components (LTSpice name -> circuitikz name):

- Resistors (`res` -> `resistor`)
- Independent Current Sources (`current` -> `isource`)
- Voltage Sources (`voltage` -> `vsource`)
- Controlled Current Sources (`bi`, `f` -> `cisource`)
- Controlled Voltage Sources (`bv`, `h`, `e` -> `cvsource`)
- Diodes (`diode` -> `diode`)
- npn transistors (`npn` -> `npn`)
- NMOS transistors (`nmos` -> `nmos`)
- Ideal Op Amps\* (`OpAmps\\opamp` -> `op amp`)
- Capacitors (`cap` -> `capacitor`)
- Inductors (`ind` -> `cute inductor`)

\*Op Amps may have minor alignment issues
