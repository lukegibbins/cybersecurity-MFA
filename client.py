import socket
import datetime

def write_response(start, finish, artist, length):
    # This writes information to the log file 'client.log
    new_file = open("client.log", 'a+')
    new_file.write("Server took {} to complete the request for '{}' ".format(str(finish - start), artist))
    new_file.write("\nThe response length was {} bytes ".format(str(length)))
    new_file.write("\nThe response was received on {} \n".format(str(datetime.datetime.now())))
    new_file.write("\n\n")
    new_file.close()

class RunningConnection:
    def __init__(self):
        # Initialise the socket and address
        self.sock = socket.socket(socket.AF_INET)
        server_address = ('localhost', 6666) #change port number if necessary. If changed here you should also change it in the server.py program.
        print('connecting to %s on port %s' % server_address)
        try:
            # Set a timeout for the connection to allow it to fail if another client is already connected
            self.sock.settimeout(10)
            # Attempt to connect to the server
            self.sock.connect(server_address)
            print("Waiting to connect to the server...")
            print(self.sock.recv(22).decode())
        except socket.timeout:
            # Catch a timeout error
            print("There was a timeout error, as another user is already connected to the server!")
            print("No other connections will be able to be made to the server whilst it is running.")
            exit()
        except socket.error:
            # Catch any other errors that may arise, such as the server not running
            print("There was an error connecting to the server as it is not available/running.")
            exit()


    # method to invoke basic authentication (username and password)
    def auth(self):
        # until authenticated is true, keep asking the user to provide a valid username and password
        authenticated = False
        while authenticated is False:
            username = input("Enter username ")  # Requests username from user
            password = input("Enter password ")  # Requests password from user
            while username is '' or password is '': # If no credentials are given
                print("ERROR: Missing username or password. Please retry")  # Throw error and retry
                username = input("Enter username ")  # Requests username from user
                password = input("Enter password ")  # Requests password from user
            self.sock.sendall(username.encode()) # sends username
            self.sock.sendall(password.encode()) # sends password
            data = self.sock.recv(1024)          # receives response from server
            if data.decode() == 'error':
                quit()
            # if the response from the server is not invalid (pass), then authenticate the user and proceed
            # .. to two-factor authentication.
            if data.decode() == 'lockout':       # If the response given is a lockout response
                print('*********************')
                print("You have had 3 failed attempts at login. Locking account.")
                break                            # Inform the client and terminate the client connection
            if data.decode() != 'Invalid':
                authenticated = True
                print(data.decode())
                RunningConnection.two_factor_auth(self)  # invokes the two-factor authentication method
            else:
            # authenticated is still false, therefore continue the loop
             print("Invalid credentials. Please retry.")


    # method for two-factor authentication (token authentication)
    def two_factor_auth(self):
        print('*** Two-factor-authentication Initialised: TOKEN RECOGNITION ***')
        data = self.sock.recv(1024)            # User receives data (token) from server
        print('Token received:')
        print('*********************')
        print(data.decode())                   # token decoded into an 6 digit number
        print('*********************')
        authenticated = False
        # until the user enters a valid 6 digit code supplied by the server, then keep asking the user to enter
        # .. a valid token
        while authenticated is False:
            token = input("Enter token ")       # Requests server token
            while token is '':                  # If no token is given
                print("ERROR: No token given. Please retry")  # Throw error and retry
                token = input("Enter token ")  # Requests server token
            self.sock.sendall(token.encode())   # client sends token for verification
            data = self.sock.recv(1024)         # response received
            if data.decode() == 'error':        # if the response is error, the quite/close the app
                exit()
            if data.decode() == 'lockout':
                print('*********************')
                print("You have had 3 failed attempts at login. Locking account.")
                break
            # if the response is not invalid (valid), then authenticate the user and initial multi-factor auth
            if data.decode() != 'Invalid authentication.':
                print (data.decode())
                authenticated = True
                RunningConnection.multi_factor_authentication(self) # initiates multi-factor authentication
            else:
                print("Invalid two-factor-authentication. Please retry.")  # inform the user of an invalid authentication


    # method for multi-factor authentication (facial/image recognition)
    def multi_factor_authentication(self):
        print('*** Multi-factor-authentication Initialised: FACIAL RECOGNITION ***')
        authenticated = False
        # until a true value is given, keep asking the user to provide an image (regardless of the filename)
        # .. which is VISUALLY IDENTICAL to the image stored for them on the server
        while authenticated is False:
            # Requests user to provide an image in the form of a filename. E.g alt2.jpg
            image_upload = input("Enter filename of image on server ")
            while image_upload is '':      # if no image is given
                print("ERROR: No image filename given. Please retry")  # Throw error and retry
                image_upload = input("Enter filename of image on server  ")  # Requests server token
            self.sock.sendall(image_upload.encode())
            data = self.sock.recv(1024)                  # Waits to receive data
            if data.decode() == 'error':  # if the response is error, the quite/close the app
                exit()
            if data.decode() == 'lockout':
                print('*********************')
                print("You have had 3 failed attempts at login. Locking account.")
                break
            # if the response is not equal to 'invalid' (valid - a matching image), then authenticate the user.
            if data.decode() != 'Invalid authentication.':
                print(data.decode())
                authenticated = True
                RunningConnection.__init__(self)     # re-initiates connection
                RunningConnection.running(self)      # initiates the running method to allow the user to search for songs
            else:
                # if the images do not match, then inform the user of a invalid authentication
                print("Invalid multi-factor-authentication. Please retry.")


    def running(self):
        try:
            # Loop until the user inputs close or quit
            while 1:
                message = ''
                # Loop until the user inputs a message (No blank message)
                while message == '':
                    message = input("What artist would you like to search for? ") # Getting the name of an artists from a user
                    
                    if message == '': # simple error checking
                        print("ERROR: You should not send an empty message!")

                # Send the message to the server
                self.sock.sendall(message.encode())
                # Set the time that the message was sent
                start_time = datetime.datetime.now()

                # If the user input 'quit' or 'close', exit the while loop and close the connection
                if message == 'quit' or message == 'close':
                    print("Disconnecting!")
                    break

                # Output what the user is sending to the terminal
                print('You are sending "%s" message to the server: ' % message)

                # Receive a response from the server
                data = self.sock.recv(39)
                print(data.decode())
                data = self.sock.recv(1024)

                # 'error' is returned if no songs are found, otherwise the songs are displayed on the terminal
                if data.decode() == 'error':
                    print("There are no songs under the author", message)
                else:
                    print("The songs made by ", message, "are:")
                    print(data.decode())

                # Set the finish time, and call the function to write to the log file
                finish_time = datetime.datetime.now()
                write_response(start_time, finish_time, message, len(data))
                print("\nType in 'quit' to disconnect, or 'close' to quit and shut down the server!\n")
        except socket.timeout:
            # Catch a timeout error
            print("There was a timeout error!")
            self.sock.sendall('quit'.encode())
            self.sock.close()
            exit()
        except socket.error:
            # Catch any other errors that may arise, such as the server not running
            print("There was an error with the connection!")
            exit()
        finally:
            # Close the connection
            self.sock.close()

connect_client = RunningConnection()
connect_client.auth()   # auth is now the first method launched