import math
import pygame

class CircleHitbox:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    @property
    def center(self):
        return (self.x, self.y)

    def collidepoint(self, point):
        px, py = point
        dx = px - self.x
        dy = py - self.y
        return dx * dx + dy * dy <= self.radius * self.radius

    def collidecircle(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        distance_sq = dx * dx + dy * dy
        radius_sum = self.radius + other.radius
        return distance_sq <= radius_sum * radius_sum

    def colliderect(self, rect: pygame.Rect):
        # Clamp circle center to nearest point in rect
        closest_x = max(rect.left, min(self.x, rect.right))
        closest_y = max(rect.top, min(self.y, rect.bottom))

        dx = closest_x - self.x
        dy = closest_y - self.y
        return dx * dx + dy * dy <= self.radius * self.radius