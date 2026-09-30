import random
import pygame
from game.text_box import TextBox

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.secret_number = random.randint(1, 100)
        self.attempts = 0
        self.max_attempts = 7
        self.game_over = False
        self.low_bound = 1
        self.high_bound = 100
        self.history = []  # last 5 guesses as (guess, result) tuples
        self.feedback_msg = "Enter a number between 1 and 100"
        self.feedback_color = (220, 220, 220)
        self.game_won = False

        self.input_box = TextBox(width // 2 - 110, 150, 120, 48)
        self.submit_btn = pygame.Rect(width // 2 + 25, 150, 100, 48)

        self.font_title = pygame.font.SysFont(None, 42)
        self.font_medium = pygame.font.SysFont(None, 28)
        self.font_btn = pygame.font.SysFont(None, 26)
        self.font_small = pygame.font.SysFont(None, 20)

    def submit_guess(self):
        if self.game_won or self.game_over:
            return

        # Fix: empty input no longer crashes; attempts are preserved.
        if not self.input_box.text.strip():
            self.feedback_msg = "Please enter a number first!"
            self.feedback_color = (240, 200, 80)
            return

        guess = int(self.input_box.text)

        self.attempts += 1
        self.input_box.clear()

        if guess < self.secret_number:
            self.low_bound = max(self.low_bound, guess + 1)
            self.record_guess(guess, "LOW")
            self.feedback_msg = f"TOO LOW! (Guess was {guess})"
            self.feedback_color = (80, 160, 240)
        elif guess > self.secret_number:
            self.high_bound = min(self.high_bound, guess - 1)
            self.record_guess(guess, "HIGH")
            self.feedback_msg = f"TOO HIGH! (Guess was {guess})"
            self.feedback_color = (240, 100, 80)
        else:
            self.feedback_msg = f"CORRECT! Found in {self.attempts} attempts."
            self.feedback_color = (80, 220, 90)
            self.low_bound = self.high_bound = guess
            self.record_guess(guess, "HIT")
            self.game_won = True

        if not self.game_won and self.attempts >= self.max_attempts:
            self.game_over = True
            self.feedback_msg = f"GAME OVER! The number was {self.secret_number}"
            self.feedback_color = (240, 70, 70)

    def record_guess(self, guess, result):
        self.history.append((guess, result))
        self.history = self.history[-5:]

    def reset(self):
        self.secret_number = random.randint(1, 100)
        self.attempts = 0
        self.low_bound = 1
        self.high_bound = 100
        self.history = []
        self.game_over = False
        self.feedback_msg = "Enter a number between 1 and 100"
        self.feedback_color = (220, 220, 220)
        self.game_won = False
        self.input_box.clear()
        self.input_box.active = True

    def handle_event(self, event):
        self.input_box.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.submit_guess()
            elif event.key == pygame.K_r and (self.game_won or self.game_over):
                self.reset()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.submit_btn.collidepoint(event.pos):
                # Clicking SUBMIT deactivates the TextBox; re-focus it so typing keeps working.
                self.input_box.active = True
                self.submit_guess()

    def update(self):
        pass

    def render(self, screen):
        screen.fill((30, 34, 42))

        title_surf = self.font_title.render("Number Guessing Arena", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 35))

        attempts_surf = self.font_medium.render(f"Attempts: {self.attempts} / {self.max_attempts}", True, (180, 185, 195))
        screen.blit(attempts_surf, (self.width // 2 - attempts_surf.get_width() // 2, 95))
        self.input_box.render(screen)

        pygame.draw.rect(screen, (50, 150, 80), self.submit_btn, border_radius=6)
        pygame.draw.rect(screen, (220, 220, 220), self.submit_btn, width=2, border_radius=6)
        btn_text = self.font_btn.render("SUBMIT", True, (255, 255, 255))
        screen.blit(
            btn_text,
            (self.submit_btn.centerx - btn_text.get_width() // 2, self.submit_btn.centery - btn_text.get_height() // 2),
        )

        feedback_surf = self.font_medium.render(self.feedback_msg, True, self.feedback_color)
        screen.blit(feedback_surf, (self.width // 2 - feedback_surf.get_width() // 2, 235))

        range_surf = self.font_medium.render(
            f"Current Possible Range: {self.low_bound} - {self.high_bound}", True, (200, 205, 215)
        )
        screen.blit(range_surf, (self.width // 2 - range_surf.get_width() // 2, 265))

        self.render_history(screen)

        if self.game_won or self.game_over:
            prompt = "Press [R] to Start a New Game" if self.game_won else "Press [R] to Try Again"
            restart_surf = self.font_medium.render(prompt, True, (255, 220, 80))
            screen.blit(restart_surf, (self.width // 2 - restart_surf.get_width() // 2, 295))

    def render_history(self, screen):
        colors = {"HIGH": (240, 100, 80), "LOW": (80, 160, 240), "HIT": (80, 220, 90)}
        label = self.font_small.render("Recent guesses (newest on the right)", True, (150, 155, 165))
        screen.blit(label, (self.width // 2 - label.get_width() // 2, 320))

        chip_w, chip_h, gap, y = 104, 30, 3, 340
        total_w = 5 * chip_w + 4 * gap
        x0 = self.width // 2 - total_w // 2
        # Right-align so the newest guess is always in the last slot
        start_slot = 5 - len(self.history)
        for i, (guess, result) in enumerate(self.history):
            x = x0 + (start_slot + i) * (chip_w + gap)
            color = colors[result]
            chip = pygame.Rect(x, y, chip_w, chip_h)
            pygame.draw.rect(screen, (42, 47, 58), chip, border_radius=6)
            pygame.draw.rect(screen, color, chip, width=2, border_radius=6)

            cy = chip.centery
            if result == "HIGH":    # arrow up: guess was above the secret number
                points = [(x + 9, cy - 5), (x + 15, cy + 5), (x + 3, cy + 5)]
                pygame.draw.polygon(screen, color, points)
            elif result == "LOW":   # arrow down: guess was below the secret number
                points = [(x + 3, cy - 5), (x + 15, cy - 5), (x + 9, cy + 5)]
                pygame.draw.polygon(screen, color, points)
            else:
                pygame.draw.circle(screen, color, (x + 9, cy), 5)

            num = self.font_btn.render(str(guess), True, (240, 240, 240))
            screen.blit(num, (x + 22, cy - num.get_height() // 2))
            tag = self.font_small.render(result, True, color)
            screen.blit(tag, (chip.right - tag.get_width() - 6, cy - tag.get_height() // 2))
