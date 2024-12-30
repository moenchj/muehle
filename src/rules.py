import enum
from typing import Any, Dict, Optional
from xmlrpc.client import boolean

from board import Color, Event, MillGameBoard
from positions import Directions, positions


class Phase(enum.Enum):
    SET = "set"
    MOVE = "move"
    END = "end"


class NextAction(enum.Enum):
    SET = "set"
    MOVE = "move"
    REMOVE = "remove"
    RESET = "reset"


"""
Mill game rules engine.
"""


class MillRules:
    _waiting_for_stone_removal_col: Optional[Color] = None
    _white_stones_set = 0
    _black_stones_set = 0

    def __init__(self, board: MillGameBoard):
        self._phase: Phase = Phase.SET
        self._board = board
        self._board.register_event_handler(self._board_event_handler)
        self._last_move_col: Optional[Color] = None

    def get_phase(self) -> Phase:
        """
        Returns the current phase of the game.
        """
        return self._phase

    def can_place(self, position: int, color: Color) -> bool:
        """
        Checks if the given color can be placed on the given position.
        Placement is only possible in SET phase
        :param position: number of the position.
        :param color: the color of the stone to be placed.
        """
        if self._phase == Phase.SET and self._board.get_stone_col(position) == None and self.is_turn_col(color):
            return True
        else:
            return False

    def is_turn_col(self, color: Color) -> bool:
        """
        Checks if the given color is the next to act.
        :param color: the color of the player.
        """
        if self._waiting_for_stone_removal_col != None:
            return color != self._waiting_for_stone_removal_col
        elif self._last_move_col == None:
            return color == Color.WHITE
        else:
            return color != self._last_move_col

    def may_select(self, position: int) -> bool:
        """
        Checks if the given position may be selected.
        :param position: the position to be checked.
        """
        selected_color = self._board.get_stone_col(position)
        if selected_color != None and (self.is_turn_col(selected_color)):
            return True
        else:
            return False

    def get_next_action(self) -> NextAction:
        if self.get_phase() == Phase.SET:
            if self._waiting_for_stone_removal_col != None:
                return NextAction.REMOVE
            else:
                return NextAction.SET
        elif self.get_phase() == Phase.MOVE:
            if self._waiting_for_stone_removal_col != None:
                return NextAction.REMOVE
            else:
                return NextAction.MOVE
        else:
            return NextAction.RESET

    def may_place(self, position: int, color: Color) -> bool:
        """
        Checks if the given color may be placed at the given position.
        :param position: the position a stone shall be placed at.
        :param color: the color to be placed.
        """
        pos_col = self._board.get_stone_col(position)
        if self.get_phase() == Phase.SET and pos_col == None:
            return True
        else:
            return False

    def may_move(self, from_pos: int, to_pos: int) -> bool:
        """
        Checks if the given move is valid.
        :param fromPos: the position to be moved from.
        :param fromTo: the position to be moved to.
        """
        from_pos_col = self._board.get_stone_col(from_pos)
        to_pos_col = self._board.get_stone_col(to_pos)

        if (self._waiting_for_stone_removal_col == None
                    and from_pos_col != None
                    and self.is_turn_col(from_pos_col)
                    and to_pos_col == None
                    and self._move_valid(from_pos, to_pos, from_pos_col)
                ):
            return True
        else:
            return False

    def may_remove(self, position: int) -> bool:
        """
        Checks if the stone on the given position may be removed.
        :param position: the position to remove a stone from.
        """
        if (self._waiting_for_stone_removal_col and self._waiting_for_stone_removal_col == self._board.get_stone_col(position)):
            return True
        return False

    def _check_mill(self, color: Color, position: int) -> None:
        """
        Checks if the given color created a mill with the set stone.
        Checks for every positions left, right, up, down and with the position in center
        """
        # Check for a horizontal or vertical mill at the current position
        start_directions = positions.get(position)
        if start_directions != None and (self._check_horizontal_mill(color, start_directions) or self._check_vertical_mill(color, start_directions)):
            self._waiting_for_stone_removal_col = Color.BLACK if color == Color.WHITE else Color.WHITE

        # Check for a horizontal mill one field left
        if start_directions != None and start_directions.left != None and self._board.get_stone_col(start_directions.left) == color:
            moved_directions = positions.get(start_directions.left)
            if moved_directions != None and self._check_horizontal_mill(color, moved_directions):
                self._waiting_for_stone_removal_col = Color.BLACK if color == Color.WHITE else Color.WHITE

        # Check for a horizontal mill one field right
        if start_directions != None and start_directions.right != None and self._board.get_stone_col(start_directions.right) == color:
            moved_directions = positions.get(start_directions.right)
            if moved_directions != None and self._check_horizontal_mill(color, moved_directions):
                self._waiting_for_stone_removal_col = Color.BLACK if color == Color.WHITE else Color.WHITE

        # Check for a vertical mill one field up
        if start_directions != None and start_directions.up != None and self._board.get_stone_col(start_directions.up) == color:
            moved_directions = positions.get(start_directions.up)
            if moved_directions != None and self._check_vertical_mill(color, moved_directions):
                self._waiting_for_stone_removal_col = Color.BLACK if color == Color.WHITE else Color.WHITE

        # Check for a vertical mill one field down
        if start_directions != None and start_directions.down != None and self._board.get_stone_col(start_directions.down) == color:
            moved_directions = positions.get(start_directions.down)
            if moved_directions != None and self._check_vertical_mill(color, moved_directions):
                self._waiting_for_stone_removal_col = Color.BLACK if color == Color.WHITE else Color.WHITE

    def _check_horizontal_mill(self, color: Color, directions: Directions | None) -> boolean:
        return (directions != None and
                (directions.left != None and self._board.get_stone_col(directions.left) == color and directions.right != None and self._board.get_stone_col(directions.right) == color))

    def _check_vertical_mill(self, color: Color, directions: Directions | None) -> boolean:
        return (directions != None and
                (directions.up != None and self._board.get_stone_col(directions.up) == color and directions.down != None and self._board.get_stone_col(directions.down) == color))

    def _board_event_handler(
        self, event: Event, event_data: Optional[Dict[str, Any]]
    ) -> None:
        print("_board_event_handler rules")
        """
        The event handler of the rules engine. Handles all board events.
        :param event: an event that was raised from the board.
        :param eventData: the data for the raised event.
        """
        black_stones = self._count_stones(Color.BLACK)
        white_stones = self._count_stones(Color.WHITE)
        if event == Event.STONE_SET:
            if event_data != None:
                self._last_move_col = event_data["color"]
                if self._last_move_col == Color.WHITE:
                    self._white_stones_set += 1
                else:
                    self._black_stones_set += 1
                self._check_mill(event_data["color"], event_data["position"])
            if self._white_stones_set >= 9 and self._black_stones_set >= 9:
                self._advance_phase()
        elif event == Event.STONE_REMOVED:
            self._waiting_for_stone_removal_col = None
            if self.get_phase() == Phase.MOVE and black_stones <= 2 or white_stones <= 2:
                self._advance_phase()
        elif event == Event.STONE_MOVED:
            if event_data != None:
                self._last_move_col = event_data["color"]
                self._check_mill(event_data["color"], event_data["to"])
        elif event == Event.RESET:
            self._reset()

    def _move_valid(self, from_pos: int, to_pos: int, color: Color) -> bool:
        """
        Checks if the move from from_pos to to_pos is valid for the given color.
        Does only check move validity not constraints.
        :param from_pos: the position to move from.
        :param to_pos: the position to move to.
        :param color: the color of the player.
        """
        position = positions.get(from_pos)
        if position != None and (self._count_stones(color) <= 3 or position.has_neighbor(to_pos)):
            return True
        return False

    def _count_stones(self, color: Color) -> int:
        """
        Counts the stones of the given color on the board.
        :param color: the color of the player.
        """
        num_stones = sum(x == color for x in self._board.get_stones().values())
        return num_stones

    def _advance_phase(self) -> None:
        """
        Advances the phase to the next one.
        """
        if self._phase == Phase.SET:
            self._phase = Phase.MOVE
        elif self._phase == Phase.MOVE:
            self._phase = Phase.END

    def _reset(self) -> None:
        """
        Resets the rule engine.
        """
        self._phase = Phase.SET
        self._waiting_for_stone_removal_col = None
        self._last_move_col = None
        self._white_stones_set = 0
        self._black_stones_set = 0


# Test Usage
if __name__ == "__main__":
    board = MillGameBoard()
    rulesEngine = MillRules(board)

    print("White turn: " + str(rulesEngine.is_turn_col(Color.WHITE)))
    print("Black turn: " + str(rulesEngine.is_turn_col(Color.BLACK)))

    print("Next action: " + str(rulesEngine.get_next_action()))
    print("May place White: " + str(rulesEngine.may_place(0, Color.WHITE)))
    print("May place Black: " + str(rulesEngine.may_place(0, Color.BLACK)))
    board.place_stone(0, Color.WHITE)

    print("Next action: " + str(rulesEngine.get_next_action()))
    print("May place White: " + str(rulesEngine.may_place(1, Color.WHITE)))
    print("May place Black: " + str(rulesEngine.may_place(1, Color.BLACK)))
    board.place_stone(1, Color.BLACK)

    print("Next action: " + str(rulesEngine.get_next_action()))
    print("May place White: " + str(rulesEngine.may_place(2, Color.WHITE)))
    print("May place Black: " + str(rulesEngine.may_place(2, Color.BLACK)))
    board.place_stone(2, Color.WHITE)

    print("Next action: " + str(rulesEngine.get_next_action()))
    board.place_stone(3, Color.BLACK)
    print("Next action: " + str(rulesEngine.get_next_action()))
    board.place_stone(4, Color.WHITE)
    print("Next action: " + str(rulesEngine.get_next_action()))
    board.place_stone(5, Color.BLACK)
    print("Next action: " + str(rulesEngine.get_next_action()))
    board.place_stone(6, Color.WHITE)
    print("Next action: " + str(rulesEngine.get_next_action()))
    board.place_stone(7, Color.BLACK)
    print("Next action: " + str(rulesEngine.get_next_action()))
    board.place_stone(8, Color.WHITE)
    print("Next action: " + str(rulesEngine.get_next_action()))
    board.place_stone(9, Color.BLACK)
    print("Next action: " + str(rulesEngine.get_next_action()))
    print("Next action: " + str(rulesEngine.get_next_action()))
    board.place_stone(10, Color.WHITE)
    print("Next action: " + str(rulesEngine.get_next_action()))
    board.place_stone(11, Color.BLACK)
    print("Next action: " + str(rulesEngine.get_next_action()))
    print("Next action: " + str(rulesEngine.get_next_action()))
    board.place_stone(12, Color.WHITE)
    print("Next action: " + str(rulesEngine.get_next_action()))
    board.place_stone(13, Color.BLACK)
    print("Next action: " + str(rulesEngine.get_next_action()))
    print("Next action: " + str(rulesEngine.get_next_action()))
    board.place_stone(14, Color.WHITE)
    print("Next action: " + str(rulesEngine.get_next_action()))
    board.place_stone(15, Color.BLACK)
    print("Next action: " + str(rulesEngine.get_next_action()))
    board.place_stone(16, Color.WHITE)
    print("Next action: " + str(rulesEngine.get_next_action()))
    board.place_stone(17, Color.BLACK)

    print("Next action: " + str(rulesEngine.get_next_action()))
    print("May place White: " + str(rulesEngine.may_place(0, Color.WHITE)))
    print("May place Black: " + str(rulesEngine.may_place(0, Color.BLACK)))

    print("May move Black: " + str(rulesEngine.may_move(9, 21)))
    print("May move White: " + str(rulesEngine.may_move(14, 23)))
    board.move_stone(14, 23)
    print("May move Black: " + str(rulesEngine.may_move(9, 21)))
    print("May move White: " + str(rulesEngine.may_move(14, 23)))

    board.draw_board()
