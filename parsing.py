from typing import Any
import sys
import re

RESET = "\033[0m"
RED = "\033[31m"


class Parsing():
    def __init__(self, path: str) -> None:
        """
        Initialize parsing needed attributes
        """
        self.data: list[str] = []
        self.path: str = path
        self.nb_drones: int = 0
        self.zones: dict = {}
        self.names: set[str] = set()
        self.coordinates: set[tuple] = set()
        self.connections: set[str] = set()
        self.pattern1: Any = r"^nb_drones:\s*(\d+)$"
        self.pattern2: Any = (
            r"^hub:\s+"
            r"([^#\s]+)\s+"
            r"(-?\d+(?:\.\d+)?)\s+"
            r"(-?\d+(?:\.\d+)?)"
            r"(?:\s+\[([^\[\]]+)\])?$"
        )
        self.pattern3: Any = (
            r"^connection:\s+"
            r"([^#\s]+)-([^#\s]+)(?:\s+\[([^\[\]]+)\])?$"
        )

    def _read_data(self) -> None:
        """
        Function responsible for reading file content
        (if it's exist)
        """
        try:
            with open(self.path, 'r') as file:
                data: str = file.read()

                if not (data):
                    self._print_error("Config file should not be empty")

                self.data = data.split('\n')

        except Exception:
            self._print_error("File not found")

    def _print_error(self, s: str) -> None:
        sys.exit(f"[ERROR]: {RED}{s}{RESET}!")

    def _convert_num(self, n: str, s: str) -> Any:
        """
        Function responsible for converting a
        possilbe n of type 'str'
        """
        try:
            nbr: int = int(n)
        except Exception:
            self._print_error(f"number of {s} is not valid")

        return (nbr)

    def _reverse_connection(self, connection: str) -> str:
        """
        Reversing connection between to hubs
        """
        return ('-'.join(connection.split('-')[::-1]))

    def _extract_regex_values(
            self,
            pattern: str,
            type: str,
            data: str) -> Any:
        """
        Function responsible for extracting
        values of ('hub' and 'connection')
        """
        values: Any = []

        try:
            match: Any = re.search(pattern, data)
            num_groups: Any = len(match.groups())
            for i in range(1, num_groups+1):
                if (match.group(i)):
                    values.append(match.group(i))

        except Exception:
            self._print_error(f"Wrong '{type}' format")

        return (values)

    def _extract_metadata(self, meta: str, type: str) -> Any:
        """
        Function responsible for extracting
        from metadata
        """
        rules: dict = {
                'zone': {
                    'normal': 1, 'blocked': -1,
                    'restricted': 2, 'priority': 1},
                'color': [
                    'red', 'blue', 'gray', 'orange', 'green',
                    'yellow', 'cyan', 'purple', 'brown', 'gold',
                    'lime', 'magenta', 'maroon', 'gold', 'black',
                    'darkred', 'crimson', 'rainbow', 'violet'
                    ],
                'max_drones': 1
                }
        metadata = {
                'zone': 'normal',
                'cost': 1,
                'max_drones': 1 if type == 'hub' else self.nb_drones,
                'color': "blue"
                }

        if (type == 'connection'):
            metadata = {'max_link_capacity': 1}

        pairs = re.findall(r"(\S+?)=(\S+)", meta)

        for p in pairs:
            key, value = p
            if (
                (type == 'connection' and key not in {'max_link_capacity'}) or
                (type == 'hub' and key not in {'zone', 'color', 'max_drones'})
            ):
                self._print_error("Wrong 'key' in metadata")

            if (key == 'zone'):
                if (value not in rules['zone']):
                    self._print_error("Wrong 'zone' value in metadata")
                metadata[key] = value
                metadata['cost'] = rules['zone'][value]

            if (key == 'color'):
                if (value not in rules['color']):
                    self._print_error("Wrong 'color' value in metadata")
                metadata[key] = value

            if (key == 'max_drones'):
                value = int(value)
                if (value < 1):
                    self._print_error("Wrong 'max_drones' value in metadata")
                metadata[key] = value

            if (key == 'max_link_capacity'):
                value = int(value)
                if not (1 <= value <= self.nb_drones):
                    self._print_error(
                        "Wrong 'max_link_capacity' " +
                        "value in metadata")
                metadata[key] = value

        return (metadata)

    def _create_zone(self, data: Any, hub: str = 'hub') -> dict:
        """
        Function responsible for creating a 'zone'
        """
        zone: dict = {'edges': []}
        meta: Any = {
                'zone': 'normal',
                'cost': 1,
                'max_drones': 1,
                'color': "blue"
                }

        if (len(data) == 3):
            name, x, y = data
        else:
            name, x, y, meta = data
            meta = self._extract_metadata(meta, hub)

        x = self._convert_num(x, 'x')
        y = self._convert_num(y, 'y')

        if (name in self.names):
            self._print_error(f"Name hub {name} is already exit")

        if ((x, y) in self.coordinates):
            self._print_error(f"Hub coordinate ({x,y}) is already exit")

        if (
            hub in {'start_hub', 'end_hub'} and
            meta['max_drones'] < self.nb_drones
        ):
            self._print_error(
                "Number of 'max_drones' in 'start_hub'" +
                " and 'end_hub' should not be less than 'nb_drones'")

        self.names.add(name)
        self.coordinates.add((x, y))

        zone['name'] = name
        zone['x'] = x
        zone['y'] = y
        zone |= meta
        zone['type'] = hub

        zone['x'], zone['y'] = zone['y'], zone['x']

        return (zone)

    def _create_connection(self, data: Any) -> None:
        """
        Function responsible for creating a 'connection'
        betweem two zones if they exist
        """
        meta: Any = {'max_link_capacity': 1}
        connection: str = ""

        if (len(data) == 2):
            src, dst = data
        else:
            src, dst, meta = data
            meta = self._extract_metadata(meta, 'connection')

        if (src not in self.names or dst not in self.names):
            self._print_error("Zone name not in the list")

        if (dst not in self.names):
            self._print_error(f"There is no hub called f'{dst}'")

        connection = f'{src}-{dst}'

        if (
            connection in self.connections or
            self._reverse_connection(connection) in self.connections
        ):
            self._print_error(f"This '{connection}' is already exist")

        self.connections.add(connection)

        self.zones[src]['edges'].append(
            {'to': dst, 'cost': self.zones[dst]['cost']} | meta
            )
        # self.zones[dst]['edges'].append(
        #     {'to': src, 'cost': self.zones[src]['cost']} | meta)

    def _check_data(self) -> None:
        """
        Function responsible for checking
        file data
        """
        order: list[bool] = [False for _ in range(5)]

        for line in self.data:
            line = line.strip()

            if (line.startswith(('#', '\n')) or not len(line)):
                continue

            if ('nb_drones:' in line):
                if (order[0]):
                    self._print_error(
                        "You can not define 'nb_drones'" +
                        " more than one time")
                else:
                    order[0] = True
                    nb_drones = int(self._extract_regex_values(self.pattern1,
                                                               'nb_drones',
                                                               line)[0])
                    if (nb_drones < 1):
                        self._print_error("'nb_drones' must a positive number")
                    self.nb_drones = nb_drones

                continue

            if ('hub' in line):
                if not (order[0]):
                    self._print_error(
                        "You can not define zones before " +
                        "defining 'nb_drones'")

                if (line.startswith('start_hub:')):
                    line = line.replace('start_hub', 'hub')
                    if (order[1]):
                        self._print_error(
                            "You can not define 'start_hub'" +
                            " more than one time")
                    else:
                        order[1] = True
                        values = self._extract_regex_values(
                            self.pattern2,
                            'start_hub',
                            line)
                        zone = self._create_zone(values, 'start_hub')
                        self.zones[zone['name']] = zone

                    continue

                if (line.startswith('end_hub:')):
                    line = line.replace('end_hub', 'hub')
                    if (order[2]):
                        self._print_error(
                            "You can not define 'end_hub' " +
                            "more than one time")
                    else:
                        order[2] = True
                        values = self._extract_regex_values(
                            self.pattern2,
                            'end_hub',
                            line)
                        zone = self._create_zone(values, 'end_hub')
                        self.zones[zone['name']] = zone

                    continue

                if (line.startswith('hub:')):
                    values = self._extract_regex_values(
                        self.pattern2, 'hub', line)
                    zone = self._create_zone(values, 'hub')
                    self.zones[zone['name']] = zone

                    continue

            if ('connection' in line):
                if not (order[0] or order[1] or order[2]):
                    self._print_error(
                        "You can define 'connections' before" +
                        " defining 'hubs' and 'nb_drones'")
                else:
                    order[3] = True
                    values = self._extract_regex_values(
                        self.pattern3,
                        'connection',
                        line)
                    self._create_connection(values)

    def generate_graph(self) -> None:
        """
        Entry point
        """
        self._read_data()
        self._check_data()
