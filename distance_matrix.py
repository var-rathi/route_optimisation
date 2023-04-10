import numpy as np
import pandas as pd
import utm
import re
from data_loader import data_loader_opsvone
class coordinates_preprocesing(data_loader_opsvone):
    def __init__(self,dates,time_slots):
        super().__init__()
        self.data=self.load_data(dates,time_slots)
        self.names=np.array(self.data.invoice_number)
        self.coordinates=np.array(self.data.location_coordinates)

    def clean_coordinates(self,s):
        if len(s.split(' ')) != 4:
            return [0, 0]
        deg0, dec0 = s.split(' ')[1].split('°')
        deg1, dec1 = s.split(' ')[-1].split('°')

        deg0 = float(deg0)
        deg1 = float(deg1)
        minu0, seco0 = dec0.split("'")
        minu1, seco1 = dec1.split("'")
        seco0 = float(re.findall("\d+\.\d+", seco0)[0])
        seco1 = float(re.findall("\d+\.\d+", seco1)[0])
        n1 = float(deg0) + float(minu0) / 60 + float(seco0) / (60 * 60)
        n2 = float(deg1) + float(minu1) / 60 + float(seco1) / (60 * 60)
        return [n1, n2]
    def cleaned_coordinates(self):
        return np.array([self.clean_coordinates(x) for x in self.coordinates])
    def convert_to_xy(self):
        return np.array([utm.from_latlon(cor[0],cor[1])[:2] for cor in self.cleaned_coordinates()])

class distance_matrix(coordinates_preprocesing):
    # The Structure is such that we can only input dates and time_slots once
    # Only when the class is distance_matrix class is constructed
    def __init__(self,dates=['2023-02-01', '2023-02-02'],time_slots=['5:31 PM to 8:30 PM']):
        super().__init__(dates,time_slots)
    def euclidean_matrix_raw(self):
        xy=self.convert_to_xy()
        k = (np.array(xy) * np.ones_like(np.array(xy), shape=(len(xy), len(xy), 2))).T
        kx, ky = k[0], k[1]
        A = np.sqrt(np.add(np.square(kx-kx.T),np.square(ky-ky.T)))
        return A.astype(int)
    def euclidean_matrix_dataframe(self):
        return pd.DataFrame(self.euclidean_matrix_raw(),columns=self.names,index=self.names)

