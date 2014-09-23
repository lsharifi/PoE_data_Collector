'''
    Created on Sep 16, 2014
    
    @author: leila
'''

import matplotlib.pyplot as plt
import datetime 

def parse_data_from_db(content):
    '''
    
    '''
    i1 = []
    v1 = []
    power1 = []
    i2 = []
    v2 = []
    power2 = []
    temprature = []
    time = []
    final_content = []
    for element in content:
        items = element.split("|")[1:-1]
        i1.append(float(items[0]) / 1000) # Original values are in mA so it is converted to A
        v1.append(float(items[1]) / 1000)
        power1.append(float(items[2]))
        i2.append(float(items[3]) / 1000)
        v2.append(float(items[4]) / 1000)
        power2.append(float(items[5]))
        temprature.append(float(items[6]))
        x = items[7][1:20]
        temp = datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
        time.append(temp)
        final_content.append(element.split("|")[1:-1])     
    return i1, v1, power1, i2, v2, power2, temp , time    


def visualize_data(x , y , x_label , y_label , title):
    '''
    list, list , str , str, str -> null
    '''
    plt.plot(x , y , 'b-')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.show()
    
    
########################    
def main():
    with open("../data/data.txt" , mode='r' ) as my_file:
        content = my_file.read().splitlines()
    #print(content[3:-2])
    #print parse_data_from_db(content[3: -2])
    i1, v1, power1, i2, v2, power2, temp , time = parse_data_from_db(content[3 : -2])
    visualize_data(time , power1 , 'time' , 'power', 'power1')
    visualize_data(time , power2 , 'time' , 'power', 'power2')
    visualize_data(time , i1 , 'time' , 'i(A)', 'i1')
    visualize_data(time , i2 , 'time' , 'i(A)', 'i2')
    visualize_data(time , v1 , 'time' , 'v', 'v1')
    visualize_data(time , v2 , 'time' , 'v', 'v2')
    
    #plt.plot(time , power1 , 'b-' , time , i1  , 'r--' , time , v1  , 'gs')
    #plt.xlabel('time')
    #plt.ylabel(y_label)
    #plt.show()
    

main()
if __name__ == '__main__':
    pass
