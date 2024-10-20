import json
import socket
import threading
import time

import pygame


class SnakeClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 6969):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_socket.connect((host, port))
        except socket.error as e:
            print("Connection error:", e)
            exit(1)

        self.running = True
        self.username = input("Enter your username: ")
        self.game_state = {}
        self.cell_size = 20
        self.grid_size = 20

        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.grid_size * self.cell_size, self.grid_size * self.cell_size)
        )
        pygame.display.set_caption("Snake Game")
        self.font = pygame.font.Font(None, 36)

        self.server_socket.sendall(self.username.encode())
        threading.Thread(target=self.receive_data, daemon=True).start()

    def receive_data(self):
        while self.running:
            try:
                data = self.server_socket.recv(1024).decode()
                if not data:
                    break
                self.game_state = json.loads(data)
            except Exception as e:
                print("Error receiving data:", e)
                self.running = False

    def send_direction(self, direction: str):
        try:
            self.server_socket.sendall(direction.encode())
        except Exception as e:
            print("Error sending data:", e)

    def draw(self):
        self.screen.fill((0, 0, 0))

        for segment in self.game_state.get("snake", []):
            pygame.draw.rect(
                self.screen,
                (0, 255, 0),
                (
                    segment[0] * self.cell_size,
                    segment[1] * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                ),
            )

        food_position = self.game_state.get("food_position", (0, 0))
        pygame.draw.rect(
            self.screen,
            (255, 0, 0),
            (
                food_position[0] * self.cell_size,
                food_position[1] * self.cell_size,
                self.cell_size,
                self.cell_size,
            ),
        )

        score_text = self.font.render(
            f"Score: {self.game_state.get('score', 0)}", True, (255, 255, 255)
        )
        self.screen.blit(score_text, (10, 10))

        pygame.display.flip()

    def start(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.send_direction("U")
                    elif event.key == pygame.K_DOWN:
                        self.send_direction("D")
                    elif event.key == pygame.K_LEFT:
                        self.send_direction("L")
                    elif event.key == pygame.K_RIGHT:
                        self.send_direction("R")

            self.draw()
            time.sleep(0.1)

        pygame.quit()
        self.server_socket.close()


def main():
    client = SnakeClient()
    client.start()


if __name__ == "__main__":
    main()
