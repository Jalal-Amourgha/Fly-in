from parsing import Parsing
from start_simulate import Start_Simulation
import sys


def main() -> None:
    """
    Entry point
    """
    args: list[str] = sys.argv
    simulation: Start_Simulation
    pars: Parsing
    path: str = ""

    if (len(args) != 2):
        sys.exit("[ERROR]: Wrong program usage (py main.py <path>)")

    path = args[1]

    pars = Parsing(path)
    pars.generate_graph()

    simulation = Start_Simulation(pars.zones, pars.nb_drones)
    simulation.let_drone_fly()


if (__name__ == "__main__"):
    main()
