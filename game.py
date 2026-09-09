"""The Unwritten Dawn - a folklore-inspired text-based adventure game."""

from __future__ import annotations

from dataclasses import dataclass, field
from textwrap import dedent, fill


WIDTH = 78


def say(text: str = "") -> None:
    """Print wrapped story text while preserving paragraph breaks."""
    for paragraph in dedent(text).strip().split("\n\n"):
        if paragraph.strip():
            print(fill(" ".join(paragraph.split()), width=WIDTH))
        print()


def line() -> None:
    print("=" * WIDTH)

@dataclass
class GameState:
    name: str
    location: str = "Village Square"
    fragments: set[str] = field(default_factory=set)
    lore: set[str] = field(default_factory=set)
    relationships: dict[str, int] = field(
        default_factory=lambda: {"Amara": 0, "Borin": 0, "Celia": 0}
    )
    flags: set[str] = field(default_factory=set)
    checkpoints: list[str] = field(default_factory=lambda: ["Midnight Village"])

class Game:
    checkpoint_text = {
        "Midnight Village": "Return to the village square at the beginning.",
        "Three Threads": "Return before exploring the 3 broken stories.",
        "Lantern Fields": "Return to the final Dawn-Gate",
    }

    def __init__(self) -> None:
        self.state = GameState | None = None

    def title(self) -> None:
        line()
        print("                         THE UNWRITTEN DAWN")
        print("                 A story that changes as you tell it")
        line()
        say(
            "Dawn has vanished from Ndembe. You are its youngest storykeeper, "
            "and only three forgotten story-fragments can bring morning back."
        )
        print("Type HELP at any time.\n")

    def choose(self, prompt: str, options: list[str]) -> int:
        """Present numbered choices while allowing typed commands."""
        while True:
            for index, option in enumerate(options, start=1):
                print(f"  {index}. {option}")

            answer = input(f"\n{prompt} ").strip()

            if answer.isdigit() and 1 <= int(answer) <= len(options):
                return int(answer)

            if self.command(answer):
                continue

            print("\nPlease enter a listen number or type HELP.\n")

    def command(self, raw: str) -> bool:
        """Handle a non-story command. Returns True if recognized."""
        words = raw.lower().split()
        if not words:
            return False

        command = words[0]
        argument = " ".join(words[1:])

        if command in {"help", "h", "?"}:
            say (
                "Commands: LOOK describes your location. INVENTORY shows your "
                "story fragments. STORIES show remembered love. TALK shows your "
                "companions. RETELL <fragment> gives a hint. CHECKPOINT lets you "
                "revisit an unlocked chapter. RESTART begins again. QUIT exits."
            )

        elif command in {"look", "l"}:
            self.look()

        elif command in {"inventory", "i", "fragments"}:
            self.inventory()

        elif command in {"stories", "lore"}:
            self.stories()

        elif command in {"talk", "companions", "friends"}:
            self.talk()

        elif command == "retell":
            self.retell_hint(argument)

        elif command in {"checkpoint", "checkpoints"}:
            self.checkpoint_menu()

        elif command == "restart":
            self.restart()

        elif command in {"quit", "exit", "q"}:
            print("\nThe unfinished story waits patiently for your return. Goodbye.")
            raise SystemExit

        else:
            return False

        return True

    def look(self) -> None:
        places = {
            "Village Square": (
                "A moon that has forgotten how to set hangs over Ndembe. "
                "Paths lead west to the silent market, north to the baobab "
                "archive, and east to the river of echoes."
            ),
            "Silent Market": (
                "Shuttered stalls surround a copper bell above the baker's stall. "
                "Amara watches it as though it has accused her of something."
            ),
            "Baobab Archive": (
                "The old baobab holds a library in its roots. Borin sits inside "
                "its sealed hollow, surrounded by pages that refuse to keep words."
            ),
            "River of Echoes": (
                "The black river repeats every sound except its own. Celia listens "
                "at its edge for an answer beneath the water."
            ),
            "Lantern Fields": (
                "Unlit lanterns stretch towards the horizon. The Dawn-Gate beyond "
                "them is stitched shut with silver thread."
            ),
        }
        say(places.get(self.state.location, "You are between chapters of the story."))

    def inventory(self) -> None:
        if not self.state.fragments:
            say("Your story bag is empty. Its pages are waiting for a beginning.")
            return

        say("Story fragments: " + ", ".join(sorted(self.state.fragments)) + ".")
        print("Use RETELL COURAGE, RETELL MEMORY, or RETELL MERCY for hints.\n")

    def stories(self) -> None:
        if not self.state.lore:
            say("You have not uncovered any hidden lore yet.")
            return

        say("Remembered lore: " + "; ".join(sorted(self.state.lore)) + ".")

    def talk(self) -> None:
        descriptions = {
            "Amara": "the baker's daughter, whose bell has falled silent",
            "Borin": "the archivist, whose pages have lost their words",
            "Celia": "the river listener, whose voice has been swallowed by the water",
        }

        for person, description in descriptions.items():
            trust = self.state.relationships[person]
            mood = "wary" if trust <= 0 else "friendly" if trust == 0 else "devoted"
            print(f"  {person} - ({mood}): {description}.")

        print()

    def retell_hint(self, argument: str) -> None:
        if not argument:
            say("Try RETELL COURAGE, RETELL MEMORY, or RETELL MERCY for a hint.")
            return

        fragment = argument.title()

        if fragment not in self.state.fragments:
            say("You do not carry that story fragment yet.")
            return

        hints = {
            "Courage": "Courage gives a voice to something that has been silenced.",
            "Memory": "Memory restores what fear has hidden or erased.",
            "Mercy": "Mercy lets a wound become a door instead of a wall.",
        }

        say(hints[fragment])

    def unlock(self, checkpoint: str) -> None:
        if checkpoint not in self.state.checkpoint:
            self.state.checkpoints.append(checkpoint)

    def checkpoint_menu(self) -> None:
        say (
            "Choose a chapter to revisit. Revisiting resets the story to that "
            "chapter's opening, but keeps your unlocked chapter list."
        )

        for index, checkpoint in enumerate(self.state.checkpoints, start=1):
            print(f"  {index}. {checkpoint} - {self.description_text[checkpoint]}")

        print("  0. Return to the current scene\n")

        while True:
            answer = input("Chapter: ").strip()

            if answer == "0":
                print()
                return

            if answer.isdigit() and 1 <= int(answer) <= len(self.state.checkpoints):
                self.restore_checkpoint(self.state.checkpoints[int(answer) - 1])
                return

            print("Please enter a listen number.")

    def restore_checkpoint(self, checkpoint: str) -> None:
        old_name = self.state.name
        unlocked = self.state.checkpoints[:]
        self.state = GameState(name=old_name, checkpoints=unlocked)

        if checkpoint == "Three Threads":
            self.state.flags.add("three_threads")

        elif checkpoint == "Lantern Fields":
            self.state.fragments.update({"Courage", "Memory", "Mercy"})
            self.state.flags.update({"market_done", "archive_done", "river_done"})

        say(f"You return to: {checkpoint}.")

        if checkpoint == "Midnight Village":
            self.prologue()
        elif checkpoint == "Three Threads":
            self.story_hub()
        else:
            self.lantern_fields()

    def restart(self) -> None:
        answer = input("Are you sure you want to restart? (yes/no) ").strip().lower()

        if answer in {"yes", "y"}:
            self.new_game()
        else:
            print()

    def new_game(self) -> None:
        name = input("What is your name, storykeeper? ").strip()
        self.state = GameState(name=name or "Storykeeper")
        self.prologue()

    def prologue(self) -> None:
        self.state.location = "Village Square"

        say(
            f"{self.state.name}, you wake to a village that has forgotten how to greet the dawn. "
            "No birds call. No smoke rises from ovens. The moon hangs in the sky, but it has forgotten how to set. "
            "Ndembe like an eye that refuses to blink."
        )

        say(
            "At your door rests your teacher's story bag. Inside is one silver "
            "thread and a note: 'Morning is not a thing that arrives. It is a "
            "story we agree to tell together. Find its 3 lost lines.'"
        )

        self.state.lore.add("A dawn is a story told together")
        say("Three paths lead from the square. Each holds a broken tale.")
        self.story_hub()

    def story_hub(self) -> None:
        self.unlock("Three Threads")

        while len(self.state.fragments) < 3:
            self.state.location = "Village Square"

            labels = []
            actions = []

            if "market_done" not in self.state.flags:
                labels.append("Visit the silent market with Amara")
                actions.append(self.market)

            if "archive_done" not in self.state.flags:
                labels.append("Visit the baobab archive with Borin")
                actions.append(self.archive)

            if "river_done" not in self.state.flags:
                labels.append("Visit the river of echoes with Celia")
                actions.append(self.river_of_echoes)

            say("The silver thread pulls toward three unfinished stories.")
            selected = self.choose("Where will you go?", labels)
            actions[selected - 1]()

        self.unlock("Lantern Fields")
        self.lantern_fields()

    def market(self) -> None:
        self.state.location = "Silent Market"

        say(
            "Amara stands beneath her family's copper bell. 'The bell used to "
            "call the morning bread awake,' she says. 'Last night I lied and "
            "told everyone the ovens would be fine. Now the bell will not "
            "speak to a liar.'"
        )

        answer = self.choose(
            "How do you answer Amara?",
            [
                "Tell Amara that a lie can be repaired by a brave truth.",
                "Promise to fix the bell before anyone notices.",
                "Ask what was she trying to protect.",
            ],
        )

        if answer == 1:
            self.state.relationships["Amara"] += 2
            say("Amara nods, though her eyes glisten. 'Then listen with me.'")

        elif answer == 2:
            say("'That is what I did,' Amara says softly. 'It is why the silence grew.'")

        else:
            self.state.relationships["Amara"] += 1
            self.state.lore.add("Amara feared the village would lose hope.")
            say(
                "'My father is ill,' Amara admits. 'I wanted one ordinary morning "
                "before everyone knew.'"
            )

        say("The bell's clapper is missing. Three objects wait beneath the stall.")

        answer = self.choose(
            "What do you use to call the bell's voice back?"
            [
                "A hard stone, to force the bell to ring.",
                "Amara's spoken confession beneath the bell.",
                "A coin from the till, as payment to the bell.",
            ],
        )

        if answer == 2:
            self.state.relationships["Amara"] += 1
            say(
                "Amara tells the market exactly what she feared. Her voice shakes, "
                "then steadies. The copper bell answers with one bright note: "
                "'The small voice that tells the truth can wake a mountain.'"
            )
        else:
            say(
                "The bell makes no sound. Amara tells the truth anyway. Only then "
                "does its note bloom across the market. It did not need force or "
                "payment. It needed courage."
            )

        self.state.fragments.add("Courage")
        self.state.flags.add("market_done")
        say("You collect the Fragment of Courage. It warms the story-bag like sunrise.")

    def archive(self) -> None:
        self.state.location = "Baobab Archive"

        say(
            "Borin is surrounded by pages that empty themselves as he reads. "
            "'I wrote down every story in Ndembe,' he says. 'But the oldest "
            "tale was never written. Now I cannot remember it, and the tree "
            "has sealed its hollow.'" 
        )

        answer = self.choose(
            "What do you tell Borin?",
            [
                "A story can live in people, not only on pages.",
                "We should copy the remaining pages before they vanish.",
                "The tree is wrong to keep its knowledge hidden.",
            ],
        )

        if answer == 1:
            self.state.relationships["Borin"] += 2
            say("'Then perhaps I have been keeping stories instead of listening to them.'")

        elif answer == 2:
            self.state.relationships["Borin"] += 1
            say("Together you save a few lines, but each copied word grows thinner.")

        else:
            say(
                "Borin flinches. 'The tree has kept us safe for generations. "
                "It does not close without grief"
            )

        say("Three root-knots mark the sealed hollow: a handprint, blank page, and broken quill.")

        answer = self.choose(
            "Which memory do you offer the baobab?",
            [
                "Borin's first written story, praised by his teacher.",
                "A village song you remember imperfectly, but sing anyway.",
                "The blank page, promising the tree a record of its secrets.",
            ],
        )

        if answer == 2:
            self.state.relationships["Borin"] += 1
            self.state.lore.add("The first story was sung, not written")
            say(
                "Your uncertain song winds through the roots. Borin joins on the "
                "second line; the baobab hums the missing third. Its hollow opens. "
                "'Memory is not perfect,' it whispers. 'Memory is shared.'"
            )
        else:
            say(
                "The roots remain still until Borin stops seeking exact words and "
                "sings the old song as he remembers it. The hollow opens."
            )

        self.state.fragments.add("Memory")
        self.state.flags.add("archive_done")
        say("You collect the Fragment of Memory. Its letters rearrange when you blink.")

    def river(self) -> None:
        self.state.location = "River of Echoes"

        say(
            "Celia kneels beside the river. 'My sister crossed years ago,' he says. "
            "'Tonight the water repeats her last words forever. I asket it to give "
            "her back. It answered by taking every other voice from the village.'"
        )

        answer = self.choose(
            "How do you respond?",
            [
                "Tell Celia to command the river ro release what it stole.",
                "Sit beside her and listen without trying to solve the grief.",
                "Tell her the river should be damned before it hurts anyone else.",
            ],
        )

        if answer == 2:
            self.state.relationships["Celia"] += 2
            say(
                "At last Celia says, 'She did not ask me to bring her back. "
                "She asked me to let her go.'"
            )
        else:
            say(
                "Beneath the water, Celia's sister's echo says, "
                "'Sister, do not turn love into a net.'"
            )

        say("The river offers a reed bridge, submerged stones, and a frayed boat.")

        answer = self.choose(
            "How do you cross towards the echo?",
            [
                "Take the bridge and refuse to look down.",
                "Step on the stones and repeat Celia's sister's words.",
                "Untie the boat and demand the river carry you.",
            ],
        )

        if answer == 2:
            self.state.relationships["Celia"] += 1
            self.state.lore.add("Love can release without forgetting")
            say(
                "You repeat: 'Do not turn love into a net.' The river clears. "
                "Celia's sister smiles from the far bank-not returned, but no "
                "longer trapped. A pearl of light rises from the water."
            )
        else:
            say(
                "The river returns you gently to shore. Celia finally speaks her "
                "sister's words as a farewell. A pearl of light rises from the water."
            )

        self.state.fragments.add("Mercy")
        self.state.flags.add("river_done")
        say("You collect the Fragment of Mercy. It is cool, bright and heavy.")

    def lantern_fields(self) -> None:
        