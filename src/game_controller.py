from typing import Any, Dict, Optional

from board import Color, Event, MillGameBoard
from player import HumanPlayer, Player
from rules import MillRules, NextAction, Phase


class GameController:
    _selected_pos: Optional[int] = None
    def __init__(self):
        self._board = MillGameBoard()
        self._rules_engine = MillRules(self._board)
        self._player1: Player = HumanPlayer(self._board, self._rules_engine, Color.WHITE)
        self._player2: Player = HumanPlayer(self._board, self._rules_engine, Color.BLACK)
        self._board.register_event_handler(self._board_event_handler)
        self._board.register_click_handler(self._board_click_handler)

    def _board_click_handler(self, position: Optional[int]) -> None:
        if self._rules_engine.get_phase() == Phase.END:
            self._board.clear_board()
            self._setup_board()

    def _board_event_handler(self, event: Event, eventData: Optional[Dict[str, Any]]) -> None:
        if event != Event.RESET:
            self._setup_board()

    def _setup_board(self) -> None:
        text = self._get_board_text()
        self._board.set_information_text(text)
        self._board.draw_board()

    def _get_board_text(self) -> str:
        if self._rules_engine.get_next_action() == NextAction.SET:
            if self._rules_engine.is_next_turn_col(Color.WHITE):
                return "White: Please set stone"
            else:
                return "Black: Please set stone"
        if self._rules_engine.get_next_action() == NextAction.MOVE:
            if self._rules_engine.is_next_turn_col(Color.WHITE):
                return "White: Please move stone"
            else:
                return "Black: Please move stone"
        if self._rules_engine.get_next_action() == NextAction.REMOVE:
            if self._rules_engine.is_next_turn_col(Color.WHITE):
                return "White: Please select black stone to remove"
            else:
                return "Black: Please select white stone to remove"
        if self._rules_engine.get_next_action() == NextAction.RESET:
            num_black_stones = sum(x == Color.BLACK for x in self._board.get_stones().values())
            num_white_stones = sum(x == Color.WHITE for x in self._board.get_stones().values())
            if num_black_stones < num_white_stones:
                return "White won!! Please click to start new game."
            else:
                return "Black won!! Please click to start new game."
        return ""
    
    def start(self):
        self._setup_board()


if __name__ == "__main__":
    game = GameController()
    game.start()