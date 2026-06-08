import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as mpatches
from typing import Any
import tkinter as tk

ZONE_COLORS: dict[str, str] = {
    "normal":     "#4A90D9",
    "restricted": "#E67E22",
    "blocked":    "#C0392B",
    "priority":   "#27AE60",
}
START_COLOR = "#2ECC71"
END_COLOR = "#F1C40F"
EDGE_COLOR = "#7F8C8D"

DRONE_PALETTE = [
    "#E74C3C", "#3498DB", "#9B59B6", "#1ABC9C",
    "#F39C12", "#D35400", "#2980B9", "#8E44AD",
]


def _drone_color(drone_id: int) -> str:
    return DRONE_PALETTE[drone_id % len(DRONE_PALETTE)]


def _node_color(zone: Any) -> str:
    if zone.type == "start_hub":
        return START_COLOR
    if zone.type == "end_hub":
        return END_COLOR
    return ZONE_COLORS.get(zone.zone, "#4A90D9")


# ─────────────────────────────────────────────
#  History recorder  (call once per turn)
# ─────────────────────────────────────────────
class SimHistory:
    """Stores the per-turn snapshot needed by the visualizer."""

    def __init__(self) -> None:
        self.turns: list[dict] = []

    def record(
        self,
        turn: int,
        output_line: str,
        drones: list,          # list[Drone]
        zones: dict,           # dict[str, Zone]
    ) -> None:
        """Call this at the END of each simulation turn."""
        self.turns.append({
            "turn":    turn,
            "output":  output_line.strip(),
            "positions": {d.id: d.current_zone for d in drones},
            # snapshot occupancy for coloring
            "occupancy": {
                name: len(z.current_drones)
                for name, z in zones.items()
            },
        })


# ─────────────────────────────────────────────
#  Visualizer
# ─────────────────────────────────────────────
class DroneVisualizer:
    """
    Animates the drone simulation on a matplotlib figure.

    Parameters
    ----------
    zones   : dict[str, Zone]   – the parsed zone objects
    history : SimHistory        – recorded turn data
    interval: int               – ms between frames (default 900)
    """

    def __init__(
        self,
        zones: dict,
        history: "SimHistory",
        interval: int = 900
    ) -> None:
        self.zones = zones
        self.history = history
        self.interval = interval
        self.nb_drones = max(
            max(s["positions"].keys()) + 1 for s in history.turns
        ) if history.turns else 0

        # ── get real screen dimensions ──────────────────────────────
        _root = tk.Tk()
        _root.withdraw()
        screen_w = _root.winfo_screenwidth()
        screen_h = _root.winfo_screenheight()
        dpi = _root.winfo_fpixels("1i")
        _root.destroy()

        figsize = (screen_w / dpi, screen_h / dpi)
        # ────────────────────────────────────────────────────────────

        self.fig, (self.ax_graph, self.ax_log) = plt.subplots(
            1, 2,
            figsize=figsize,
            gridspec_kw={"width_ratios": [3, 1]},
        )
        self.fig.patch.set_facecolor("#1A1A2E")
        for ax in (self.ax_graph, self.ax_log):
            ax.set_facecolor("#16213E")
            ax.tick_params(colors="white")
            for spine in ax.spines.values():
                spine.set_edgecolor("#0F3460")

        self._drone_scatters: list = []
        self._drone_labels:   list = []
        self._setup_static_graph()
        self._setup_drone_artists()
        self._setup_log_panel()

    # ── static graph (nodes + edges) ──────────────────────────────
    def _setup_static_graph(self) -> None:
        ax = self.ax_graph
        ax.set_title("Drone Routing Simulation", color="white",
                     fontsize=13, fontweight="bold", pad=12)

        drawn_edges: set[frozenset] = set()

        # edges
        for name, zone in self.zones.items():
            for edge in zone.edges:
                key = frozenset([name, edge["to"]])
                if key in drawn_edges:
                    continue
                drawn_edges.add(key)
                nb = self.zones[edge["to"]]
                ax.plot(
                    [zone.y, nb.y], [zone.x, nb.x],
                    color=EDGE_COLOR, linewidth=1.4,
                    alpha=0.6, zorder=1,
                )

        # nodes
        for name, zone in self.zones.items():
            color = _node_color(zone)
            ax.scatter(
                zone.y, zone.x,
                s=600, c=color, zorder=3,
                edgecolors="white", linewidths=1.5,
            )
            ax.text(
                zone.y, zone.x - 0.35, name,
                ha="center", va="top", fontsize=7,
                color="white", zorder=4,
            )

        # legend
        legend_items = [
            mpatches.Patch(color=START_COLOR,  label="Start"),
            mpatches.Patch(color=END_COLOR,    label="End"),
            mpatches.Patch(color=ZONE_COLORS["normal"],     label="Normal"),
            mpatches.Patch(
                color=ZONE_COLORS["restricted"], label="Restricted (x2)"),
            mpatches.Patch(color=ZONE_COLORS["blocked"],    label="Blocked"),
            mpatches.Patch(color=ZONE_COLORS["priority"],   label="Priority"),
        ]
        ax.legend(
            handles=legend_items, loc="upper right",
            facecolor="#0F3460", labelcolor="white",
            fontsize=7, framealpha=0.8,
        )

        # axis padding
        xs = [z.x for z in self.zones.values()]
        ys = [z.y for z in self.zones.values()]
        pad = 1.0
        ax.set_xlim(min(ys) - pad, max(ys) + pad)  # y is now horizontal
        ax.set_ylim(min(xs) - pad, max(xs) + pad)  # x is now vertical

    # ── animated drone artists ─────────────────────────────────────
    def _setup_drone_artists(self) -> None:
        ax = self.ax_graph
        for i in range(self.nb_drones):
            color = _drone_color(i)
            sc = ax.scatter([], [], s=220, c=color, zorder=5,
                            marker="^", edgecolors="white", linewidths=1)
            lb = ax.text(0, 0, f"D{i}", fontsize=7, color="white",
                         ha="center", va="bottom", zorder=6, visible=False)
            self._drone_scatters.append(sc)
            self._drone_labels.append(lb)

    # ── log panel ─────────────────────────────────────────────────
    def _setup_log_panel(self) -> None:
        ax = self.ax_log
        ax.set_title("Turn Log", color="white", fontsize=11,
                     fontweight="bold", pad=10)
        ax.axis("off")
        self._log_text = ax.text(
            0.05, 0.95, "", transform=ax.transAxes,
            va="top", ha="left", fontsize=8,
            color="#A8DADC", fontfamily="monospace",
        )
        self._turn_text = self.ax_graph.text(
            0.02, 0.98, "", transform=self.ax_graph.transAxes,
            va="top", color="white", fontsize=11, fontweight="bold",
        )

    # ── per-frame update ──────────────────────────────────────────
    def _update(self, frame: int) -> list:
        state = self.history.turns[frame]

        # turn counter
        self._turn_text.set_text(f"Turn {state['turn']}")

        # drone positions  (offset if multiple drones share a zone)
        zone_counts: dict[str, int] = {}
        for drone_id, zone_name in state["positions"].items():
            zone_counts[zone_name] = zone_counts.get(zone_name, 0) + 1

        zone_offset_idx: dict[str, int] = {}

        for drone_id, zone_name in state["positions"].items():

            # ── transit state: drone is on a connection, not in a zone ──
            if zone_name.startswith("transit:"):
                dest_name = zone_name[len("transit:"):]
                if dest_name not in self.zones:
                    continue
                dest = self.zones[dest_name]
                # draw the drone halfway toward its destination
                dx, dy = dest.y - 0.3, dest.x - 0.3
                self._drone_scatters[drone_id].set_offsets([[dx, dy]])
                self._drone_labels[drone_id].set_position((dx, dy + 0.18))
                self._drone_labels[drone_id].set_visible(True)
                continue

            # ── normal zone ──────────────────────────────────────────────
            zone = self.zones[zone_name]
            count = zone_counts[zone_name]
            idx = zone_offset_idx.get(zone_name, 0)
            zone_offset_idx[zone_name] = idx + 1

            if count > 1:
                angle = (2 * math.pi / count) * idx
                ox = 0.25 * math.cos(angle)
                oy = 0.25 * math.sin(angle)
            else:
                ox, oy = 0.0, 0.0

            dx, dy = zone.y + ox, zone.x + oy
            self._drone_scatters[drone_id].set_offsets([[dx, dy]])
            self._drone_labels[drone_id].set_position((dx, dy + 0.18))
            self._drone_labels[drone_id].set_visible(True)

        # log panel — show last 20 turns
        log_lines = [
            f"T{s['turn']:>2}: {s['output'] or '(wait)'}"
            for s in self.history.turns[max(0, frame - 18): frame + 1]
        ]
        self._log_text.set_text("\n".join(log_lines))

        artists: list = list(self._drone_scatters) + list(self._drone_labels)
        artists += [self._log_text, self._turn_text]
        return artists

    # ── public entry point ────────────────────────────────────────
    def run(self) -> None:
        """Start the animation window."""
        self._ani = animation.FuncAnimation(
            self.fig,
            self._update,
            frames=len(self.history.turns),
            interval=self.interval,
            blit=False,
            repeat=True,
        )
        plt.tight_layout()
        plt.show()
