import enum
import math
from typing import Any, Callable, Dict, List, Optional, Tuple

import matplotlib
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton

matplotlib.use("TkAgg")


class Event(enum.Enum):
    STONE_SET = "stone_set"
    STONE_REMOVED = "stone_removed"
    STONE_MOVED = "stone_moved"
    RESET = "reset"


class Color(enum.Enum):
    WHITE = "white"
    BLACK = "black"


"""
Visualization of a mill game board.
"""


class MillGameBoard:
    _click_handlers: List[Callable[[Optional[int]], None]] = []
    _event_handlers: List[Callable[[Event, Optional[Dict[str, Any]]], None]] = []
    _information_text: str = ""
    _max_click_dist: float = 0.18
    _valid_positions: Dict[int, Tuple[int, int]] = {
        0: (0, 6),
        1: (3, 6),
        2: (6, 6),
        3: (1, 5),
        4: (3, 5),
        5: (5, 5),
        6: (2, 4),
        7: (3, 4),
        8: (4, 4),
        9: (0, 3),
        10: (1, 3),
        11: (2, 3),
        12: (4, 3),
        13: (5, 3),
        14: (6, 3),
        15: (2, 2),
        16: (3, 2),
        17: (4, 2),
        18: (1, 1),
        19: (3, 1),
        20: (5, 1),
        21: (0, 0),
        22: (3, 0),
        23: (6, 0),
    }
    _valid_positions_reverse: Dict[Tuple[int, int], int] = dict(
        zip(_valid_positions.values(), _valid_positions.keys())
    )
    _color_config: Dict[Color, str] = {Color.WHITE: "white", Color.BLACK: "black"}

    def __init__(self):
        self._stones: Dict[int, Color] = {}
        self._selected_pos: Optional[int] = None
        self._fig: Any
        self._ax: Any
        self._fig, self._ax = plt.subplots(figsize=(7, 7))  # type: ignore
        self._fig.canvas.mpl_connect("button_press_event", self._on_click)

    def draw_board(self):
        """
        Draws the Mill game board and all stones.
        """
        self._ax.cla()
        self._ax.axis("off")
        # Draw the three rectangles (concentric squares)
        rect: Patch = plt.Rectangle((0, 0), 6, 6, fill=False, color="black", linewidth=2)  # type: ignore
        self._ax.add_patch(rect)
        rect = plt.Rectangle((1, 1), 4, 4, fill=False, color="black", linewidth=2)  # type: ignore
        self._ax.add_patch(rect)
        rect = plt.Rectangle((2, 2), 2, 2, fill=False, color="black", linewidth=2)  # type: ignore
        self._ax.add_patch(rect)

        # Draw the connecting lines between rectangles
        self._ax.plot([3, 3], [0, 2], color="black", linewidth=2)
        self._ax.plot([3, 3], [4, 6], color="black", linewidth=2)
        self._ax.plot([0, 2], [3, 3], color="black", linewidth=2)
        self._ax.plot([4, 6], [3, 3], color="black", linewidth=2)

        # Draw the points at intersections
        for _pos, coord in self._valid_positions.items():
            self._ax.plot(coord[0], coord[1], "o", color="black", markersize=5)

        # Add the stones
        for position, color in self._stones.items():
            self._draw_stone(self._ax, position, color)

        # Add informational text
        self._draw_information_text()
        plt.show()  # type: ignore

    def set_information_text(self, text: str) -> None:
        """
        Sets a text to display above the board.
        :text position: The text to display.
        """
        self._information_text = text

    def place_stone(self, position: int, color: Color) -> None:
        """
        Places a stone on the board.
        :param position: number for the stone position.
        :param color: "black" or "white".
        """
        if color not in Color:
            raise ValueError("Stone color must be 'black' or 'white'.")

        # Check if the position is a valid crossing
        if position in self._valid_positions:
            self._stones[position] = color
            self.select_stone(None)
            self._on_event(Event.STONE_SET, {"color": color, "position": position})
        else:
            raise ValueError(
                "Invalid position. Stones can only be placed on crossings."
            )

    def remove_stone(self, position: int) -> None:
        """
        Removes a stone from the board.
        :param position: number for the stone position.
        """
        # Check if the position is a valid crossing
        if position in self._valid_positions:
            color = self._stones.get(position)
            if color != None:
                self.select_stone(None)
                del self._stones[position]
                self._on_event(Event.STONE_REMOVED, {"color": color, "position": position})
        else:
            raise ValueError(
                "Invalid position. Stones can only be placed on crossings."
            )

    def move_stone(self, fromPos: int, toPos: int):
        """
        Moves a stone on the board.
        :param fromPos: position of the stone to move.
        :param toPos: position to move the stone to.
        """
        # Check if the position is a valid crossing
        if fromPos in self._valid_positions and toPos in self._valid_positions:
            stoneCol = self._stones.get(fromPos)
            if stoneCol != None:
                del self._stones[fromPos]
                self._stones[toPos] = stoneCol
                self.select_stone(None)
                self._on_event(Event.STONE_MOVED, {"color": stoneCol, "from": fromPos, "to": toPos})

        else:
            raise ValueError(
                "Invalid position. Stones can only be placed on crossings."
            )

    def get_stone_col(self, position: int) -> Optional[Color]:
        """
        Gets the color of a stone on a position on the board.
        :param position: number of the position.
        """
        # Check if the position is a valid crossing
        if position in self._valid_positions:
            if position in self._stones:
                return self._stones.get(position)
            else:
                return None
        else:
            raise ValueError(
                "Invalid position. Stones can only be placed on crossings."
            )

    def get_stones(self) -> Dict[int, Color]:
        """
        Gets all stones on the board.
        """
        return self._stones

    def select_stone(self, position: Optional[int]) -> None:
        """
        Selects and highlights a stone on a position on the board.
        :param position: number of the position.
        """
        # Check if the position is a valid crossing
        if position != None and position in self._valid_positions and position in self._stones:
            self._selected_pos = position
        else:
            self._selected_pos = None

    def get_selection(self) -> Optional[int]:
        """
        Get the currently selected stone position.
        """
        return self._selected_pos

    def clear_board(self) -> None:
        """
        Clears all stones from the board.
        """
        self._stones = {}
        self.select_stone(None)
        self._on_event(Event.RESET, None)

    def register_click_handler(self, handler: Callable[[Optional[int]], None]) -> None:
        """
        Registers a handler function that is called on left button click with the click position.
        :handler: Click handler function that takes a position as argument (def handler(position): ...)
        """
        self._click_handlers.append(handler)

    def unregister_click_handler(self, handler: Callable[[Optional[int]], None]) -> None:
        """
        Unregisters a click handler function.
        :handler: A handler function formerly registered as click handler
        """
        self._click_handlers.remove(handler)

    def register_event_handler(
        self, handler: Callable[[Event, Optional[Dict[str, Any]]], None]
    ) -> None:
        """
        Registers a handler function that is called on events on the board.
        :handler: handler function that takes an event as argument (def handler(event, eventData): ...)
        """
        self._event_handlers.append(handler)

    def unregister_event_handler(
        self, handler: Callable[[Event, Optional[Dict[str, Any]]], None]
    ) -> None:
        """
        Unregisters an event handler function.
        :handler: A handler function formerly registered as event handler
        """
        self._event_handlers.remove(handler)

    def _draw_information_text(self) -> None:
        """
        Draws text above the board.
        """
        font_prop = font_manager.FontProperties(size=14)
        matplotlib.pyplot.text(  # type: ignore
            3,
            6.7,
            self._information_text,
            horizontalalignment="center",
            fontproperties=font_prop,
        )

    def _draw_stone(self, ax: Any, position: int, color: Color) -> None:
        """
        Draws a game stone at the specified position.
        :param ax: Matplotlib axis.
        :param position: number for the stone position.
        :param color: "black" or "white" for the stone color.
        """
        (x, y) = self._valid_positions[position]
        if position == self._selected_pos:
            ax.plot(x, y, "o", color="red", markersize=20)
            ax.plot(x, y, "o", color=self._color_config[color], markersize=14)
        else:
            ax.plot(x, y, "o", color="black", markersize=17)
            ax.plot(x, y, "o", color=self._color_config[color], markersize=15)

    def _on_click(self, event: Any) -> None:
        """
        Is called on every click and distributed the click event to the registered handlers if it was near a stone.
        :param event: Matplotlib click event.
        """
        position = None
        if (
            event.button is MouseButton.LEFT
            and event.xdata != None
            and event.ydata != None
            and math.dist([round(event.xdata)], [event.xdata]) < self._max_click_dist
            and math.dist([round(event.ydata)], [event.ydata]) < self._max_click_dist
        ):
            x = round(event.xdata)
            y = round(event.ydata)
            position = self._valid_positions_reverse.get((x, y))
        for handler in self._click_handlers:
            handler(position)
    
    def _on_event(self, event: Event, eventData: Optional[Dict[str, Any]]) -> None:
        """
        Is called on every event that happens on the board and calls all registered event handlers.
        :param event: Mill board event.
        """
        for handler in self._event_handlers:
            handler(event, eventData)


def click_handler(position: Optional[int]) -> None:
    print("Click position: " + str(position))


# Test Usage
if __name__ == "__main__":
    board = MillGameBoard()
    board.set_information_text("White draws")
    board.register_click_handler(click_handler)
    board.place_stone(0, Color.BLACK)
    board.place_stone(1, Color.WHITE)
    board.place_stone(2, Color.BLACK)
    board.place_stone(3, Color.BLACK)
    board.place_stone(4, Color.WHITE)
    board.place_stone(5, Color.BLACK)
    board.place_stone(6, Color.BLACK)
    board.place_stone(7, Color.WHITE)
    board.place_stone(8, Color.BLACK)
    board.place_stone(9, Color.BLACK)
    board.place_stone(10, Color.WHITE)
    board.place_stone(11, Color.BLACK)
    #    board.place_stone(12, Color.BLACK)
    #    board.place_stone(13, Color.WHITE)
    #    board.place_stone(14, Color.BLACK)
    #    board.place_stone(15, Color.BLACK)
    #    board.place_stone(16, Color.WHITE)
    #    board.place_stone(17, Color.BLACK)
    #    board.place_stone(18, Color.BLACK)
    #    board.place_stone(19, Color.WHITE)
    #    board.place_stone(20, Color.BLACK)
    #    board.place_stone(21, Color.BLACK)
    # board.place_stone(22, Color.WHITE)
    #    board.place_stone(23, Color.BLACK)
    board.select_stone(11)
    board.draw_board()
