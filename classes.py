class Zone():
    def __init__(
            self,
            name: str,
            x: int,
            y: int,
            zone: str,
            type: str,
            color: str,
            max_capacity: int,
            edges: list[dict],
            current_drones: list = [],
            ) -> None:
        """
        Initialize Zone needed attributes
        """
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone: str = zone
        self.type: str = type
        self.color: str = color
        self.max_capacity: int = max_capacity
        self.edges: list[dict] = edges
        self.current_drones: list[int] = []
        self.counter: int = 0


class Drone():
    def __init__(self, id: int) -> None:
        """
        Initialize Drone needed attributes
        """
        self.id: int = id
        self.current_zone: str = 'start'
        self.target_zone: str = ''
        self.path: list[dict] = []
        self.pos: int = 0
        self.skip_next: bool = False
        self.transit_dest: str = ''
