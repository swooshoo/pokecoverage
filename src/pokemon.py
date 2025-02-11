import csv
from src.types import pokemon_type_checker
from src.radar import generate_radar  # Import radar chart function

def pokemon_info(pokedex_number):
    print("Pokemon Info!")
    """
    Retrieves Pokémon information from the CSV using its Pokédex number.

    Args:
        pokedex_number: The Pokédex number of the Pokémon (integer).

    Returns:
        A tuple (pokemon_name, output, type1, type2) containing the Pokémon's name,
        formatted string with Pokémon info, and its type(s).
    """
    try:
        with open("151pokemon.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                if int(row["pokedex"]) == pokedex_number:  # Match by Pokédex number
                    pokemon_name = row["pokemon"].upper()
                    type1 = row["type1"]
                    type2 = row["type2"] if row["type2"] else None

                    output = f"{pokemon_name} (Pokédex #{pokedex_number}) is a "

                    if type1 and type2:
                        output += f"{type1}/{type2} type Pokémon.\n"
                        type_info1 = pokemon_type_checker(type1)                   
                        type_info2 = pokemon_type_checker(type2)
                        if isinstance(type_info1, dict):
                            output += format_type_info(type1, type_info1)
                        else:
                            output += f"{type1}: {type_info1}\n"

                        if isinstance(type_info2, dict):
                            output += format_type_info(type2, type_info2)
                        else:
                            output += f"{type2}: {type_info2}\n"

                    elif type1:
                        output += f"{type1} type Pokémon.\n"
                        type_info = pokemon_type_checker(type1)
                        
                        if isinstance(type_info, dict):
                            output += format_type_info(type1, type_info)
                        else:
                            output += f"{type1}: {type_info}\n"

                    return pokemon_name, output, type1, type2

            return None, f"Pokémon with Pokédex number {pokedex_number} not found.\n", None, None

    except FileNotFoundError:
        return None, "Error: '151pokemon.csv' not found. Please make sure the file is in the same directory.", None, None
    except ValueError:
        return None, "Error: Invalid Pokédex number format. Please enter a number.", None, None

def format_type_info(type_name, type_info):
    strengths = type_info["strong"]
    weaknesses = type_info["weak"]
    no_effects = type_info["no_effect"]
    
    output = f"{type_name} is 2x effective against: "
    output += ", ".join(strengths) if strengths else "None"
    
    output += "\n"
    output += f"{type_name} is 0.5x effective against: "
    output += ", ".join(weaknesses) if weaknesses else "None"
    
    if no_effects:
        output += "\n"
        output += f"{type_name} has no effect on: "
        output += ", ".join(no_effects)
    
    output += "\n"
    return output

# Prompt user for input with confirmation
try:
    while True:
        user_input = input("Enter a Pokémon's Pokédex number (1-151): ").strip()
        
        if not user_input.isdigit():
            print("Invalid input. Please enter a number.")
            continue
        
        pokedex_number = int(user_input)
        pokemon_name, info_output, type1, type2 = pokemon_info(pokedex_number)

        if not pokemon_name:
            print(info_output)
            continue  # Ask again if the number is invalid

        confirmation = input(f"You selected {pokemon_name}. Are you sure? (y/n): ").strip().lower()
        
        if confirmation == "y":
            print(info_output)
            
            # Generate and display radar chart(s)
            generate_radar(type1, type2)
            
            break
        elif confirmation == "n":
            print("Selection canceled. Try again.")
        else:
            print("Invalid response. Please enter 'y' or 'n'.")
        
except ValueError:
    print("Invalid input. Please enter a number.")
