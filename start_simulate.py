from visualizer import SimHistory, DroneVisualizer
from typing import Any
from classes import Zone, Drone
import random
import sys

RESET = "\033[0m"
WHITE = "\033[0m"
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
PURPLE = "\033[35m"
LIGHT_GREEN = "\033[36m"
GRAY = "\033[37m"
RAINBOW = ""


class Start_Simulation():
    def __init__(self, data: Any, nb_drones: int) -> None:
        """
        Initialize simulation needed attributes
        """
        self.data: Any = data
        self.nb_drones: int = nb_drones
        self.Zones: dict = {}
        self.Drones: list[Drone] = []
        self.paths: list = []
        self.start_hub: Zone
        self.end_hub: Zone

    def _create_zones_class(self) -> None:
        """
        Function responsible for creating
        'zone' classes
        """
        for (name, zone) in self.data.items():
            self.Zones[name] = Zone(
                    name,
                    zone['x'],
                    zone['y'],
                    zone['zone'],
                    zone['type'],
                    zone['color'],
                    zone['max_drones'],
                    zone['edges'],
                    )

    def _create_drones(self) -> None:
        """
        Function responsible for creating
        'drone' classes
        """
        for drone in range(self.nb_drones):
            self.Drones.append(Drone(drone))

    def _find_all_paths(self) -> None:
        """
        Function responsible for finding all the paths possilbe
        using DFS algorithm
        """
        graph = self.Zones
        self.start_hub = [
            zone for (_, zone) in self.Zones.items() if
            zone.type == 'start_hub'][0]
        self.end_hub = [
            zone for (_, zone) in self.Zones.items() if
            zone.type == 'end_hub'][0]
        self.start_hub.current_drones = [id for id in range(self.nb_drones)]

        stack: list[tuple] = [(self.start_hub, [], 0, set())]

        while (stack):
            curr, path, cost, visited = stack.pop()

            if (curr.type == 'end_hub'):
                self.paths.append({'cost': cost, 'path': path})
                continue

            if (curr.name in visited or curr.zone == 'blocked'):
                continue

            new_visited = visited | {curr.name}

            for neighbor in curr.edges:
                stack.append(
                    (
                        graph[neighbor['to']],
                        path + [neighbor['to']],
                        cost + neighbor['cost'],
                        new_visited))

            self.paths = sorted(self.paths, key=lambda x: x['cost'])

    def _print_log(
            self,
            drone_id: int,
            zone_name: str) -> None:
        """
        Function responsible for printing simulation
        logs
        """
        colors: dict = {
            WHITE: [],
            BLACK: ['black', 'darkred'],
            RED: ['red', 'maroon', 'crimson'],
            GREEN: ['green'],
            YELLOW: ['orange', 'yellow', 'brown', 'gold'],
            BLUE: ['blue', 'cyan'],
            PURPLE: ['purple', 'magenta', 'violet'],
            LIGHT_GREEN: ['lime'],
            GRAY: ['gray'],
            RAINBOW: ['rainbow']
        }
        zone_color: str = self.Zones[zone_name].color
        color_selected: str = ""
        last_color: str = ""

        for (color, opts) in colors.items():
            if (zone_color in opts):
                color_selected = color
                break

        if (color_selected == RAINBOW):
            output: str = (
                f'D{drone_id}' +
                f'-{zone_name}-' +
                f'{len(self.Zones[zone_name].current_drones)}')

            for c in output:
                color_selected = last_color
                while (color_selected == last_color):
                    color_selected = random.choice(list(colors.keys()))

                print(
                    f'{color_selected}{c}{RESET}', end='')
                last_color = color_selected
            print(' ', end='')

        else:
            print(
                f'{color_selected}D{drone_id}-{zone_name}' +
                f'-{len(self.Zones[zone_name].current_drones)}' +
                f'{RESET}', end=' ')

    def let_drone_fly(self) -> None:
        """
        The main function that's runs everything
        Steps:
            1: Creating Zone classes
            2: Creating Drone classes
            3: Finding all the possible
            4: start simulation by move each drone to the selected drone path
                (selected drone path = drone.id % paths.length)
                (i limited paths length to 4 for using only the 4 shortest
                    paths)
        """
        self._create_zones_class()
        self._create_drones()
        self._find_all_paths()
        paths_length = len(self.paths)
        paths_length = paths_length if paths_length <= 4 else 4

        # print(self.paths)

        history = SimHistory()

        if (paths_length == 0):
            sys.exit(
                "[ERROR]: There is no path" +
                " between 'start_hub' to 'end_hub'!")

        all_received = 0
        turns = 0

        while not all_received:
            output: str = ""

            for drone in self.Drones:
                if drone.current_zone == self.end_hub.name:
                    continue

                if drone.skip_next:
                    drone.skip_next = False
                    dest_name = drone.transit_dest

                    # dest_zone = self.Zones[dest_name]
                    # dest_zone.current_drones.append(drone.id)

                    drone.current_zone = dest_name
                    output += f"D{drone.id}-{dest_name} "
                    self._print_log(drone.id, dest_name)
                    continue

                if (drone.pos >= len(
                        self.paths[drone.id % paths_length]['path'])):
                    continue

                curr_zone = self.Zones[drone.current_zone]
                drone_path = self.paths[drone.id % paths_length]['path']
                next_name = drone_path[drone.pos]
                next_zone = self.Zones[next_name]

                if (len(next_zone.current_drones) < next_zone.max_capacity):
                    drone.pos += 1

                    if next_zone.zone == 'restricted':
                        drone.skip_next = True
                        drone.transit_dest = next_name
                        conn = f"{drone.current_zone}-{next_name}"

                        curr_zone.current_drones.remove(drone.id)
                        drone.current_zone = f"transit:{next_name}"

                        target_zone = self.Zones[next_zone.name]
                        target_zone.current_drones.append(drone.id)

                        output += f"D{drone.id}-{conn} "

                        self._print_log(drone.id, next_name)
                        # drone.pos += 1
                        continue
                    else:
                        curr_zone.current_drones.remove(drone.id)
                        next_zone.current_drones.append(drone.id)
                        drone.current_zone = next_name
                        output += f"D{drone.id}-{next_name} "
                        self._print_log(drone.id, next_name)

            turns += 1
            print()

            all_received = all(
                D.current_zone == self.end_hub.name for D in self.Drones)
            history.record(turns, output, self.Drones, self.Zones)

        print(f"Turns: {turns}")
        viz = DroneVisualizer(self.Zones, history, interval=900)
        viz.run()
