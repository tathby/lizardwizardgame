"""Lizard Wizard Arena - 2v2 turn-based RPG.

Features:
- Reptiles are spellcasters; mammals are melee specialists.
- Two-player style move selection (you choose moves for both teams) each round.
- Round actions resolve in order of fighter speed (SPD).
- Detailed character roster with unique HP/DEF/SPD and ability drawbacks.

Run:
    python rpg_game.py
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Callable


@dataclass(frozen=True)
class Ability:
    name: str
    power: int
    kind: str  # attack | heavy_attack | self_heal | guard_break
    accuracy: float = 1.0
    self_damage: int = 0
    self_slow: int = 0
    target_defense_scale: float = 1.0
    heal_amount: int = 0
    description: str = ""


@dataclass
class Fighter:
    name: str
    faction: str  # reptile | mammal
    hp: int
    max_hp: int
    defense: int
    speed: int
    abilities: list[Ability]

    @property
    def alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> int:
        dealt = max(amount, 0)
        self.hp = max(self.hp - dealt, 0)
        return dealt

    def heal(self, amount: int) -> int:
        before = self.hp
        self.hp = min(self.max_hp, self.hp + max(0, amount))
        return self.hp - before


@dataclass
class PlannedAction:
    actor: Fighter
    ability: Ability
    target: Fighter


def build_roster() -> dict[str, dict[str, Fighter]]:
    reptiles = {
        "pyra": Fighter(
            name="Pyra",
            faction="reptile",
            hp=100,
            max_hp=100,
            defense=8,
            speed=14,
            abilities=[
                Ability("Flame Dart", 24, "attack", description="Reliable fire spell."),
                Ability("Volcanic Surge", 38, "heavy_attack", accuracy=0.75, self_damage=6, description="Huge burst; recoil on cast."),
                Ability("Molten Shedding", 0, "self_heal", heal_amount=20, self_slow=2, description="Heals but lowers own speed this round."),
            ],
        ),
        "strix": Fighter(
            name="Strix",
            faction="reptile",
            hp=92,
            max_hp=92,
            defense=7,
            speed=18,
            abilities=[
                Ability("Arc Lash", 20, "attack", description="Fast crackling strike."),
                Ability("Static Implosion", 34, "heavy_attack", accuracy=0.8, self_slow=3, description="Big damage but drains momentum."),
                Ability("Hex Siphon", 16, "guard_break", target_defense_scale=0.4, description="Penetrates defense with cursed shock."),
            ],
        ),
        "verdra": Fighter(
            name="Verdra",
            faction="reptile",
            hp=112,
            max_hp=112,
            defense=11,
            speed=10,
            abilities=[
                Ability("Thorn Volley", 22, "attack", description="Nature-infused projectile burst."),
                Ability("Basilisk Gaze", 30, "guard_break", target_defense_scale=0.3, accuracy=0.85, description="Armor-piercing petrify beam."),
                Ability("Regrowth Ritual", 0, "self_heal", heal_amount=26, self_damage=5, description="Powerful heal that costs blood."),
            ],
        ),
        "nox": Fighter(
            name="Nox",
            faction="reptile",
            hp=98,
            max_hp=98,
            defense=9,
            speed=15,
            abilities=[
                Ability("Shadow Fang", 23, "attack", description="Dark magic bite."),
                Ability("Nightfall Rift", 40, "heavy_attack", accuracy=0.7, self_damage=8, description="Massive tear in space, harsh recoil."),
                Ability("Veil Pierce", 18, "guard_break", target_defense_scale=0.2, description="Low raw damage, almost ignores armor."),
            ],
        ),
    }

    mammals = {
        "brakk": Fighter(
            name="Brakk",
            faction="mammal",
            hp=120,
            max_hp=120,
            defense=13,
            speed=9,
            abilities=[
                Ability("Cleaver Chop", 22, "attack", description="Heavy cleaver slash."),
                Ability("Earthsplitter", 36, "heavy_attack", accuracy=0.78, self_slow=2, description="Crushing blow; slows the wielder."),
                Ability("Ribbreaker", 19, "guard_break", target_defense_scale=0.35, description="Armor-cracking strike."),
            ],
        ),
        "lyra": Fighter(
            name="Lyra",
            faction="mammal",
            hp=96,
            max_hp=96,
            defense=8,
            speed=19,
            abilities=[
                Ability("Twin Daggers", 21, "attack", description="Rapid dual stab."),
                Ability("Crimson Rush", 33, "heavy_attack", accuracy=0.82, self_damage=5, description="Risky lunge with self-bleed."),
                Ability("Bandage Twist", 0, "self_heal", heal_amount=18, self_slow=1, description="Patch wounds, lose a bit of tempo."),
            ],
        ),
        "tor": Fighter(
            name="Tor",
            faction="mammal",
            hp=110,
            max_hp=110,
            defense=12,
            speed=12,
            abilities=[
                Ability("Warhammer Jab", 23, "attack", description="Controlled hammer strike."),
                Ability("Sundering Slam", 31, "guard_break", target_defense_scale=0.25, accuracy=0.86, description="Defense-shattering overhead swing."),
                Ability("Last Stand", 39, "heavy_attack", accuracy=0.72, self_damage=9, description="Huge hit with dangerous recoil."),
            ],
        ),
        "sable": Fighter(
            name="Sable",
            faction="mammal",
            hp=104,
            max_hp=104,
            defense=10,
            speed=16,
            abilities=[
                Ability("Spear Thrust", 22, "attack", description="Precise piercing thrust."),
                Ability("Skewer Storm", 35, "heavy_attack", accuracy=0.79, self_slow=2, description="Ferocious combo that overextends."),
                Ability("Hamstring Cut", 17, "guard_break", target_defense_scale=0.3, description="Lowers impact of enemy armor."),
            ],
        ),
    }

    return {"reptile": reptiles, "mammal": mammals}


InputFn = Callable[[str], str]


def show_main_menu() -> None:
    print("\n=== Lizard Wizard Arena ===")
    print("1) Start 2v2 Battle")
    print("2) View Character Compendium")
    print("3) Quit")


def print_roster_details(roster: dict[str, dict[str, Fighter]]) -> None:
    print("\n=== Character Compendium ===")
    for faction in ("reptile", "mammal"):
        print(f"\n{faction.title()} Team")
        print("-" * 60)
        for fighter in roster[faction].values():
            print(f"{fighter.name}: HP {fighter.max_hp} | DEF {fighter.defense} | SPD {fighter.speed}")
            for ab in fighter.abilities:
                drawback = []
                if ab.self_damage:
                    drawback.append(f"self-dmg {ab.self_damage}")
                if ab.self_slow:
                    drawback.append(f"self-slow {ab.self_slow}")
                if ab.accuracy < 1.0:
                    drawback.append(f"{int(ab.accuracy * 100)}% hit")
                drawback_text = f" | Drawback: {', '.join(drawback)}" if drawback else ""
                effect = f"power {ab.power}" if ab.kind != "self_heal" else f"heal {ab.heal_amount}"
                print(f"  - {ab.name}: {effect}. {ab.description}{drawback_text}")


def prompt_choice(input_fn: InputFn, prompt: str, low: int, high: int) -> int:
    while True:
        raw = input_fn(prompt).strip()
        if raw.isdigit() and low <= int(raw) <= high:
            return int(raw)
        print(f"Please enter a number from {low} to {high}.")


def choose_team(
    label: str,
    faction: str,
    roster: dict[str, dict[str, Fighter]],
    input_fn: InputFn,
) -> list[Fighter]:
    available = list(roster[faction].keys())
    selected: list[Fighter] = []
    print(f"\nChoose 2 {faction} fighters for {label}:")

    while len(selected) < 2:
        print("\nAvailable fighters:")
        for i, key in enumerate(available, start=1):
            f = roster[faction][key]
            print(f"{i}) {f.name} (HP {f.max_hp}, DEF {f.defense}, SPD {f.speed})")

        idx = prompt_choice(input_fn, f"Select fighter {len(selected) + 1}: ", 1, len(available)) - 1
        picked_key = available.pop(idx)
        proto = roster[faction][picked_key]
        selected.append(
            Fighter(
                name=proto.name,
                faction=proto.faction,
                hp=proto.max_hp,
                max_hp=proto.max_hp,
                defense=proto.defense,
                speed=proto.speed,
                abilities=proto.abilities,
            )
        )
    return selected


def list_targets(enemy_team: list[Fighter]) -> list[Fighter]:
    return [f for f in enemy_team if f.alive]


def choose_action(actor: Fighter, enemy_team: list[Fighter], input_fn: InputFn, controller_label: str) -> PlannedAction:
    print(f"\n[{controller_label}] {actor.name} (HP {actor.hp}/{actor.max_hp}, SPD {actor.speed}) choose ability:")
    for i, ab in enumerate(actor.abilities, start=1):
        extra = []
        if ab.self_damage:
            extra.append(f"self-dmg {ab.self_damage}")
        if ab.self_slow:
            extra.append(f"self-slow {ab.self_slow}")
        if ab.accuracy < 1.0:
            extra.append(f"{int(ab.accuracy * 100)}% hit")
        extra_text = f" ({', '.join(extra)})" if extra else ""
        print(f"{i}) {ab.name} - {ab.description}{extra_text}")

    ability = actor.abilities[prompt_choice(input_fn, "Choose ability: ", 1, len(actor.abilities)) - 1]

    targets = list_targets(enemy_team)
    if not targets:
        return PlannedAction(actor=actor, ability=ability, target=actor)

    print("Choose target:")
    for i, t in enumerate(targets, start=1):
        print(f"{i}) {t.name} (HP {t.hp}/{t.max_hp}, DEF {t.defense}, SPD {t.speed})")
    target = targets[prompt_choice(input_fn, "Choose target: ", 1, len(targets)) - 1]
    return PlannedAction(actor=actor, ability=ability, target=target)


def calculate_damage(ability: Ability, attacker: Fighter, target: Fighter) -> int:
    base = ability.power + random.randint(-4, 4)
    effective_def = int(target.defense * ability.target_defense_scale)
    dmg = base - effective_def
    return max(dmg, 1)


def resolve_action(action: PlannedAction) -> None:
    actor = action.actor
    ability = action.ability
    target = action.target

    if not actor.alive:
        print(f"{actor.name} is down and cannot act.")
        return

    if ability.kind == "self_heal":
        healed = actor.heal(ability.heal_amount)
        print(f"{actor.name} uses {ability.name} and heals {healed} HP.")
    else:
        if not target.alive:
            print(f"{actor.name} tries {ability.name}, but target is already down.")
        elif random.random() <= ability.accuracy:
            damage = calculate_damage(ability, actor, target)
            target.take_damage(damage)
            print(f"{actor.name} uses {ability.name} on {target.name} for {damage} damage.")
        else:
            print(f"{actor.name} uses {ability.name} but misses!")

    if ability.self_damage:
        recoil = actor.take_damage(ability.self_damage)
        print(f" -> Drawback: {actor.name} takes {recoil} recoil damage.")

    if ability.self_slow:
        old_speed = actor.speed
        actor.speed = max(1, actor.speed - ability.self_slow)
        print(f" -> Drawback: {actor.name}'s speed drops {old_speed} -> {actor.speed}.")


def all_down(team: list[Fighter]) -> bool:
    return all(not f.alive for f in team)


def display_teams(team_a: list[Fighter], team_b: list[Fighter]) -> None:
    print("\nTeam Reptiles:")
    for f in team_a:
        print(f"- {f.name}: HP {f.hp}/{f.max_hp} | DEF {f.defense} | SPD {f.speed}")

    print("Team Mammals:")
    for f in team_b:
        print(f"- {f.name}: HP {f.hp}/{f.max_hp} | DEF {f.defense} | SPD {f.speed}")


def battle_2v2(reptiles: list[Fighter], mammals: list[Fighter], input_fn: InputFn) -> None:
    round_no = 1
    print("\n=== 2v2 BATTLE START ===")

    while not all_down(reptiles) and not all_down(mammals):
        print(f"\n===== ROUND {round_no} =====")
        display_teams(reptiles, mammals)

        plans: list[PlannedAction] = []

        # Both "players" choose for their side before actions resolve.
        for fighter in reptiles:
            if fighter.alive:
                plans.append(choose_action(fighter, mammals, input_fn, "Reptile Player"))
        for fighter in mammals:
            if fighter.alive:
                plans.append(choose_action(fighter, reptiles, input_fn, "Mammal Player"))

        # Resolve by current speed descending; tiebreak random.
        plans.sort(key=lambda p: (p.actor.speed, random.random()), reverse=True)

        print("\n--- Action Resolution (by speed) ---")
        for action in plans:
            resolve_action(action)

        round_no += 1

    print("\n=== BATTLE OVER ===")
    if all_down(reptiles) and all_down(mammals):
        print("It's a draw! Both teams were wiped out.")
    elif all_down(mammals):
        print("Reptiles win!")
    else:
        print("Mammals win!")


def main(input_fn: InputFn = input) -> None:
    roster = build_roster()

    while True:
        show_main_menu()
        choice = prompt_choice(input_fn, "Choose option: ", 1, 3)

        if choice == 2:
            print_roster_details(roster)
            continue

        if choice == 3:
            print("Goodbye!")
            return

        reptiles = choose_team("Reptile Player", "reptile", roster, input_fn)
        mammals = choose_team("Mammal Player", "mammal", roster, input_fn)
        battle_2v2(reptiles, mammals, input_fn)

        again = input_fn("\nPlay another match? (y/n): ").strip().lower()
        if again != "y":
            print("Thanks for playing!")
            return


if __name__ == "__main__":
    main()
