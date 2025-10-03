import pygame
import state
from utility import resource_path

class Question:
    def __init__(self, question_text, options, correct_answer):
        self.question_text = question_text
        self.options = options  # List of 4 options
        self.correct_answer = correct_answer  # Index 0-3

class Quiz:
    def __init__(self, quiz_file=resource_path('quiz_data.txt')):
        self.display_surface = pygame.display.get_surface()
        self.questions = []
        self.current_question_index = 0
        self.score = 0
        self.answered = False
        self.selected_answer = None
        self.quiz_complete = False
        
        # Colors
        self.bg_color = (14, 15, 44)  # Match game background
        self.text_color = (255, 255, 255)
        self.correct_color = (50, 205, 50)
        self.incorrect_color = (220, 20, 60)
        self.option_color = (100, 149, 237)
        self.selected_color = (255, 215, 0)
        
        # Fonts
        self.title_font = pygame.font.Font(None, 48)
        self.question_font = pygame.font.Font(None, 36)
        self.option_font = pygame.font.Font(None, 28)
        self.score_font = pygame.font.Font(None, 32)
        
        # Load questions
        self.load_questions(quiz_file)
    
    def load_questions(self, filename):
        """Parse the quiz text file and load questions"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split by double newlines to separate questions
            question_blocks = content.strip().split('\n\n')
            
            for block in question_blocks:
                lines = block.strip().split('\n')
                if len(lines) < 5:
                    continue
                
                # First line is the question
                question_text = lines[0]
                
                # Next 4 lines are options
                options = []
                correct_answer = -1
                
                for i, line in enumerate(lines[1:5]):
                    # Remove the letter prefix (A), B), etc.)
                    option_text = line[3:].strip()
                    
                    # Check if this is the correct answer (has ✅)
                    if '✅' in option_text:
                        option_text = option_text.replace('✅', '').strip()
                        correct_answer = i
                    
                    options.append(option_text)
                
                if correct_answer != -1:
                    self.questions.append(Question(question_text, options, correct_answer))
        
        except FileNotFoundError:
            print(f"Quiz file '{filename}' not found!")
            # Add a default question so the game doesn't crash
            self.questions.append(Question(
                "Quiz file not found!",
                ["Option A", "Option B", "Option C", "Option D"],
                0
            ))
    
    def handle_events(self, event):
        """Handle keyboard input for quiz"""
        if event.type == pygame.KEYDOWN:
            if self.quiz_complete:
                # On quiz complete screen, any key restarts
                if event.key == pygame.K_r:
                    # Restart game
                    state.GAME_STATE = state.GameState.RESTART
                    self.reset()
                elif event.key == pygame.K_ESCAPE:
                    state.GAME_STATE = state.GameState.EXIT
            
            elif not self.answered:
                # Map keys to answer indices
                answer_map = {
                    pygame.K_1: 0, pygame.K_a: 0,
                    pygame.K_2: 1, pygame.K_b: 1,
                    pygame.K_3: 2, pygame.K_c: 2,
                    pygame.K_4: 3, pygame.K_d: 3,
                }
                
                if event.key in answer_map:
                    self.selected_answer = answer_map[event.key]
                    self.check_answer()
            
            else:
                # After answering, press any key to continue
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    self.next_question()
    
    def check_answer(self):
        """Check if the selected answer is correct"""
        current_q = self.questions[self.current_question_index]
        if self.selected_answer == current_q.correct_answer:
            self.score += 1
        self.answered = True
    
    def next_question(self):
        """Move to the next question or finish quiz"""
        self.current_question_index += 1
        self.answered = False
        self.selected_answer = None
        
        if self.current_question_index >= len(self.questions):
            self.quiz_complete = True
    
    def reset(self):
        """Reset quiz to beginning"""
        self.current_question_index = 0
        self.score = 0
        self.answered = False
        self.selected_answer = None
        self.quiz_complete = False
    
    def draw(self):
        """Draw the quiz interface"""
        self.display_surface.fill(self.bg_color)
        
        if self.quiz_complete:
            self.draw_results()
        else:
            self.draw_question()
    
    def draw_question(self):
        """Draw the current question and options"""
        screen_width = self.display_surface.get_width()
        screen_height = self.display_surface.get_height()
        
        current_q = self.questions[self.current_question_index]
        
        # Draw title
        title_text = self.title_font.render("Space Quiz", True, self.text_color)
        title_rect = title_text.get_rect(center=(screen_width // 2, 50))
        self.display_surface.blit(title_text, title_rect)
        
        # Draw progress
        progress_text = self.score_font.render(
            f"Question {self.current_question_index + 1}/{len(self.questions)} | Score: {self.score}",
            True, self.text_color
        )
        progress_rect = progress_text.get_rect(center=(screen_width // 2, 100))
        self.display_surface.blit(progress_text, progress_rect)
        
        # Draw question text (wrap if needed)
        question_y = 160
        self.draw_wrapped_text(current_q.question_text, self.question_font, 
                              self.text_color, screen_width // 2, question_y, screen_width - 100)
        
        # Draw options
        option_start_y = 250
        option_spacing = 80
        
        for i, option in enumerate(current_q.options):
            y_pos = option_start_y + i * option_spacing
            
            # Determine color based on state
            if self.answered:
                if i == current_q.correct_answer:
                    color = self.correct_color
                elif i == self.selected_answer:
                    color = self.incorrect_color
                else:
                    color = self.option_color
            else:
                color = self.option_color
            
            # Draw option box
            option_rect = pygame.Rect(100, y_pos - 10, screen_width - 200, 60)
            pygame.draw.rect(self.display_surface, color, option_rect, border_radius=10)
            pygame.draw.rect(self.display_surface, self.text_color, option_rect, 2, border_radius=10)
            
            # Draw option text
            option_label = ['A', 'B', 'C', 'D'][i]
            option_text = self.option_font.render(f"{option_label}) {option}", True, self.text_color)
            option_text_rect = option_text.get_rect(midleft=(120, y_pos + 20))
            self.display_surface.blit(option_text, option_text_rect)
        
        # Draw instructions
        if not self.answered:
            instruction_text = self.option_font.render(
                "Press 1-4 or A-D to answer",
                True, (200, 200, 200)
            )
        else:
            instruction_text = self.option_font.render(
                "Press SPACE or ENTER to continue",
                True, (200, 200, 200)
            )
        instruction_rect = instruction_text.get_rect(center=(screen_width // 2, screen_height - 50))
        self.display_surface.blit(instruction_text, instruction_rect)
    
    def draw_results(self):
        """Draw the final results screen"""
        screen_width = self.display_surface.get_width()
        screen_height = self.display_surface.get_height()
        
        # Draw title
        title_text = self.title_font.render("Quiz Complete!", True, self.text_color)
        title_rect = title_text.get_rect(center=(screen_width // 2, 100))
        self.display_surface.blit(title_text, title_rect)
        
        # Draw score
        percentage = (self.score / len(self.questions)) * 100
        score_text = self.title_font.render(
            f"Score: {self.score}/{len(self.questions)}",
            True, self.correct_color if percentage >= 70 else self.incorrect_color
        )
        score_rect = score_text.get_rect(center=(screen_width // 2, 200))
        self.display_surface.blit(score_text, score_rect)
        
        # Draw percentage
        percent_text = self.question_font.render(
            f"{percentage:.1f}%",
            True, self.text_color
        )
        percent_rect = percent_text.get_rect(center=(screen_width // 2, 260))
        self.display_surface.blit(percent_text, percent_rect)
        
        # Draw performance message
        if percentage >= 90:
            message = "Excellent! You're a space expert!"
        elif percentage >= 70:
            message = "Great job! You know your space facts!"
        elif percentage >= 50:
            message = "Good effort! Keep learning!"
        else:
            message = "Keep studying the cosmos!"
        
        message_text = self.score_font.render(message, True, self.text_color)
        message_rect = message_text.get_rect(center=(screen_width // 2, 340))
        self.display_surface.blit(message_text, message_rect)
        
        # Draw restart instructions
        restart_text = self.option_font.render(
            "Press R to return to game | ESC to exit",
            True, (200, 200, 200)
        )
        restart_rect = restart_text.get_rect(center=(screen_width // 2, screen_height - 100))
        self.display_surface.blit(restart_text, restart_rect)
    
    def draw_wrapped_text(self, text, font, color, x, y, max_width):
        """Draw text with word wrapping"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = font.render(test_line, True, color)
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw all lines
        for i, line in enumerate(lines):
            line_surface = font.render(line, True, color)
            line_rect = line_surface.get_rect(center=(x, y + i * 40))
            self.display_surface.blit(line_surface, line_rect)
