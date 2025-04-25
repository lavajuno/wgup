class Input:
    @staticmethod
    def get_int():
        while True:
            try:
                return int(input())
            except ValueError: 
                print("Please enter a valid integer.")
                pass
