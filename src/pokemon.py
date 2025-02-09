import csv
from src.types import pokemon_type_checker

def pokemon_info(pokemon_name):
    """
    Retrieves Pokémon information from the CSV, including type effectiveness.

    Args:
        pokemon_name: The name of the Pokémon.

    Returns:
        A formatted string with Pokémon info and type effectiveness, or a 
        message if the Pokémon is not found or the type is invalid.
    """

    try:
        with open("151pokemon.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                if row["pokemon"].lower() == pokemon_name.lower():
                    type1 = row["type1"]
                    type2 = row["type2"] if row["type2"] else None
                    
                    pokemon_name=pokemon_name.upper()
                    output = f"{pokemon_name} is a "

                    if type1 and type2:
                        output += f"{type1}/{type2} type Pokémon.\n"
                        type_info1 = pokemon_type_checker(type1) # Use imported type checker
                        type_info2 = pokemon_type_checker(type2) # Use imported type checker

                        if isinstance(type_info1, dict): # Check if it's a valid type info dict
                            output += format_type_info(type1, type_info1)
                        else:
                            output += f"{type1}: {type_info1}\n" # Print the error if not

                        if isinstance(type_info2, dict): # Check if it's a valid type info dict
                            output += format_type_info(type2, type_info2)
                        else:
                            output += f"{type2}: {type_info2}\n" # Print the error if not

                    elif type1:
                        output += f"{type1} type Pokémon.\n"
                        type_info = pokemon_type_checker(type1) # Use imported type checker
                        if isinstance(type_info, dict): # Check if it's a valid type info dict
                            output += format_type_info(type1, type_info)
                        else:
                            output += f"{type1}: {type_info}\n"  # Print the error

                    else:
                        return f"Invalid type for {pokemon_name}"

                    return output

            return f"'{pokemon_name}' not found. \n"

    except FileNotFoundError:
        return "pokemon.csv not found. Please make sure the file is in the same directory."


def format_type_info(type_name, type_info):
    strengths = type_info["strong"]
    weaknesses = type_info["weak"]
    no_effects = type_info["no_effect"]
    output = ""
    output += f"{type_name} is 2x effective against: "
    if strengths:
        output += ", ".join(strengths)  # Join with commas
    else:
        output += "None"  # Handle empty list

    output += "\n"  # Newline for better formatting
    output += f"{type_name} is 0.5x effective against: "  # Assuming 0.5x for weaknesses
    if weaknesses:
        output += ", ".join(weaknesses)
    else:
        output += "None"

    if no_effects:
        output += "\n"
        output += f"{type_name} has no effect on: "
        output += ", ".join(no_effects)

    output += "\n"
    return output

print("Pokemon Called!")