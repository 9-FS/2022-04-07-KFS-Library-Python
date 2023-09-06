# Copyright (c) 2023 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
length={        # m
    "ft": 0.3048,
    "in": 0.0254,
    "NM": 1852,
    "SM": 1609.344,
    "yd": 0.9144
}

area={          # m²
    "ft²": length["ft"]**2,
    "ha": 100**2,
    "in²": length["in"]**2,
    "SM²": length["SM"]**2
}

volume={        # m³
    "ft³": length["ft"]**3,
    "gal": 0.003785411784,
    "in³": length["in"]**3,
    "l": 0.001,
    "qt": 0.003785411784/4
}

time={          # s
    "d": 86400,
    "h": 3600,
    "min": 60,
    "week": 7*86400,
    "year": 365.2425*86400
}

speed={         # m/s
    "c": 299792458,
    "ft/min": length["ft"]/time["min"],
    "ft/s": length["ft"]/1,
    "km/h": 1000/time["h"],
    "SM/h": length["SM"]/time["h"],
    "kt": length["NM"]/time["h"]
}

acceleration={  # m/s²
    "g": 9.80665,
    "kt/s": speed["kt"]/1
}

flow={          # m³/s
    "gal/h": volume["gal"]/time["h"],
    "l/h": volume["l"]/time["h"]
}

mass={          # kg
    "lb": 0.45359237,
    "oz": 0.028349523125,
    "st": 14*0.45359237
}

density={       # kg/m³
    "g/cm³": 1000
}
    

force={         # kg*m/s²
    "kgf": 1*acceleration["g"],
    "lbf": mass["lb"]*acceleration["g"]
}

pressure={      # kg/(m*s²)
    "atm": 101325,
    "bar": 100000,
    "inHg": 3386.389,
    "lbf/ft²": force["lbf"]/area["ft²"],
    "lbf/in²": force["lbf"]/area["in²"],
    "mmHg": 133.322387415
}

energy={        # kg*m²/s²
    "cal": 4.184,
    "hp*h": 75*acceleration["g"]*time["h"],
    "W*h": 1*time["h"]
}

torque={        # kg*m²/s²
    "kgf*m": 1*acceleration["g"]*1,
    "lbf*in": mass["lb"]*acceleration["g"]*length["in"]
}

power={         # kg*m²/s³
    "hp": 550*length["ft"]*mass["lb"]*acceleration["g"]/1,
    "ps": 75*1*acceleration["g"]*1/1,
}