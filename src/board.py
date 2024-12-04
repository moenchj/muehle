import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton
import matplotlib.font_manager as font_manager
import matplotlib
import math

matplotlib.use("TkAgg")


class MillGameBoard:
    _click_handlers = []
    _information_text = ""
    _max_click_dist = 0.18
    _valid_positions = {
        0: (0, 0),
        1: (3, 0),
        2: (6, 0),
        3: (1, 1),
        4: (3, 1),
        5: (5, 1),
        6: (2, 2),
        7: (3, 2),
        8: (4, 2),
        9: (0, 3),
        10: (1, 3),
        11: (2, 3),
        12: (4, 3),
        13: (5, 3),
        14: (6, 3),
        15: (2, 4),
        16: (3, 4),
        17: (4, 4),
        18: (1, 5),
        19: (3, 5),
        20: (5, 5),
        21: (0, 6),
        22: (3, 6),
        23: (6, 6),
    }

    _colors = {"white": "white", "black": "black"}

    def __init__(self):
        self.stones = {}
        self.highlighted_pos = None
        # plt.connect("button_press_event", self._on_click)

    def draw_board(self):
        """
        Draws the Mill game board with three rectangles and connecting lines.
        """
        plt.close("all")
        fig, ax = plt.subplots(figsize=(7, 7))
        cid = fig.canvas.mpl_connect("button_press_event", self._on_click)

        # Draw the three rectangles (concentric squares)
        rect = plt.Rectangle((0, 0), 6, 6, fill=False, color="black", linewidth=2)
        ax.add_patch(rect)
        rect = plt.Rectangle((1, 1), 4, 4, fill=False, color="black", linewidth=2)
        ax.add_patch(rect)
        rect = plt.Rectangle((2, 2), 2, 2, fill=False, color="black", linewidth=2)
        ax.add_patch(rect)

        # Draw the connecting lines between rectangles
        ax.plot([3, 3], [0, 2], color="black", linewidth=2)
        ax.plot([3, 3], [4, 6], color="black", linewidth=2)
        ax.plot([0, 2], [3, 3], color="black", linewidth=2)
        ax.plot([4, 6], [3, 3], color="black", linewidth=2)

        # Draw the points at intersections
        for pos, coord in self._valid_positions.items():
            ax.plot(coord[0], coord[1], "o", color="black", markersize=5)

        # Add the stones
        for position, color in self.stones.items():
            self._draw_stone(ax, position, color)

        # Add informational text
        self._draw_information_text()

        # Remove axes
        ax.axis("off")
        plt.show()

    def set_information_text(self, text):
        self._information_text = text

    def place_stone(self, position, color):
        """
        Places a stone on the board.
        :param position: number for the stone position.
        :param color: "black" or "white".
        """
        if color not in ["black", "white"]:
            raise ValueError("Stone color must be 'black' or 'white'.")

        # Check if the position is a valid crossing
        if position in self._valid_positions:
            self.stones[position] = color
        else:
            raise ValueError(
                "Invalid position. Stones can only be placed on crossings."
            )

    def remove_stone(self, position):
        """
        Removes a stone from the board.
        :param position: number for the stone position.
        """
        # Check if the position is a valid crossing
        if position in self._valid_positions:
            del self.stones[position]
        else:
            raise ValueError(
                "Invalid position. Stones can only be placed on crossings."
            )

    def get_stone_col(self, position):
        """
        Gets the color of a stone on a position on the board.
        :param position: number of the position.
        """
        # Check if the position is a valid crossing
        if position in self._valid_positions:
            if position in self.stones:
                return self.stones[position]
            else:
                return None
        else:
            raise ValueError(
                "Invalid position. Stones can only be placed on crossings."
            )

    def highlight_stone(self, position):
        """
        Highlights a stone on a position on the board.
        :param position: number of the position.
        """
        # Check if the position is a valid crossing
        if position in self._valid_positions and position in self.stones:
            self.highlighted_pos = position
        else:
            self.highlighted_pos = None

    def clear_board(self):
        """
        Clears all stones from the board.
        """
        self.stones = {}

    def register_click_handler(self, handler):
        self._click_handlers.append(handler)

    def unregister_click_handler(self, handler):
        self._click_handlers.remove(handler)

    def _draw_information_text(self):
        font_prop = font_manager.FontProperties(size=14)
        matplotlib.pyplot.text(
            3,
            6.7,
            self._information_text,
            horizontalalignment="center",
            fontproperties=font_prop,
        )

    def _draw_stone(self, ax, position, color):
        """
        Draws a game stone at the specified position.
        :param ax: Matplotlib axis.
        :param position: number for the stone position.
        :param color: "black" or "white" for the stone color.
        """
        (x, y) = self._valid_positions[position]
        if position == self.highlighted_pos:
            ax.plot(x, y, "o", color="red", markersize=20)
            ax.plot(x, y, "o", color=self._colors[color], markersize=14)
        else:
            ax.plot(x, y, "o", color="black", markersize=17)
            ax.plot(x, y, "o", color=self._colors[color], markersize=15)

    def _on_click(self, event):
        if (
            event.button is MouseButton.LEFT
            and math.dist([round(event.xdata)], [event.xdata]) < self._max_click_dist
            and math.dist([round(event.ydata)], [event.ydata]) < self._max_click_dist
        ):
            x = round(event.xdata)
            y = round(event.ydata)
            for handler in self._click_handlers:
                handler(x, y)


def click_handler(x, y):
    print("Click x: " + str(x) + ", y: " + str(y))


# Example Usage
if __name__ == "__main__":
    board = MillGameBoard()
    board.set_information_text("White draws")
    board.register_click_handler(click_handler)
    board.place_stone(0, "black")
    board.place_stone(1, "white")
    board.place_stone(2, "black")
    board.place_stone(3, "black")
    board.place_stone(4, "white")
    board.place_stone(5, "black")
    board.place_stone(6, "black")
    board.place_stone(7, "white")
    board.place_stone(8, "black")
    board.place_stone(9, "black")
    board.place_stone(10, "white")
    board.place_stone(11, "black")
    # board.highlight_stone(11)
    #    board.place_stone(12, "black")
    #    board.place_stone(13, "white")
    #    board.place_stone(14, "black")
    #    board.place_stone(15, "black")
    #    board.place_stone(16, "white")
    #    board.place_stone(17, "black")
    #    board.place_stone(18, "black")
    #    board.place_stone(19, "white")
    #    board.place_stone(20, "black")
    #    board.place_stone(21, "black")
    board.place_stone(22, "white")
    #    board.place_stone(23, "black")
    board.draw_board()
