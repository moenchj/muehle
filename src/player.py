from typing import Optional

from board import Color, MillGameBoard
from rules import MillRules, NextAction


class Player:
    def __init__(self, board: MillGameBoard, rules_engine: MillRules, color: Color):
        self._board = board
        self._rules_engine = rules_engine
        self._color = color


class HumanPlayer(Player):
    def __init__(self, board: MillGameBoard, rules_engine: MillRules, color: Color):
        super().__init__(board, rules_engine, color)
        self._board.register_click_handler(self._board_click_handler)

    def _board_click_handler(self, position: Optional[int]) -> None:
        print("_board_click_handler player")
        if self._rules_engine.is_turn_col(self._color):
            if self._rules_engine.get_next_action() == NextAction.SET and position != None and self._rules_engine.can_place(position, self._color):
                self._board.place_stone(position, self._color)
            if self._rules_engine.get_next_action() == NextAction.MOVE:
                if position != None:
                    selected_pos = self._board.get_selection()
                    if self._rules_engine.may_select(position):
                        self._board.select_stone(position)
                    elif selected_pos != None and self._rules_engine.may_move(selected_pos, position):
                        self._board.move_stone(selected_pos, position)
                else:
                    self._board.select_stone(None)
                self._board.draw_board()
            if position != None and self._rules_engine.get_next_action() == NextAction.REMOVE and self._rules_engine.may_remove(position):
                self._board.remove_stone(position)
