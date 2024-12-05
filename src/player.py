from typing import Optional

from board import Color, MillGameBoard
from rules import MillRules, NextAction


class Player:
    def __init__(self, board: MillGameBoard, rulesEngine: MillRules, color: Color):
        self._board = board
        self._rulesEngine = rulesEngine
        self._color = color

class HumanPlayer(Player):
    def __init__(self, board: MillGameBoard, rulesEngine: MillRules, color: Color):
        super().__init__(board, rulesEngine, color)
        self._board.register_click_handler(self._board_click_handler)

    def _board_click_handler(self, position: Optional[int]) -> None:
        if self._rulesEngine.is_next_turn_col(self._color):
            if self._rulesEngine.get_next_action() == NextAction.SET and position != None and self._rulesEngine.can_place(position, self._color):
                self._board.place_stone(position, self._color)
            if self._rulesEngine.get_next_action() == NextAction.MOVE:
                if position != None:
                    selected_pos = self._board.get_selection()
                    if self._rulesEngine.may_select(position):
                        self._board.select_stone(position)
                    elif selected_pos != None and self._rulesEngine.may_move(selected_pos, position):
                        self._board.move_stone(selected_pos, position)
                else:
                    self._board.select_stone(None)
                self._board.draw_board()
            if position != None and self._rulesEngine.get_next_action() == NextAction.REMOVE and self._rulesEngine.may_remove(position):
                self._board.remove_stone(position)
