
import serial, struct
import getopt, sys

def frequency_config( conn, frequency ):
    the_padded_frequency = frequency.replace(".", "") 
    
    group1 = the_padded_frequency[0:2]
    group2 = the_padded_frequency[2:4]
    group3 = the_padded_frequency[4:6]
    
    exec("hex1 = 0x%s" % (group1, )) 
    exec("hex2 = 0x%s" % (group2, )) 
    exec("hex3 = 0x%s" % (group3, )) 
    
    data = struct.pack('BBBBB', hex1, hex2, hex3, 0x00, 0x01)
    conn.write(data)
    
    s = conn.read(1)
    print( ">> Frequency ack: %s" % s )
    

def mode_config( conn, mode):
    valid_mode = {
        '00' : 'LSB', '01' : 'USB',
        '02' : 'CW', '03' : 'CWR',
        '04' : 'AM', '08' : 'FM',
        '88' : 'FM-N', '0A' : 'DIG',
        '0C' : 'PKT',
    }
    yaesu_commands = dict (zip(valid_mode.values(),valid_mode.keys()))
    
    if mode.upper() in yaesu_commands:
        
        if mode.upper() in yaesu_commands:
            hex_command = yaesu_commands[mode.upper()]
            
            exec("hex4 = 0x%s" % (hex_command, )) 
            
            # Inspiration from PD7L on the initial python struct implementation
            # https://pd7l.wordpress.com/2014/05/21/212/
            # 
            data = struct.pack('BBBBB', hex4, 0x00, 0x00, 0x00, 0x07)
            conn.write(data)
            s = conn.read(1)
            print( ">> Mode ack: %s" % s )
    else:
        print("Invalid mode")

def usage():
    print(u"\npyradiocontrol.py usage:")
    print(u"\t-s or --serial")
    print(u"\t\tSet serial device. On Windows e.g. COM5, On Mac or Linux e.g. /dev/cu.usbserial")
    print(u"\t-f or --frequency")
    print(u"\t\tSet frequency of radio. e.g. 146.640")
    print(u"\t-m or --mode")
    print(u"\t\tSet mode of radio. Valid modes: LSB, USB, CW, CWR, AM, FM, FM-N, DIG, PKT")
    print(u"\n")

def radio_control():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "s:f:m:c:h", [ "serial", "frequency", "mode", "ctcss", "help"])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)
    
    serial_port = '/dev/cu.usbserial'
    
    commands = []
    
    for opt, arg in opts:
        if opt in ('-s', '--serial'):
            print(u"Setting Serial Port to: %s" % arg)
            serial_port = arg
        elif opt in ('-f', '--frequency'):
            print(u"Setting frequency: %s" % arg)
            commands.append( [frequency_config, arg] )
        elif opt in ('-m', '--mode'):
            print(u"Setting mode: %s" % arg.upper() )
            commands.append( [mode_config, arg] )
        elif opt in ('-c', '--ctcss'):
            print(u"Setting ctcss: %s"% arg)
        else:
            usage()
            sys.exit(2)
    
    if len( commands ) > 0 and serial_port:
        conn = serial.Serial(
          port=serial_port,
          baudrate=4800,
          parity=serial.PARITY_NONE,
          stopbits=serial.STOPBITS_TWO,
          bytesize=serial.EIGHTBITS
        )
    
        if conn.isOpen():
            print(u"Serial port %s connnected" % serial_port)
            
            for c in commands:
                c[0]( conn, c[1] )
    
            conn.close()
            print(u"Serial port %s closed" % serial_port)
    else:
        usage()  

if __name__ == "__main__":
    radio_control()
