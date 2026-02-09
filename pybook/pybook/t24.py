def order_by_age_city(persons: list):
    persons.sort(key=lambda x: (x[1], x[2]))
