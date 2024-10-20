import json
import random
import socket
import threading
import time
from typing import Tuple, Dict, List


class SnakeServer:
    def __init__(
        self, host: str = "127.0.0.1", port: int = 6969, grid_size: int = 20
    ) -> None:
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen()
        self.lock = threading.Lock()
        self.grid_size = grid_size
        self.running = True

    def handle_client(
        self, client_socket: socket.socket, client_address: Tuple[str, int]
    ) -> None:
        print(f"Client connecting: {client_address}.")
        username = client_socket.recv(1024).decode()
        print(f"Client connected: {username}.")
        game_state = self.new_game_state(username)

        try:
            while self.running:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                if data in ("U", "D", "L", "R"):
                    game_state["direction"] = data

                self.update_snake(game_state)

                client_socket.sendall(json.dumps(game_state).encode())
                time.sleep(0.1)

        except ConnectionResetError:
            print(f"Client disconnected: {client_address}.")

        finally:
            client_socket.close()

    def new_game_state(self, username: str) -> Dict[str, any]:
        return {
            "username": username,
            "snake": [(5, 5)],
            "score": 0,
            "direction": "R",
            "food_position": self.generate_food_position([(5, 5)]),
        }

    def generate_food_position(self, snake: List[Tuple[int, int]]) -> Tuple[int, int]:
        while True:
            position = (
                random.randint(0, self.grid_size - 1),
                random.randint(0, self.grid_size - 1),
            )
            if position not in snake:
                return position

    def update_snake(self, game_state: Dict[str, any]) -> None:
        snake = game_state["snake"]
        head = snake[0]
        direction = game_state["direction"]
        new_head = self.calculate_new_head(head, direction)

        if self.is_game_over(new_head, snake):
            print(
                f"Game over for {game_state['username']} with a score of {game_state['score']}"
            )
            game_state["snake"] = [(5, 5)]
            game_state["score"] = 0
            game_state["food_position"] = self.generate_food_position(snake)
            return

        snake.insert(0, new_head)

        if new_head == game_state["food_position"]:
            game_state["score"] += 1
            game_state["food_position"] = self.generate_food_position(snake)
        else:
            snake.pop()

    @staticmethod
    def calculate_new_head(head: Tuple[int, int], direction: str) -> Tuple[int, int]:
        if direction == "U":
            return head[0], head[1] - 1
        elif direction == "D":
            return head[0], head[1] + 1
        elif direction == "L":
            return head[0] - 1, head[1]
        elif direction == "R":
            return head[0] + 1, head[1]
        return head

    def is_game_over(
        self, new_head: Tuple[int, int], snake: List[Tuple[int, int]]
    ) -> bool:
        return new_head in snake or not (
            0 <= new_head[0] < self.grid_size and 0 <= new_head[1] < self.grid_size
        )

    def start(self) -> None:
        print("Server started. Waiting for connections...")
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address),
                    daemon=True,
                ).start()
            except Exception as e:
                if not self.running:
                    break
                print(f"Error accepting connection: {e}")

    def stop(self) -> None:
        self.running = False
        self.server_socket.close()
        print("Server stopped.")


def main():
    server = SnakeServer()
    try:
        server.start()
    except Exception as e:
        print(f"Error running server: {e}")
        server.stop()


if __name__ == "__main__":
    main()
