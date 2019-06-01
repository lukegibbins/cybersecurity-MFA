import socket
import re
import datetime
import random
import string
from PIL import Image  # PIL import is used for image handling. Installed using pip install pillow

# User account information. This stores a user's username, password and profile image.
# The user's profile image references an image file stored in the 'client-server-no-authentication' folder
class Accounts:
  def __init__(self, username, password, image):
    self.username = username
    self.password = password
    self.image = image

# Initialising account data
a1 = Accounts("admin", "123", "henry.jpg")
a2 = Accounts("sv78gh", "Password2!", "sterling.jpg")

# Adding accounts to an account list
accountList = []
accountList.append(a1)
accountList.append(a2)

def write_startup():
    # Write information to the log file 'server.log'
    new_file = open("server.log", 'a+')
    new_file.write("Server started {} \n".format(str(datetime.datetime.now())))
    new_file.close()

def write_connection():
    # Write information to the log file
    new_file = open("server.log", 'a+')
    new_file.write("Client connected at {} ".format(str(datetime.datetime.now())))
    new_file.write("\nConnection was successful! ")
    new_file.close()

def write_disconnection(start):
    # Write information to the log file
    new_file = open("server.log", 'a+')
    connection = datetime.datetime.now() - start
    new_file.write("\nClient was connected for {} \n".format(str(connection)))
    new_file.write("\n")
    new_file.close()

def write_data(data):
    # Write information to the log file
    new_file = open("server.log", 'a+')
    new_file.write("\nClient requested songs under the artist name {} ".format(data))
    new_file.close()

class ReadingFile:
    def __init__(self):
        # Create regex that will be used for reading the file 'songs.txt
        self.start_line = re.compile('\S')
        self.end_line = re.compile('\d')

    def read_file(self, f_name):
        all_songs_dictionary = {}
        new_file = open(f_name, 'r')
        i = 0
        # Adds 100 songs to the dictionary
        while i < 100:
            hold = new_file.readline()
            # Calls the check function
            test = self.check(hold)

            # Adds the song and artist/artists to the dictionary
            if test == 'full':
                song = hold[4:34].strip()
                author = hold[35:-6].strip()
                for x in author.split('/'):
                    for y in x.split(' featuring '):
                        all_songs_dictionary.setdefault(y, []).append(song)
                i += 1
            elif test == 'name':
                song = hold[4:-1].strip()
                author = new_file.readline()[:-6].strip()
                all_songs_dictionary.setdefault(author, []).append(song)
                i += 1
        new_file.close()
        return all_songs_dictionary

    def check(self, full_line):
        # Uses the regex created previously to check that a line is valid
        if self.start_line.match(full_line[:1]):
            if self.end_line.match(full_line[-4:]):
                # This is when a full line has all the information
                return 'full'
            # This is when 2 lines contain all the information
            return 'name'
        else:
            # This is when the line is not required
            return 'none'


class Server:
    signed_in = "" # this variable determines which user is signed in after basic authentication.
    lockout_counter = 0  # counts how many failed attempts the user has had
    def __init__(self, songs):
        # Initialise the socket and address
        self.server_socket = socket.socket(socket.AF_INET)
        server_address = ('localhost', 6666) ## change if necessary, if changed here you should also change in the client.py program.
        print('Starting up on %s port %s' % server_address)
        try:
            # Attempt to start the server
            self.server_socket.bind(server_address)
            write_startup()
            # Listen for a connection
            self.server_socket.listen(0)
        except socket.error:
            # Catch any errors, such as the port being in use
            print("The server failed to initialise as the socket is already in use!")
            exit()
        self.song_dictionary = songs


    # method to run basic authentication (username and password)
    def auth(self):
        print('Waiting for a connection')
        connection, client_address = self.server_socket.accept()   # makes initial connection
        connection.send("Successful connection!".encode())
        authenticated = False    # initialises the authenticated variable to false
        match = False            # initialises the match variable to false
        # while the user is not authenticated, keep asking for a username and password until a match is found
        while authenticated is False:
            username = connection.recv(1024).decode()    # received username from client
            password = connection.recv(1024).decode()    # received password from client
            if password == 'quit' or password == 'close': # if close or quit entered, exit program.
                connection.send('error'.encode())
                print('Connection terminated by client.')
                Server.auth(self)
            # for each account, check to see whether there is a match from the received username and password
            for elem in accountList:
                if elem.username == username and elem.password == password:  # Iterate through the list of accounts to to find a match
                    match = True;  # if a match is found, authenticated == true, else false
                    Server.signed_in = elem.image  # associates the user profile image to the user currently signed in
            if match:
                # if a match is found, notify the client, set authentication to true
                connection.send('Username and password successfully verified!'.encode())
                print('Username and password successfully verified!')
                authenticated = True
                # initiate two-factor authentication protocol
                running_server.two_factor_auth(connection)
            else:
                print("Invalid credentials.")
                Server.lockout_counter += 1
                if Server.lockout_counter == 3:             # if account is locked out 3 times
                    connection.send('lockout'.encode())     # inform the user the account is locked out
                    print('*********************')
                    print("Suspicious activity. Locking user account.")
                    Server.lockout_counter = 0               # reset locked counter to 0
                    Server.auth(self)                        # restart the main method with the connection
                else:
                    connection.send('Invalid'.encode())  # inform the user of bad credentials



    # method to run two-factor authentication (token authentication)
    def two_factor_auth(self, connection):
        # sets authentication to false and assigns the client a randomly generated 6 digit token
        print('*** Two-factor-authentication Initialised ***')
        authenticated = False
        token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))  # 6 digit token
        print('Token assigned:')
        print('*********************')
        print(token)
        print('*********************')
        connection.send(token.encode())
        # while authentication is false, keep asking the user for the correct token which has been supplied
        while authenticated is False:
            user_token = connection.recv(1024).decode()     # token received back from client
            if user_token == 'quit' or user_token == 'close': # if close or quit entered, exit program.
                connection.send('error'.encode())
                print('Connection terminated by client.')
                Server.auth(self)
            # if the token matches the token which was sent, then successful authentication
            # multi-factor authentication is then initiated
            if user_token == token:
                print('Two-factor-authentication successful...')
                connection.send('Authentication successful.'.encode())
                authenticated = True
                running_server.multi_factor_auth(connection)    # multi-factor authentication initiated
            else:
                # if token does not match, inform the client of an invalid authentication
                Server.lockout_counter += 1
                if Server.lockout_counter == 3:
                    print('*********************')
                    print("Suspicious activity. Locking user account.")
                    connection.send('lockout'.encode())  # inform the user of bad credentials
                    Server.lockout_counter = 0
                    Server.auth(self)
                connection.send('Invalid authentication.'.encode())
                print("Invalid two-factor-authentication.")


    # method to run multi-factor authentication (facial/image recognition)
    def multi_factor_auth(self, connection):
        print('*** Multi-factor-authentication Initialised ***')
        authenticated = False
        # while authenticated is false, keep asking for the correct recognised image from the user
        while authenticated is False:
            image_upload_filename = connection.recv(1024).decode()    # receive the client's image filename
            if image_upload_filename == 'quit' or image_upload_filename == 'close': # if close or quit entered, exit program.
                connection.send('error'.encode())
                print('Connection terminated by client.')
                Server.auth(self)
            try:
                # get the client's uploaded image and the image stored on file for the user trying to login,
                # .. and then compared the images pixels to verify whether the images match, regardless of their file names
                uploaded_image = Image.open(image_upload_filename)
                image_from_authenticated_user = Image.open(Server.signed_in)
                is_validated = PixelCompare(uploaded_image, image_from_authenticated_user, "s")  # returns true or false
                print('Facial recognition status: "%s" ' % is_validated)
                # if the users image matches, then run the method for listening for songs; authentication successful
                if is_validated:
                    print('Multi-factor-authentication successful...')
                    connection.send('Authentication successful.'.encode())
                    authenticated = True
                    running_server.running() # method for listening for songs
                # if the images do not match, then inform the user of a invalid authentication. Continue with loop
                else:
                    Server.lockout_counter += 1
                    if Server.lockout_counter == 3:
                        print('*********************')
                        print("Suspicious activity. Locking user account.")
                        connection.send('lockout'.encode())  # inform the user of bad credentials
                        Server.lockout_counter = 0
                        Server.auth(self)
                    connection.send('Invalid authentication.'.encode())
                    print("Invalid multi-factor-authentication.")
                # catch any image uploads which are not in fact images to prevent errors
            except IOError:
                connection.send('Invalid authentication.'.encode())
                print("Invalid multi-factor-authentication.")


    def running(self):
        # Wait for a connection
        # The while loops means that the server will keep listening after a client disconnects, unless they send 'close'
        while 1:
            print('Waiting for a connection')
            connection, client_address = self.server_socket.accept()
            connection.send("Successful connection!".encode())
            try:
                # Output that a client has connected
                print('connection from', client_address)
                write_connection()
                # Set the time that the client connected
                start_time = datetime.datetime.now()
                # Loop until the client disconnects from the server
                while 1:
                    # Receive information from the client
                    data = connection.recv(1024).decode()
                    if (data != 'quit') and (data != 'close'):
                        print('received "%s" ' % data)
                        connection.send('Your request was successfully received!'.encode())
                        write_data(data)
                        # Check the dictionary for the requested artist name
                        # If it exists, get all their songs and return them to the user
                        if data in self.song_dictionary:
                            songs = ''
                            for i in range(len(self.song_dictionary.get(data))):
                                songs += self.song_dictionary.get(data)[i] + ', '
                            songs = songs[:-2]
                            print('sending data back to the client')
                            connection.send(songs.encode())
                            print("Sent", songs)
                        # If it doesn't exist return 'error' which tells the client that the artist does not exist
                        else:
                            print('sending data back to the client')
                            connection.send('error'.encode())
                    else:
                        # Exit the while loop
                        break
                # Write how long the client was connected for
                write_disconnection(start_time)
            except socket.error:
                # Catch any errors and safely close the connection with the client
                print("There was an error with the connection, and it was forcibly closed.")
                write_disconnection(start_time)
                connection.close()
                data = ''
            finally:
                if data == 'close':
                    print('Closing the connection and the server')
                    # Close the connection
                    connection.close()
                    # Exit the main While loop, so the server does not listen for a new client
                    break
                else:
                    print('Closing the connection')
                    # Close the connection
                    connection.close()
                    # The server continues to listen for a new client due to the While loop
                    

# method used to compare pixels of images
# this will return true is the pixels match and false if they don't
# referenced from https://www.cs.hmc.edu/~jlevin/ImageCompare.py
def PixelCompare(im1, im2, mode="pct", alpha=.01):
    if im1.size == im2.size and im1.mode == im2.mode:
        randPix = im1.getpixel((0, 0))
        maxSum = []
        diff = []
        for channel in range(len(randPix)):
            diff += [0.0]
            maxSum += [0.0]
        width = im1.size[0]
        height = im1.size[1]
        for i in range(width):
            for j in range(height):
                pixel1 = im1.getpixel((i, j))
                pixel2 = im2.getpixel((i, j))
                for channel in range(len(randPix)):
                    maxSum[channel] += 255
                    diff[channel] += abs(pixel1[channel] - pixel2[channel])
        if mode == "pct":
            ret = ()
            for channel in range(len(randPix)):
                ret += (diff[channel] / maxSum[channel],)
            return ret
        for channel in range(len(randPix)):
            if diff[channel] > alpha * maxSum[channel]:
                return False
        return True
    return False

read = ReadingFile()
dictionary = read.read_file("songs.txt")
running_server = Server(dictionary)
running_server.auth() # use basic authentication as the first running method



