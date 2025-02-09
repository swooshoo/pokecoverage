from src.pokemon import pokemon_info
from src.types import pokemon_type_checker


fire_pokemon_info = pokemon_type_checker("Fire")
print(fire_pokemon_info)

water_pokemon_info = pokemon_type_checker("Water")
print(water_pokemon_info)

invalid_pokemon = pokemon_type_checker("Normal")
print(invalid_pokemon)

# Example usage:
print(pokemon_info("Charizard"))
print(pokemon_info("bulbasaur"))
print(pokemon_info("Mewtwo"))
print(pokemon_info("pikachu"))
print(pokemon_info("MissingNo"))
print(pokemon_info("Charmander"))
