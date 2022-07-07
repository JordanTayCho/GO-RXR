from data_structure import *
from material_structure import *
import matplotlib.pyplot as plt
import numpy as np
from numba import *
from scipy import interpolate
from scipy.fft import fft, fftfreq,fftshift, rfft, irfft
from scipy.interpolate import UnivariateSpline
from scipy import signal


if __name__ == '__main__':

    sample = slab(8)

    sample.addlayer(0, 'SrTiO3', 50, density =[0.027904,0.027904,0.083712], roughness=[7.58207,False,5.77093])
    sample.addlayer(1, 'SrTiO3', 5, density=[0, 0.027904, 0], roughness=[7.58207, 4.03102, 5.77093])

    sample.addlayer(2,'LaMnO3', 5, density=[0.021798,0.0209,0.084], roughness=[3.77764,2,2],linked_roughness=[False, 0.5, False])
    sample.polymorphous(2,'Mn',['Mn2+', 'Mn3+'], [1,0], sf=['Mn', 'Fe'])
    sample.magnetization(2,['Mn2+','Mn3+'], [0.025,0], ['Co','Ni'])

    sample.addlayer(3,'LaMnO3', 18.8437, density=[0.021798,0.0209,0.084], roughness=[3.77764,2,2])
    sample.polymorphous(3, 'Mn', ['Mn2+', 'Mn3+'], [1, 0], sf=['Mn', 'Fe'])
    sample.magnetization(3, ['Mn2+', 'Mn3+'], [0.025, 0], ['Co', 'Ni'])

    sample.addlayer(4, 'LaMnO3', 10, density=[0.021798, 0.0209, 0.084], roughness=[3.77764, 2, 2])
    sample.polymorphous(4, 'Mn', ['Mn2+', 'Mn3+'], [1, 0], sf=['Mn', 'Fe'])
    sample.magnetization(4, ['Mn2+', 'Mn3+'], [0.016, 0], ['Co', 'Ni'])

    sample.addlayer(5, 'LaMnO3', 3, density=[0.025, 0.024, 0.05], roughness=[0.25, 0.25, 2])
    sample.polymorphous(5, 'Mn', ['Mn2+', 'Mn3+'], [1, 0], sf=['Mn', 'Fe'])
    sample.magnetization(5, ['Mn2+', 'Mn3+'], [0.016, 0], ['Co', 'Ni'])

    sample.addlayer(6, 'LaMnO3', 4, density=[0.025, 0.042, 0.04], roughness=[0.25, 0.25, 2])
    sample.polymorphous(6, 'Mn', ['Mn2+', 'Mn3+'], [0.4, 0.6], sf=['Mn', 'Fe'])
    sample.magnetization(6, ['Mn2+', 'Mn3+'], [0.0053, 0], ['Co', 'Ni'])

    sample.addlayer(7,'CCO', 10.1373, density =[0.05,0.05,0.01], roughness=2, linked_roughness=[3,1.5,False])


    fname = "Pim10uc.h5"
    # WriteSampleHDF5(fname, sample)
    f, data, data_dict, sim_dict = ReadDataHDF5(fname)
    sample = ReadSampleHDF5(fname)
    sample.plot_density_profile(8)
    name = data[6][2]
    print(name)
    my_data = list(data_dict[name])
    qz = my_data[0]
    R = my_data[2]



    tck = interpolate.splrep(qz, np.log10(R), s=0)
    qz_new = np.arange(qz[0],qz[-1]+min(np.diff(qz)), min(np.diff(qz)))
    R_interp = interpolate.splev(qz_new,tck)

    spl = UnivariateSpline(qz_new, R_interp, k=3)
    figure(4)
    plt.plot(qz_new, R_interp)
    plt.plot(qz_new, spl(qz_new))
    Rnew = R_interp - spl(qz_new)

    N = len(qz_new)
    T = min(np.diff(qz))
    Rf = fft(Rnew)
    qzf = fftfreq(N,T)
    qzf = fftshift(qzf)
    Rfplot = fftshift(Rf)
    plt.figure(1)
    plt.plot(qzf, 1.0/N*np.abs(Rfplot))

    plt.figure(2)
    plt.plot(qz_new, Rnew)

    f.close()
    val = 101
    window = np.zeros(N)
    M = val//2
    w = signal.windows.blackman(val)
    window[N//2-M:N-N//2+M] = w

    Rf_new = np.multiply(window, Rfplot)

    R_filtered = ifft(ifftshift(Rf_new))
    plt.figure(3)
    plt.plot(R_filtered)
    plt.show()

    plt.figure(7)
    plt.suptitle('Noise Removal')
    plt.plot(qz_new, R_interp)
    plt.plot(qz_new, R_filtered+spl(qz_new))
    plt.legend(['Original', 'Filtered'])
    plt.xlabel("Momentum Transfer (A^{-1})")
    plt.ylabel("log10(R)")
    plt.show()


