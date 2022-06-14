import os


def connectToWifi(WiFiName='ESP_C7D315'):
    os.system(f'cmd /c "netsh wlan connect name={WiFiName}"')


def seeWifiNetworks():
    # scan available Wifi networks
    os.system('cmd /c "netsh wlan show networks"')


def chooseWiFi():
    seeWifiNetworks()

    # input Wifi name
    name_of_router = input('Enter Name/SSID of the Wifi Network you wish to connect to: ')

    # connect to the given wifi network
    connectToWifi(name_of_router)


if __name__ == '__main__':
    chooseWiFi()


