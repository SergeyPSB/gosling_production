import random

def generate_map(size: int, time_effect_step=5):
    map_data = []

    # Generate random fields
    for i in range(size):
        field_type = random.choice(['positive', 'negative', 'neutral'])
        if field_type == 'positive':
            time_effect = random.randint(1, 15) * time_effect_step  # Increase time effect for positive fields
        elif field_type == 'negative':
            time_effect = random.randint(-15, -1) * time_effect_step  # Random time effect for other fields
        else:
            time_effect = 0

        map_data.append({"type": field_type, "time_effect": time_effect})
    return map_data


class SessionTimer:
    
    def __init__(self, init_time_secs: int):
        self.time_secs = init_time_secs
        
    def __init__(self, init_time_hour: int):
        self.time_secs = self.__hours_to_secs(init_time_hour)
    
    def add_minutes(self, mins: int):
        secs = self.__mins_to_secs(mins)
        self.time_secs += secs
        
    def remove_minutes(self, mins: int):
        secs = self.__mins_to_secs(mins)
        self.time_secs -= secs
        
    def __mins_to_secs(self, mins: int):
        return mins * 60
    
    def __hours_to_secs(self, hours: int):
        return self.__mins_to_secs(hours * 60)
    
    def __format_seconds_to_hours_minutes(self):
        hours, remainder = divmod(self.time_secs, 3600)  # Get hours and remaining seconds
        minutes, _ = divmod(remainder, 60)  # Get minutes from remaining seconds

        # Format the hours and minutes into a string
        formatted_time = "{:02d}:{:02d}".format(hours, minutes)
        return formatted_time
    
    def get_timer(self):
        if self.time_secs < 0:
            return "00:00"
        else:
            return self.__format_seconds_to_hours_minutes()