class State:
    def __init__(self):
        self.mode = []  #all the display instructions are stored here
        self.left_coordinate=[0,0]   #the position of the curser linked to the left image
        self.right_coordinate=[0,0]   #the position of the curser linked to the right image
        pass

    def get_img_data(self):
        # TODO: return the image data
        return self.img_data

    def set_img_data(self):
        # TODO: return the image data
        self.img_data = img_data

    def set_left_coordinate(self,coord):

        self.left_coordinate=coord

    def get_left_coordinate(self):
        return self.left_coordinate

    def set_right_coordinate(self,coord):

        self.right_coordinate=coord

    def get_right_coordinate(self):
        return self.right_coordinate

    