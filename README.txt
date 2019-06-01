
*** IMPORTANT NOTICE ***
- The Python library 'Pillow' must be installed to allow the newly added imports on the program to work. 
- Pillow was used to implement the multi-factor authentication functionality; this was used for biometric facial recognition simulation.
- Pillow can be installed using: 'pip install pillow'


---------- Running on Windows/Linux via command line: ----------

This system is compatible with Python version 3.5 and above.

********** Initialising and starting the system **********
Step one: start the server program first
- open a command line
- navigate to the folder where the system is stored
- run "python server.py"

Step two: start the client program
- open a different command line
- navigate to the same folder where the system is stored
- run "python client.py"


********** Basic Authentication **********
To login to the system using basic authentication, enter a valid username and password using any of the following accounts:
- Account 1 (RECOMMENDED): username=admin password=123          IGNORE FOR NOW... =>  BiometricImagePicture = henry.jpg
- Account 2: username=sv78gh password=Password2!                IGNORE FOR NOW... =>  BiometricImagePicture = sterling.jpg
*Account information for users can be found in server.py
*Be careful, 3 failed login attempts will lock a user out and close the client connection. The server connection will still remain.


********** Two-factor Authentication **********
Once authenticated using basic authentication, the server will send you a token to be re-authenticated.
- Enter the code on the token supplied by the server
*Be careful, 3 failed login attempts will lock a user out and close the client connection. The server connection will still remain.


********** Multi-factor Authentication **********
Once authenticated using two-factor authentication, you will be asked to supply an image of yourself for a final layer of authentication.
- To do this, firstly check in the 'client-server-no-authentication' folder, and locate an image file which is visually identical to the 
  .. image associated with the account you have logged in with.
- For example, if you have logged in with 'Account 1' which has an associated BiometricImagePicture of 'henry.jpg' as mentioned above,
  ..  then locate an image in the 'client-server-no-authentication' folder which is identical to the image 'henry.jpg' but has a DIFFERENT FILENAME.
- For all intents and purposes, if you are logging in with Account 1, then use 'alt2.jpg' as the image to be authenticated with.
*Be careful, 3 failed login attempts will lock a user out and close the client connection. The server connection will still remain.


********** using the system **********
- Once the server and the client programs are running, you can search for songs 
associate with specific artists via the client program.
- The client prompts you to enter the name of an artist. Enter a name from the 
songs.txt file, e.g., ABBA. The client then returns the songs for Abba


********** Shuting down the system **********
- To close client connection with the server, but leaving server running 
(e.g., allow another client to connect) enter 'quit' from the client's command line window.
- To close the connection and abort the system enter 'close' form the client's command line window

Notes:
- Log files do not get overwritten! Delete them to get fresh log files.
- If server is forcibly closed then log file will not be written.