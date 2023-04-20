"""

Library: main.py
Version: 0.1
Author: Lucas Korol
Institution: University of Saskatchewan
Last Updated: April 6, 2023
Python: version 3.7

Purpose: This script contains functions that are used to update the form factor database

Imported Libraries

numpy (version 1.21.4) - used for array manipulation

Note - This python script is also used to test out function and analyze data
"""
import os

import numpy as np
import data_structure as ds
import matplotlib.pyplot as plt
from numba import *

def getFF(name):
    """
    Purpose: Retrieve the form factor information from the database
    :param name: Name of the form factor
    :return: data - the data
             source - the source of the form factor
             updated - the date of when the form factor was last updated
    """

    import pickle

    # opens the current form factor database
    with open('form_factor.pkl', 'rb') as f:
        my_dict = pickle.load(f)  # This is made a global variable so we do not have to keep on loading in the file
    my_dict.close()
    data = ''
    source = ''
    updated = ''
    if name not in my_dict.keys():
        print(name, ' not in keys')
    else:
        data = my_dict[name]['Data']
        source = my_dict[name]['Source']
        updated = my_dict[name]['Updated']

    return data, source, updated

def getFFM(name):
    """
    Purpose: Retrieve the form factor information from the database
    :param name: Name of the form factor
    :return: data - the data
             source - the source of the form factor
             updated - the date of when the form factor was last updated
    """
    import pickle

    # opens the current form factor database
    with open('form_factor_magnetic.pkl', 'rb') as f:
        my_dict = pickle.load(f)  # This is made a global variable so we do not have to keep on loading in the file
    my_dict.close()

    data = ''
    source = ''
    updated = ''
    if name not in my_dict.keys():
        print(name, ' not in keys')
    else:
        data = my_dict[name]['Data']
        source = my_dict[name]['Source']
        updated = my_dict[name]['Updated']

    return data, source, updated

def createFF(directory, name , source, date):
    """
    Purpose: Add a new or change form factor in form factor database
    :param directory: Path to the desired form factor textfile
    :param name: Desired name of form factor (e.g. A, Mn, Mn2+...)
    :param source: Name of place the form factor was retrieved (e.g. The Center for X-ray Optics)
    :param date: Date the change was made (entered as a sting)
    """
    import os
    import pickle

    # opens the current form factor database
    with open('form_factor.pkl', 'rb') as f:
        my_dict = pickle.load(f)  # This is made a global variable so we do not have to keep on loading in the file
    my_dict.close()

    data = np.loadtxt(directory)

    # includes the new form factor into the database
    my_dict[name]['Data'] = data  # stores the form factor data
    my_dict[name]['Source'] = source  # stores the url of the source
    my_dict[name]['Updated'] = date  # stores the date last updated

    with open('form_factor.pkl', 'wb') as handle:
        pickle.dump(my_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)


def createFFM(directory, name ,source, date):
    """
        Purpose: Add a new or change form factor in form factor database
        :param directory: Path to the desired form factor textfile
        :param name: Desired name of form factor (e.g. A, Mn, Mn2+...)
        :param source: Name of place the form factor was retrieved (e.g. The Center for X-ray Optics)
        :param date: Date the change was made (entered as a sting)
        """
    import os
    import pickle

    # opens the current form factor database
    with open('form_factor_magnetic.pkl', 'rb') as f:
        my_dict = pickle.load(f)  # This is made a global variable so we do not have to keep on loading in the file
    my_dict.close()

    data = np.loadtxt(directory)

    # includes the new form factor into the database
    my_dict[name]['Data'] = data  # stores the form factor data
    my_dict[name]['Source'] = source  # stores the url of the source
    my_dict[name]['Updated'] = date  # stores the date last updated

    with open('form_factor_magnetic.pkl', 'wb') as handle:
        pickle.dump(my_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)


@njit()
def ALS(alpha, beta, precision=1e-6):
    """
    Purpose: Perform the adaptive layer segmentation
    :param alpha: numpy array of real values
    :param beta: numpy array of imaginary values
    :param precision: precision value for slicing
    :return: my_slabs - contains indices for slicing
    """

    precision = 1e-5
    alpha = alpha / np.linalg.norm(alpha)  # normalizes epsilon
    beta = beta / np.linalg.norm(beta)  # normalizes epsilon_mag
    idx_a = 0  # keeps track of surface of previous slab
    n = alpha.size
    my_slabs = np.zeros(n)  # pre-initialize the slab array

    dsSlab = 1  # counts the number of slices

    for idx_b in range(1, n):
        if idx_b > 0:
            # retrieves permittivity values
            f1 = alpha[idx_a]
            f2 = alpha[idx_b]
            f1b = beta[idx_a]
            f2b = beta[idx_b]

            delta_a = np.absolute(f2 - f1)  # varitation of epsilon
            delta_b = np.absolute(f2b - f1b)  # variation of epsilon_mag

            # checks if variation is of minimum variation set by 'precision'
            if delta_a > precision or delta_b > precision:
                # my_slabs = np.append(my_slabs, idx_b)  # append slice
                my_slabs[dsSlab] = idx_b
                idx_a = idx_b  # change previous slice location
                dsSlab = dsSlab + 1
            elif idx_b == n - 1:  # reached the end of the array
                my_slabs[dsSlab] = idx_b
                dsSlab = dsSlab + 1
        else:
            idx_a = idx_b
            my_slabs[dsSlab] = idx_b
            dsSlab = dsSlab + 1
    my_slabs = my_slabs[:dsSlab]

    return my_slabs
if __name__ == '__main__':
    """
    from scipy.interpolate import UnivariateSpline
    import material_structure as ms
    fname = "//cabinet/work$/lsk601/My Documents/SrTiO3-LaMnO3/Pim7uc_unitCell_v3.h5"

    sample = ds.ReadSampleHDF5(fname)
    sample.energy_shift()
    Theta = 15
    energy = 640.2
    qz = np.sin(Theta * np.pi / 180) * (energy * 0.001013546143)

    
    struct_names, mag_names = mm._use_given_ff(os.getcwd())  # look for form factors in directory

    data, data_dict, sim_dict = ds.ReadDataHDF5(fname)

    keys = ['26_452.77_S' ,'35_460.76_S','19_500.71_S', '31_635.99_S','22_640.99_S','24_644.02_S','33_834.59_S',
            '9_642.12_LC' ,'10_642.12_RC', '9-10_642.12_AC_Asymm', '13_644.03_LC','14_644.03_RC','13-14_644.03_AC_Asymm',
            '16_653.06_LC', '17_653.06_RC', '16-17_653.06_AC_Asymm']

    for key in keys:
        E = data_dict[key]['Energy']
        pol = data_dict[key]['Polarization']
        qz = data_dict[key]['Data'][0]

        # use to create new number of points!
        qz_min = qz[0]
        qz_max = qz[-1]
        number_points = 1000

        qz_new = np.linspace(qz_min,qz_max,num=number_points)
        Theta = np.arcsin(qz_new / E / (0.001013546247)) * 180 / np.pi  # initial angle

        qz_new, R = sample.reflectivity(E,qz_new)
        R = R[pol]


        sim_dict[key]['Data'] = np.array([qz_new, Theta, R])


        print('Done - ', key)

    ds.saveSimulationHDF5(fname, sim_dict)
    
    


    thickness, density, mag_density = sample.density_profile()

    my_keys = ['Sr', 'Ti', 'La', 'Mn','O']
    my_keys = ['Mn2','Mn3']


    d = 37.550
    idx = [i for i in range(len(thickness)) if thickness[i] < d]


    electron = {'Sr':2,'La':3,'Ti':4,'Mn2':2,'Mn3':3, 'O':-2}
    density['Mn'] = density['Mn2'] + density['Mn3']

    from scipy import integrate

    total = integrate.trapezoid(mag_density['Mn3'], x=thickness)
    print(total/10)
    #print(total/10/4)

    x = [4,7,10]
    y = [0.009153213732481595/4, 0.06715542943115324/7, 0.09526111771582044/10]
    plt.figure(1)
    plt.bar(x,y,)
    plt.xlabel('Sample (uc)')
    plt.ylabel('Magnetic Density per units cell')
    plt.show()

    plt.figure(2)
    for key in my_keys:
        plt.plot(thickness, density[key], c=np.random.rand(3,))
    
    plt.ylabel('Density (mol/cm^3)')
    plt.xlabel('Thickness (angstroms)')
    plt.legend(my_keys)
    plt.show()

    oxidation = np.zeros(len(thickness))
    total = np.zeros(len(thickness))
    for key in electron.keys():
        oxidation = oxidation + electron[key]*density[key]
        total = total+density[key]

    oxidation = oxidation/total

    plt.figure()
    plt.plot(thickness[idx], oxidation[idx])
    plt.show()
    
    x = [4,7,10]
    y = [0.0007044,0.00220607,0.00279876]

    plt.figure(3)
    plt.plot(x,y)
    plt.ylabel('Average Magnetic Density (mol/cm^2)')
    plt.xlabel('Unit Cells (uc)')


    
    
    #KK = variationKK(E_prime,E0,E2,E4)
    

    fname = "//cabinet/work$/lsk601/My Documents/LSMO_For_Lucas/RXR_Twente-EM1-150K_v9.h5"

    struct_names, mag_names = mm._use_given_ff("//cabinet/work$/lsk601/My Documents/LSMO_For_Lucas")  # look for form factors in directory

    sample = ds.ReadSampleHDF5(fname)
    sample.energy_shift()


    
    data, data_dict, sim_dict = ds.ReadDataHDF5(fname)

    keys = ['26_452.77_S', '35_460.76_S', '19_500.71_S', '31_635.99_S', '22_640.99_S', '24_644.02_S', '33_834.59_S',
            '9_642.12_LC', '10_642.12_RC', '9-10_642.12_AC_Asymm', '13_644.03_LC', '14_644.03_RC',
            '13-14_644.03_AC_Asymm',
            '16_653.06_LC', '17_653.06_RC', '16-17_653.06_AC_Asymm']


    
    destination = '\\cabinet\work$\lsk601\My Documents\Data_for_Jesus\RXR-Twente-E1-150K-simulation-0.1eV'
    for i in range(0,300+1,1):
        E = 450 + i*0.1
        Theta = np.linspace(0.1, 60, num=2000)
        qz = np.sin(Theta * np.pi / 180) * E * (0.001013546247)

        qz, R = sample.reflectivity(E, qz)

        filename = 'E1_' + str(E)
        dat = np.transpose(np.array([qz, R['S']]))
        file = r"\\cabinet\work$\lsk601\My Documents\Data_for_Jesus\RXR-Twente-E1-150K-simulation-0.1eV"
        file = file + '\E1_' + str(E)
        np.savetxt(file, dat)



    #np.savetxt('E1_' + str(E), dat)
    

    #E = np.arange(10,3000,1)
    #imaginary = np.zeros(len(E))
    #real = np.zeros(len(E))

    #data = np.transpose(np.array([E, imaginary, real]))

    #np.savetxt('Z.txt', data,fmt='%.4s')

    
    dir= "C:/Users/lsk601/PycharmProjects/MaterialReflection/Magnetic_Scattering_Factor"
    import pickle
    import os

    #with open('form_factor.pkl', 'rb') as f:
    #    my_dict = pickle.load(f)  # This is made a global variable so we do not have to keep on loading in the file
    #f.close()

    my_dict = dict()

    source = 'The Center for X-ray Optics'
    date = 'April 6, 2023'
    for filename in os.listdir(dir):
        f = os.path.join(dir, filename)
        if not (filename.startswith('README')):
            name = filename.split('.')[0]
            data = np.loadtxt(f)
            my_dict[name] = dict()
            my_dict[name]['Data'] = data  # stores the form factor data
            my_dict[name]['Source'] = source  # stores the url of the source
            my_dict[name]['Updated'] = date  # stores the date last updated


    import pickle
    with open('form_factor_magnetic.pkl', 'wb') as handle:
        pickle.dump(my_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    

    """
    new = np.loadtxt('833.csv')
    t = new[:,0]

    text = np.loadtxt('833_ReMagX.txt')



    #plt.figure(1)
    #plt.suptitle('Figure')
    #plt.plot(new[:, 0], new[:, 3])
    #plt.plot(text[:,0], np.log10(text[:,1]))
    #plt.legend(['GO-RXR', 'ReMagX'])
    #plt.xlabel('Momentum Transfer (A^{-1})')
    #plt.ylabel('Reflectivity, R')



    #print(sum(abs(np.log10(text[:,3])-new[:,1]))/len(text[:,0]))
    import material_structure as ms
    remagx = np.loadtxt('optical_profile_text.txt')
    d_d = remagx[:,0]
    delta_r = remagx[:,1]
    idx_d = [i for i in range(0, len(d_d),4)]
    d_b = remagx[:,2]
    idx = [i for i in range(len(d_b)) if d_b[i]!=0]
    d_b = d_b[idx]
    beta_r = remagx[:,3][idx]



    idx_b = [i for i in range(0,len(d_b),2)]
    thickness_r = d_b[idx_b]  # thickness I will be using
    n_r = 1 + np.vectorize(complex)(-delta_r[idx_d], beta_r[idx_b])  # index of refraction

    new_delta = []
    new_beta = []
    new_thickness = []
    for i in range(0,len(delta_r[idx_d])-1):
        new_thickness.append(thickness_r[i])
        new_thickness.append(thickness_r[i])

        new_delta.append(delta_r[idx_d][i])
        new_delta.append(delta_r[idx_d][i+1])

        new_beta.append(beta_r[idx_b][i])
        new_beta.append(beta_r[idx_b][i+1])

    epsilon_r = n_r ** 2  # epsilon for ReMagX

    import Pythonreflectivity as pr
    m = len(epsilon_r)  # number of slabs
    A = pr.Generate_structure(m)  # creates Pythonreflectivity object class

    E = 833.85
    h = 4.135667696e-15  # Plank's constant eV*s
    c = 2.99792458e8  # speed of light m/s
    wavelength = h * c / (E * 1e-10)  # wavelength

    m_j = 0
    idx = 0

    for m_i in range(len(epsilon_r)):
        m_i = int(m_i)
        d = thickness_r[m_i] - thickness_r[m_j]  # computes thickness of slab

        # eps = (epsilon[m_i] + epsilon[m_j])/2  # computes the dielectric constant value to use
        eps = epsilon_r[m_i]


        # A[idx].seteps(eps)  # sets dielectric tensor for non-magnetic layer
        A[idx].seteps([eps, eps, eps, 0])

        if idx != 0:
            A[idx].setd(d)  # sets thickness of layer if and only if not substrate layer

        # move onto the next layer
        m_j = m_i
        idx = idx + 1

    qz = new[:, 0]
    plt.show()

    Theta = np.arcsin(qz / E / (0.001013546247)) * 180 / np.pi  # initial angle
    R = pr.Reflectivity(A, Theta, wavelength, MagneticCutoff=1e-20)  # Computes the reflectivity



    data = np.loadtxt('optical_profile.csv')
    delta = data[:,1]
    beta = data[:,3]
    n = 1 + np.vectorize(complex)(-delta, beta)  # index of refraction

    epsilon = n ** 2
    thickness = data[:,0]
    my_slabs = ALS(delta, beta, precision=1e-1000)

    my_thickness = []
    my_delta = []
    my_beta = []
    # Recent versions of Pythonreflectivity use the susceptibility instead of the dielectric constant
    import Pythonreflectivity as pr
    my_slabs = my_slabs[1:]  # removes first element
    import copy
    copy_slabs = copy.copy(my_slabs)

    m = len(my_slabs)  # number of slabs
    A = pr.Generate_structure(m)  # creates Pythonreflectivity object class

    E = 833.85
    h = 4.135667696e-15  # Plank's constant eV*s
    c = 2.99792458e8  # speed of light m/s
    wavelength = h * c / (E * 1e-10)  # wavelength

    m_j=0
    idx = 0

    for m_i in my_slabs:
        m_i = int(m_i)
        d = thickness[m_i] - thickness[m_j]  # computes thickness of slab

        # eps = (epsilon[m_i] + epsilon[m_j])/2  # computes the dielectric constant value to use
        eps = epsilon[m_j]


        # A[idx].seteps(eps)  # sets dielectric tensor for non-magnetic layer
        A[idx].seteps([eps, eps, eps, 0])

        if idx != 0:
            A[idx].setd(d)  # sets thickness of layer if and only if not substrate layer

        # move onto the next layer
        m_j = m_i
        idx = idx + 1


    new_d = []
    new_epsilon = []
    rough = []
    cool_d = [0]
    dto = 0
    for i in range(len(copy_slabs)):
        if i == 0:
            new_d.append(0)
        else:
            new_d.append(A[i].d())
            dto = dto + A[i].d()
            cool_d.append(dto)

        new_epsilon.append(A[i].epsxx())
        rough.append(A[i].sigma())


    new_epsilon = np.array(new_epsilon).imag
    copy_slabs = [int(i) for i in copy_slabs]
    old_eps = np.array(epsilon[copy_slabs]).imag


    Theta = np.arcsin(qz / E / (0.001013546247)) * 180 / np.pi  # initial angle
    Rtemp = pr.Reflectivity(A, Theta, wavelength, MagneticCutoff=1e-20)  # Computes the reflectivity

    plt.figure(5)
    plt.plot(qz, np.log10(Rtemp[0]))
    plt.plot(qz, np.log10(R[0]))
    plt.legend(['GO-RXR','ReMagX'])
    plt.show()


    for i, m_i in enumerate(my_slabs):
        if m_i != 0:
            m_i = int(m_i)
            m_j = int(m_j)


            my_thickness.append(thickness[m_i-1])
            my_thickness.append(thickness[m_i-1])


            eps = delta[m_j]  # computes the dielectric constant value to use

            my_delta.append(eps)
            my_beta.append(beta[m_j])
            my_delta.append(delta[m_i])
            my_beta.append(beta[m_i])

            m_j=m_i


    plt.figure(2)
    #plt.plot(data[:,0], data[:,1])
    plt.stem(my_thickness, my_delta, bottom=0, markerfmt='b-', linefmt='b-')
    plt.stem(new_thickness, new_delta, bottom=0, markerfmt='r-', linefmt='r-')

    plt.legend(['GO-RXR', 'ReMagX'])
    #plt.plot(thickness, delta,'r')
    plt.suptitle('GO-RXR Segmentation')
    #plt.legend(['Segmentation', 'Original'])
    plt.show()

    """

    plt.figure(3)
    plt.plot(remagx[:,0],remagx[:,1])
    #plt.plot(thickness, delta)
    #plt.stem(my_thickness, my_delta, linefmt='r-',bottom=0, markerfmt='')
    plt.suptitle('ReMagX Segmentation')
    plt.show()

    plt.figure(4)
    plt.plot(data[:,0], data[:,1])
    #plt.legend(['ReMagX', 'Go-RXR'])
    plt.suptitle('GO-RXR Optical Profile')

    """