import random
import sys

import pygame

from settings import TOP_LIMIT, BOTTOM_LIMIT, LEFT_LIMIT, RIGHT_LIMIT, CONTROLLER_ICON_PATH


class Controller:
    def __init__(self, best_weights=None):
        if best_weights is None:
            best_weights = []
        self.parent = None

        self.weights = []
        self.bias = 0.1

        self.inputs = []

        self.pontuation = 0

        #l = ix*wx

        self.processed_inputs = []

        self.hidden_one = []
        self.hidden_two = []

        self.output0 = 0
        self.output1 = 0

        self.hidden_per_layer = 4

        self.weights_quantity = 100

        self.previous_distance = 340

        if best_weights == []:
            for i in range(self.weights_quantity):
                self.weights.append(random.randint(-1000, 1000))
        else:
            for i in range(self.weights_quantity):
                self.weights.append(best_weights[i] + random.randint(-10, 10))
        self.ram_usage_kb = sys.getsizeof(self) / 1024
        print(f"         [+] node ram usage -> {self.ram_usage_kb} KB")

        self.icon = pygame.image.load(CONTROLLER_ICON_PATH)


    def update(self):
        self.processed_inputs.clear()
        self.inputs.clear()
        self.hidden_one.clear()
        self.hidden_two.clear()

        current_w = 0

        self.inputs.append(self.parent.position.x)
        self.inputs.append(self.parent.position.y)
        self.inputs.append(self.parent.velocity.x)
        self.inputs.append(self.parent.velocity.y)
        self.inputs.append(self.parent.speed)
        self.inputs.append(self.parent.target_reference.position.x)
        self.inputs.append(self.parent.target_reference.position.y)
        self.inputs.append(self.parent.target_reference.velocity.x)
        self.inputs.append(self.parent.target_reference.velocity.y)
        self.inputs.append(self.parent.target_reference.speed)
        self.inputs.append(TOP_LIMIT)
        self.inputs.append(BOTTOM_LIMIT)
        self.inputs.append(LEFT_LIMIT)
        self.inputs.append(RIGHT_LIMIT)

        for i in range(self.hidden_per_layer):
            v = 0
            for tv in self.inputs:
                v += tv * self.weights[current_w]
                current_w += 1
            self.hidden_one.append(v * self.bias)

        for i in range(self.hidden_per_layer):
            v = 0
            for tv in self.hidden_one:
                v += tv * self.weights[current_w]
                current_w += 1
            self.hidden_two.append(v * self.bias)

        if round(self.hidden_two[0]) > 0:
            self.parent.position.x += self.parent.speed
        if round(self.hidden_two[1]) > 0:
            self.parent.position.x -= self.parent.speed
        if round(self.hidden_two[2]) > 0:
            self.parent.position.y += self.parent.speed
        if round(self.hidden_two[3]) > 0:
            self.parent.position.y -= self.parent.speed


        self.calculate_pontuation()


    def calculate_pontuation(self):
        distance_to_target = self.parent.position.distance_to(self.parent.target_reference.position)
        if distance_to_target < 15:
            self.pontuation += 1000
        else:
            self.pontuation += self.previous_distance - distance_to_target
            self.previous_distance = distance_to_target

        self.pontuation += 0.01


    def render(self):
        pass