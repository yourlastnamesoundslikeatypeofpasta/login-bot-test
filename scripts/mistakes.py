class Mistakes:
    mistake_values = {'flex': 0, 'batt min': 0, 'pp': 0, 'packg': 0, 'we': 1, 'de': 2, 'packg2': 2, 'de2': 2,
                      'ph2': 2, 'lu': 2, 'pp2': 2, 'osd': 4, 'hk': 4, 'da': 4, 'l-ph': 4, 'item': 4, 'tw': 4,
                      'upc': 4, 'psl': 4, 'ms': 4, 'fsp': 4, 'mi': 4, 'ph4': 4, 'sn': 4, 'qd': 4, 'ps': 5, 'ml': 7,
                      'wn': 7, 'sh': 8, 'fpp': 8, 'fxr': 12, 'fmd': 12, 'ffw': 12, 'fdg': 12, 'batt maj': 12,
                      'in': 18, 'la': 18, 'wa': 18, 'cm': 22, 'utl': 25}
    instances = []

    def __init__(self):
        self.mistake_points = 0
        self.mistake_lst = []
        self.instances.append(self)

    def get_mistake_lst(self):
        return self.mistake_lst

    def get_mistake_points(self):
        points = 0
        for mistake in self.mistake_lst:
            for point in mistake.values():
                points += point
        self.mistake_points = points
        return self.mistake_points

    def add_mistake(self, mistake):
        new_mistake = {mistake: self.mistake_values[mistake]}
        self.mistake_lst.append(new_mistake)

    def remove_mistake(self, mistake):
        for index, mistake_dict  in enumerate(self.mistake_lst):
            for key in mistake_dict.keys():
                if key == mistake:
                    del self.mistake_lst[index]
                    return

    def remove_all_mistakes(self):
        self.mistake_lst.clear()

