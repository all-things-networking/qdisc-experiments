import time
from client1 import send_data  # Reuse same function

time.sleep(5)  # Delay before starting
send_data(35)  # Second session tries to get 35 KB/s
