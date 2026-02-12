"""Turn-based RPG: Reptiles (spellcasters) vs Mammals (melee fighters).

Run:
    python rpg_game.py
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Callable


@dataclass(frozen=True)
class Move:
    name: str
    min_damage: int
    max_damage: int
    description: str

    def roll_damage(self) -> int:
        return random.randint(self.min_damage, self.max_damage)


@dataclass
class Fighter:
    name: str
    species_type: str
    hp: int
    max_hp: int
    moves: list[Move]
    is_ai: bool = False

    @property
    def alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        self.hp = max(self.hp - amount, 0)

    def heal(self, amount: int) -> None:
        self.hp = min(self.hp + amount, self.max_hp)


REPTILE_MOVES = [
    Move("Fire Spit", 12, 20, "Spit blazing magic at your enemy."),
    Move("Venom Hex", 8, 18, "Curse the foe with poisonous sorcery."),
    Move("Tailstorm", 10, 16, "Summon a whipping magical tail wind."),
]

MAMMAL_MOVES = [
    Move("Sword Slash", 10, 18, "A fast cut with a sharp blade."),
    Move("Hammer Blow", 12, 20, "A heavy strike with crushing force."),
    Move("Shield Bash", 8, 14, "Bash the opponent and stagger them."),
]


InputFn = Callable[[str], str]


def choose_species(input_fn: InputFn = input) -> str:
    while True:
        print("Choose your class:")
        print("1) Reptile (spellcaster)")
        print("2) Mammal (melee)")
        choice = input_fn("Enter 1 or 2: ").strip()

        if choice == "1":
            return "reptile"
        if choice == "2":
            return "mammal"

        print("Invalid choice. Try again.\n")


def build_fighter(name: str, species_type: str, is_ai: bool = False) -> Fighter:
    if species_type == "reptile":
        return Fighter(name=name, species_type=species_type, hp=100, max_hp=100, moves=REPTILE_MOVES.copy(), is_ai=is_ai)
    return Fighter(name=name, species_type=species_type, hp=110, max_hp=110, moves=MAMMAL_MOVES.copy(), is_ai=is_ai)


def choose_move_human(fighter: Fighter, input_fn: InputFn = input) -> Move:
    while True:
        print(f"\n{fighter.name}'s turn. HP: {fighter.hp}/{fighter.max_hp}")
        for i, move in enumerate(fighter.moves, start=1):
            print(f"{i}) {move.name} ({move.min_damage}-{move.max_damage} dmg): {move.description}")

        raw = input_fn("Select move number: ").strip()
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(fighter.moves):
                return fighter.moves[idx]

        print("Invalid move selection. Try again.")


def choose_move_ai(fighter: Fighter) -> Move:
    return random.choice(fighter.moves)


def perform_turn(attacker: Fighter, defender: Fighter, input_fn: InputFn = input) -> None:
    move = choose_move_ai(attacker) if attacker.is_ai else choose_move_human(attacker, input_fn)
    damage = move.roll_damage()
    defender.take_damage(damage)

    print(f"\n{attacker.name} uses {move.name}! It deals {damage} damage to {defender.name}.")
    print(f"{defender.name} HP: {defender.hp}/{defender.max_hp}")


def battle(player: Fighter, enemy: Fighter, input_fn: InputFn = input) -> Fighter:
    print("\n=== BATTLE START ===")
    print(f"{player.name} ({player.species_type.title()}) vs {enemy.name} ({enemy.species_type.title()})")

    turn_order = [player, enemy]
    random.shuffle(turn_order)

    print(f"\n{turn_order[0].name} goes first!")

    while player.alive and enemy.alive:
        attacker, defender = turn_order
        perform_turn(attacker, defender, input_fn)

        if not defender.alive:
            print(f"\n{defender.name} has fallen!")
            print(f"{attacker.name} wins the battle!")
            return attacker

        turn_order.reverse()

    return player if player.alive else enemy


def main() -> None:
    print("Welcome to Lizard Wizard RPG!")
    player_name = input("Enter your fighter name: ").strip() or "Hero"
    player_species = choose_species()
    player = build_fighter(player_name, player_species, is_ai=False)

    ai_species = "mammal" if player_species == "reptile" else "reptile"
    enemy_name = random.choice(["Fang", "Brutus", "Sable", "Rexa"])
    enemy = build_fighter(enemy_name, ai_species, is_ai=True)

    print(f"\nYou are a {player.species_type} with {player.hp} HP.")
    print(f"Your opponent is {enemy.name}, a {enemy.species_type} with {enemy.hp} HP.")

    winner = battle(player, enemy)

    if winner is player:
        print("\nVictory is yours!")
    else:
        print("\nDefeat... but you can always play again!")


if __name__ == "__main__":
    main()
