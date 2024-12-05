import enum
from typing import Any, Dict, Optional

from board import Color, Event, MillGameBoard


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
    _valid_moves = {
        0: [1, 9],
        1: [0, 2, 4],
        2: [1, 14],
        3: [4, 10],
        4: [3, 5, 1, 7],
        5: [4, 13],
        6: [7, 11],
        7: [6, 8, 4],
        8: [7, 12],
        9: [0, 10, 21],
        10: [9, 11, 3, 18],
        11: [10, 6, 15],
        12: [8, 13, 17],
        13: [12, 14, 5, 20],
        14: [2, 13, 23],
        15: [11, 16],
        16: [15, 17, 19],
        17: [16, 12],
        18: [19, 10],
        19: [18, 20, 16, 22],
        20: [19, 13],
        21: [9, 22],
        22: [21, 23, 19],
        23: [22, 14],
    }
    _waiting_for_stone_removal_col: Optional[Color] = None

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
        if self._phase == Phase.SET and self._board.get_stone_col(position) == None and self.is_next_turn_col(color):
            return True
        else:
            return False

    def is_next_turn_col(self, color: Color) -> bool:
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
        selectedColor = self._board.get_stone_col(position)
        if selectedColor != None and (self.is_next_turn_col(selectedColor)):
            return True
        else:
            return False

    def get_next_action(self) -> NextAction:
        if self.get_phase() == Phase.SET:
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
        posCol = self._board.get_stone_col(position)
        if self.get_phase() == Phase.SET and posCol == None:
            return True
        else:
            return False

    def may_move(self, fromPos: int, toPos: int) -> bool:
        """
        Checks if the given move is valid.
        :param fromPos: the position to be moved from.
        :param fromTo: the position to be moved to.
        """
        fromPosCol = self._board.get_stone_col(fromPos)
        toPosCol = self._board.get_stone_col(toPos)

        if (self._waiting_for_stone_removal_col == None
            and fromPosCol != None
            and self.is_next_turn_col(fromPosCol)
            and toPosCol == None
            and self._move_valid(fromPos, toPos, fromPosCol)
        ):
            return True
        else:
            return False

    def may_remove(self, position: int) -> bool:
        """
        Checks if the stone on the given position may be removed.
        :param position: the position to remove a stone from.
        """
        if(self._waiting_for_stone_removal_col and self._waiting_for_stone_removal_col == self._board.get_stone_col(position)):
            return True
        return False

    def _board_event_handler(
        self, event: Event, eventData: Optional[Dict[str, Any]]
    ) -> None:
        """
        The event handler of the rules engine. Handles all board events.
        :param event: an event that was raised from the board.
        :param eventData: the data for the raised event.
        """
        black_stones = self._count_stones(Color.BLACK)
        white_stones = self._count_stones(Color.WHITE)
        if event == Event.STONE_SET:
            if black_stones == 9 and white_stones == 9:
                self._advance_phase()
            if eventData != None:
                self._last_move_col = eventData['color']
        elif event == Event.STONE_REMOVED:
            self._waiting_for_stone_removal_col = None
            if black_stones <= 0 or white_stones <= 0:
                self._advance_phase()                
        elif event == Event.STONE_MOVED:
            if black_stones <= 0 or white_stones <= 0:
                self._advance_phase()
            if eventData != None:
                self._last_move_col = eventData['color']
        elif event == Event.RESET:
            self._reset()

    def _move_valid(self, fromPos: int, toPos: int, color: Color) -> bool:
        """
        Checks if the move from fromPos to toPos is valid for the given color.
        :param fromPos: the position to move from.
        :param toPos: the position to move to.
        :param color: the color of the player.
        """
        possibleMoves = self._valid_moves.get(fromPos)
        if possibleMoves != None and (self._count_stones(color) <= 3 or toPos in possibleMoves):
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

# Test Usage
if __name__ == "__main__":
    board = MillGameBoard()
    rulesEngine = MillRules(board)

    print("White turn: " + str(rulesEngine.is_next_turn_col(Color.WHITE)))
    print("Black turn: " + str(rulesEngine.is_next_turn_col(Color.BLACK)))

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
