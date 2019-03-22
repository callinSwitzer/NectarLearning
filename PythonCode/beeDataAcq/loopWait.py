import time

def otherFunct(conn):
    for ii in range(5):
        if conn.poll():
            print(str(ii) + str(conn.recv()))
        else: 
             print(str(ii) + "no data received")
        time.sleep(1)
    print("DONE")
    


def main(conn):
    otherFunct(conn)
    
if __name__ == "__main__":
    main(directory)
   