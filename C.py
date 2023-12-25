import cv2, imutils, socket
import numpy as np
import time, os
import base64
import random

#Stimulation HERE
Simulate = True

# testing 0% -> 20% -> 50% -> 80%
def simulate_packet_loss():
    # Simulate packet loss (start from dropping 20% of packets)
	return random.random() < 0.8

#Stimulation HERE

BUFF_SIZE = 65536

BREAK = False
client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print(host_ip)
port = 9699
message = b'Hello'
client_socket.sendto(message,(host_ip,port))



cv2.namedWindow('receiving video....')        
cv2.moveWindow('receiving video....', 750,120) 
fps,st,frames_to_count,cnt = (0,0,20,0)
while True and not BREAK:
	try:
		packet,_ = client_socket.recvfrom(BUFF_SIZE)
		if(packet.decode() == "-1"):
			BREAK = True
			break
		data = base64.b64decode(packet)
		npdata = np.fromstring(data,dtype=np.uint8)
		frame = cv2.imdecode(npdata,1)

		# Simulate packet loss
		if(Simulate):
			if simulate_packet_loss():
				print("Packet dropped")
				continue
		#frame = cv2.putText(frame,'FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
		cv2.imshow("receiving video....",frame)
		key = cv2.waitKey(1) & 0xFF
		
		if key == ord('q'):
			BREAK = True
			client_socket.sendto(b"-1",(host_ip,port))
			break

		if cnt == frames_to_count:
			try:
				fps = round(frames_to_count/(time.time()-st),1)
				st=time.time()
				cnt=0
			except:
				pass
		cnt+=1
	#handle keyboard interrupt	
	except KeyboardInterrupt:
		BREAK = True
	
client_socket.sendto(b"-1",(host_ip,port))		
client_socket.close()
print("CLIENT CLOSED")
cv2.destroyAllWindows() 

