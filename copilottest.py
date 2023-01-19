



def  display_spatial_graph(state):
    img_data = state.img_data()
    # display the image

class State:
    def __init__(self):
        pass

    def get_img_data(self):
        # TODO: return the image data
        return self.img_data

    def set_img_data(self):
        # TODO: return the image data
        self.img_data = img_data

def next_state(state):
    return state

def load(file_name: str, state: State):
    load_data = np.load(file_name)

    state.set_img_data(load_data)

