import logging

elementList = [
    "H",
    "D",
    "HE",
    "C",
    "N",
    "O",
    "F",
    "P",
    "S",
    "CL",
    "LI",
    "NA",
    "MG",
    "SI",
    "PAH",
    "15N",
    "13C",
    "18O",
    "E-",
    "FE",
]
elementMass = [
    1,
    2,
    4,
    12,
    14,
    16,
    19,
    31,
    32,
    35,
    3,
    23,
    24,
    28,
    420,
    15,
    13,
    18,
    0,
    56,
]
symbols = ["#", "@", "*", "+", "-", "(", ")"]


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


class Species:
    """Species is a class that holds all the information about an individual species in the
    network. It also has convenience functions to check whether the species is a gas or grain
    species and to help compare between species.
    """

    def __init__(self, inputRow):
        self.name = inputRow[0].upper()
        self.mass = int(inputRow[1])

        self.is_refractory = str(inputRow[2]).lower() == "inf"
        if self.is_refractory:
            self.binding_energy = 99.9e9
        else:
            self.binding_energy = float(inputRow[2])

        self.solidFraction = float(inputRow[3])
        self.monoFraction = float(inputRow[4])
        self.volcFraction = float(inputRow[5])
        self.enthalpy = float(inputRow[6])
        self.n_atoms = 0

        # in first instance, assume species freeze/desorb unchanged
        # this is updated by `check_freeze_desorbs()` later.
        if self.is_grain_species():
            # this will make any excited species desorb as their base counterparts
            if "*" in self.name:
                self.desorb_products = [self.name[1:-1], "NAN", "NAN", "NAN"]
            else:
                self.desorb_products = [self.name[1:], "NAN", "NAN", "NAN"]
        else:
            self.freeze_products = {}

    def get_name(self) -> str:
        return self.name

    def get_mass(self) -> int:
        return self.mass

    def set_desorb_products(self, new_desorbs: list[str]) -> None:
        self.desorb_products = new_desorbs

    def get_desorb_products(self) -> list[str]:
        return self.desorb_products

    def set_freeze_products(self, product_list: list[str], freeze_alpha: float) -> None:
        self.freeze_products[",".join(product_list)] = freeze_alpha

    def get_freeze_products(self) -> dict:
        keys = self.freeze_products.keys()
        values = self.freeze_products.values()
        logging.debug(f"freeze keys: {keys}, products {values}")
        for key, value in zip(keys, values):
            yield key.split(","), value

    def get_freeze_products_list(self) -> list[list[str]]:
        # TODO: Write an unit test for get_freeze_product_behaivour
        return [key.split(",") for key in self.freeze_products.keys()]

    def get_freeze_alpha(self, product_list: list[str]) -> float:
        return self.freeze_products[",".join(product_list)]

    def is_grain_species(self):
        if self.name in ["BULK", "SURFACE"]:
            return True
        else:
            try:
                return self.name[0] in ["#", "@"]
            except IndexError:
                return False

    def is_surface_species(self):
        return self.name[0] == "#"

    def is_bulk_species(self):
        return self.name[0] == "@"

    def is_ion(self):
        return self.name[-1] == "+" or self.name[-1] == "-"

    def add_default_freeze(self):
        freeze = "#" + self.name
        if freeze[-1] in ["+", "-"]:
            freeze = freeze[:-1]
        if self.name == "E-":
            freeze = ""
        self.set_freeze_products([freeze, "NAN", "NAN", "NAN"], 1.0)

    def find_constituents(self):
        """Loop through the species' name and work out what its consituent
        atoms are. Then calculate mass and alert user if it doesn't match
        input mass.
        """
        speciesName = self.name[:]
        i = 0
        atoms = []
        bracket = False
        bracketContent = []
        # loop over characters in species name to work out what it is made of
        while i < len(speciesName):
            # if character isn't a #,+ or - then check it otherwise move on
            if speciesName[i] not in symbols:
                if i + 1 < len(speciesName):
                    # if next two characters are (eg) 'MG' then atom is Mg not M and G
                    if speciesName[i : i + 3] in elementList:
                        j = i + 3
                    elif speciesName[i : i + 2] in elementList:
                        j = i + 2
                    # otherwise work out which element it is
                    elif speciesName[i] in elementList:
                        j = i + 1

                # if there aren't two characters left just try next one
                elif speciesName[i] in elementList:
                    j = i + 1
                # if we've found a new element check for numbers otherwise print error
                if j > i:
                    if bracket:
                        bracketContent.append(speciesName[i:j])
                    else:
                        atoms.append(speciesName[i:j])  # add element to list
                    if j < len(speciesName):
                        if is_number(speciesName[j]):
                            if int(speciesName[j]) > 1:
                                for k in range(1, int(speciesName[j])):
                                    if bracket:
                                        bracketContent.append(speciesName[i:j])
                                    else:
                                        atoms.append(speciesName[i:j])
                                i = j + 1
                            else:
                                i = j
                        else:
                            i = j
                    else:
                        i = j
                else:
                    raise ValueError(
                        f"Contains elements not in element list: {speciesName}"
                    )
                    logging.warning(speciesName[i])
                    logging.warning(
                        "\t{0} contains elements not in element list:".format(
                            speciesName
                        )
                    )
                    logging.warning(elementList)
            else:
                # if symbol is start of a bracketed part of molecule, keep track
                if speciesName[i] == "(":
                    bracket = True
                    bracketContent = []
                    i += 1
                # if it's the end then add bracket contents to list
                elif speciesName[i] == ")":
                    if is_number(speciesName[i + 1]):
                        for k in range(0, int(speciesName[i + 1])):
                            atoms.extend(bracketContent)
                        i += 2
                    else:
                        atoms.extend(bracketContent)
                        i += 1
                # otherwise move on
                else:
                    i += 1

        self.n_atoms = len(atoms)
        mass = 0
        for atom in atoms:
            mass += elementMass[elementList.index(atom)]
        if mass != int(self.mass):
            logging.warning(
                f"Input mass of {self.name} ({self.mass}) does not match calculated mass of constituents, using calculated mass: {int(mass)}"
            )
            self.mass = int(mass)

    def get_n_atoms(self) -> int:
        return self.n_atoms

    def set_n_atoms(self, new_n_atoms) -> None:
        self.n_atoms = new_n_atoms

    def __eq__(self, other):
        if isinstance(other, Species):
            return self.name == other.name
        elif isinstance(other, str):
            return self.name == other
        else:
            raise NotImplementedError

    def __lt__(self, other):
        return self.mass < other.mass

    def __gt__(self, other):
        return self.mass > other.mass

    def __repr__(self):
        return f"Specie: {self.name}"

    def __str__(self):
        return self.name