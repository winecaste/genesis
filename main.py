import random
import string
from dataclasses import dataclass
from typing import List, Dict, Tuple
import heapq
import json


@dataclass
class Planet:
    name: str
    coordinates: Tuple[float, float]  # x, y координаты для простоты расчетов


@dataclass
class StarSystem:
    name: str
    planets: List[Planet]
    distances: Dict[Tuple[str, str], float]  # кэш расстояний между планетами


class GalaxyGenerator:
    def __init__(self):
        self.systems: Dict[str, StarSystem] = {}
        self.used_names: set = set()

    def generate_unique_name(self, prefix: str) -> str:
        """Генерирует уникальное имя для планеты или системы"""
        while True:
            name = prefix + '-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            if name not in self.used_names:
                self.used_names.add(name)
                return name

    def calculate_distance(self, p1: Planet, p2: Planet) -> float:
        """Рассчитывает расстояние между планетами в световых часах"""
        x1, y1 = p1.coordinates
        x2, y2 = p2.coordinates
        return round(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5, 2)

    def generate_star_system(self, num_planets: int = random.randint(3, 8)) -> StarSystem:
        """Создает новую звездную систему с указанным количеством планет"""
        system_name = self.generate_unique_name("SYS")
        planets = []
        distances = {}

        # Генерируем планеты со случайными координатами
        for _ in range(num_planets):
            planet = Planet(
                name=self.generate_unique_name("PLT"),
                coordinates=(
                    random.uniform(-100, 100),
                    random.uniform(-100, 100)
                )
            )
            planets.append(planet)

        # Рассчитываем расстояния между всеми планетами
        for i, p1 in enumerate(planets):
            for j, p2 in enumerate(planets[i + 1:], i + 1):
                distance = self.calculate_distance(p1, p2)
                distances[(p1.name, p2.name)] = distance
                distances[(p2.name, p1.name)] = distance

        return StarSystem(system_name, planets, distances)

    def add_star_system(self, system: StarSystem):
        """Добавляет звездную систему в галактику"""
        self.systems[system.name] = system

    def save_to_file(self, filename: str):
        """Сохраняет данные галактики в JSON файл"""
        data = {
            name: {
                "planets": [
                    {"name": p.name, "coordinates": p.coordinates}
                    for p in system.planets
                ],
                "distances": {
                    f"{k[0]}-{k[1]}": v
                    for k, v in system.distances.items()
                }
            }
            for name, system in self.systems.items()
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)


class RouteCalculator:
    def __init__(self, star_system: StarSystem):
        self.system = star_system

    def find_shortest_path(self, start_planet: str, end_planet: str) -> Tuple[List[str], float]:
        """
        Находит кратчайший путь между планетами используя алгоритм Дейкстры
        Возвращает список планет в порядке посещения и общее расстояние
        """
        distances = {p.name: float('infinity') for p in self.system.planets}
        distances[start_planet] = 0
        previous = {p.name: None for p in self.system.planets}

        pq = [(0, start_planet)]
        visited = set()

        while pq:
            current_distance, current_planet = heapq.heappop(pq)

            if current_planet in visited:
                continue

            visited.add(current_planet)

            if current_planet == end_planet:
                break

            # Проверяем все возможные переходы к другим планетам
            for planet in self.system.planets:
                if planet.name == current_planet:
                    continue

                distance = self.system.distances.get((current_planet, planet.name))
                if distance is None:
                    continue

                new_distance = current_distance + distance

                if new_distance < distances[planet.name]:
                    distances[planet.name] = new_distance
                    previous[planet.name] = current_planet
                    heapq.heappush(pq, (new_distance, planet.name))

        # Восстанавливаем путь
        path = []
        current = end_planet
        while current is not None:
            path.append(current)
            current = previous[current]

        return path[::-1], distances[end_planet]


# Пример использования
def example_usage():
    # Создаем генератор галактики
    generator = GalaxyGenerator()

    # Генерируем звездную систему
    system = generator.generate_star_system(5)
    generator.add_star_system(system)

    # Сохраняем данные
    generator.save_to_file("galaxy_data.json")

    # Создаем планировщик маршрута
    router = RouteCalculator(system)

    # Находим путь между первой и последней планетой
    start_planet = system.planets[0].name
    end_planet = system.planets[-1].name

    path, total_distance = router.find_shortest_path(start_planet, end_planet)

    print(f"Маршрут от {start_planet} до {end_planet}:")
    print(" -> ".join(path))
    print(f"Общее расстояние: {total_distance:.2f} световых часов")


if __name__ == "__main__":
    example_usage()