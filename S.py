#sudo sysctl -w net.inet.udp.maxdgram=65535
import cv2, imutils, socket
import time
import base64
import threading
import random
import queue

#Stimulation HERE
Simulate = False

# testing 0% -> 20% -> 50% -> 80%
def simulate_packet_loss():
    # Simulate packet loss (start from dropping 20% of packets)
	return random.random() < 0.2

#Stimulation HERE
global BREAK 
BREAK = False
q = queue.Queue(maxsize=10)

filename =  'test.mp4'
vid = cv2.VideoCapture(filename)
FPS = vid.get(cv2.CAP_PROP_FPS)

BUFF_SIZE = 65536
server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print(host_ip)
port = 9699
socket_address = (host_ip,port)
server_socket.bind(socket_address)
print('Listening at:',socket_address)



TS = (1/FPS)

print('FPS:',FPS,TS)
# totalNoFrames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
# durationInSeconds = float(totalNoFrames) / float(FPS)
# d=vid.get(cv2.CAP_PROP_POS_MSEC)
#print(durationInSeconds,d)

def video_stream_gen():
	global BREAK
	WIDTH=600
	while(vid.isOpened()):
		if BREAK:
			break
		try:
			_,frame = vid.read()
			frame = imutils.resize(frame,width=WIDTH)
			q.put(frame)
		except:
			print('Player Closed')
			BREAK=True
			break   
	       
	vid.release()
	
	
	



t1 = threading.Thread(target=video_stream_gen, args=())
t1.start()


fps,st,frames_to_count,cnt = (0,0,1,0)
cv2.namedWindow('sending video.....')        
cv2.moveWindow('sending video.....', 120,120) 

while True and not BREAK:
	msg,client_addr = server_socket.recvfrom(BUFF_SIZE)
	#print('GOT connection from ',type(msg.decode()))
	WIDTH=400
	server_socket.setblocking(False)

	while True:
		try:
			try:
				msg,_ = server_socket.recvfrom(BUFF_SIZE)
			except:
				if BREAK:
					break
		
			if msg and (msg.decode() == "-1"):
				#print("Reveived " + msg.decode())
				BREAK = True	
			
			frame = q.get()


			# Simulate packet loss
			if(Simulate):
				if simulate_packet_loss():
					print("Packet dropped")
					continue
				
			#print("packet NOT lose")
				

			encoded,buffer = cv2.imencode('.jpeg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
			message = base64.b64encode(buffer)
			server_socket.sendto(message,client_addr)


			#frame = cv2.putText(frame,'FPS: '+str(round(fps,1)),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
			if cnt == frames_to_count:
				try:
					fps = (frames_to_count/(time.time()-st))
					st=time.time()
					cnt=0
					if fps>FPS:
						TS+=0.001
					elif fps<FPS:
						TS-=0.001
					else:
						pass
				except:
					pass
			cnt+=1


			cv2.imshow('sending video.....', frame)


			key = cv2.waitKey(int(1000*TS)) & 0xFF	
			if key == ord('q'):
				BREAK = True
				break
		#handle keyboard interrupt	
		except KeyboardInterrupt:
			BREAK = True


q.get()
#t1.join()
server_socket.sendto(b"-1",client_addr)
server_socket.close()
print("SERVER CLOSED")
time.sleep(0.0745)		

