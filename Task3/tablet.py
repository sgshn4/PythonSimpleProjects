class Tablet:
    def __init__(self, title, memory, rating, price):
        self.__title = title
        self.__memory = memory
        self.__rating = rating
        self.__price = price

    def get_title(self):
        return self.__title

    def get_memory(self):
        return self.__memory

    def get_rating(self):
        return self.__rating

    def get_price(self):
        return self.__price

