def pokemon_type_checker(pokemon_type):
    """
    Checks if a Pokémon is a pokemon type and identifies its strengths and weaknesses.

    Args:
        pokemon_type: A string representing the Pokémon's type (e.g., "Fire", "Water").

    Returns:
        A dictionary containing information about the Pokémon's type, 
        strengths, and weaknesses, or a message if the type is invalid.
    """

    type_chart = {
        "Normal": {"strong": [], "weak": ["Rock", "Steel"], "no_effect": ["Ghost"]},
        "Fire": {"strong": ["Grass", "Bug", "Steel", "Ice"], "weak": ["Fire", "Water", "Rock", "Dragon"], "no_effect": []},
        "Water": {"strong": ["Fire", "Ground", "Rock"], "weak": ["Water", "Grass", "Dragon"], "no_effect": []},
        "Grass": {"strong": ["Water", "Ground", "Rock"], "weak": ["Fire", "Grass", "Poison", "Flying", "Bug", "Dragon", "Steel"], "no_effect": []},
        "Electric": {"strong": ["Water", "Flying"], "weak": ["Electric", "Grass", "Dragon"], "no_effect": ["Ground"]},
        "Rock": {"strong": ["Fire", "Flying", "Bug", "Ice"], "weak": ["Fighting", "Ground", "Steel", "Water", "Grass"], "no_effect": []},
        "Ground": {"strong": ["Fire", "Electric", "Poison", "Rock", "Steel"], "weak": ["Water", "Grass", "Ice"], "no_effect": ["Flying"]},
        "Flying": {"strong": ["Fighting", "Bug", "Grass"], "weak": ["Electric", "Ice", "Rock"], "no_effect": []},
        "Poison": {"strong": ["Grass", "Fairy"], "weak": ["Poison", "Ground", "Rock", "Ghost"], "no_effect": []},
        "Fighting": {"strong": ["Normal", "Rock", "Steel", "Ice", "Dark"], "weak": ["Flying", "Psychic", "Fairy", "Poison", "Bug"], "no_effect": []},
        "Psychic": {"strong": ["Fighting", "Poison"], "weak": ["Psychic", "Steel", "Dark"], "no_effect": []},
        "Bug": {"strong": ["Grass", "Psychic", "Dark"], "weak": ["Fire", "Flying", "Poison", "Fighting", "Steel", "Fairy"], "no_effect": []},
        "Ghost": {"strong": ["Ghost", "Psychic"], "weak": ["Ghost", "Dark"], "no_effect": ["Normal"]},
        "Steel": {"strong": ["Ice", "Rock", "Fairy"], "weak": ["Fire", "Fighting", "Ground"], "no_effect": []},
        "Dark": {"strong": ["Ghost", "Psychic"], "weak": ["Fighting", "Fairy", "Bug"], "no_effect": []},
        "Dragon": {"strong": ["Dragon"], "weak": ["Dragon", "Ice", "Fairy"], "no_effect": []},
        "Ice": {"strong": ["Grass", "Ground", "Flying", "Dragon"], "weak": ["Fire", "Fighting", "Rock", "Steel"], "no_effect": []},
        "Fairy": {"strong": ["Fighting", "Dragon", "Dark"], "weak": ["Poison", "Steel", "Fire"], "no_effect": []},
    }

    if pokemon_type in type_chart:
        type_info = type_chart[pokemon_type]
        strengths = type_info["strong"]
        weaknesses = type_info["weak"]
        no_effects = type_info["no_effect"]

        output = f"{pokemon_type} is 2x effective against: "
        if strengths:
            output += ", ".join(strengths)  # Join with commas
        else:
            output += "None" # Handle empty list

        output += "\n"  # Newline for better formatting
        output += f"{pokemon_type} is 0.5x effective against: " # Assuming 0.5x for weaknesses
        if weaknesses:
            output += ", ".join(weaknesses)
        else:
            output += "None"

        if no_effects:
            output += "\n"
            output += f"{pokemon_type} has no effect on: "
            output += ", ".join(no_effects)
        return output
    else:
        return f"'{pokemon_type}' is an invalid Pokémon type."


# Example usage:
print("Types Called!")