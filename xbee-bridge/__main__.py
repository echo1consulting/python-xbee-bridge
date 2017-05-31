import binascii
import glob
import paho.mqtt.client as mqtt
import serial
import serial.tools.list_ports
import socket
import sys
import time
from re import search
from xbee import DigiMesh


def get_serial_port():
    """
    Obtains all serial ports and checks if any are connected to
    a serial number of a usb to XBEE device
    :raises EnvironmentError: On unsupported or unknown platforms
    :returns: the port of the found XBee or None if none found
    """
    # depending on the system, reads available ports
    if sys.platform.startswith('win'):
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if "USB Serial Port" in str(p):
                return p.device
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        # mac
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    # scan each found port and check the serial number
    XB = None
    for ser in ports:
        # look for serial devices, which name includes either
        # a D or a A following a hyphen (-)
        # more at https://docs.python.org/2/library/re.html
        if bool(search('(?<=-)[DA]\w+', str(ser))) or 'USB0' in ser:
            XB = ser
            break

    return XB


def print_data(data):
    """
    This method is called whenever data is received
    from the associated XBee device. Its first and
    only argument is the data contained within the
    frame.
    """
    global client

    source = binascii.hexlify(data['source_addr']).upper()

    print("Source: {}".format(source))
    print("Message: {}\n". format(data['data']))

    client.publish("paho/temperature", data['data'])


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    try:
        global client
        client = mqtt.Client()
        client.on_connect = on_connect
        client.connect("broker.mqttdashboard.com", 1883, 5)
        time.sleep(1)
    except socket.gaierror as e:
        # print(sys.exc_info()[:2])
        print(str(e))
        exit()

    attached = get_serial_port()

    if attached is not None:
        print("Connected to XBee on {}.\n".format(attached))
        serial_port = serial.Serial(attached, 9600)
        xbee = DigiMesh(serial_port, callback=print_data)
        print("Connected to MQTT Broker.\n")
        client.loop_start()
    else:
        print("Unable to detect XBee.\n")
        exit()

    while True:
        try:
            time.sleep(0.001)
        except KeyboardInterrupt:
            break

    print("Disconnected from MQTT Broker.\n")
    client.disconnect()
    client.loop_stop()
    print("Disconnected from XBee on {}.\n".format(attached))
    xbee.halt()
    serial_port.close()


def on_connect(client, userdata, flags, rc):
    print("Connected with result code: {}.\n".format(str(rc)))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")


if __name__ == "__main__":
    main()
