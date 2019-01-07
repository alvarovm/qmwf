import os
import re
from munch import Munch
from operator import itemgetter

SINGLET_START = "CIS-EXCITED STATES (SINGLETS)"
SINGET_END = "********************************"
TRIPLET_START = "CIS EXCITED STATES (TRIPLETS)"
TRIPLET_END = "ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS"


def parse_states_from_line(lines, START_MARKER, ENDING_MARKER):
    state_list = []
    current_state = None

    NEL = n_electrons(lines)

    for j, line in enumerate(lines):
        if START_MARKER in line:
            cur_line = j + 4
        if 'ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS' in line:
            later_line = j + 5
        if '%cis NRoots' in line:
            expect_state_count = int(line.split()[4])

    line = lines[cur_line]

    while ENDING_MARKER not in line:
        if "STATE " in line:
            if current_state is not None:
                state_list.append(current_state)
            current_state = {}
            current_state["orbital_list"] = []
            num, energyAU, energyeV, energycm1 = re.findall("(\d+(?:\.\d+)?)", line)[:-1]
            current_state["state_number"] = int(num)
            current_state["energy"] = float(energyeV)
            current_state["multiplicity"] = START_MARKER.split()[-1][1:-2].lower()
        if "->" in line:
            i, f, asq, a = re.findall("\-?\d+(?:\.\d+)?", line)
            initial = int(i)
            final = int(f)-NEL/2+1
            amp = float(a)
            current_state["orbital_list"].append(dict(initial=initial, final=final, amplitude=amp))
        cur_line += 1
        line = lines[cur_line]
    state_list.append(current_state)  # put on last excited state

    line = lines[later_line]
    j = 1
    if START_MARKER.split()[-1][1:-2].lower() == 'singlet':
        while 'spin forbidden' not in line:
            if int(line.split()[0]) == j:
                state_list[j-1]["oscillator_strength"] = float(line.split()[3])
            later_line += 1
            j += 1
            line = lines[later_line]

    if START_MARKER.split()[-1][1:-2].lower() == 'triplet':
        for j in range(expect_state_count):
            state_list[j]["oscillator_strength"] = 0.0000000

    assert(len(state_list) == expect_state_count)
    return state_list


def theory():
    theory = Munch()
    theory.name = 'semiempirical_zindo'
    theory.description = "ZINDO/S"
    return theory


def duration(lines):
    for line in reversed(lines):
        if "Sum of individual times " in line:
            return float(re.findall("(\d+(?:\.\d+)?)", line)[0])


def n_electrons(lines):
    for line in lines:
        if "Number of Electrons    NEL" in line:
            text = line.split()
            return int(text[5])


def load_calc_list(job_dir, context=None):
    meta_data = Munch()

    out_filename = 'zindo.out'
    out_path = os.path.join(job_dir, out_filename)

    with open(out_path, 'r') as f:
        lines = f.readlines()
#   if '                             ****ORCA TERMINATED NORMALLY****\n' not in lines:
    if '                             ****ORCA TERMINATED NORMALLY****\n' not in lines:
        raise Exception("' ****ORCA TERMINATED NORMALLY****' not found in ORCA calc output")
    for line in lines:
        if "Program Version" in line:
            text = line.split()
            meta_data.program = "ORCA"
            meta_data.version = text[2]
            break
    meta_data.wall_clock_time = duration(lines)

    meta_data.worker_name = "zindo"
    calc = Munch(meta_data=meta_data)
    calc.theory = theory()
    all_excts = sorted( parse_states_from_line(lines, SINGLET_START, SINGET_END) + parse_states_from_line(lines, TRIPLET_START, TRIPLET_END), key=itemgetter('energy'))
    for i, exct in enumerate(all_excts):
        all_excts[i]["state_number"] = i+1
    calc.excited_states = all_excts
    return calc



# qmwf : quantum mechanics workflow for data science
# author: alvarovm at gihub

